import json
import pandas as pd

from config import DATA_DIR, SCREENSHOT_METADATA_CSV, SCREENSHOT_RECORDS_JSONL


def ingest_screenshots():
    df = pd.read_csv(SCREENSHOT_METADATA_CSV)
    records = []
    skipped = []

    for _, row in df.iterrows():
        rel_path = row["file_path"]
        full_path = DATA_DIR / rel_path

        if not full_path.exists():
            skipped.append(rel_path)
            continue

        records.append({
            "image_id": row["image_id"],
            "file_path": rel_path,
            "title": row["title"],
            "topic": row.get("topic", ""),
            "screen_area": row.get("screen_area", ""),
            "manual_text": row.get("manual_text", ""),
            "related_documents": row.get("related_documents", ""),
        })

    SCREENSHOT_RECORDS_JSONL.parent.mkdir(parents=True, exist_ok=True)
    with open(SCREENSHOT_RECORDS_JSONL, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"wrote {len(records)} screenshot records to {SCREENSHOT_RECORDS_JSONL}")
    if skipped:
        print(f"skipped {len(skipped)} file(s): {skipped}")


if __name__ == "__main__":
    ingest_screenshots()
