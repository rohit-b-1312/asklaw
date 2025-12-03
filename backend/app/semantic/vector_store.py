from functools import lru_cache
from typing import List, Dict
import os

from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

from app.semantic.qdrant_setup import get_qdrant_client, COLLECTION_NAME


# ---------------------------
# Lazy load SentenceTransformer model
# ---------------------------
@lru_cache(maxsize=1)
def get_model() -> SentenceTransformer:
    model_name = os.getenv("SENTENCE_TRANSFORMER", "all-MiniLM-L6-v2")
    return SentenceTransformer(model_name)


# ---------------------------
# Lazy load Qdrant client
# ---------------------------
client: QdrantClient = get_qdrant_client()


# ---------------------------
# Prepare a Qdrant Point
# ---------------------------
def _prepare_point(doc: Dict) -> PointStruct:
    model = get_model()
    vector = model.encode(doc["text"]).tolist()

    payload = dict(doc.get("metadata", {}))
    payload.update({
        "text": doc["text"],
        "source_id": doc.get("source_id"),
    })

    return PointStruct(
        id=int(doc["id"]),
        vector=vector,
        payload=payload,
    )


# ---------------------------
# Add (upsert) documents to Qdrant
# ---------------------------
def add_documents(docs: List[Dict], batch_size: int = 64) -> None:
    points = [_prepare_point(d) for d in docs]

    for i in range(0, len(points), batch_size):
        batch = points[i:i + batch_size]
        client.upsert(
            collection_name=COLLECTION_NAME,
            points=batch,
        )


# ---------------------------
# Search Similar documents
# ---------------------------
def search_similar(query: str, top_k: int = 5):
    model = get_model()
    query_vector = model.encode(query).tolist()

    # qdrant-client 1.6.1 requires `.search()`
    result = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=top_k,
    )

    docs: List[str] = []
    metadata: List[Dict] = []

    for hit in result:
        payload = hit.payload or {}
        docs.append(payload.get("text", ""))
        metadata.append({**payload, "_score": hit.score})

    return docs, metadata
