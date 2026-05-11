import hashlib
import re
from datetime import datetime
from typing import Optional


def generate_post_id(source: str, original_id: str) -> str:
    return f"{source}_{original_id}"


def extract_urls(text: str) -> list:
    return re.findall(r'https?://\S+', text)


def extract_hashtags(text: str) -> list:
    return re.findall(r'#\w+', text)


def extract_mentions(text: str) -> list:
    return re.findall(r'@\w+', text)


def truncate_text(text: str, max_length: int = 500) -> str:
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def calculate_engagement_score(upvotes: int = 0, comments: int = 0, retweets: int = 0, likes: int = 0) -> float:
    return (upvotes * 1.0) + (comments * 2.0) + (retweets * 1.5) + (likes * 1.0)


def sanitize_text(text: str) -> str:
    text = re.sub(r'[^\w\s.,!?\'"-]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text
