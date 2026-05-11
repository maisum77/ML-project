from fastapi import APIRouter, Query, Path
from typing import Optional
from backend.app.services.propagation_service import trace_origin, get_propagation_for_topic

router = APIRouter()


@router.get("/origin/{post_id}")
async def get_origin(post_id: str = Path(...)):
    result = await trace_origin(post_id)
    if not result:
        return {"error": "Post not found", "post_id": post_id}
    return result


@router.get("/topic/{topic}")
async def get_topic_propagation(topic: str = Path(...)):
    result = await get_propagation_for_topic(topic)
    return result


@router.get("/")
async def get_propagation(topic_hash: Optional[str] = Query(None), topic: Optional[str] = Query(None)):
    if topic:
        result = await get_propagation_for_topic(topic)
        return result
    if topic_hash:
        result = await get_propagation_for_topic(topic_hash)
        return result
    return {"message": "Provide topic or topic_hash query parameter"}
