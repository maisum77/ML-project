from fastapi import APIRouter, Query
from backend.app.services.authority_service import check_authority, check_post_authority
from backend.app.core.database import raw_posts_collection

router = APIRouter()


@router.get("/check")
async def check(author: str = Query(...), platform: str = Query("twitter")):
    result = await check_authority(author=author, platform=platform)
    return result


@router.get("/post/{post_id}")
async def check_post(post_id: str):
    post = await raw_posts_collection.find_one({"id": post_id})
    if not post:
        return {"error": "Post not found"}
    result = await check_post_authority(post)
    return result
