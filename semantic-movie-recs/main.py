import argparse
from sentence_transformers import SentenceTransformer
from index_manager import EndeeClient

# Configuration
INDEX_NAME = "movies"
MODEL_NAME = "all-MiniLM-L6-v2"

def search_movies(query, limit=3):
    client = EndeeClient()
    
    # 1. Check health
    if not client.check_health():
        print("Error: Could not connect to Endee server.")
        return

    # 2. Load model
    model = SentenceTransformer(MODEL_NAME)

    # 3. Generate query vector
    print(f"Searching for: '{query}'...")
    query_vector = model.encode(query).tolist()

    # 4. Search Endee
    results = client.search(INDEX_NAME, query_vector, limit=limit)

    if not results:
        print("No matches found or index does not exist.")
        return

    # 5. Display results
    print(f"\nTop {len(results)} matches:")
    print("-" * 50)
    for idx, res in enumerate(results):
        payload = res.get("payload", {})
        score = res.get("score", 0)
        print(f"{idx+1}. {payload.get('title')} ({payload.get('year')})")
        print(f"   Genre: {payload.get('genre')}")
        print(f"   Similarity Score: {score:.4f}")
        print(f"   Overview: {payload.get('overview')[:150]}...")
        print("-" * 50)

def main():
    parser = argparse.ArgumentParser(description="CinemaMind - Semantic Movie Search")
    parser.add_argument("query", type=str, help="The search query (e.g., 'space exploration')")
    parser.add_argument("--limit", type=int, default=3, help="Number of results to return")
    
    args = parser.parse_args()
    
    try:
        search_movies(args.query, args.limit)
    except KeyboardInterrupt:
        print("\nExiting...")

if __name__ == "__main__":
    main()
