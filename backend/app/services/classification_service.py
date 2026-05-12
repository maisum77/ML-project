import re
from typing import Optional, List, Dict
from ml_models.sentiment.predict import predict_sentiment
from ml_models.fake_news.predict import predict_fake_news
from backend.app.models.authority_sources import get_source_type, get_authority_score


SENSATIONALISM_PATTERNS = [
    (r"\b(shocking|bombshell|explosive|earth[- ]shattering|game[- ]changer)\b", 15, "sensationalist_adjective"),
    (r"\b(you won'?t believe|what happens next|will blow your mind|must see)\b", 20, "clickbait_phrase"),
    (r"!!+", 5, "excessive_exclamation"),
    (r"[A-Z]{5,}", 10, "excessive_caps"),
    (r"\b(100%|guaranteed|proven|confirmed|definitive)\b", 10, "absolute_certainty"),
    (r"\b(secret|hidden|they don'?t want you|they'?re hiding|cover[- ]up)\b", 15, "conspiracy_language"),
    (r"\b(miracle|cure|hack|trick|one weird)\b", 12, "miracle_cure_claim"),
    (r"(?:^|\s)URGENT(?:$|\s)", 8, "urgency_marker"),
    (r"\b(breaking|developing|just in)\b", 5, "breaking_news_marker"),
    (r"http[s]?://\S+", 3, "contains_url"),
    (r"#{1,2}\w+", 2, "hashtag_usage"),
    (r"\b(fake|hoax|scam|fraud|lie|lies|liar)\b", 8, "accusatory_language"),
    (r"\b(doctors hate|scientists hate|they hate|big pharma|deep state)\b", 18, "anti_authority"),
]

EMOTIONAL_WORDS = {
    "anger": ["angry", "outrageous", "furious", "rage", "disgusting", "appalling", "unacceptable"],
    "fear": ["terrifying", "scary", "dangerous", "threat", "crisis", "panic", "alarm", "warning"],
    "joy": ["amazing", "wonderful", "incredible", "fantastic", "breakthrough", "exciting"],
    "sadness": ["tragic", "devastating", "heartbreaking", "terrible", "awful", "grim"],
}

TOPIC_KEYWORDS = {
    "politics": ["election", "vote", "president", "congress", "senate", "government", "democrat", "republican", "political", "legislation"],
    "health": ["vaccine", "disease", "doctor", "hospital", "medicine", "covid", "pandemic", "virus", "treatment", "health"],
    "technology": ["ai", "artificial intelligence", "tech", "software", "startup", "data", "algorithm", "robot", "cyber", "digital"],
    "climate": ["climate", "carbon", "emission", "renewable", "fossil", "temperature", "environment", "pollution", "sustainability"],
    "economy": ["market", "stock", "inflation", "recession", "gdp", "economy", "trade", "employment", "tax", "financial"],
    "science": ["research", "study", "experiment", "theory", "discovery", "evidence", "peer", "journal", "hypothesis", "scientific"],
    "conflict": ["war", "attack", "military", "conflict", "violence", "terror", "troops", "invasion", "ceasefire", "sanctions"],
    "social_media": ["viral", "trending", "influencer", "platform", "algorithm", "content", "social", "post", "share", "misinformation"],
}


def _extract_entities(text: str) -> Dict[str, List[str]]:
    people = []
    organizations = []
    locations = []

    org_patterns = [
        r"\b(WHO|UNICEF|UN|NATO|NASA|CDC|FDA|NIH|FBI|CIA|EU|Congress|Senate|Parliament)\b",
        r"\b([A-Z][a-z]+ (?:Inc|Corp|Ltd|LLC|Group|Foundation|Institute|University|College|Hospital))\b",
    ]
    for pattern in org_patterns:
        organizations.extend(re.findall(pattern, text))

    location_patterns = [
        r"\b(United States|USA|UK|China|Russia|India|Europe|Asia|Africa|Middle East|America)\b",
        r"\b([A-Z][a-z]+ (?:City|State|Country|Republic|Kingdom|Province|Island))\b",
        r"\b(New York|London|Washington|Beijing|Moscow|Paris|Berlin|Tokyo|Sydney|Toronto)\b",
    ]
    for pattern in location_patterns:
        locations.extend(re.findall(pattern, text))

    people_patterns = [
        r"\b(President|Dr\.|Prof\.|Mr\.|Ms\.|Sen\.|Gov\.)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b",
        r"\b([A-Z][a-z]+\s+[A-Z][a-z]+)\b",
    ]
    excluded_people = {
        "New York", "San Francisco", "Los Angeles", "Las Vegas", "Hong Kong",
        "The Lancet", "According To", "World Health", "Health Organization",
    }
    for pattern in people_patterns:
        matches = re.findall(pattern, text)
        for m in matches:
            name = f"{m[0]} {m[1]}" if isinstance(m, tuple) else m
            if name not in excluded_people and len(name.split()) >= 2:
                people.append(name)

    return {
        "people": list(set(people)),
        "organizations": list(set(organizations)),
        "locations": list(set(locations)),
    }


