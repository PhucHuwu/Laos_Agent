"""
Face Verification Service for real-time and batch face verification
"""

import asyncio
import websockets
import json
import base64
import requests
import threading
import websocket
from typing import Dict, Any, Optional, Callable
from ..config import settings
from ..models.verification import VerificationResult


class FaceVerificationClient:
    """Client for batch face verification via WebSocket"""

    def __init__(self, websocket_url: Optional[str] = None):
        self.websocket_url = websocket_url or settings.OCR_WEBSOCKET_URL

    def image_to_base64(self, image_url: str) -> Optional[str]:
        """Convert image from URL to base64"""
        try:
            response = requests.get(image_url)
            response.raise_for_status()
            image_data = response.content
            base64_data = base64.b64encode(image_data).decode('utf-8')
            return base64_data
        except Exception as e:
            print(f"Error converting image to base64: {e}")
            return None

    async def verify_face_async(self, id_card_image_url: str, selfie_image_url: str) -> Dict[str, Any]:
        """Asynchronous face verification"""
        try:
            # Convert images to base64
            id_card_base64 = self.image_to_base64(id_card_image_url)
            selfie_base64 = self.image_to_base64(selfie_image_url)

            if not id_card_base64 or not selfie_base64:
                return {
                    "success": False,
                    "error": "Could not convert images to base64"
                }

            # Connect to WebSocket
            async with websockets.connect(self.websocket_url) as websocket_conn:
                # Prepare data
                data = {
                    "id_card_image": id_card_base64,
                    "selfie_image": selfie_base64
                }

                # Send data
                await websocket_conn.send(json.dumps(data))

                # Receive response
                response = await websocket_conn.recv()
                result = json.loads(response)

                return {
                    "success": True,
                    "result": result
                }

        except websockets.exceptions.ConnectionRefused:
            return {
                "success": False,
                "error": "Could not connect to WebSocket server"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error during face verification: {str(e)}"
            }

    def verify_face(self, id_card_image_url: str, selfie_image_url: str) -> Dict[str, Any]:
        """Synchronous face verification"""
        try:
            # Run async function in event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                self.verify_face_async(id_card_image_url, selfie_image_url)
            )
            loop.close()
            return result
        except Exception as e:
            return {
                "success": False,
                "error": f"Error running face verification: {str(e)}"
            }


