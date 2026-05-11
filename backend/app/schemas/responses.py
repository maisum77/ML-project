from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class FeedFilter(BaseModel):
    platform: Optional[str] = None
    sentiment: Optional[str] = None
    classification: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = 50
    offset: int = 0


class TrendingResponse(BaseModel):
    topics: list
    updated_at: datetime


class SentimentResponse(BaseModel):
    topic: str
    sentiment_timeline: list
    overall_sentiment: str


class ClassificationRequest(BaseModel):
    text: str
    source: Optional[str] = None


class ExportResponse(BaseModel):
    format: str
    data: list
    count: int
