"""
Chat service for managing chat functionality
"""

from typing import Dict, Any, Callable, Optional
from .api_service import APIService


class ChatService:
    """Service for chat functionality"""

    def __init__(self, apiService: APIService):
        self.apiService = apiService
        self.onMessageReceived: Optional[Callable] = None
        self.onTypingStart: Optional[Callable] = None
        self.onTypingStop: Optional[Callable] = None
        self.onToolCall: Optional[Callable] = None

    def setMessageHandler(self, handler: Callable[[str, str], None]):
        """Set message handler for received messages"""
        self.onMessageReceived = handler

    def setTypingHandlers(self, startHandler: Callable, stopHandler: Callable):
        """Set typing indicator handlers"""
        self.onTypingStart = startHandler
        self.onTypingStop = stopHandler

    def setToolCallHandler(self, handler: Callable[[list], None]):
        """Set tool call handler"""
        self.onToolCall = handler

    async def sendMessage(self, message: str) -> bool:
        """
        Send message to backend

        Args:
            message: Message to send

        Returns:
            bool: Success status
        """
        if not message.strip():
            return False

        # Show typing indicator
        if self.onTypingStart:
            self.onTypingStart()

        try:
            # Send to backend
            response = await self.apiService.sendChatMessage(message)

            # Hide typing indicator
            if self.onTypingStop:
                self.onTypingStop()

            if response.get("success"):
                # Check if response contains tool calls
                if response.get("tool_calls"):
                    if self.onToolCall:
                        self.onToolCall(response["tool_calls"])
                else:
                    # Regular message response
                    if self.onMessageReceived:
                        self.onMessageReceived(response.get("response", ""), "bot")

                return True
            else:
                # Error response
                if self.onMessageReceived:
                    self.onMessageReceived(
                        f"Lỗi: {response.get('error', 'Có lỗi xảy ra')}",
                        "bot"
                    )
                return False

        except Exception as e:
            # Hide typing indicator on error
            if self.onTypingStop:
                self.onTypingStop()

            # Show error message
            if self.onMessageReceived:
                self.onMessageReceived(f"Lỗi kết nối: {str(e)}", "bot")

            return False

    async def resetConversation(self) -> bool:
        """Reset conversation"""
        try:
            response = await self.apiService.resetConversation()
            return response.get("success", False)
        except Exception:
            return False
