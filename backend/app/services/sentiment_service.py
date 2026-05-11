from datetime import datetime, timedelta
from typing import Optional
from backend.app.core.database import sentiment_collection, raw_posts_collection


async def get_sentiment_by_topic(topic: str, hours: int = 24):
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    pipeline = [
        {"$match": {
            "topic": topic,
            "timestamp": {"$gte": cutoff}
        }},
        {"$group": {
            "_id": {
                "hour": {"$hour": "$timestamp"},
                "sentiment": "$sentiment"
            },
            "count": {"$sum": 1}
        }},
        {"$sort": {"_id.hour": 1}}
    ]
    results = await sentiment_collection.aggregate(pipeline).to_list(length=None)
    return results


async def get_overall_sentiment(platform: Optional[str] = None, hours: int = 24):
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    query = {"timestamp": {"$gte": cutoff}}
    if platform:
        query["platform"] = platform

    pipeline = [
        {"$match": query},
        {"$group": {
            "_id": "$sentiment",
            "count": {"$sum": 1}
        }}
    ]
    results = await sentiment_collection.aggregate(pipeline).to_list(length=None)
    return results
