"""
WebSocket service for real-time communication
"""

from typing import Callable, Optional, Dict, Any
from .api_service import APIService


class WebSocketService:
    """Service for WebSocket operations"""

    def __init__(self, apiService: APIService):
        self.apiService = apiService
        self.isConnected = False
        self.idCardUrl: Optional[str] = None
        self.onResult: Optional[Callable[[Dict[str, Any]], None]] = None
        self.onStatusChange: Optional[Callable[[str], None]] = None
        self.frameCount = 0
        self.SEND_INTERVAL = 30  # Send every 30 frames

    def setCallbacks(self, onResult: Optional[Callable[[Dict[str, Any]], None]] = None,
                     onStatusChange: Optional[Callable[[str], None]] = None):
        """Set WebSocket event callbacks"""
        self.onResult = onResult
        self.onStatusChange = onStatusChange

    async def startVerification(self, idCardUrl: str) -> bool:
        """
        Start WebSocket verification

        Args:
            idCardUrl: URL of ID card image

        Returns:
            bool: Success status
        """
        try:
            self.idCardUrl = idCardUrl

            # Start WebSocket verification
            response = await self.apiService.startWebSocketVerification(idCardUrl)

            if response.get("success"):
                self.isConnected = True
                if self.onStatusChange:
                    self.onStatusChange("connected")
                return True
            else:
                if self.onStatusChange:
                    self.onStatusChange("error")
                return False

        except Exception as e:
            print(f"Error starting WebSocket verification: {e}")
            if self.onStatusChange:
                self.onStatusChange("error")
            return False

    async def sendFrame(self, frameBase64: str) -> bool:
        """
        Send frame for verification

        Args:
            frameBase64: Base64 encoded frame

        Returns:
            bool: Success status
        """
        if not self.isConnected:
            return False

        try:
            response = await self.apiService.sendFrame(frameBase64)

            if response.get("success") and response.get("result"):
                result = response["result"]

                if self.onResult:
                    self.onResult(result)

                # Check if verification is successful
                if (result.get("same_person") and
                        result.get("similarity", 0) > 0.8):
                    # Auto-stop after successful verification
                    await self.stopVerification()

                return True
            else:
                return False

        except Exception as e:
            print(f"Error sending frame: {e}")
            return False

    async def stopVerification(self) -> bool:
        """
        Stop WebSocket verification

        Returns:
            bool: Success status
        """
        try:
            if not self.isConnected:
                return True

            response = await self.apiService.stopWebSocketVerification()

            self.isConnected = False
            self.idCardUrl = None

            if self.onStatusChange:
                self.onStatusChange("disconnected")

            return response.get("success", False)

        except Exception as e:
            print(f"Error stopping WebSocket verification: {e}")
            return False

    def shouldSendFrame(self) -> bool:
        """Check if frame should be sent (based on interval)"""
        self.frameCount += 1
        return self.frameCount % self.SEND_INTERVAL == 0

    def resetFrameCount(self):
        """Reset frame counter"""
        self.frameCount = 0
