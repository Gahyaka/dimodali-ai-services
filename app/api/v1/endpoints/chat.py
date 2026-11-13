from urllib.parse import quote
from fastapi import APIRouter, Depends, HTTPException, status
from app.core.config import settings
from app.core.security import verify_internal_api_key
from app.schemas.chat_schema import ChatAction, ChatData, ChatRequest, StandardResponse
from app.services.intent_service import intent_service
from app.services.rag_service import rag_service

router = APIRouter()

STATIC_FAQ_ATURAN_PO = (
    "Berikut ketentuan pemesanan di Toko Roti DimoDali Kak:\n"
    "• Lokasi Toko: Sidomulyo, Sendangrejo, Kec. Minggir, Kab. Sleman, DIY.\n"
    "• Jam Operasional: Setiap hari pukul 07.00 – 19.00 WIB.\n"
    "• Aturan Pre-Order (PO): Minimal pemesanan H-1 sebelum jadwal pengambilan, "
    "dengan uang muka (DP) 50% untuk konfirmasi produksi.\n"
    "• Pembayaran: Tunai di toko, QRIS, atau transfer bank.\n"
    "Silakan pilih menu di katalog atau racik paket di Custom Snack Box Builder ya Kak!"
)


def _build_wa_redirect(prefill_text: str) -> ChatAction:
    encoded = quote(prefill_text)
    return ChatAction(
        type="wa_redirect",
        url=f"https://wa.me/{settings.WHATSAPP_ADMIN_NUMBER}?text={encoded}",
    )


@router.post(
    "/chat",
    response_model=StandardResponse[ChatData],
    dependencies=[Depends(verify_internal_api_key)],
    tags=["Chatbot RAG Assistant"],
)
async def chat_assistant(payload: ChatRequest):
    user_msg = payload.message.strip()

    # 1. Pre-processing Sapaan via Regex (0 Token)
    if intent_service.is_greeting(user_msg):
        return StandardResponse(
            status_code=200,
            message="Chat response generated successfully",
            data=ChatData(
                reply=(
                    "Halo! Selamat datang di Toko Roti DimoDali. "
                    "Ada yang bisa kami bantu seputar varian roti manis, bolen pisang, "
                    "pizza mini, atau paket snack box hari ini?"
                ),
                detected_intent="greeting",
                confidence=1.0,
                sources=[],
                action=None,
            ),
        )

    # 2. Klasifikasi 5 Intent
    intent, confidence, _ = intent_service.predict(user_msg)

    # 3. Confidence Threshold < 0.60 (Fallback Klarifikasi)
    if confidence < 0.60:
        return StandardResponse(
            status_code=200,
            message="Chat response generated successfully",
            data=ChatData(
                reply=(
                    "Mohon maaf Kak, bisa diperjelas pertanyaan seputar menu roti, paket snack box, "
                    "atau aturan pemesanan di DimoDali? Atau Kakak bisa langsung menghubungi admin WhatsApp kami."
                ),
                detected_intent="low_confidence_fallback",
                confidence=confidence,
                sources=[],
                action=_build_wa_redirect("Halo Admin DimoDali, saya ingin bertanya seputar menu/pesanan."),
            ),
        )

    # 4. Downstream Intent Routing
    if intent == "aturan_pemesanan":
        return StandardResponse(
            status_code=200,
            message="Chat response generated successfully",
            data=ChatData(
                reply=STATIC_FAQ_ATURAN_PO,
                detected_intent=intent,
                confidence=confidence,
                sources=[],
                action=None,
            ),
        )

    if intent == "keluhan":
        return StandardResponse(
            status_code=200,
            message="Chat response generated successfully",
            data=ChatData(
                reply=(
                    "Mohon maaf atas ketidaknyamanan yang Kakak alami. "
                    "Agar kendala pesanan dapat segera ditangani langsung oleh pemilik toko, "
                    "silakan klik tombol di bawah untuk terhubung ke WhatsApp Admin DimoDali."
                ),
                detected_intent=intent,
                confidence=confidence,
                sources=[],
                action=_build_wa_redirect("Halo Admin DimoDali, saya ingin menyampaikan kendala terkait pesanan saya."),
            ),
        )

    if intent == "out_of_scope":
        return StandardResponse(
            status_code=200,
            message="Chat response generated successfully",
            data=ChatData(
                reply=(
                    "Maaf Kak, asisten virtual ini hanya melayani informasi seputar produk roti, "
                    "paket snack box, dan pemesanan di Toko Roti DimoDali. "
                    "Jika ada kebutuhan khusus lainnya, silakan hubungi Admin kami via WhatsApp."
                ),
                detected_intent=intent,
                confidence=confidence,
                sources=[],
                action=_build_wa_redirect("Halo Admin DimoDali, saya ingin bertanya."),
            ),
        )

    # 5. RAG Pipeline untuk intent 'tanya_produk' dan 'rekomendasi_paket'
    try:
        history_dicts = [h.model_dump() for h in payload.history]
        reply_text, sources = rag_service.generate_rag_reply(
            message=user_msg,
            intent=intent,
            history=history_dicts,
        )
        return StandardResponse(
            status_code=200,
            message="Chat response generated successfully",
            data=ChatData(
                reply=reply_text,
                detected_intent=intent,
                confidence=confidence,
                sources=sources,
                action=None,
            ),
        )
    except Exception as exc:
        error_msg = str(exc)
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "code": "GEMINI_RATE_LIMIT",
                    "message": "Kuota API LLM sedang padat, silakan coba sesaat lagi.",
                    "details": None,
                },
            ) from exc
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "LLM_SERVICE_UNAVAILABLE",
                "message": "Layanan AI generatif sedang tidak dapat dihubungi.",
                "details": None,
            },
        ) from exc