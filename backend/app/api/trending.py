from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List
from backend.app.services.trending_service import get_trending_topics, get_trending_realtime
from backend.app.services.clustering_service import get_topic_clusters, compare_topics

router = APIRouter()


@router.get("/")
async def get_trending(platform: Optional[str] = Query(None), limit: int = Query(10)):
    topics = await get_trending_topics(platform=platform, limit=limit)
    return {"topics": topics, "count": len(topics)}


@router.get("/realtime")
async def get_trending_realtime_endpoint(hours: int = Query(1)):
    results = await get_trending_realtime(hours=hours)
    return {"trending": results, "window_hours": hours}


@router.get("/clusters")
async def get_clusters(platform: Optional[str] = Query(None)):
    clusters = await get_topic_clusters(platform=platform)
    return {"clusters": clusters, "count": len(clusters)}


@router.get("/compare")
async def compare_topics_endpoint(
    topics: str = Query(..., description="Comma-separated topic names"),
    platform: Optional[str] = Query(None),
):
    topic_list = [t.strip() for t in topics.split(",") if t.strip()]
    if len(topic_list) < 2:
        raise HTTPException(status_code=400, detail="Provide at least 2 comma-separated topics")
    result = await compare_topics(topic_list, platform=platform)
    return result