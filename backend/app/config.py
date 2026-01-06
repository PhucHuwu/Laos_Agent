"""
Application settings and configuration using pydantic-settings
"""

from typing import Set
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings class with validation"""

    # API Configuration
    API_KEY: str
    API_URL: str = "https://openrouter.ai/api/v1/chat/completions"
    MODEL: str = "z-ai/glm-4.5"

    # OCR API Configuration
    OCR_UPLOAD_URL: str = "http://your-ocr-server:8000/api/v1/ocr/upload-image"
    OCR_SCAN_URL: str = "http://your-ocr-server:8000/api/v1/ocr/scan-url"
    OCR_WEBSOCKET_URL: str = "ws://your-ocr-server:8000/api/v1/ocr/ws/verify"

    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    SECRET_KEY: str = "your-secret-key-here-change-in-production"

    # Upload Configuration
    MAX_CONTENT_LENGTH: int = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS: Set[str] = {"png", "jpg", "jpeg", "gif", "bmp", "webp"}

    # Session Configuration
    SESSION_TIMEOUT: int = 3600  # 1 hour

    # Application Info
    APP_NAME: str = "Laos eKYC API"
    APP_VERSION: str = "2.0.0"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()
