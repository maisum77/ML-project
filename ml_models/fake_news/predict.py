import re

_fake_keywords = [
    "shocking truth", "they don't want you to know", "wake up",
    "conspiracy", "hoax", "secret cure", "big pharma", "deep state",
    "100% proven", "miracle", "doctors hate", "one weird trick",
    "government hiding", "banned video", "censored",
]


def predict_fake_news(text: str) -> dict:
    text_lower = text.lower()
    score = 0

    for kw in _fake_keywords:
        if kw in text_lower:
            score += 20

    if re.search(r"(?i)(click|share|repost)\s+(here|now|this)", text):
        score += 15

    if re.search(r"(?i)(?!it'?s\b)(\b\w{12,}\b)", text):
        score += 5

    exclamation_count = text.count("!")
    if exclamation_count > 2:
        score += min(exclamation_count * 5, 15)

    if any(w in text_lower for w in ["100%", "guaranteed", "proven", "confirmed"]):
        score += 10

    confidence = min(score, 99)
    if confidence > 40:
        return {"label": "fake", "confidence": confidence}
    else:
        return {"label": "real", "confidence": 100 - confidence}
