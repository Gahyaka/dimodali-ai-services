from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.v1.router import api_router
from app.core.config import settings
from app.schemas.chat_schema import ErrorDetail, ErrorResponse

app = FastAPI(
    title=settings.APP_NAME,
    description="Microservice REST API (Intent Classification & RAG) untuk Toko Roti DimoDali — Tim A26-CS039",
    version=settings.APP_VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException):
    if isinstance(exc.detail, dict) and "code" in exc.detail:
        error_detail = ErrorDetail(**exc.detail)
    else:
        error_detail = ErrorDetail(code="HTTP_ERROR", message=str(exc.detail), details=None)

    payload = ErrorResponse(success=False, status_code=exc.status_code, error=error_detail)
    return JSONResponse(status_code=exc.status_code, content=payload.model_dump())


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError):
    payload = ErrorResponse(
        success=False,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        error=ErrorDetail(
            code="VALIDATION_ERROR",
            message="Request schema validation failed",
            details=exc.errors(),
        ),
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=payload.model_dump(),
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(_: Request, exc: Exception):
    payload = ErrorResponse(
        success=False,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error=ErrorDetail(
            code="INTERNAL_SERVER_ERROR",
            message="Terjadi kesalahan internal pada microservice AI.",
            details=str(exc) if settings.APP_ENV == "development" else None,
        ),
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=payload.model_dump(),
    )


app.include_router(api_router, prefix="/api/v1")