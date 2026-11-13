import os
from typing import Any, Dict, List, Tuple
import chromadb
from chromadb.utils import embedding_functions
from google import genai
from google.genai import types
from app.core.config import settings


class RAGService:
    def __init__(self) -> None:
        self.is_ready = False
        self.collection = None
        self.ai_client = None
        self._init_clients()

    def _init_clients(self) -> None:
        try:
            os.makedirs(settings.CHROMA_DB_PATH, exist_ok=True)
            chroma_client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
            ef = embedding_functions.DefaultEmbeddingFunction()
            self.collection = chroma_client.get_or_create_collection(
                name=settings.CHROMA_COLLECTION_NAME,
                embedding_function=ef,
                metadata={"hnsw:space": "cosine"},
            )
            self.is_ready = True
        except Exception:
            self.is_ready = False

        if settings.GEMINI_API_KEY:
            self.ai_client = genai.Client(api_key=settings.GEMINI_API_KEY)

    def retrieve_context(self, query: str, top_k: int = 3) -> Tuple[str, List[Dict[str, Any]]]:
        if not self.is_ready or not self.collection or self.collection.count() == 0:
            return "", []

        results = self.collection.query(query_texts=[query], n_results=top_k)
        docs = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]

        context_text = "\n".join(docs)
        sources = [meta for meta in metadatas if meta]
        return context_text, sources

    def generate_rag_reply(
        self,
        message: str,
        intent: str,
        history: List[Dict[str, str]],
    ) -> Tuple[str, List[Dict[str, Any]]]:
        context_text, sources = self.retrieve_context(message)

        if not self.ai_client:
            fallback = (
                "Maaf Kak, layanan asisten cerdas sedang dalam konfigurasi API. "
                "Silakan cek katalog menu kami di halaman utama atau hubungi WhatsApp admin DimoDali."
            )
            return fallback, sources

        system_instruction = (
            "Anda adalah Asisten Virtual Toko Roti DimoDali (Minggir, Sleman, Yogyakarta) yang ramah, sopan, dan membantu. "
            "Jawab pertanyaan pelanggan HANYA berdasarkan KONTEKS KATALOG MENU di bawah ini. "
            "Dilarang mengarang harga, varian, atau promo yang tidak ada di konteks. "
            "Jika intent adalah 'rekomendasi_paket', berikan kombinasi menu sesuai anggaran/acara pelanggan dan arahkan pelanggan "
            "untuk mencoba fitur 'Custom Snack Box Builder' di website agar dapat menghitung rincian harga secara langsung.\n\n"
            f"KONTEKS KATALOG MENU:\n{context_text or 'Belum ada data katalog yang dimuat.'}"
        )

        # Sertakan maksimal 4 pesan riwayat terakhir untuk menjaga efisiensi token
        recent_history = "\n".join(
            [f"{item['role'].upper()}: {item['content']}" for item in history[-4:]]
        )
        prompt = f"Riwayat singkat:\n{recent_history}\n\nPertanyaan pelanggan:\n{message}" if recent_history else message

        response = self.ai_client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.3,
            ),
        )
        return response.text, sources


rag_service = RAGService()