def _extract_topics(text: str) -> List[str]:
    text_lower = text.lower()
    topics = []
    for topic, keywords in TOPIC_KEYWORDS.items():
        keyword_count = sum(1 for kw in keywords if kw in text_lower)
        if keyword_count >= 2:
            topics.append({"topic": topic, "relevance": min(keyword_count / len(keywords) * 100, 100)})

    if not topics:
        for topic, keywords in TOPIC_KEYWORDS.items():
            keyword_count = sum(1 for kw in keywords if kw in text_lower)
            if keyword_count >= 1:
                topics.append({"topic": topic, "relevance": min(keyword_count / len(keywords) * 100, 50)})

    return sorted(topics, key=lambda x: x["relevance"], reverse=True)[:4]


def _analyze_linguistic_signals(text: str) -> Dict:
    flags = []
    total_score = 0

    for pattern, score, label in SENSATIONALISM_PATTERNS:
        flags_re = re.IGNORECASE if label != "excessive_caps" else 0
        matches = re.findall(pattern, text, flags_re)
        if matches:
            flags.append({"flag": label, "count": len(matches), "score": score})
            total_score += score

    word_count = len(text.split())
    if word_count > 0:
        caps_words = len([w for w in text.split() if w.isupper() and len(w) > 2])
        caps_ratio = caps_words / word_count
        if caps_ratio > 0.15:
            flags.append({"flag": "high_caps_ratio", "count": caps_words, "score": 10})
            total_score += 10

    avg_word_length = sum(len(w) for w in text.split()) / max(word_count, 1)
    if avg_word_length > 7:
        flags.append({"flag": "complex_vocabulary", "score": 5, "count": 1})
        total_score += 5

    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    avg_sentence_length = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
    if avg_sentence_length > 30:
        flags.append({"flag": "long_sentences", "score": 3, "count": 1})
        total_score += 3

    return {
        "score": min(total_score, 100),
        "flags": flags,
        "word_count": word_count,
        "avg_sentence_length": round(avg_sentence_length, 1),
    }


def _analyze_emotional_language(text: str) -> Dict:
    text_lower = text.lower()
    emotion_scores = {}

    for emotion, words in EMOTIONAL_WORDS.items():
        count = sum(1 for w in words if w in text_lower)
        if count > 0:
            emotion_scores[emotion] = count

    primary_emotion = max(emotion_scores, key=emotion_scores.get) if emotion_scores else "neutral"
    total_emotional = sum(emotion_scores.values())
    word_count = max(len(text.split()), 1)
    subjectivity = min(total_emotional / word_count * 10, 1.0)

    return {
        "primary_emotion": primary_emotion,
        "emotion_scores": emotion_scores,
        "subjectivity": round(subjectivity, 2),
        "emotional_intensity": min(total_emotional * 15, 100),
    }


def _analyze_source(source: Optional[str], text: str) -> Dict:
    if source:
        source_type = get_source_type(source, "twitter")
        authority_score = get_authority_score(source, "twitter", False)
    else:
        source_type = "unattributed"
        authority_score = 0

    url_matches = re.findall(r'https?://([^\s/]+)', text)
    domains = list(set(url_matches))

    has_attribution = bool(re.search(r'(?:according to|said|reported by|source:|cited in)\b', text, re.IGNORECASE))
    has_quotes = bool(re.search(r'["\u201c\u201d].*?["\u201c\u201d]', text))

    attribution_score = 0
    if has_attribution:
        attribution_score += 20
    if has_quotes:
        attribution_score += 15
    if source_type == "official":
        attribution_score += 30
    elif source_type == "journalist":
        attribution_score += 20

    return {
        "source_type": source_type,
        "authority_score": authority_score,
        "domains": domains,
        "has_attribution": has_attribution,
        "has_quotes": has_quotes,
        "attribution_score": attribution_score,
    }


