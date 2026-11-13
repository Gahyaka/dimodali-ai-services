# 🥐 DimoDali AI Service (Microservice REST API)

Repositori ini memuat layanan *microservice* berbasis FastAPI yang menangani fungsionalitas kecerdasan buatan untuk **Toko Roti DimoDali** (Capstone Team A26-CS039 - Program Asah 2026 led by Dicoding supported by GoTo).

---

## 📌 1. Latar Belakang & Permasalahan Bisnis
Toko Roti DimoDali menghadapi kendala tingginya volume pesan berulang pada obrolan WhatsApp mengenai varian rasa, harga paket *snack box*, batas minimal pemesanan, serta ketentuan *Pre-Order* (PO). Keterlambatan membalas pesan berpotensi menurunkan konversi penjualan. Layanan AI ini dibangun untuk:
1. Mengklasifikasikan niat (*intent*) percakapan pelanggan secara otomatis ke dalam 4 kategori utama.
2. Memberikan rekomendasi menu dan simulasi paket *snack box* berbasis anggaran menggunakan *Retrieval-Augmented Generation* (RAG).
3. Melindungi konteks obrolan (*guardrails*) agar bot menolak topik di luar seputar produk dan operasional Toko Roti DimoDali.

---

## 🏗️ 2. Arsitektur Sistem & Alur Integrasi
Sistem AI dibangun secara modular (*decoupled microservice*) yang berkomunikasi dengan Back-End utama:
`Pengguna (Web Browser)` ➡️ `Back-End (Express.js)` ➡️ `REST API (FastAPI - Port 8000)` ➡️ `ChromaDB (RAG)` + `Gemini API`

---

## 📊 3. Dataset & Pra-Pemrosesan Data (Sinergi Tim Data Science)
Dataset disediakan oleh tim Data Science (`dimodali-data-analytics`):
- **Sumber Data:** `intent_dataset.csv` (data teks pertanyaan berlabel) dan `menu_catalog.json` (basis pengetahuan menu asli UMKM).
- **Keseimbangan Kelas (Class Balance):** Dataset intent dirancang seimbang antarkelas (~60–75 sampel per intent) untuk mencegah bias klasifikasi.
- **Preprocessing Pipeline:**
  1. *Text Case Folding* (konversi teks ke huruf kecil).
  2. *Regex Cleaning* (pembersihan tanda baca, tautan, dan karakter non-alfanumerik).
  3. *Tokenization & Stopwords Removal* (Bahasa Indonesia).
  4. *Vectorization*: TF-IDF N-Gram (1, 2) untuk model klasifikasi teks.

---

## 🔬 4. Eksperimen & Perbandingan Model (Main Quest Checklist)
Untuk memenuhi standar evaluasi model buatan sendiri, dilakukan perbandingan terhadap 2 algoritma klasifikasi intent menggunakan *stratified test split* (rasio 80:20):

| Model AI | Accuracy | Macro Precision | Macro Recall | Macro F1-Score | Status Pemilihan |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Multinomial Naive Bayes (Baseline)** | 85.0% | 0.86 | 0.84 | 0.84 | Pembanding dasar; cepat namun kurang peka pada sinonim lokal. |
| **Logistic Regression (Tuned)** | **92.5%** | **0.93** | **0.92** | **0.92** | **Model Terpilih**; memiliki generalisasi terbaik dan performa F1-Score tertinggi. |

> **Alasan Pemilihan:** Logistic Regression dengan tuning regularisasi $C=1.0$ menghasilkan batas keputusan yang lebih stabil pada data teks pendek obrolan pelanggan. Bobot model disimpan secara lokal pada `models/intent_classifier.pkl`.

---

## 🤖 5. Integrasi Generative AI & Lightweight RAG
- **Foundation LLM:** Google Gemini 3.5 Flash-lite (`gemini-3.5-flash-lite`) via `google-genai` SDK.
- **Vector Database:** ChromaDB (lokal/persistent storage).
- **RAG Workflow:** Teks pertanyaan pengguna di-*embed* untuk mengambil dokumen relevan dari ChromaDB (profil menu, harga, daya tahan roti, aturan PO), lalu diinjeksikan ke dalam *system prompt* terstruktur.
- **Guardrails:** Menerapkan instruksi ketat agar model menolak pertanyaan *out-of-context* (politik, pemrograman, tugas sekolah) dengan respons ramah khas layanan pelanggan DimoDali.

---

## 🚀 6. Panduan Menjalankan Layanan Secara Lokal

### Prasyarat
- Python 3.10 atau versi lebih baru
- Google AI Studio API Key (`GEMINI_API_KEY`)

### Langkah Instalasi
```bash
# 1. Clone repositori
git clone [https://github.com/putraghayaka/dimodali-ai-service.git](https://github.com/putraghayaka/dimodali-ai-service.git)
cd dimodali-ai-service

# 2. Buat virtual environment
python -m venv venv
source venv/bin/activate  # Untuk Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Konfigurasi Environment Variables (.env)
cp .env.example .env
# Isi GEMINI_API_KEY Anda di dalam file .env

# 5. Latih model klasifikasi intent (jika bobot belum ada)
python scripts/train_intent_model.py

# 6. Jalankan Server FastAPI
uvicorn app.main:app --reload --port 8000
