# Internal Training Content Search Assistant

A local search tool for operations training content — PDFs, SOP notes, and screenshots. Type a question, get back the right source with a confidence label. It's a retrieval tool, not a chatbot — it doesn't generate free-form answers, only structured summaries of what's actually in the corpus.

Built for the Spinnaker Analytics BIA project.

## What it does

Extracts and chunks PDF/note text, indexes screenshots using written metadata (the screenshots here are mock UI cards, not real ones, so OCR isn't reliable enough to depend on), embeds everything locally with MiniLM, and stores it in Chroma. A query returns the top matching text and screenshot sources, a confidence label, a query category, and a short grounded answer.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Heads up on requirements: I had to pin `numpy<2.0.0`, `torch==2.2.0`, and `sentence-transformers==2.7.0` specifically. The latest sentence-transformers pulls in torch 2.4+, which doesn't play nice with numpy 2.x, which then breaks scipy. Spent a good chunk of a day chasing that before landing on these exact pins.

Tesseract (optional, only if you want to try OCR instead of the manual metadata):
```bash
brew install tesseract
```

## Running it

```bash
cd src
python3 ingest_documents.py
python3 ingest_screenshots.py
python3 build_index.py
cd ..
streamlit run app.py
```

## Evaluation

```bash
python3 eval/run_eval.py
```

Runs all 20 test queries, checks if the expected source lands at top-1 and in the top-3, writes results to `eval/results/eval_results.csv`.

Current numbers on the full hybrid corpus (53 records): **precision@1 = 65% (13/20)**, **precision@3 = 80% (16/20)**. See "What I found" below for how this compares to the starter-pack-only numbers and why it dropped.

## Architecture

`docs/architecture.png`. PDFs/notes and screenshots go through separate ingestion scripts, both feed into embedding, then Chroma. Retrieval runs on top of that with confidence scoring and query classification layered on, and Streamlit is just the display layer on top of all of it.

## What I found

Confidence labels are weaker than I'd like. I checked cosine similarity scores for correct vs. incorrect top-1 matches across the eval set, and they overlap — a wrong match scored 0.338 while some correct matches only scored around 0.18. Two queries in the eval set (Q005, Q012) retrieved the wrong document but still came back "High" confidence, because MiniLM was picking up on shared vocabulary ("escalation," "review") between documents rather than actual relevance to the query. I set the thresholds based on where most correct matches cluster, but I'm not pretending it's a clean separation — it isn't. Confidence here should be read as a rough signal, not something to fully trust.

I saw this get worse once I added the public source corpus. I ran the same 20 test queries before and after adding 19 public documents and 20 public screenshots, to see if more data actually helped:

| Metric | Starter pack only (14 records) | + Public sources (53 records) |
|---|---|---|
| Precision@1 | 80% (16/20) | 65% (13/20) |
| Precision@3 | 95% (19/20) | 80% (16/20) |

Both dropped, and it's not spread evenly — it's mostly the `dashboard_filter_setup` topic. Two queries (Q010, Q016) that used to correctly retrieve the starter pack's short SOP note now pull a public Salesforce cheatsheet PDF instead, because that PDF is longer and more keyword-dense on "dashboard filter" language than the three-line SOP note was. Cosine similarity rewards term density, not correctness, so a topic-heavy public doc can outrank a sparse original one even when the original is the actual right answer.

What worries me more than the precision drop itself: 4 of the 7 new top-1 misses (Q002, Q005, Q010, Q012) still came back "High" confidence. Adding more documents just gave the system more ways to be confidently wrong, it didn't make the confidence signal any better at catching that. Same root problem as before, just more visible at scale.

I didn't try to threshold-tune my way out of this. Since similarity score already doesn't separate right from wrong cleanly at the smaller scale, tuning harder on this bigger corpus would just be overfitting to my own 20 test queries. A real fix would be something structural — like weighting starter pack sources higher than public ones when both are relevant, or adding a reranking step — but that's beyond what I built here.

Chunking had a real bug early on: my first version applied text overlap twice for PDF pages (once during the hard-slice, once in a second pass), so chunks were literally repeating sentences. Fixed by dropping the redundant second pass. Also had chunks starting mid-word at the overlap boundary — fixed by snapping the cut point to the nearest space instead of a raw character count.

The corpus is small and everything is topic-bounded across five areas (access, approval, refunds, dashboards, quality review). I wouldn't expect these same precision numbers, this will probably fall apart on a bigger corpus.

Screenshot search depends entirely on the `manual_text` field someone wrote by hand, not actual OCR. That's fine for this sanitized starter pack since the screenshots are clean without noise, but a real deployment with actual noisy screenshots would need OCR tested properly, and I'd expect worse results.

## Known misses from eval

- **Q005** — "What should be included in an escalation note?" pulled the Refund Exception guide instead of the Approval Escalation PDF. Both documents have their own "escalation" section with similar wording.

- **Q012** — "What should be visible in a screenshot attached for supervisor review?" pulled a general use-cases note instead of the dashboard filter content — the query phrasing matched that file's own wording more than the actual answer.

## Structure

```
data/documents/pdfs/    source PDFs
data/documents/notes/   SOP notes
data/screenshots/       mock screenshots
data/metadata/          corpus + screenshot metadata
data/public_sources/    public reference material for hybrid mode
src/                    pipeline code
eval/                   test queries, eval script, results
docs/                   architecture diagram
app.py                  Streamlit app
```