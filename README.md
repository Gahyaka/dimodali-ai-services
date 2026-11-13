# 🥐 Toko Roti DimoDali — Next-Gen AI Microservice (`dimodali-ai-services`)

> **Microservice REST API** mandiri berbasis **FastAPI** untuk mendukung sistem rekomendasi menu, klasifikasi intent obrolan, dan arsitektur *Retrieval-Augmented Generation* (RAG) pada aplikasi web katalog interaktif Toko Roti DimoDali.

---

## 🏗️ Arsitektur & Teknologi Utama
Repositori ini dikembangkan menggunakan arsitektur *decoupled* yang terisolasi dari *backend* utama (Express.js) guna memisahkan logika komputasi AI secara efisien:
* **Framework API:** `FastAPI` + `Uvicorn` (Asynchronous ASGI Server).
* **Validasi Skema:** `Pydantic v2` dengan penanganan error terstandar ala **RFC 7807**.
* **Generative AI & LLM:** Google Gen AI SDK (`google-genai`) menggunakan model **`gemini-3.5-flash-lite`**.
* **Vector Database:** `ChromaDB` (Persistent Client) untuk pencarian semantik basis pengetahuan menu.
* **Intent Classification:** `Scikit-Learn` (TF-IDF Vectorizer + Classifier lokal) dengan efisiensi sapaan berbasis *regex* (0 token).

---

## 📂 Struktur Direktori Proyek

```text
dimodali-ai-services/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── chat.py          # Endpoint POST /api/v1/chat (RAG + Intent Routing)
│   │       │   ├── health.py        # Endpoint GET /api/v1/health (Diagnostics)
│   │       │   └── intent.py        # Endpoint POST /api/v1/intent/classify
│   │       └── router.py            # Central API Router v1
│   ├── core/
│   │   ├── config.py                # Konfigurasi Pydantic Settings & ENV
│   │   └── security.py              # Middleware validasi X-Internal-API-Key
│   ├── models/
│   │   ├── intent_classifier.pkl    # Bobot model Scikit-Learn terlatih
│   │   └── tfidf_vectorizer.pkl     # TF-IDF Vectorizer terlatih
│   ├── schemas/
│   │   └── chat_schema.py           # Skema Request/Response DTO Pydantic & RFC 7807 Wrapper
│   └── services/
│   │   ├── intent_service.py        # Logika pre-filtering regex & klasifikasi intent
│   │   └── rag_service.py           # Orchestrator ChromaDB + Google Gen AI SDK
│   └── main.py                      # Entry point FastAPI, CORS Middleware, & Global Handlers
├── data/
│   ├── menu_catalog.json            # Kamus data menu tervalidasi UMKM
│   └── intent_dataset.csv           # Dataset latih 5 kelas intent
├── scripts/
│   ├── build_vector_store.py        # Skrip indexing dokumen ke ChromaDB
│   └── train_intent_model.py        # Skrip training model Scikit-Learn & evaluasi metrik
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md

```

---

## 🔒 Keamanan & Kontrak API

Komunikasi antara *backend* Express.js dan microservice FastAPI dilindungi menggunakan mekanisme *static shared secret key* melalui header kustom:

* **Header Name:** `X-Internal-API-Key`
* **Nilai Default (Dev):** `dmd_secret_ai_key_2026_xyz123`

Setiap *request* yang tidak menyertakan header atau menggunakan kunci yang keliru akan ditolak secara otomatis dengan status **`HTTP 401 Unauthorized`** berformat RFC 7807.

---

## 🚀 Panduan Instalasi & Menjalankan Lokal

1. **Clone repositori dan buat virtual environment:**
```bash
git clone [https://github.com/gahyaka/dimodali-ai-services.git](https://github.com/gahyaka/dimodali-ai-services.git)
cd dimodali-ai-services
python -m venv venv
```
2. **Aktifkan virtual environment:**
* **Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```
* **macOS / Linux:**
```bash
source venv/bin/activate
```
3. **Install dependensi yang diperlukan:**
```bash
pip install -r requirements.txt
```
4. **Konfigurasi Environment Variables:**
Salin file `.env.example` menjadi `.env` lalu sesuaikan isinya:
```powershell
copy .env.example .env
```
5. **Jalankan server pengembangan FastAPI:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

```
6. **Akses Dokumentasi Interaktif (Swagger UI):**
Buka peramban dan kunjungi: [http://localhost:8000/docs](http://localhost:8000/docs)
---

## 🧪 Skenario Endpoint & Pengujian

| Endpoint | Method | Autentikasi | Deskripsi Singkat |
| --- | --- | --- | --- |
| `/api/v1/health` | `GET` | Publik | Pemeriksaan status kesiapan service dan ChromaDB.|
| `/api/v1/intent/classify` | `POST` | Wajib (`X-Internal-API-Key`) | Memetakan teks ke 5 kelas intent (`tanya_produk`, `rekomendasi_paket`, `aturan_pemesanan`, `keluhan`, `out_of_scope`).|
| `/api/v1/chat` | `POST` | Wajib (`X-Internal-API-Key`) | Alur percakapan RAG penuh dengan optimasi token, *guardrails*, dan aksi `wa_redirect`.|

---

## 📊 Evaluasi Model & Eksperimen *(Wajib Main Quest)*

*(Tabel perbandingan metrik evaluasi model Scikit-Learn akan diperbarui setelah skrip `train_intent_model.py` dieksekusi bersama dataset dari tim Data Science).*

```

```
