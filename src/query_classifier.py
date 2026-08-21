CATEGORY_KEYWORDS = {
    "access_request_routing": ["access", "role", "reviewer", "team lead", "viewer", "processor", "expiry"],
    "approval_escalation": ["approval", "escalat", "supervisor review", "queue", "freeze"],
    "refund_exception_handling": ["refund", "exception", "finance ops", "chargeback", "duplicate charge"],
    "dashboard_filter_setup": ["dashboard", "filter", "saved filter", "queue monitoring"],
    "quality_review": ["quality review", "monthly review", "sample", "review dimension"],
}


def classify_query(query):
    query_lower = query.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in query_lower:
                return category
    return "general"
