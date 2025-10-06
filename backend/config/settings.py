"""
Application settings and configuration
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings:
    """Application settings class"""

    def __init__(self):
        # API Configuration
        self.API_KEY: Optional[str] = os.getenv("API_KEY")
        self.API_URL: str = os.getenv("API_URL", "https://openrouter.ai/api/v1/chat/completions")
        self.MODEL: str = os.getenv("MODEL", "z-ai/glm-4.6")

        # OCR API Configuration
        self.OCR_UPLOAD_URL: str = os.getenv("OCR_UPLOAD_URL", "http://172.16.5.10:8001/api/v1/ocr/upload-image")
        self.OCR_SCAN_URL: str = os.getenv("OCR_SCAN_URL", "http://172.16.5.10:8001/api/v1/ocr/scan-url")
        self.OCR_WEBSOCKET_URL: str = os.getenv("OCR_WEBSOCKET_URL", "ws://172.16.5.10:8001/api/v1/ocr/ws/verify")

        # Flask Configuration
        self.FLASK_HOST: str = os.getenv("FLASK_HOST", "0.0.0.0")
        self.FLASK_PORT: int = int(os.getenv("FLASK_PORT", "5001"))
        self.FLASK_DEBUG: bool = os.getenv("FLASK_DEBUG", "False").lower() == "true"
        self.FLASK_SECRET_KEY: str = os.getenv("FLASK_SECRET_KEY", "your-secret-key-here")

        # Upload Configuration
        self.UPLOAD_FOLDER: str = os.getenv("UPLOAD_FOLDER", "uploads")
        self.MAX_CONTENT_LENGTH: int = int(os.getenv("MAX_CONTENT_LENGTH", str(16 * 1024 * 1024)))  # 16MB
        self.ALLOWED_EXTENSIONS: set = {
            'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'
        }

        # Application Info
        self.APP_NAME: str = "ລະບົບ eKYC ບັດປະຈໍາຕົວ ສປປ ລາວ"
        self.APP_VERSION: str = "1.0.0"

    def validate(self) -> bool:
        """Validate required settings"""
        if not self.API_KEY:
            raise ValueError("API_KEY is required but not set in environment variables")
        return True

    def __str__(self) -> str:
        return f"{self.APP_NAME} v{self.APP_VERSION}"
