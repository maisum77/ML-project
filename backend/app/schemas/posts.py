from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class RawPost(BaseModel):
    id: str
    source: str
    platform: str
    title: Optional[str] = None
    text: str
    author: str
    upvotes: int = 0
    comments_count: int = 0
    retweets: int = 0
    likes: int = 0
    url: str
    subreddit: Optional[str] = None
    hashtags: list = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    fetched_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "post_001",
                "source": "reddit",
                "platform": "reddit",
                "title": "Breaking news about AI",
                "text": "New AI breakthrough announced today...",
                "author": "user123",
                "upvotes": 150,
                "comments_count": 45,
                "url": "https://reddit.com/r/technology/...",
                "subreddit": "technology",
            }
        }


class CleanedPost(BaseModel):
    original_id: str
    source: str
    platform: str
    original_text: str
    cleaned_text: str
    language: str = "en"
    tokens: list = []
    processed_at: datetime = Field(default_factory=datetime.utcnow)


class TrendingTopic(BaseModel):
    topic_id: str
    topic_name: str
    platform: str
    post_count: int
    engagement_score: float
    sentiment_distribution: dict
    top_keywords: list
    detected_at: datetime = Field(default_factory=datetime.utcnow)


class FactCheckResult(BaseModel):
    claim: str
    verdict: str
    confidence: float
    source_urls: list
    checked_at: datetime = Field(default_factory=datetime.utcnow)


class ClassificationResult(BaseModel):
    text: str
    classification: str
    confidence: float
    sentiment: str
    sentiment_score: float
    fact_check: Optional[FactCheckResult] = None
