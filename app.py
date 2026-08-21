import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

import streamlit as st
from retrieval import search_text, search_screenshots
from confidence import label_confidence
from query_classifier import classify_query
from answer_draft import build_answer_draft
from config import DATA_DIR

st.set_page_config(page_title="Ops Training Search", layout="wide")

st.title("Internal Training Content Search Assistant")
st.caption("Search across PDFs, SOP notes, and screenshots. This is a retrieval tool, not a chatbot.")

query = st.text_input("Enter your question", placeholder="e.g. Which access role requires supervisor review?")

if query:
    text_matches = search_text(query, top_k=5)
    screenshot_matches = search_screenshots(query, top_k=3)

    confidence = label_confidence(text_matches[0]["similarity"]) if text_matches else "Low"
    category = classify_query(query)
    answer = build_answer_draft(query, text_matches, screenshot_matches, confidence)

    st.subheader("Query category")
    st.write(category.replace("_", " ").title())

    st.subheader("Answer draft")
    st.write(answer)

    confidence_color = {"High": "green", "Medium": "orange", "Low": "red"}[confidence]
    st.markdown(f"**Confidence:** :{confidence_color}[{confidence}]")

    if confidence == "Low":
        st.info("Suggested next step: review the original source directly, or escalate to the operations lead if unclear.")
    elif confidence == "Medium":
        st.info("Suggested next step: verify against the source before using this in a decision.")
    else:
        st.info("Suggested next step: use the source directly.")

    st.subheader("Top text sources")
    for m in text_matches:
        with st.expander(f"{m['title']} — {m['page_or_section']} (similarity {m['similarity']:.3f})"):
            st.write(m["text"])
            st.caption(m["file_path"])

    st.subheader("Screenshot matches")
    cols = st.columns(3)
    for i, m in enumerate(screenshot_matches):
        with cols[i % 3]:
            image_path = DATA_DIR / m["file_path"]
            st.image(str(image_path), caption=m["title"])
            st.caption(f"similarity {m['similarity']:.3f}")