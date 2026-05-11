from fastapi import APIRouter, Query
from typing import Optional
from backend.app.services.trending_service import get_trending_topics, get_trending_realtime

router = APIRouter()


@router.get("/")
async def get_trending(platform: Optional[str] = Query(None), limit: int = Query(10)):
    topics = await get_trending_topics(platform=platform, limit=limit)
    return {"topics": topics, "count": len(topics)}


@router.get("/realtime")
async def get_trending_realtime_endpoint(hours: int = Query(1)):
    results = await get_trending_realtime(hours=hours)
    return {"trending": results, "window_hours": hours}
