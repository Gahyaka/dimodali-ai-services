from fastapi import APIRouter, Depends
from app.core.security import verify_internal_api_key
from app.schemas.chat_schema import (
    IntentClassifyData,
    IntentClassifyRequest,
    StandardResponse,
)
from app.services.intent_service import intent_service

router = APIRouter()


@router.post(
    "/intent/classify",
    response_model=StandardResponse[IntentClassifyData],
    dependencies=[Depends(verify_internal_api_key)],
    tags=["Intent Classification"],
)
async def classify_intent(payload: IntentClassifyRequest):
    intent, confidence, probabilities = intent_service.predict(payload.text)
    return StandardResponse(
        status_code=200,
        message="Intent classified successfully",
        data=IntentClassifyData(
            intent=intent,
            confidence=confidence,
            probabilities=probabilities,
        ),
    )