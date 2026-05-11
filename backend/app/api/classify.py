from fastapi import APIRouter
from backend.app.schemas.responses import ClassificationRequest
from backend.app.services.classification_service import classify_text

router = APIRouter()


@router.post("/")
async def classify(request: ClassificationRequest):
    result = await classify_text(text=request.text, source=request.source)
    return result
