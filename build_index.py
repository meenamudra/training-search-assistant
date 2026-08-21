import json
from sentence_transformers import SentenceTransformer
import chromadb

from config import (
    CHUNKS_JSONL, SCREENSHOT_RECORDS_JSONL, CHROMA_PERSIST_DIR,
    TEXT_COLLECTION_NAME, SCREENSHOT_COLLECTION_NAME, EMBEDDING_MODEL_NAME,
)


def load_jsonl(path):
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            records.append(json.loads(line))
    return records


def build_index():
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)

    client.delete_collection(TEXT_COLLECTION_NAME) if TEXT_COLLECTION_NAME in [c.name for c in client.list_collections()] else None
    client.delete_collection(SCREENSHOT_COLLECTION_NAME) if SCREENSHOT_COLLECTION_NAME in [c.name for c in client.list_collections()] else None

    text_collection = client.create_collection(TEXT_COLLECTION_NAME)
    screenshot_collection = client.create_collection(SCREENSHOT_COLLECTION_NAME)

    chunks = load_jsonl(CHUNKS_JSONL)
    chunk_texts = [c["text"] for c in chunks]
    chunk_embeddings = model.encode(chunk_texts).tolist()

    text_collection.add(
        ids=[c["chunk_id"] for c in chunks],
        embeddings=chunk_embeddings,
        documents=chunk_texts,
        metadatas=[{
            "record_id": c["record_id"],
            "title": c["title"],
            "file_path": c["file_path"],
            "topic": c["topic"],
            "document_type": c["document_type"],
            "page_or_section": c["page_or_section"],
        } for c in chunks],
    )

    screenshots = load_jsonl(SCREENSHOT_RECORDS_JSONL)
    screenshot_texts = [s["manual_text"] for s in screenshots]
    screenshot_embeddings = model.encode(screenshot_texts).tolist()

    screenshot_collection.add(
        ids=[s["image_id"] for s in screenshots],
        embeddings=screenshot_embeddings,
        documents=screenshot_texts,
        metadatas=[{
            "title": s["title"],
            "file_path": s["file_path"],
            "topic": s["topic"],
            "related_documents": s["related_documents"],
        } for s in screenshots],
    )

    print(f"indexed {len(chunks)} text chunks and {len(screenshots)} screenshots")


if __name__ == "__main__":
    build_index()