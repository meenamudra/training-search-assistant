import json
import pandas as pd

from config import DATA_DIR, CORPUS_METADATA_CSV, CHUNKS_JSONL
from chunking import chunk_text


def extract_pdf_text(pdf_path):
    import fitz
    pages = []
    with fitz.open(pdf_path) as doc:
        for page_num, page in enumerate(doc, start=1):
            text = page.get_text("text")
            if text.strip():
                pages.append((page_num, text))
    return pages


def extract_note_text(note_path):
    return note_path.read_text(encoding="utf-8", errors="ignore")


def ingest_documents():
    df = pd.read_csv(CORPUS_METADATA_CSV)
    records = []
    skipped = []

    for _, row in df.iterrows():
        rel_path = row["file_path"]
        full_path = DATA_DIR / rel_path

        if not full_path.exists():
            skipped.append(rel_path)
            continue

        content_type = str(row.get("content_type", "")).lower()

        if content_type == "pdf":
            try:
                pages = extract_pdf_text(full_path)
            except Exception as exc:
                print(f"could not read {rel_path}: {exc}")
                skipped.append(rel_path)
                continue

            for page_num, page_text in pages:
                for chunk in chunk_text(page_text):
                    records.append({
                        "chunk_id": f"{row['record_id']}-p{page_num}-c{chunk.chunk_index}",
                        "record_id": row["record_id"],
                        "title": row["title"],
                        "file_path": rel_path,
                        "topic": row.get("topic", ""),
                        "document_type": row.get("document_type", ""),
                        "page_or_section": f"page {page_num}",
                        "text": chunk.text,
                    })

        elif content_type in ("markdown", "text", "html_text"):
            raw_text = extract_note_text(full_path)
            for chunk in chunk_text(raw_text):
                records.append({
                    "chunk_id": f"{row['record_id']}-c{chunk.chunk_index}",
                    "record_id": row["record_id"],
                    "title": row["title"],
                    "file_path": rel_path,
                    "topic": row.get("topic", ""),
                    "document_type": row.get("document_type", ""),
                    "page_or_section": f"section {chunk.chunk_index + 1}",
                    "text": chunk.text,
                })

    CHUNKS_JSONL.parent.mkdir(parents=True, exist_ok=True)
    with open(CHUNKS_JSONL, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"wrote {len(records)} chunks to {CHUNKS_JSONL}")
    if skipped:
        print(f"skipped {len(skipped)} file(s): {skipped}")


if __name__ == "__main__":
    ingest_documents()
