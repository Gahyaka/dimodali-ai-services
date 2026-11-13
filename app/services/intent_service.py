import os
import re
from typing import Dict, Tuple
import joblib
from app.core.config import settings

INTENT_CLASSES = [
    "tanya_produk",
    "rekomendasi_paket",
    "aturan_pemesanan",
    "keluhan",
    "out_of_scope",
]

GREETING_PATTERN = re.compile(
    r"^(halo+|hallo+|hai+|hi+|p+|permisi|assalamualaikum|assalamu'alaikum|"
    r"selamat\s+(pagi|siang|sore|malam)|pagi|siang|sore|malam)[\s!.,?]*$",
    re.IGNORECASE,
)


class IntentService:
    def __init__(self) -> None:
        self.vectorizer = None
        self.classifier = None
        self.is_ready = False
        self._load_artifacts()

    def _load_artifacts(self) -> None:
        vec_path = os.path.join(settings.MODEL_DIR, "tfidf_vectorizer.pkl")
        clf_path = os.path.join(settings.MODEL_DIR, "intent_classifier.pkl")
        if os.path.exists(vec_path) and os.path.exists(clf_path):
            self.vectorizer = joblib.load(vec_path)
            self.classifier = joblib.load(clf_path)
            self.is_ready = True

    def is_greeting(self, text: str) -> bool:
        return bool(GREETING_PATTERN.match(text.strip()))

    def _preprocess(self, text: str) -> str:
        text = text.lower().strip()
        text = re.sub(r"[^a-z0-9\s]", " ", text)
        return re.sub(r"\s+", " ", text).strip()

    def predict(self, text: str) -> Tuple[str, float, Dict[str, float]]:
        clean_text = self._preprocess(text)

        # Jika model .pkl sudah dilatih di Minggu 1, gunakan inferensi Scikit-Learn
        if self.is_ready and self.vectorizer and self.classifier:
            vec = self.vectorizer.transform([clean_text])
            probs = self.classifier.predict_proba(vec)[0]
            classes = list(self.classifier.classes_)
            prob_map = {cls: round(float(p), 4) for cls, p in zip(classes, probs)}
            best_intent = max(prob_map, key=prob_map.get)
            return best_intent, prob_map[best_intent], prob_map

        # Fallback rule-based sementara sebelum file .pkl tersedia
        if any(k in clean_text for k in ["rusak", "basi", "komplain", "kecewa", "salah pesanan"]):
            intent = "keluhan"
        elif any(k in clean_text for k in ["po", "pre order", "dp", "jam buka", "alamat", "lokasi", "bayar"]):
            intent = "aturan_pemesanan"
        elif any(k in clean_text for k in ["budget", "anggaran", "rekomendasi", "snack box", "paket", "acara"]):
            intent = "rekomendasi_paket"
        elif any(k in clean_text for k in ["bolen", "pizza", "roti", "harga", "varian", "rasa", "tahan"]):
            intent = "tanya_produk"
        else:
            intent = "out_of_scope"

        prob_map = {cls: (0.85 if cls == intent else 0.0375) for cls in INTENT_CLASSES}
        return intent, 0.85, prob_map


intent_service = IntentService()