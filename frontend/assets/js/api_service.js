"""
API service for communicating with backend
"""

from typing import Dict, Any, Optional
import json


class APIService:
    """Service for API communication"""

    def __init__(self, baseUrl: str = ""):
        self.baseUrl = baseUrl

    async def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make POST request to API"""
        try:
            response = await fetch(f"{self.baseUrl}{endpoint}", {
                "method": "POST",
                "headers": {
                    "Content-Type": "application/json",
                },
                "body": json.dumps(data)
            })

            if not response.ok:
                raise Exception(f"HTTP error! status: {response.status}")

            return await response.json()
        except Exception as e:
            return {"error": str(e)}

    async def postFormData(self, endpoint: str, formData: 'FormData') -> Dict[str, Any]:
        """Make POST request with FormData"""
        try:
            response = await fetch(f"{self.baseUrl}{endpoint}", {
                "method": "POST",
                "body": formData
            })

            if not response.ok:
                raise Exception(f"HTTP error! status: {response.status}")

            return await response.json()
        except Exception as e:
            return {"error": str(e)}

    async def sendChatMessage(self, message: str) -> Dict[str, Any]:
        """Send chat message to backend"""
        return await self.post("/chat", {"message": message})

    async def uploadFile(self, file: 'File') -> Dict[str, Any]:
        """Upload file to backend"""
        formData = FormData()
        formData.append("file", file)
        return await self.postFormData("/upload", formData)

    async def verifyFace(self, idCardUrl: str, selfieUrl: str) -> Dict[str, Any]:
        """Verify face using two image URLs"""
        return await self.post("/verify-face", {
            "id_card_image_url": idCardUrl,
            "selfie_image_url": selfieUrl
        })

    async def verifyFaceRealtime(self, idCardUrl: str, selfieUrl: str) -> Dict[str, Any]:
        """Verify face in real-time"""
        return await self.post("/verify-face-realtime", {
            "id_card_image_url": idCardUrl,
            "selfie_image_url": selfieUrl
        })

    async def startWebSocketVerification(self, idCardUrl: str) -> Dict[str, Any]:
        """Start WebSocket verification"""
        return await self.post("/start-websocket-verification", {
            "id_card_image_url": idCardUrl
        })

    async def sendFrame(self, frameBase64: str) -> Dict[str, Any]:
        """Send frame for real-time verification"""
        return await self.post("/send-frame", {
            "frame_base64": frameBase64
        })

    async def stopWebSocketVerification(self) -> Dict[str, Any]:
        """Stop WebSocket verification"""
        return await self.post("/stop-websocket-verification", {})

    async def resetConversation(self) -> Dict[str, Any]:
        """Reset conversation"""
        return await self.post("/reset", {})
