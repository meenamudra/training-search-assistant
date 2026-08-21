from config import CONFIDENCE_HIGH_THRESHOLD, CONFIDENCE_MEDIUM_THRESHOLD


def label_confidence(top_similarity):
    if top_similarity >= CONFIDENCE_HIGH_THRESHOLD:
        return "High"
    if top_similarity >= CONFIDENCE_MEDIUM_THRESHOLD:
        return "Medium"
    return "Low"
