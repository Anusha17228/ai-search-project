import requests
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EndeeClient:
    def __init__(self, host="http://localhost:8080", auth_token=None):
        self.base_url = f"{host.rstrip('/')}/api/v1"
        self.headers = {"Content-Type": "application/json"}
        if auth_token:
            self.headers["Authorization"] = auth_token

    def check_health(self):
        """Check if the Endee server is running."""
        try:
            response = requests.get(f"{self.base_url}/health", headers=self.headers, timeout=5)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to connect to Endee: {e}")
            return None

    def create_index(self, index_name, dimension, metric="cosine", index_type="hnsw"):
        """Create a new vector index."""
        payload = {
            "name": index_name,
            "dimension": dimension,
            "metric": metric,
            "type": index_type
        }
        try:
            response = requests.post(f"{self.base_url}/index/create", headers=self.headers, json=payload)
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Error creating index: {e}")
            return False

    def list_indexes(self):
        """List all existing indexes."""
        try:
            response = requests.get(f"{self.base_url}/index/list", headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error listing indexes: {e}")
            return []

    def delete_index(self, index_name):
        """Delete an existing index."""
        payload = {"name": index_name}
        try:
            response = requests.post(f"{self.base_url}/index/delete", headers=self.headers, json=payload)
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Error deleting index: {e}")
            return False

    def upsert_vectors(self, index_name, vectors):
        """
        Upsert a list of vectors into an index.
        vectors: list of dicts with {"id": str, "vector": list[float], "payload": dict}
        """
        payload = {
            "index_name": index_name,
            "vectors": vectors
        }
        try:
            response = requests.post(f"{self.base_url}/vector/upsert", headers=self.headers, json=payload)
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Error upserting vectors: {e}")
            return False

    def search(self, index_name, vector, limit=5, filters=None):
        """Search for similar vectors."""
        payload = {
            "index_name": index_name,
            "vector": vector,
            "limit": limit
        }
        if filters:
            payload["filters"] = filters

        try:
            response = requests.post(f"{self.base_url}/vector/search", headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error during search: {e}")
            return []
