from typing import List, Dict, Optional
from collections import defaultdict
from backend.app.core.database import raw_posts_collection

TOPIC_KEYWORDS = {
    "AI & Technology": ["ai", "artificial intelligence", "ml", "machine learning", "deep learning", "neural network", "algorithm", "gpt", "chatbot", "automation", "robot", "data science", "programming", "software", "tech", "technology", "cybersecurity", "hacking", "computer", "digital", "startup", "openai", "llm", "transformer"],
    "Health & Medicine": ["health", "medical", "doctor", "hospital", "disease", "vaccine", "covid", "pandemic", "virus", "treatment", "medicine", "mental health", "cancer", "drug", "pharmaceutical", "public health", "who", "clinical", "therapy", "patient"],
    "Climate & Environment": ["climate", "carbon", "emission", "renewable", "fossil", "temperature", "environment", "pollution", "green", "sustainability", "global warming", "net zero", "solar", "wind energy", "ecosystem", "deforestation"],
    "Politics & Government": ["election", "vote", "president", "congress", "senate", "government", "democrat", "republican", "political", "legislation", "policy", "law", "court", "supreme court", "democracy", "parliament", "policy"],
    "Economy & Business": ["economy", "market", "stock", "inflation", "recession", "gdp", "trade", "employment", "tax", "financial", "bank", "crypto", "bitcoin", "interest rate", "fed", "wall street", "investment", "business"],
    "Science & Research": ["research", "study", "experiment", "theory", "discovery", "evidence", "peer review", "journal", "scientific", "hypothesis", "publication", "space", "nasa", "physics", "biology", "chemistry"],
    "Social Media & Misinformation": ["viral", "trending", "fake news", "misinformation", "disinformation", "social media", "platform", "algorithm", "content", "propaganda", "conspiracy", "hoax", "fact check", "censorship"],
    "Conflict & Security": ["war", "attack", "military", "conflict", "violence", "terror", "troops", "invasion", "sanctions", "nuclear", "weapons", "defense", "security", "peace", "refugee"],
}


def _compute_similarity(keywords_a: set, keywords_b: set) -> float:
    if not keywords_a or not keywords_b:
        return 0.0
    intersection = len(keywords_a & keywords_b)
    union = len(keywords_a | keywords_b)
    return intersection / union if union > 0 else 0.0


def _extract_post_keywords(post: Dict) -> set:
    text = ((post.get("title") or "") + " " + (post.get("text") or "")).lower()
    keywords = set()
    for topic_name, topic_kws in TOPIC_KEYWORDS.items():
        for kw in topic_kws:
            if kw in text:
                keywords.add(topic_name)
                break
    hashtags = post.get("hashtags") or []
    for h in hashtags:
        h_clean = h.lower().lstrip("#")
        for topic_name, topic_kws in TOPIC_KEYWORDS.items():
            if h_clean in [kw.replace(" ", "") for kw in topic_kws]:
                keywords.add(topic_name)
    if post.get("subreddit"):
        sub = post["subreddit"].lower()
        if sub in ["technology", "programming", "machinelearning", "datascience"]:
            keywords.add("AI & Technology")
        elif sub in ["science", "physics", "biology"]:
            keywords.add("Science & Research")
        elif sub in ["worldnews", "politics", "news"]:
            keywords.add("Politics & Government")
    return keywords


