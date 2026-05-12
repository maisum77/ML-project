from fastapi import APIRouter, Query
from typing import Optional
from backend.app.core.database import raw_posts_collection

router = APIRouter()


@router.get("/")
async def get_feed(
    platform: Optional[str] = Query(None),
    sentiment: Optional[str] = Query(None),
    classification: Optional[str] = Query(None),
    limit: int = Query(50),
    offset: int = Query(0),
):
    query = {}
    if platform:
        query["platform"] = platform

    cursor = (await raw_posts_collection.find(query)).sort("upvotes", -1).skip(offset).limit(limit)
    posts = await cursor.to_list(length=limit)

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
