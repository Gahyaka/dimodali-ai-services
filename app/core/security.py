from fastapi import Header, HTTPException, status
from app.core.config import settings


async def verify_internal_api_key(
    x_internal_api_key: str | None = Header(default=None, alias="X-Internal-API-Key")
) -> str:
    if not x_internal_api_key or x_internal_api_key != settings.INTERNAL_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "UNAUTHORIZED_ACCESS",
                "message": "Invalid or missing internal API Key header (X-Internal-API-Key)",
                "details": None,
            },
        )
    return x_internal_api_key