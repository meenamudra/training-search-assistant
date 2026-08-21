from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"

PDF_DIR = DATA_DIR / "documents" / "pdfs"
NOTES_DIR = DATA_DIR / "documents" / "notes"
SCREENSHOT_DIR = DATA_DIR / "screenshots"
METADATA_DIR = DATA_DIR / "metadata"

PUBLIC_TEXT_DIR = DATA_DIR / "public_sources" / "texts"
PUBLIC_SCREENSHOT_DIR = DATA_DIR / "public_sources" / "screenshots"

CORPUS_METADATA_CSV = METADATA_DIR / "corpus_metadata.csv"
SCREENSHOT_METADATA_CSV = METADATA_DIR / "screenshot_metadata.csv"

INDEX_DIR = ROOT_DIR / "index_store"
CHUNKS_JSONL = INDEX_DIR / "chunks.jsonl"
SCREENSHOT_RECORDS_JSONL = INDEX_DIR / "screenshot_records.jsonl"

CHROMA_PERSIST_DIR = str(INDEX_DIR / "chroma")
TEXT_COLLECTION_NAME = "training_text_chunks"
SCREENSHOT_COLLECTION_NAME = "training_screenshots"

CHUNK_SIZE_CHARS = 900
CHUNK_OVERLAP_CHARS = 150

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

TOP_K_TEXT = 5
TOP_K_SCREENSHOTS = 3

CONFIDENCE_HIGH_THRESHOLD = 0.20
CONFIDENCE_MEDIUM_THRESHOLD = 0.0

INDEX_DIR.mkdir(parents=True, exist_ok=True)