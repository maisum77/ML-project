from fastapi import APIRouter
from backend.app.api import trending, sentiment, classify, feed, export, propagation, geo, authority

router = APIRouter()

router.include_router(trending.router, prefix="/trending", tags=["Trending"])
router.include_router(sentiment.router, prefix="/sentiment", tags=["Sentiment"])
router.include_router(classify.router, prefix="/classify", tags=["Classification"])
router.include_router(feed.router, prefix="/feed", tags=["Feed"])
router.include_router(export.router, prefix="/export", tags=["Export"])
router.include_router(propagation.router, prefix="/propagation", tags=["Propagation"])
router.include_router(geo.router, prefix="/geo", tags=["Geo"])
router.include_router(authority.router, prefix="/authority", tags=["Authority"])
