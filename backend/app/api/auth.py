from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Optional
from pydantic import BaseModel
from backend.app.services.auth_service import (
    register_user, login_user, verify_token, get_user,
    save_analysis, add_keyword_alert, remove_keyword_alert,
)

router = APIRouter()


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class SaveAnalysisRequest(BaseModel):
    topic: str
    text: str
    verdict: Optional[dict] = None
    analysis: Optional[dict] = None


class KeywordAlertRequest(BaseModel):
    keyword: str


def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid or missing token")
    token = authorization.split(" ")[1]
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token expired or invalid")
    return payload["sub"]


@router.post("/register")
async def register(request: RegisterRequest):
    if len(request.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    result = await register_user(request.username, request.email, request.password)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/login")
async def login(request: LoginRequest):
    result = await login_user(request.username, request.password)
    if "error" in result:
        raise HTTPException(status_code=401, detail=result["error"])
    return result


@router.get("/me")
async def get_me(username: str = Depends(get_current_user)):
    user = await get_user(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/save-analysis")
async def save_user_analysis(request: SaveAnalysisRequest, username: str = Depends(get_current_user)):
    result = await save_analysis(username, request.dict())
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/alerts")
async def create_alert(request: KeywordAlertRequest, username: str = Depends(get_current_user)):
    result = await add_keyword_alert(username, request.keyword)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.delete("/alerts/{keyword}")
async def delete_alert(keyword: str, username: str = Depends(get_current_user)):
    result = await remove_keyword_alert(username, keyword)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.get("/notifications")
async def get_notifications(username: str = Depends(get_current_user)):
    from backend.app.core.database import raw_posts_collection
    user = await get_user(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    alerts = user.get("keyword_alerts", [])
    if not alerts:
        return {"count": 0, "matches": []}

    from datetime import datetime, timedelta, timezone
    since = datetime.now(timezone.utc) - timedelta(hours=24)

    matches = []
    for keyword in alerts:
        kw_lower = keyword.lower()
        cursor = await raw_posts_collection.find({
            "$or": [
                {"title": {"$regex": kw_lower, "$options": "i"}},
                {"text": {"$regex": kw_lower, "$options": "i"}},
            ]
        })
        posts = await cursor.to_list(length=10)
        if posts:
            matches.append({
                "keyword": keyword,
                "count": len(posts),
                "latest_title": (posts[0].get("title") or posts[0].get("text", ""))[:80],
            })

    return {"count": len(matches), "matches": matches}