async def get_topic_clusters(platform: Optional[str] = None) -> List[Dict]:
    cursor = await raw_posts_collection.find({})
    posts = await cursor.to_list(length=500)

    cluster_data = defaultdict(lambda: {
        "posts": [],
        "subtopics": set(),
        "total_engagement": 0,
        "avg_authority": 0,
        "sentiment_counts": {"positive": 0, "neutral": 0, "negative": 0},
        "platforms": set(),
        "keywords": set(),
    })

    for post in posts:
        if platform and post.get("platform") != platform:
            continue
        post_topics = _extract_post_keywords(post)
        if not post_topics:
            post_topics = {"Other"}
        for topic in post_topics:
            cluster = cluster_data[topic]
            cluster["posts"].append(post)
            cluster["subtopics"].add(post.get("subreddit") or post.get("hashtags", [None])[0] or "general")
            engagement = (post.get("upvotes", 0) + post.get("comments_count", 0) +
                         post.get("retweets", 0) + post.get("likes", 0))
            cluster["total_engagement"] += engagement
            cluster["platforms"].add(post.get("platform", "unknown"))
            sentiment = post.get("sentiment", {})
            label = sentiment.get("label", "neutral") if isinstance(sentiment, dict) else "neutral"
            if label in cluster["sentiment_counts"]:
                cluster["sentiment_counts"][label] += 1
            authority = post.get("authority_score", 30)
            cluster["avg_authority"] += authority
            if post.get("hashtags"):
                for h in post["hashtags"]:
                    cluster["keywords"].add(h.lower().lstrip("#"))

    results = []
    for topic, data in sorted(cluster_data.items(), key=lambda x: len(x[1]["posts"]), reverse=True):
        post_count = len(data["posts"])
        avg_authority = round(data["avg_authority"] / post_count, 1) if post_count > 0 else 0
        avg_engagement = round(data["total_engagement"] / post_count, 1) if post_count > 0 else 0
        results.append({
            "topic": topic,
            "post_count": post_count,
            "avg_engagement": avg_engagement,
            "avg_authority_score": avg_authority,
            "sentiment_distribution": data["sentiment_counts"],
            "platforms": list(data["platforms"]),
            "top_keywords": list(data["keywords"])[:10],
            "related_topics": [],
        })

    for i, result in enumerate(results):
        topic_kws = set(TOPIC_KEYWORDS.get(result["topic"], []))
        related = []
        for j, other in enumerate(results):
            if i == j:
                continue
            other_kws = set(TOPIC_KEYWORDS.get(other["topic"], []))
            sim = _compute_similarity(topic_kws, other_kws)
            if sim > 0.05:
                related.append({"topic": other["topic"], "similarity": round(sim, 2)})
        result["related_topics"] = sorted(related, key=lambda x: x["similarity"], reverse=True)[:3]

    return results


async def compare_topics(topic_names: List[str], platform: Optional[str] = None) -> Dict:
    clusters = await get_topic_clusters(platform=platform)
    cluster_map = {c["topic"]: c for c in clusters}

    selected = []
    for name in topic_names:
        if name in cluster_map:
            selected.append(cluster_map[name])
        else:
            matched = None
            for key in cluster_map:
                if name.lower() in key.lower() or key.lower() in name.lower():
                    matched = cluster_map[key]
                    break
            selected.append(matched or {"topic": name, "post_count": 0, "avg_engagement": 0,
                                        "avg_authority_score": 0, "sentiment_distribution": {"positive": 0, "neutral": 0, "negative": 0},
                                        "platforms": [], "top_keywords": [], "related_topics": []})

    metrics = ["post_count", "avg_engagement", "avg_authority_score"]
    max_vals = {}
    for m in metrics:
        max_vals[m] = max(s.get(m, 0) for s in selected) or 1

    sentiment_totals = {"positive": 0, "neutral": 0, "negative": 0}
    for s in selected:
        sd = s.get("sentiment_distribution", {})
        for k in sentiment_totals:
            sentiment_totals[k] += sd.get(k, 0)

    comparison = []
    for s in selected:
        sd = s.get("sentiment_distribution", {})
        total_s = sd.get("positive", 0) + sd.get("neutral", 0) + sd.get("negative", 0) or 1
        comparison.append({
            "topic": s["topic"],
            "post_count": s.get("post_count", 0),
            "avg_engagement": round(s.get("avg_engagement", 0), 1),
            "avg_authority_score": round(s.get("avg_authority_score", 0), 1),
            "sentiment": {
                "positive_pct": round(sd.get("positive", 0) / total_s * 100, 1),
                "neutral_pct": round(sd.get("neutral", 0) / total_s * 100, 1),
                "negative_pct": round(sd.get("negative", 0) / total_s * 100, 1),
            },
            "platforms": s.get("platforms", []),
            "top_keywords": s.get("top_keywords", [])[:5],
            "relative_scores": {
                m: round(s.get(m, 0) / max_vals[m] * 100, 1) for m in metrics
            },
        })

    return {"comparison": comparison, "metrics_max": max_vals, "total_sentiment": sentiment_totals}