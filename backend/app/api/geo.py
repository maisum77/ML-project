from fastapi import APIRouter, Query
from typing import Optional
from backend.app.services.geo_service import get_geo_distribution, get_globe_data

router = APIRouter()


@router.get("/topic/{topic}")
async def get_topic_geo(topic: str, platform: Optional[str] = Query(None)):
    distribution = await get_geo_distribution(topic=topic, platform=platform)
    return {
        "topic": topic,
        "points": distribution,
        "total_locations": len(distribution),
        "total_posts": sum(p["count"] for p in distribution),
    }


@router.get("/globe")
async def get_globe():
    data = await get_globe_data()
    return data


@router.get("/")
async def get_geo(platform: Optional[str] = Query(None)):
    distribution = await get_geo_distribution(platform=platform)
    return {
        "points": distribution,
        "total_locations": len(distribution),
        "total_posts": sum(p["count"] for p in distribution),
    }
