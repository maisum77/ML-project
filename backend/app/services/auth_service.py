import os
import hashlib
import hmac
from datetime import datetime, timezone, timedelta
from typing import Optional
import jwt
from backend.app.core.config import get_settings
from backend.app.core.dynamodb import dynamodb

settings = get_settings()
_table = dynamodb.Table("socialpulse_users")

SECRET = settings.api_key_secret or "change_this_to_a_random_secret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET, algorithm=ALGORITHM)


def verify_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None


async def register_user(username: str, email: str, password: str) -> dict:
    existing = _table.get_item(Key={"id": f"user_{username}"})
    if existing.get("Item"):
        return {"error": "Username already exists"}

    user_id = f"user_{username}"
    user = {
        "id": user_id,
        "username": username,
        "email": email,
        "password_hash": _hash_password(password),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "saved_analyses": [],
        "keyword_alerts": [],
    }
    _table.put_item(Item=user)

    token = create_access_token({"sub": username, "email": email})
    return {
        "token": token,
        "token_type": "bearer",
        "user": {"username": username, "email": email},
    }


async def login_user(username: str, password: str) -> dict:
    user_id = f"user_{username}"
    result = _table.get_item(Key={"id": user_id})
    user = result.get("Item")

    if not user or user.get("password_hash") != _hash_password(password):
        return {"error": "Invalid credentials"}

    token = create_access_token({"sub": username, "email": user.get("email", "")})
    return {
        "token": token,
        "token_type": "bearer",
        "user": {"username": username, "email": user.get("email", "")},
    }


async def get_user(username: str) -> Optional[dict]:
    result = _table.get_item(Key={"id": f"user_{username}"})
    user = result.get("Item")
    if not user:
        return None
    user.pop("password_hash", None)
    return user


async def save_analysis(username: str, analysis_data: dict) -> dict:
    user_id = f"user_{username}"
    result = _table.get_item(Key={"id": user_id})
    user = result.get("Item")
    if not user:
        return {"error": "User not found"}

    analysis_id = f"analysis_{analysis_data.get('topic', 'untitled')}_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
    saved = user.get("saved_analyses") or []
    saved.append({
        "id": analysis_id,
        "data": analysis_data,
        "saved_at": datetime.now(timezone.utc).isoformat(),
    })
    if len(saved) > 50:
        saved = saved[-50:]
    _table.update_item(
        Key={"id": user_id},
        UpdateExpression="SET saved_analyses = :s",
        ExpressionAttributeValues={":s": saved},
    )
    return {"id": analysis_id, "message": "Analysis saved"}


async def add_keyword_alert(username: str, keyword: str) -> dict:
    user_id = f"user_{username}"
    result = _table.get_item(Key={"id": user_id})
    user = result.get("Item")
    if not user:
        return {"error": "User not found"}

    alerts = user.get("keyword_alerts") or []
    if keyword not in alerts:
        alerts.append(keyword)
        _table.update_item(
            Key={"id": user_id},
            UpdateExpression="SET keyword_alerts = :a",
            ExpressionAttributeValues={":a": alerts},
        )
    return {"keyword": keyword, "message": "Alert added"}


async def remove_keyword_alert(username: str, keyword: str) -> dict:
    user_id = f"user_{username}"
    result = _table.get_item(Key={"id": user_id})
    user = result.get("Item")
    if not user:
        return {"error": "User not found"}

    alerts = [a for a in (user.get("keyword_alerts") or []) if a != keyword]
    _table.update_item(
        Key={"id": user_id},
        UpdateExpression="SET keyword_alerts = :a",
        ExpressionAttributeValues={":a": alerts},
    )
    return {"keyword": keyword, "message": "Alert removed"}