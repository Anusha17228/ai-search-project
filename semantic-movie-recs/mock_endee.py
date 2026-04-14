import flask
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import numpy as np
import uuid
import logging

app = Flask(__name__)
CORS(app)

# In-memory storage for indexes and vectors
# Structure: { index_name: { "dimension": int, "vectors": [ {id, vector, payload} ] } }
SAVE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "mock_index_db.json")
indexes = {}

def save_data():
    try:
        with open(SAVE_FILE, "w") as f:
            json.dump(indexes, f)
        logger.info(f"Data saved to {SAVE_FILE}")
    except Exception as e:
        logger.error(f"Failed to save data: {e}")

def load_data():
    global indexes
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r") as f:
                indexes = json.load(f)
            logger.info(f"Data loaded from {SAVE_FILE} ({len(indexes)} indexes)")
        except Exception as e:
            logger.error(f"Failed to load data: {e}")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mock-endee")

load_data()

@app.route("/api/v1/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "version": "mock-1.0"}), 200

@app.route("/api/v1/index/create", methods=["POST"])
def create_index():
    data = request.json
    name = data.get("name")
    dimension = data.get("dimension")
    if name in indexes:
        return jsonify({"error": f"Index {name} already exists"}), 400
    
    indexes[name] = {
        "dimension": dimension,
        "vectors": []
    }
    save_data()
    logger.info(f"Created index: {name} with dimension {dimension}")
    return jsonify({"status": "created"}), 201

@app.route("/api/v1/index/list", methods=["GET"])
def list_indexes():
    result = [{"name": name, "dimension": info["dimension"]} for name, info in indexes.items()]
    return jsonify(result), 200

@app.route("/api/v1/index/delete", methods=["POST"])
def delete_index():
    data = request.json
    name = data.get("name")
    if name in indexes:
        del indexes[name]
        save_data()
        return jsonify({"status": "deleted"}), 200
    return jsonify({"error": "not found"}), 404

@app.route("/api/v1/vector/upsert", methods=["POST"])
def upsert_vectors():
    data = request.json
    index_name = data.get("index_name")
    new_vectors = data.get("vectors", [])
    
    if index_name not in indexes:
        return jsonify({"error": "Index not found"}), 404
    
    # Simple upsert: update if id exists, otherwise append
    existing_ids = {v["id"]: i for i, v in enumerate(indexes[index_name]["vectors"])}
    
    for v in new_vectors:
        if v["id"] in existing_ids:
            indexes[index_name]["vectors"][existing_ids[v["id"]]] = v
        else:
            indexes[index_name]["vectors"].append(v)
            
    save_data()
    logger.info(f"Upserted {len(new_vectors)} vectors to {index_name}")
    return jsonify({"status": "success", "count": len(new_vectors)}), 200

@app.route("/api/v1/vector/search", methods=["POST"])
def search_vectors():
    data = request.json
    index_name = data.get("index_name")
    query_vector = np.array(data.get("vector"))
    limit = data.get("limit", 5)
    
    if index_name not in indexes:
        return jsonify({"error": "Index not found"}), 404
    
    vectors_info = indexes[index_name]["vectors"]
    if not vectors_info:
        return jsonify([]), 200
    
    # Calculate cosine similarity
    results = []
    for v in vectors_info:
        target_vector = np.array(v["vector"])
        # Cosine similarity: (A dot B) / (||A|| * ||B||)
        norm_a = np.linalg.norm(query_vector)
        norm_b = np.linalg.norm(target_vector)
        if norm_a == 0 or norm_b == 0:
            score = 0
        else:
            score = np.dot(query_vector, target_vector) / (norm_a * norm_b)
            
        results.append({
            "id": v["id"],
            "score": float(score),
            "payload": v.get("payload", {})
        })
    
    # Sort by score descending
    results.sort(key=lambda x: x["score"], reverse=True)
    return jsonify(results[:limit]), 200

if __name__ == "__main__":
    print("Starting Mock Endee Server on port 8080...")
    print("Press Ctrl+C to stop.")
    app.run(port=8080)
