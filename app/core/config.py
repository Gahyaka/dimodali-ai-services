from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Toko Roti DimoDali - AI Microservice API"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"

    INTERNAL_API_KEY: str = "dmd_secret_ai_key_2026_xyz123"
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-3.5-flash-lite"

    CHROMA_DB_PATH: str = "./chroma_db"
    CHROMA_COLLECTION_NAME: str = "dimodali_menu_catalog"
    MODEL_DIR: str = "./app/models"

    WHATSAPP_ADMIN_NUMBER: str = "6285235234052"
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:5000"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]


settings = Settings()