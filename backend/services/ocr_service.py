"""
OCR Service for image processing and text extraction
"""

import requests
from typing import Dict, Any, Optional
from ..config import settings
from ..models.verification import ScanResult


class OCRService:
    """Service for OCR operations"""

    def __init__(self):
        self.upload_url = settings.OCR_UPLOAD_URL
        self.scan_url = settings.OCR_SCAN_URL

    def upload_image(self, image_path: str) -> Dict[str, Any]:
        """
        Upload image to OCR server

        Args:
            image_path: Path to the image file

        Returns:
            Dictionary containing upload result
        """
        try:
            with open(image_path, 'rb') as image_file:
                files = {'file': image_file}
                response = requests.post(self.upload_url, files=files)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to upload image: {str(e)}"
            }

    def scan_image_from_url(self, image_url: str) -> ScanResult:
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
            response = requests.post(self.scan_url, json=payload, headers=headers)
            response.raise_for_status()

            result_data = response.json()

            # Remove img_base64 to save tokens
            if isinstance(result_data, dict) and 'img_base64' in result_data:
                result_data.pop('img_base64')

            return ScanResult.from_dict(result_data)

        except Exception as e:
            return ScanResult(
                status="error",
                message=f"Failed to scan image: {str(e)}"
            )

    def process_image(self, image_path: str) -> Dict[str, Any]:
        """
        Complete image processing: upload and scan

        Args:
            image_path: Path to the image file

        Returns:
            Dictionary containing both upload and scan results
        """
        # Upload image
        upload_result = self.upload_image(image_path)

        if not upload_result.get("success", True):  # Some APIs don't return success field
            return upload_result

        # Get image URL
        image_url = None
        if isinstance(upload_result, str):
            image_url = upload_result
        elif isinstance(upload_result, dict):
            image_url = upload_result.get('url')

        if not image_url:
            return {
                "success": False,
                "error": "Could not get image URL from upload result"
            }

        # Scan image
        scan_result = self.scan_image_from_url(image_url)

        return {
            "success": True,
            "image_url": image_url,
            "scan_result": scan_result.to_dict()
        }