async def _analyze_fact_checks(text: str) -> Dict:
    results = {
        "claims_checked": 0,
        "matches": [],
        "claimbuster_available": False,
        "google_fact_check_available": False,
        "verdict": "unchecked",
    }

    try:
        from fact_check.google_factcheck import google_fact_check
        fact_result = google_fact_check(text[:200])
        results["google_fact_check_available"] = True
        if "error" not in fact_result:
            claims = fact_result.get("claims", [])
            results["claims_checked"] = len(claims)
            results["matches"] = [
                {
                    "claim_text": c.get("text", "")[:200],
                    "verdict": c.get("verdict", "unknown"),
                    "publisher": c.get("publisher", ""),
                }
                for c in claims[:3]
            ]
            if claims:
                results["verdict"] = fact_result.get("verdict", "no_match")
    except Exception:
        results["google_fact_check_available"] = False

    try:
        from fact_check.claimbuster import claimbuster_check
        cb_result = claimbuster_check(text[:500])
        results["claimbuster_available"] = True
        if "error" not in cb_result:
            results["claimbuster_score"] = cb_result.get("score", 0)
            results["checkworthy"] = cb_result.get("checkworthy", False)
    except Exception:
        results["claimbuster_available"] = False

    return results


def _compute_verdict(
    linguistic: Dict,
    emotional: Dict,
    source: Dict,
    fact_checks: Dict,
    sentiment: Dict,
    fake_result: Dict,
) -> Dict:
    scores = {
        "linguistic": min(linguistic["score"] / 100, 1.0),
        "emotional": min(emotional["emotional_intensity"] / 100, 1.0) * 0.6,
        "source_reliability": 1.0 - (source["authority_score"] / 100),
        "fact_check_risk": 0.3,
        "sentiment_extremity": abs(sentiment["score"]) / 100 * 0.5,
    }

    weights = {
        "linguistic": 0.25,
        "emotional": 0.15,
        "source_reliability": 0.20,
        "fact_check_risk": 0.25,
        "sentiment_extremity": 0.15,
    }

    if fake_result["label"] == "fake":
        scores["fact_check_risk"] = min(fake_result["confidence"] / 100, 1.0) * 0.7
    else:
        scores["fact_check_risk"] = max(0.1, 1.0 - fake_result["confidence"] / 100) * 0.3

    if fact_checks.get("matches"):
        fact_verdicts = [m.get("verdict", "").lower() for m in fact_checks["matches"]]
        if any("false" in v for v in fact_verdicts):
            scores["fact_check_risk"] = 0.85
        elif any("true" in v or "correct" in v for v in fact_verdicts):
            scores["fact_check_risk"] = 0.1

    composite = sum(scores[k] * weights[k] for k in scores)
    composite = max(0.0, min(1.0, composite))

    if composite >= 0.7:
        risk_level = "high"
        verdict_label = "likely_unreliable"
        verdict_text = "High risk of misinformation - multiple credibility signals detected"
    elif composite >= 0.4:
        risk_level = "medium"
        verdict_label = "needs_verification"
        verdict_text = "Moderate risk - some credibility concerns, verify with trusted sources"
    else:
        risk_level = "low"
        verdict_label = "likely_reliable"
        verdict_text = "Appears credible - no significant credibility concerns detected"

    return {
        "label": verdict_label,
        "confidence": round(composite * 100, 1),
        "risk_level": risk_level,
        "explanation": verdict_text,
        "signal_weights": scores,
    }


async def classify_text(text: str, source: Optional[str] = None) -> Dict:
    sentiment_result = predict_sentiment(text)
    fake_result = predict_fake_news(text)

    linguistic = _analyze_linguistic_signals(text)
    emotional = _analyze_emotional_language(text)
    source_analysis = _analyze_source(source, text)
    entities = _extract_entities(text)
    topics = _extract_topics(text)
    fact_checks = await _analyze_fact_checks(text)

    verdict = _compute_verdict(
        linguistic, emotional, source_analysis, fact_checks,
        sentiment_result, fake_result,
    )

    return {
        "text": text[:500],
        "analysis": {
            "sentiment": sentiment_result,
            "credibility": {
                "label": verdict["label"],
                "confidence": verdict["confidence"],
                "risk_level": verdict["risk_level"],
            },
            "linguistic_signals": linguistic,
            "emotional_analysis": emotional,
            "source_analysis": source_analysis,
            "entity_extraction": {
                "people": entities["people"],
                "organizations": entities["organizations"],
                "locations": entities["locations"],
            },
            "topic_detection": topics,
            "fact_check_results": fact_checks,
        },
        "verdict": verdict,
        "source": source,
        "model_version": "2.0",
    }


async def classify_text_simple(text: str, source: Optional[str] = None) -> Dict:
    sentiment_result = predict_sentiment(text)
    fake_result = predict_fake_news(text)

    return {
        "text": text,
        "classification": fake_result["label"],
        "confidence": fake_result["confidence"],
        "sentiment": sentiment_result["label"],
        "sentiment_score": sentiment_result["score"],
        "source": source,
    }