def build_answer_draft(query, top_text_matches, top_screenshot_matches, confidence):
    if confidence == "Low" or not top_text_matches:
        return (
            "Retrieval confidence is low for this query. "
            "No answer draft is shown to avoid an unsupported response. "
            "Please review the source material directly."
        )

    best = top_text_matches[0]
    excerpt = best["text"].strip().replace("\n", " ")
    if len(excerpt) > 300:
        excerpt = excerpt[:300].rsplit(" ", 1)[0] + "..."

    lines = [
        f"Source: {best['title']} ({best['page_or_section']}).",
        excerpt,
    ]

    if top_screenshot_matches:
        lines.append(f"Related screenshot: {top_screenshot_matches[0]['title']}.")

    lines.append("Review the linked source before acting on this answer.")

    return "\n".join(lines)