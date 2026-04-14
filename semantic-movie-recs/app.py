from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from sentence_transformers import SentenceTransformer
from index_manager import EndeeClient
import os

app = Flask(__name__, static_folder='static')
CORS(app)

# Configuration
INDEX_NAME = "movies"
MODEL_NAME = "all-MiniLM-L6-v2"

# Initialize Client and Model
client = EndeeClient()
model = SentenceTransformer(MODEL_NAME)

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def static_proxy(path):
    return send_from_directory(app.static_folder, path)

@app.route('/api/search', methods=['POST'])
def search():
    data = request.json
    query = data.get('query', '')
    limit = data.get('limit', 6)
    
    if not query:
        return jsonify([])

    try:
        # 1. Generate query vector
        query_vector = model.encode(query).tolist()

        # 2. Search Endee (Mock)
        results = client.search(INDEX_NAME, query_vector, limit=limit)
        
        return jsonify(results)
    except Exception as e:
        print(f"Search error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("CinemaMind Web Backend starting on http://localhost:5000")
    app.run(port=5000)
