from fastapi import APIRouter, Query
from typing import Optional
from backend.app.core.database import raw_posts_collection
from backend.app.services.clustering_service import TOPIC_KEYWORDS

router = APIRouter()


def _matches_topic(post: dict, topic: str) -> bool:
    text = ((post.get("title") or "") + " " + (post.get("text") or "")).lower()
    topic_lower = topic.lower()
    if topic_lower in text:
        return True
    for kw in TOPIC_KEYWORDS.get(topic, [topic_lower]):
        if kw in text:
            return True
    for h in post.get("hashtags", []):
        if topic_lower in h.lower():
            return True
    if post.get("subreddit") and topic_lower in post.get("subreddit", "").lower():
        return True
    return False


@router.get("/")
async def get_feed(
    platform: Optional[str] = Query(None),
    sentiment: Optional[str] = Query(None),
    classification: Optional[str] = Query(None),
    topic: Optional[str] = Query(None),
    limit: int = Query(50),
    offset: int = Query(0),
):
    query = {}
    if platform:
        query["platform"] = platform

    cursor = (await raw_posts_collection.find(query)).sort("upvotes", -1).skip(offset).limit(limit * 3 if topic else limit)
    posts = await cursor.to_list(length=limit * 3 if topic else limit)

    if topic:
        posts = [p for p in posts if _matches_topic(p, topic)][:limit]

    if sentiment:
        posts = [p for p in posts if p.get("sentiment", {}).get("label") == sentiment]
    if classification:
        posts = [p for p in posts if p.get("classification") == classification]

    total = await raw_posts_collection.count_documents(query)

    return {
        "posts": posts,
        "total": total,
        "limit": limit,
        "offset": offset,
    }
