from typing import Optional
from backend.app.core.database import trends_collection, raw_posts_collection


async def get_trending_topics(platform: Optional[str] = None, limit: int = 10):
    query = {}
    if platform:
        query["platform"] = platform

    cursor = trends_collection.find(query)
    topics = await cursor.to_list(length=limit)
    return topics


async def get_trending_realtime(hours: int = 1):
    cursor = raw_posts_collection.find({}).sort("upvotes", -1).limit(10)
    posts = await cursor.to_list(length=10)

    grouped = {}
    for post in posts:
        key = post.get("subreddit") or (post.get("hashtags", ["general"])[0] if post.get("hashtags") else "general")
        if key not in grouped:
            grouped[key] = {"_id": key, "count": 0, "avg_engagement": 0, "posts": [], "total_engagement": 0}
        grouped[key]["count"] += 1
        engagement = post.get("upvotes", 0) + post.get("comments_count", 0) + post.get("retweets", 0) + post.get("likes", 0)
        grouped[key]["total_engagement"] += engagement
        grouped[key]["posts"].append({"title": post.get("title"), "text": post.get("text"), "url": post.get("url")})

    for g in grouped.values():
        g["avg_engagement"] = g["total_engagement"] / g["count"] if g["count"] > 0 else 0
        del g["total_engagement"]

    return sorted(grouped.values(), key=lambda x: x["avg_engagement"], reverse=True)[:10]
