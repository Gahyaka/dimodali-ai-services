from typing import Any, Dict, Generic, List, Literal, Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


# --- Standard Wrapper (Sesuai API Contract Bagian 3) ---
class StandardResponse(BaseModel, Generic[T]):
    success: bool = True
    status_code: int = 200
    message: str
    data: T


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[Any] = None


class ErrorResponse(BaseModel):
    success: bool = False
    status_code: int
    error: ErrorDetail


# --- Endpoint 1: Health Check ---
class HealthData(BaseModel):
    status: str = "UP"
    version: str
    rag_chroma_ready: bool
    intent_model_ready: bool


# --- Endpoint 2: Intent Classification ---
class IntentClassifyRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=500, description="Teks masukan pengguna")


class IntentClassifyData(BaseModel):
    intent: str
    confidence: float
    probabilities: Dict[str, float]


# --- Endpoint 3: Chatbot RAG Assistant ---
class ChatHistoryItem(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    session_id: str = Field(..., min_length=1, description="Identifier unik sesi obrolan")
    message: str = Field(..., min_length=1, max_length=1000, description="Pesan terbaru pengguna")
    history: List[ChatHistoryItem] = Field(default_factory=list)


class ChatAction(BaseModel):
    type: Literal["wa_redirect"] = "wa_redirect"
    url: str


class ChatData(BaseModel):
    reply: str
    detected_intent: str
    confidence: float
    sources: List[Dict[str, Any]] = Field(default_factory=list)
    action: Optional[ChatAction] = None