import sys
import csv
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from retrieval import search_text, search_screenshots
from confidence import label_confidence

TEST_QUERIES = Path(__file__).resolve().parent / "test_queries.csv"
RESULTS_OUT = Path(__file__).resolve().parent / "results" / "eval_results.csv"


def source_hit(expected_sources, retrieved_paths):
    expected_list = [s.strip() for s in expected_sources.split(";")]
    for expected in expected_list:
        for retrieved in retrieved_paths:
            if expected in retrieved:
                return True
    return False


def run_eval():
    RESULTS_OUT.parent.mkdir(parents=True, exist_ok=True)
    rows_out = []

    with open(TEST_QUERIES, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            query = row["query"]
            expected_sources = row["expected_primary_source"]

            text_matches = search_text(query, top_k=3)
            screenshot_matches = search_screenshots(query, top_k=2)

            top_1_source = text_matches[0]["file_path"] if text_matches else ""
            top_1_screenshot = screenshot_matches[0]["file_path"] if screenshot_matches else ""
            hit_at_1 = source_hit(expected_sources, [top_1_source, top_1_screenshot])
            top_3_sources = [m["file_path"] for m in text_matches]
            top_3_sources += [m["file_path"] for m in screenshot_matches]

            confidence = label_confidence(text_matches[0]["similarity"]) if text_matches else "Low"
            hit_at_3 = source_hit(expected_sources, top_3_sources)

            rows_out.append({
                "query_id": row["query_id"],
                "query": query,
                "expected_primary_source": expected_sources,
                "top_1_source": top_1_source,
                "top_1_screenshot": top_1_screenshot,
                "hit_at_1": hit_at_1,
                "top_3_sources": "; ".join(top_3_sources),
                "hit_at_3": hit_at_3,
                "confidence_label": confidence,
                "output_type": row["output_type"],
            })

    with open(RESULTS_OUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows_out[0].keys())
        writer.writeheader()
        writer.writerows(rows_out)

    hits_1 = sum(1 for r in rows_out if r["hit_at_1"])
    hits_3 = sum(1 for r in rows_out if r["hit_at_3"])
    total = len(rows_out)
    print(f"precision@1: {hits_1}/{total} = {hits_1/total:.2f}")
    print(f"precision@3: {hits_3}/{total} = {hits_3/total:.2f}")
    print(f"results written to {RESULTS_OUT}")


if __name__ == "__main__":
    run_eval()