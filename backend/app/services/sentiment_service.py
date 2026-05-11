from datetime import datetime, timedelta, timezone
from typing import Optional
from backend.app.core.database import sentiment_collection, raw_posts_collection


async def get_sentiment_by_topic(topic: str, hours: int = 24):
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)

    posts = await raw_posts_collection._scan_all()
    all_items = posts.data

    results = []
    for item in all_items:
        ts_str = item.get("timestamp") or item.get("created_at")
        if not ts_str:
            continue
        try:
            ts = datetime.fromisoformat(ts_str)
        except (ValueError, TypeError):
            continue
        if ts < cutoff:
            continue

        item_topic = item.get("subreddit") or (
            item.get("hashtags", ["general"])[0] if item.get("hashtags") else "general"
        )
        if topic and topic.lower() not in item_topic.lower():
            continue

        sentiment_label = item.get("sentiment", {}).get("label", "neutral")
        hour_key = ts.strftime("%Y-%m-%dT%H:00")

        found = False
        for r in results:
            if r.get("hour") == hour_key and r.get("sentiment") == sentiment_label:
                r["count"] += 1
                found = True
                break
        if not found:
            results.append({"hour": hour_key, "sentiment": sentiment_label, "count": 1})

    results.sort(key=lambda x: x["hour"])
    return results


async def get_overall_sentiment(platform: Optional[str] = None, hours: int = 24):
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)

    posts = await raw_posts_collection._scan_all()
    all_items = posts.data

    breakdown = {"positive": 0, "neutral": 0, "negative": 0}

    for item in all_items:
        ts_str = item.get("timestamp") or item.get("created_at")
        if not ts_str:
            continue
        try:
            ts = datetime.fromisoformat(ts_str)
        except (ValueError, TypeError):
            continue
        if ts < cutoff:
            continue

        if platform and item.get("platform") != platform:
            continue

        sentiment_label = item.get("sentiment", {}).get("label", "neutral")
        if sentiment_label in breakdown:
            breakdown[sentiment_label] += 1

    return [
        {"label": "positive", "count": breakdown["positive"]},
        {"label": "neutral", "count": breakdown["neutral"]},
        {"label": "negative", "count": breakdown["negative"]},
    ]
