from fastapi import APIRouter
from app.core.config import settings
from app.schemas.chat_schema import HealthData, StandardResponse
from app.services.intent_service import intent_service
from app.services.rag_service import rag_service

router = APIRouter()


@router.get("/health", response_model=StandardResponse[HealthData], tags=["Health Check"])
async def health_check():
    return StandardResponse(
        status_code=200,
        message="AI Service is healthy",
        data=HealthData(
            status="UP",
            version=settings.APP_VERSION,
            rag_chroma_ready=rag_service.is_ready,
            intent_model_ready=intent_service.is_ready,
        ),
    )