"""
Main bot class that orchestrates all services
"""

import json
from typing import Dict, Any, Optional
from ..services.ai_service import AIService
from ..services.ocr_service import OCRService
from ..services.face_verification_service import FaceVerificationService
from ..models.conversation import Conversation
from ..models.verification import ScanResult, VerificationResult


class LaosEKYCBot:
    """Main bot class for Laos eKYC system"""

    def __init__(self):
        self.ai_service = AIService()
        self.ocr_service = OCRService()
        self.face_verification_service = FaceVerificationService()
        self.conversation = self.ai_service.conversation

    def chat(self, user_input: str) -> Any:
        """
        Process user input and return response

        Args:
            user_input: User's message

        Returns:
            AI response or tool calls
        """
        return self.ai_service.chat(user_input)

    def handle_tool_call(self, tool_call: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Handle tool calls from AI

        Args:
            tool_call: Tool call data from AI

        Returns:
            Tool execution result
        """
        try:
            function_name = tool_call['function']['name']
            arguments = json.loads(tool_call['function']['arguments'])

            if function_name == "upload_image_to_server":
                image_path = arguments.get("image_path")
                return self._handle_upload_image(image_path)

            elif function_name == "scan_image_from_url":
                image_url = arguments.get("image_url")
                return self._handle_scan_image(image_url)

            elif function_name == "verify_face":
                id_card_image_url = arguments.get("id_card_image_url")
                selfie_image_url = arguments.get("selfie_image_url")
                return self._handle_verify_face(id_card_image_url, selfie_image_url)

            else:
                # Handle other tools in AI service
                return self.ai_service._handle_tool_call(tool_call)

        except Exception as e:
            print(f"Error handling tool {tool_call['function']['name']}: {e}")
            return {
                "success": False,
                "message": f"Error: {str(e)}"
            }

    def _handle_upload_image(self, image_path: str) -> Dict[str, Any]:
        """Handle image upload"""
        print(f"Uploading image: {image_path}")
        upload_result = self.ocr_service.upload_image(image_path)

        if upload_result.get("success", True):  # Some APIs don't return success field
            image_url = None
            if isinstance(upload_result, str):
                image_url = upload_result
            elif isinstance(upload_result, dict) and 'url' in upload_result:
                image_url = upload_result['url']

            if image_url:
                print("Upload successful!")
                return {
                    "success": True,
                    "url": image_url,
                    "message": f"Upload successful. URL: {image_url}"
                }
            else:
                return {
                    "success": False,
                    "message": "Could not get URL from upload result"
                }
        else:
            return {
                "success": False,
                "message": upload_result.get("error", "Upload failed")
            }

    def _handle_scan_image(self, image_url: str) -> Dict[str, Any]:
        """Handle image scanning"""
        print("🔍 Scanning image...")
        scan_result = self.ocr_service.scan_image_from_url(image_url)

        print("Scan completed!")

        # Lưu ID card URL vào context để AI có thể sử dụng sau này
        self.conversation.set_context('id_card_url', image_url)
        self.conversation.set_context('scan_result', scan_result.to_dict())

        # Cập nhật progress: đã scan ID card thành công
        self.conversation.set_progress('id_scanned')
        print(f"✅ Progress updated: {self.conversation.get_progress()}")

        # Return scan result without auto-triggering camera
        # AI will decide when to call camera verification tool
        return {
            "success": True,
            "data": scan_result.to_dict(),
            "message": "Scan successful",
            "id_card_url": image_url
        }

    def _handle_verify_face(self, id_card_image_url: str, selfie_image_url: str) -> Dict[str, Any]:
        """Handle face verification"""
        print("🔐 Verifying face...")

        # Cập nhật progress: đang xác thực khuôn mặt
        self.conversation.set_progress('face_verifying')
        print(f"✅ Progress updated: {self.conversation.get_progress()}")

        verify_result = self.face_verification_service.verify_face_from_urls(
            id_card_image_url, selfie_image_url
        )

        if verify_result.get("success"):
            result_data = verify_result.get("result", {})
            print("Face verification completed!")

            # Check verification result
            if result_data.get("status") == "success" and result_data.get("same_person") == True:
                # Đánh dấu eKYC đã hoàn tất thành công
                self.conversation.set_context('verification_success', True)
                self.conversation.set_progress('completed')
                print(f"✅ Progress updated: {self.conversation.get_progress()}")

                return {
                    "success": True,
                    "data": result_data,
                    "message": "Face verification successful!"
                }
            else:
                # Verification failed, require retry - quay lại id_scanned
                self.conversation.set_progress('id_scanned')
                print(f"⚠️ Verification failed, progress reverted: {self.conversation.get_progress()}")

                return {
                    "success": True,
                    "data": result_data,
                    "message": "Face verification failed. Please try again.",
                    "require_retry": True,
                    "id_card_url": id_card_image_url
                }
        else:
            # Error occurred - quay lại id_scanned
            self.conversation.set_progress('id_scanned')
            print(f"⚠️ Verification error, progress reverted: {self.conversation.get_progress()}")

            return {
                "success": False,
                "message": verify_result.get("error", "Error during face verification"),
                "require_retry": True,
                "id_card_url": id_card_image_url
            }

    def process_image_upload(self, image_path: str) -> Dict[str, Any]:
        """
        Complete image processing: upload and scan

        Args:
            image_path: Path to uploaded image file

        Returns:
            Processing result with scan data
        """
        return self.ocr_service.process_image(image_path)

    def verify_face_from_urls(self, id_card_image_url: str, selfie_image_url: str) -> Dict[str, Any]:
        """
        Verify face from image URLs

        Args:
            id_card_image_url: URL of ID card image
            selfie_image_url: URL of selfie image

        Returns:
            Verification result
        """
        return self.face_verification_service.verify_face_from_urls(
            id_card_image_url, selfie_image_url
        )

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

    def clear_ekyc_data(self):
        """Clear eKYC-related data from conversation context"""
        self.conversation.clear_ekyc_context()