class RealtimeFaceVerificationClient:
    """Client for real-time face verification"""

    def __init__(self, websocket_url: Optional[str] = None):
        self.websocket_url = websocket_url or settings.OCR_WEBSOCKET_URL
        self.ws = None
        self.is_connected = False
        self.result_callback: Optional[Callable] = None
        self.id_card_base64: Optional[str] = None
        self.last_result: Optional[Dict[str, Any]] = None
        self.ignore_next_response = False  # Flag để bỏ qua response của ID card

    def set_id_card_image(self, id_card_image_url: str) -> bool:
        """Set ID card image for verification"""
        try:
            response = requests.get(id_card_image_url)
            response.raise_for_status()
            image_data = response.content
            self.id_card_base64 = base64.b64encode(image_data).decode('utf-8')
            return True
        except Exception as e:
            print(f"Error loading ID card image: {e}")
            return False

    def on_message(self, ws, message):
        """Handle WebSocket messages"""
        try:
            data = json.loads(message)
            
            # Bỏ qua response đầu tiên sau khi gửi ID card (so sánh ID card với chính nó)
            if self.ignore_next_response:
                print(f"⏭️  Ignoring ID card self-comparison response: same_person={data.get('same_person')}, similarity={data.get('similarity')}")
                self.ignore_next_response = False
                return
            
            # CHỈ lưu result khi có bbox (là kết quả xác thực frame thực sự)
            if 'bbox' in data:
                self.last_result = data
                print(f"✅ Received verification result: same_person={data.get('same_person')}, similarity={data.get('similarity'):.4f}")
            else:
                print(f"ℹ️  Received non-verification response (no bbox): {data.get('msg', 'No message')}")
            
            if self.result_callback:
                self.result_callback(data)
        except Exception as e:
            print(f"Error parsing message: {e}")

    def on_error(self, ws, error):
        """Handle WebSocket errors"""
        print(f"WebSocket error: {error}")
        self.is_connected = False
        # Log detailed error information
        if hasattr(error, 'errno'):
            print(f"Error code: {error.errno}")
        if hasattr(error, 'strerror'):
            print(f"Error message: {error.strerror}")

    def on_close(self, ws, close_status_code, close_msg):
        """Handle WebSocket close"""
        print("WebSocket closed")
        self.is_connected = False

    def on_open(self, ws):
        """Handle WebSocket open"""
        print("WebSocket connected")
        self.is_connected = True

        # Send ID card image first
        if self.id_card_base64:
            try:
                # Reset last_result và set flag để bỏ qua response của ID card
                self.last_result = None
                self.ignore_next_response = True  # Bỏ qua response so sánh ID card với chính nó
                
                ws.send(self.id_card_base64)
                print("ID card image sent (will ignore self-comparison response)")
            except Exception as e:
                print(f"Error sending ID card image: {e}")

    def connect(self, result_callback: Optional[Callable] = None):
        """Connect to WebSocket"""
        self.result_callback = result_callback

        websocket.enableTrace(False)
        self.ws = websocket.WebSocketApp(
            self.websocket_url,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
        )

        # Run WebSocket in separate thread with timeout
        def run_websocket():
            try:
                self.ws.run_forever(ping_interval=30, ping_timeout=10)
            except Exception as e:
                print(f"WebSocket connection failed: {e}")
                self.is_connected = False

        thread = threading.Thread(target=run_websocket)
        thread.daemon = True
        thread.start()

        # Wait a bit for connection to establish
        import time
        time.sleep(1)

        return self.is_connected

    def send_frame(self, frame_base64: str) -> bool:
        """Send frame from camera"""
        if self.is_connected and self.ws:
            try:
                self.ws.send(frame_base64)
                return True
            except Exception as e:
                print(f"Error sending frame: {e}")
                return False
        return False

    def get_last_result(self) -> Optional[Dict[str, Any]]:
        """Get last verification result"""
        return self.last_result
    
    def get_and_clear_result(self) -> Optional[Dict[str, Any]]:
        """Get last verification result and clear it"""
        result = self.last_result
        self.last_result = None  # Clear để tránh trả về kết quả cũ
        return result

    def disconnect(self):
        """Disconnect WebSocket"""
        if self.ws:
            self.ws.close()
            self.is_connected = False
            self.last_result = None
            self.ignore_next_response = False  # Reset flag


class FaceVerificationService:
    """Main service for face verification operations"""

    def __init__(self):
        self.batch_client = FaceVerificationClient()
        self.realtime_client: Optional[RealtimeFaceVerificationClient] = None

    def verify_face_from_urls(self, id_card_image_url: str, selfie_image_url: str) -> Dict[str, Any]:
        """
        Verify face from image URLs

        Args:
            id_card_image_url: URL of ID card image
            selfie_image_url: URL of selfie image

        Returns:
            Dictionary containing verification result
        """
        result = self.batch_client.verify_face(id_card_image_url, selfie_image_url)

        if result.get('success'):
            verification_result = VerificationResult.from_dict(result.get('result', {}))
            return {
                "success": True,
                "result": verification_result.to_dict()
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "Unknown error")
            }

    def start_realtime_verification(self, id_card_image_url: str) -> Optional[RealtimeFaceVerificationClient]:
        """
        Start real-time face verification

        Args:
            id_card_image_url: URL of ID card image

        Returns:
            RealtimeFaceVerificationClient instance or None if failed
        """
        try:
            self.realtime_client = RealtimeFaceVerificationClient()

            # Set ID card image
            if not self.realtime_client.set_id_card_image(id_card_image_url):
                return None

            # Connect
            self.realtime_client.connect()
            return self.realtime_client

        except Exception as e:
            print(f"Error starting realtime verification: {e}")
            return None

    def stop_realtime_verification(self):
        """Stop real-time face verification"""
        if self.realtime_client:
            self.realtime_client.disconnect()
            self.realtime_client = None
