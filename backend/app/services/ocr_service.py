"""
OCR Service for image processing and text extraction with async support
"""

import httpx
from typing import Dict, Any
from app.config import settings
from app.models.verification import ScanResult


class OCRService:
    """Service for OCR operations"""

    def __init__(self):
        self.upload_url = settings.OCR_UPLOAD_URL
        self.scan_url = settings.OCR_SCAN_URL

    async def upload_image(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """
        Upload image to OCR server

        Args:
            file_content: Image file bytes
            filename: Original filename

        Returns:
            Dictionary containing upload result with URL
        """
        try:
            files = {"file": (filename, file_content)}

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(self.upload_url, files=files)
                response.raise_for_status()
                return response.json()

        except httpx.RequestError as e:
            return {
                "success": False,
                "error": f"Failed to upload image: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }

    async def scan_image_from_url(self, image_url: str) -> ScanResult:
        """
        Scan image from URL for text extraction

        Args:
            image_url: URL of the image to scan

        Returns:
            ScanResult object with extracted information
        """
        try:
            payload = {"url": image_url}
            headers = {"Content-Type": "application/json"}

            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(self.scan_url, json=payload, headers=headers)
                response.raise_for_status()

                result_data = response.json()

                # Remove img_base64 to save memory/bandwidth
                if isinstance(result_data, dict) and "img_base64" in result_data:
                    result_data.pop("img_base64")

                return ScanResult.from_api_response(result_data)

        except httpx.RequestError as e:
            return ScanResult(
                status="error",
                message=f"Failed to scan image: {str(e)}"
            )
        except Exception as e:
            return ScanResult(
                status="error",
                message=f"Unexpected error: {str(e)}"
            )

    async def process_image(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """
        Complete image processing: upload and scan

        Args:
            file_content: Image file bytes
            filename: Original filename

        Returns:
            Dictionary containing both upload and scan results
        """
        # Upload image
        upload_result = await self.upload_image(file_content, filename)

        if not upload_result.get("success", True):
            return upload_result

        # Get image URL
        image_url = None
        if isinstance(upload_result, str):
            image_url = upload_result
        elif isinstance(upload_result, dict):
            image_url = upload_result.get("url")

        if not image_url:
            return {
                "success": False,
                "error": "Could not get image URL from upload result"
            }

        # Scan image
        scan_result = await self.scan_image_from_url(image_url)

        return {
            "success": True,
            "image_url": image_url,
            "scan_result": scan_result.model_dump()
        }
