import time
from fastapi import Request, HTTPException
from backend.app.core.config import get_settings

settings = get_settings()

request_counts: dict = {}


async def verify_api_key(request: Request):
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        raise HTTPException(status_code=401, detail="API key required")
    return api_key


async def rate_limit_middleware(request: Request):
    client_ip = request.client.host
    current_time = time.time()
    window = 60

    if client_ip not in request_counts:
        request_counts[client_ip] = []

    request_counts[client_ip] = [
        t for t in request_counts[client_ip] if current_time - t < window
    ]

    if len(request_counts[client_ip]) >= settings.api_rate_limit:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    request_counts[client_ip].append(current_time)
