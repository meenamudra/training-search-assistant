from sentence_transformers import SentenceTransformer
import chromadb

from config import (
    CHROMA_PERSIST_DIR, TEXT_COLLECTION_NAME, SCREENSHOT_COLLECTION_NAME,
    EMBEDDING_MODEL_NAME, TOP_K_TEXT, TOP_K_SCREENSHOTS,
)

_model = None
_client = None


def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return _model


def get_client():
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    return _client


def search_text(query, top_k=TOP_K_TEXT):
    model = get_model()
    client = get_client()
    collection = client.get_collection(TEXT_COLLECTION_NAME)

    query_embedding = model.encode([query]).tolist()
    results = collection.query(query_embeddings=query_embedding, n_results=top_k)

    matches = []
    for i in range(len(results["ids"][0])):
        distance = results["distances"][0][i]
        similarity = 1 - distance
        matches.append({
            "chunk_id": results["ids"][0][i],
            "text": results["documents"][0][i],
            "similarity": similarity,
            **results["metadatas"][0][i],
        })
    return matches


def search_screenshots(query, top_k=TOP_K_SCREENSHOTS):
    model = get_model()
    client = get_client()
    collection = client.get_collection(SCREENSHOT_COLLECTION_NAME)

    query_embedding = model.encode([query]).tolist()
    results = collection.query(query_embeddings=query_embedding, n_results=top_k)

    matches = []
    for i in range(len(results["ids"][0])):
        distance = results["distances"][0][i]
        similarity = 1 - distance
        matches.append({
            "image_id": results["ids"][0][i],
            "manual_text": results["documents"][0][i],
            "similarity": similarity,
            **results["metadatas"][0][i],
        })
    return matches
