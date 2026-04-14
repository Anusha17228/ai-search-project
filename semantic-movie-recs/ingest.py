import json
import os
from sentence_transformers import SentenceTransformer
from index_manager import EndeeClient
from tqdm import tqdm

# Configuration
INDEX_NAME = "movies"
DIMENSION = 384  # for all-MiniLM-L6-v2
MODEL_NAME = "all-MiniLM-L6-v2"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(SCRIPT_DIR, "data", "movies.json")

def main():
    # Initialize Endee Client
    client = EndeeClient()
    
    # 1. Check health
    print("Checking Endee server health...")
    if not client.check_health():
        print("Error: Could not connect to Endee server. Make sure it is running on port 8080.")
        return

    # 2. Load model
    print(f"Loading embedding model: {MODEL_NAME}...")
    model = SentenceTransformer(MODEL_NAME)

    # 3. Create index if it doesn't exist
    indexes = client.list_indexes()
    if not any(idx.get("name") == INDEX_NAME for idx in indexes):
        print(f"Creating index '{INDEX_NAME}'...")
        client.create_index(INDEX_NAME, dimension=DIMENSION)
    else:
        print(f"Index '{INDEX_NAME}' already exists.")

    # 4. Load Data
    if not os.path.exists(DATA_PATH):
        print(f"Error: Data file not found at {DATA_PATH}")
        return

    with open(DATA_PATH, "r") as f:
        movies = json.load(f)

    # 5. Prepare vectors
    print(f"Generating embeddings for {len(movies)} movies...")
    vectors_to_upsert = []
    
    for movie in tqdm(movies):
        # We average the title and overview for a better semantic representation
        text_to_embed = f"{movie['title']}: {movie['overview']}"
        embedding = model.encode(text_to_embed).tolist()
        
        vectors_to_upsert.append({
            "id": movie["id"],
            "vector": embedding,
            "payload": {
                "title": movie["title"],
                "genre": movie["genre"],
                "year": movie["year"],
                "overview": movie["overview"]
            }
        })

    # 6. Ingest data
    print("Upserting vectors to Endee...")
    if client.upsert_vectors(INDEX_NAME, vectors_to_upsert):
        print("Successfully ingested movie data into Endee!")
    else:
        print("Failed to ingest data.")

if __name__ == "__main__":
    main()
