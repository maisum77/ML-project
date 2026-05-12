from fastapi import APIRouter, Query
from backend.app.schemas.responses import ClassificationRequest
from backend.app.services.classification_service import classify_text, classify_text_simple

router = APIRouter()


@router.post("/")
async def classify(request: ClassificationRequest):
    result = await classify_text_simple(text=request.text, source=request.source)
    return result


@router.post("/detailed")
async def classify_detailed(request: ClassificationRequest):
    result = await classify_text(text=request.text, source=request.source)
    return result