# app/semantic/ingest_data.py
from typing import List, Dict
import uuid
import math
from app.semantic.vector_store import add_documents

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200):
    # chunking by characters (or you can chunk by tokens using tiktoken/tokenizers)
    start = 0
    chunks = []
    text_len = len(text)
    while start < text_len:
        end = min(start + chunk_size, text_len)
        chunk = text[start:end]
        chunks.append((start, end, chunk))
        if end == text_len:
            break
        start = end - overlap
    return chunks

def ingest_documents(sources: List[Dict], chunk_size: int = 1000, overlap: int = 200):
    # sources: [{ "id": "doc1", "text": "long text", "metadata": {...}}, ...]
    docs_to_add = []
    id_counter = 0
    for src in sources:
        sid = src.get("id", str(uuid.uuid4()))
        chunks = chunk_text(src["text"], chunk_size=chunk_size, overlap=overlap)
        for idx, (s, e, chunk) in enumerate(chunks):
            id_counter += 1
            docs_to_add.append({
                "id": id_counter,
                "text": chunk,
                "metadata": {
                    "source_id": sid,
                    "chunk_index": idx,
                    "char_start": s,
                    "char_end": e,
                    **src.get("metadata", {})
                }
            })
    add_documents(docs_to_add)
