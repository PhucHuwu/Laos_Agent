"""
Main bot class that orchestrates all services
"""

import json
from typing import Dict, Any, Optional, AsyncGenerator
from app.services.ai_service import AIService
from app.services.ocr_service import OCRService
from app.services.face_service import FaceVerificationService
from app.models.conversation import Conversation


class LaosEKYCBot:
    """Main bot class for Laos eKYC system"""

    def __init__(self):
        self.ai_service = AIService()
        self.ocr_service = OCRService()
        self.face_verification_service = FaceVerificationService()
        self.conversation = self.ai_service.conversation

    async def chat(self, user_input: str) -> Dict[str, Any]:
        """
        Process user input and return response

        Args:
            user_input: User's message

        Returns:
            AI response or tool calls
        """
        return await self.ai_service.chat(user_input)

    async def chat_stream(self, user_input: str) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Process user input and return streaming response

        Args:
            user_input: User's message

        Yields:
            Streaming chunks
        """
        async for chunk in self.ai_service.chat_stream(user_input):
            yield chunk

    async def handle_tool_call(self, tool_call: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Handle tool calls from AI

        Args:
            tool_call: Tool call data from AI

        Returns:
            Tool execution result
        """
        try:
            function_name = tool_call["function"]["name"]
            arguments = json.loads(tool_call["function"]["arguments"])

            if function_name == "open_id_scan":
                message = arguments.get("message", "ກະລຸນາອັບໂຫລດບັດປະຈຳຕົວ")
                return {
                    "success": True,
                    "action": "open_id_scan",
                    "message": message,
                    "tool_call_id": tool_call.get("id")
                }

            elif function_name == "open_face_verification":
                message = arguments.get("message", "ກະລຸນາຢັ້ງຢືນໃບໜ້າ")
                return {
                    "success": True,
                    "action": "open_face_verification",
                    "message": message,
                    "tool_call_id": tool_call.get("id")
                }

            return {
                "success": False,
                "message": f"Unknown tool: {function_name}"
            }

        except Exception as e:
            print(f"Error handling tool {tool_call['function']['name']}: {e}")
            return {
                "success": False,
                "message": f"Error: {str(e)}"
            }

    async def process_image_upload(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """
        Complete image processing: upload and scan

        Args:
            file_content: Image file bytes
            filename: Original filename

        Returns:
            Processing result with scan data
        """
        result = await self.ocr_service.process_image(file_content, filename)

        if result.get("success"):
            # Save ID card URL and scan result to context
            self.conversation.set_context("id_card_url", result.get("image_url"))
            self.conversation.set_context("scan_result", result.get("scan_result"))
            self.conversation.set_progress("id_scanned")
            print(f"Progress updated: {self.conversation.progress}")

        return result

    async def verify_face_from_urls(self, id_card_image_url: str, selfie_image_url: str) -> Dict[str, Any]:
        """
        Verify face from image URLs

        Args:
            id_card_image_url: URL of ID card image
            selfie_image_url: URL of selfie image

        Returns:
            Verification result
        """
        # Update progress
        self.conversation.set_progress("face_verifying")
        print(f"Progress updated: {self.conversation.progress}")

        result = await self.face_verification_service.verify_face_from_urls(
            id_card_image_url, selfie_image_url
        )

        if result.get("success"):
            result_data = result.get("result", {})

            # Check verification result
            if result_data.get("same_person") is True:
                # Session will be deleted by the route handler
                # Just log success here
                print(f"Face verification successful in bot.verify_face_from_urls")
            else:
                # Verification failed - revert to id_scanned
                self.conversation.set_progress("id_scanned")
                print(f"Verification failed, progress reverted: {self.conversation.progress}")
        else:
            # Error - revert to id_scanned
            self.conversation.set_progress("id_scanned")
            print(f"Verification error, progress reverted: {self.conversation.progress}")

        return result

    def start_realtime_verification(self, id_card_image_url: str):
        """
        Start real-time face verification

        Args:
            id_card_image_url: URL of ID card image

        Returns:
            RealtimeFaceVerificationClient instance
        """
        return self.face_verification_service.start_realtime_verification(id_card_image_url)

    def stop_realtime_verification(self):
        """Stop real-time face verification"""
        self.face_verification_service.stop_realtime_verification()

    def reset_conversation(self):
        """Reset conversation to initial state"""
        self.ai_service.reset_conversation()

    def get_conversation_history(self) -> list:
        """Get conversation history"""
        return self.ai_service.get_conversation_history()
