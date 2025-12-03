from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
import os

QDRANT_HOST = os.getenv("QDRANT_HOST", "qdrant")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))

COLLECTION_NAME = "legal_docs"


def get_qdrant_client() -> QdrantClient:
    return QdrantClient(
        url=f"http://{QDRANT_HOST}:{QDRANT_PORT}",
        timeout=60,
    )


def create_collection(vector_size: int = 384) -> None:
    client = get_qdrant_client()

    # Qdrant 1.6.1 does NOT have `collection_exists()`
    collections = client.get_collections().collections
    exists = any(c.name == COLLECTION_NAME for c in collections)

    if not exists:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE
            )
        )
        print(f"Collection '{COLLECTION_NAME}' created.")
    else:
        print(f"Collection '{COLLECTION_NAME}' already exists.")
