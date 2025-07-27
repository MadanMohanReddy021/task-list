from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
import os
from dotenv import load_dotenv

# Load env vars
load_dotenv()
MONGO_URL = os.getenv("MONGO_URL")

app = Flask(__name__)
CORS(app)  # To allow frontend access

# MongoDB setup
client = MongoClient(MONGO_URL)
db = client["task_db"]
tasks = db["tasks"]

# Helper: convert Mongo document to JSON-serializable
def serialize_task(task):
    return {
        "id": str(task["_id"]),
        "title": task["title"],
        "deadline": task["deadline"],
        "completed": task["completed"]
    }

# 1. Add a task
@app.route('/tasks', methods=['POST'])
def add_task():
    data = request.get_json()
    title = data.get("title")
    deadline = data.get("deadline")

    if not title or not deadline:
        return jsonify({"error": "Title and deadline are required"}), 400

    task = {
        "title": title,
        "deadline": deadline,
        "completed": False
    }
    result = tasks.insert_one(task)
    task["_id"] = result.inserted_id  # add _id to use serialize_task
    return jsonify(serialize_task(task)), 201

# 2. Get active tasks
@app.route('/tasks/active', methods=['GET'])
def get_active_tasks():
    active_tasks = tasks.find({"completed": False})
    return jsonify([serialize_task(t) for t in active_tasks])

# 3. Get all tasks
@app.route('/tasks/all', methods=['GET'])
def get_all_tasks():
    all_tasks = tasks.find()
    return jsonify([serialize_task(t) for t in all_tasks])

# 4. Mark task as complete
@app.route('/tasks/<task_id>/complete', methods=['PUT'])
def complete_task(task_id):
    result = tasks.update_one(
        {"_id": ObjectId(task_id)},
        {"$set": {"completed": True}}
    )
    if result.modified_count == 0:
        return jsonify({"error": "Task not found or already completed"}), 404
    return jsonify({"message": "Task marked as completed"}), 200

if __name__ == '__main__':
    app.run(debug=True)
