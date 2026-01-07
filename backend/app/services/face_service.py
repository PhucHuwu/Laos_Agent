"""
Face Verification Service - Using websocket-client (threading-based)
"""

import asyncio
import base64
import json
import httpx
import websockets
import websocket
import threading
import time
import requests
from typing import Dict, Any, Optional, Callable
from app.config import settings
from app.models.verification import VerificationResult


class FaceVerificationClient:
    """Client for batch face verification via WebSocket"""

    def __init__(self, websocket_url: Optional[str] = None):
        self.websocket_url = websocket_url or settings.OCR_WEBSOCKET_URL

    async def image_to_base64(self, image_url: str) -> Optional[str]:
        """Convert image from URL to base64"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(image_url)
                response.raise_for_status()
                image_data = response.content
                base64_data = base64.b64encode(image_data).decode("utf-8")
                return base64_data
        except Exception as e:
            print(f"Error converting image to base64: {e}")
            return None

    async def verify_face(self, id_card_image_url: str, selfie_image_url: str) -> Dict[str, Any]:
        """Asynchronous face verification"""
        try:
            # Convert images to base64
            id_card_base64 = await self.image_to_base64(id_card_image_url)
            selfie_base64 = await self.image_to_base64(selfie_image_url)

            if not id_card_base64 or not selfie_base64:
                return {
                    "success": False,
                    "error": "Could not convert images to base64"
                }

            # Connect to WebSocket
            async with websockets.connect(self.websocket_url) as ws:
                # Prepare data
                data = {
                    "id_card_image": id_card_base64,
                    "selfie_image": selfie_base64
                }

                # Send data
                await ws.send(json.dumps(data))

                # Receive response
                response = await ws.recv()
                result = json.loads(response)

                return {
                    "success": True,
                    "result": result
                }

        except websockets.exceptions.ConnectionClosed:
            return {
                "success": False,
                "error": "WebSocket connection closed unexpectedly"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error during face verification: {str(e)}"
            }


class RealtimeFaceVerificationClient:
    """Client for real-time face verification using websocket-client (threading-based)"""

    def __init__(self, websocket_url: Optional[str] = None):
        self.websocket_url = websocket_url or settings.OCR_WEBSOCKET_URL
        self.ws = None
        self.is_connected = False
        self.result_callback: Optional[Callable] = None
        self.id_card_base64: Optional[str] = None
        self.last_result: Optional[Dict[str, Any]] = None
        self.ignore_next_response = False

    def set_id_card_image(self, id_card_image_url: str) -> bool:
        """Set ID card image for verification (SYNC)"""
        try:
            print(f"[DOWNLOAD] Downloading ID card image from: {id_card_image_url}")
            response = requests.get(id_card_image_url, timeout=30)
            response.raise_for_status()
            image_data = response.content
            self.id_card_base64 = base64.b64encode(image_data).decode('utf-8')
            print(f"[OK] ID card image downloaded and encoded (size: {len(self.id_card_base64)} bytes)")
            return True
        except Exception as e:
            print(f"[ERROR] Error loading ID card image: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return False

    def on_message(self, ws, message):
        """Handle WebSocket messages"""
        print(f"[DEBUG] on_message callback triggered")
        try:
            print(f"[MSG] Received message from server (length: {len(message)} bytes)")
            data = json.loads(message)
            print(f"[DATA] Parsed data keys: {list(data.keys())}")
            
            if self.ignore_next_response:
                print(f"[SKIP]  Ignoring ID card self-comparison: same_person={data.get('same_person')}, similarity={data.get('similarity', 0):.4f}")
                self.ignore_next_response = False
                return
            
            if 'bbox' in data:
                self.last_result = data
                print(f"[OK] Valid verification result: same_person={data.get('same_person')}, similarity={data.get('similarity', 0):.4f}")
            else:
                print(f"[INFO]  Received non-verification response (no bbox): {data.get('msg', 'No message')}")
            
            if self.result_callback:
                self.result_callback(data)
        except json.JSONDecodeError as e:
            print(f"[ERROR] JSON decode error: {e}")
            print(f"Raw message: {message[:500]}")
        except Exception as e:
            print(f"[ERROR] Error processing message: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()

    def on_error(self, ws, error):
        """Handle WebSocket errors"""
        print(f"[DEBUG] on_error callback triggered")
        print(f"[ERROR] WebSocket error: {type(error).__name__}: {error}")
        self.is_connected = False

    def on_close(self, ws, close_status_code, close_msg):
        """Handle WebSocket close"""
        print(f"[DEBUG] on_close callback triggered")
        print(f"[CLOSED] WebSocket closed - status: {close_status_code}, message: {close_msg}")
        self.is_connected = False

    def on_open(self, ws):
        """Handle WebSocket open"""
        print(f"[DEBUG] on_open callback triggered")
        print("[OK] WebSocket connected (on_open callback)")
        self.is_connected = True

        # Send ID card image first
        if self.id_card_base64:
            try:
                self.last_result = None
                self.ignore_next_response = True
                
                print(f"[SEND] Sending ID card image to server (size: {len(self.id_card_base64)} bytes)...")
                ws.send(self.id_card_base64)
                print("[OK] ID card image sent (will ignore self-comparison response)")
            except Exception as e:
                print(f"[ERROR] Error sending ID card image: {type(e).__name__}: {e}")
                import traceback
                traceback.print_exc()

    def connect(self, result_callback: Optional[Callable] = None) -> bool:
        """Connect to WebSocket (SYNC)"""
        try:
            print(f"[CONNECT] Connecting to WebSocket server: {self.websocket_url}")
            self.result_callback = result_callback

            websocket.enableTrace(False)
            self.ws = websocket.WebSocketApp(
                self.websocket_url,
                on_open=self.on_open,
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close,
            )

            # Run WebSocket in separate thread
            def run_websocket():
                try:
                    print("[START] Starting WebSocket run_forever in thread...")
                    self.ws.run_forever(ping_interval=30, ping_timeout=10)
                    print("[END] WebSocket run_forever ended")
                except Exception as e:
                    print(f"[ERROR] WebSocket run_forever exception: {type(e).__name__}: {e}")
                    import traceback
                    traceback.print_exc()
                    self.is_connected = False

            thread = threading.Thread(target=run_websocket, daemon=True)
            thread.start()
            print("[THREAD] WebSocket thread started")

            # Wait for connection to establish
            print("[WAIT] Waiting for connection to establish...")
            time.sleep(1.0)
            
            if self.is_connected:
                print(f"[OK] Connection established successfully")
            else:
                print(f"[WARN]  Connection may not be established yet")

            return self.is_connected

        except Exception as e:
            print(f"[ERROR] WebSocket connection failed: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            self.is_connected = False
            return False

    def send_frame(self, frame_base64: str) -> bool:
        """Send frame from camera (SYNC)"""
        if not self.is_connected or not self.ws:
            print(f"[ERROR] Cannot send frame: connected={self.is_connected}, ws={self.ws is not None}")
            return False

        try:
            # Strip data URL prefix if present (e.g., "data:image/jpeg;base64,")
            if frame_base64.startswith('data:'):
                frame_base64 = frame_base64.split(',', 1)[1]
                print(f"[INFO]  Stripped data URL prefix")
            
            print(f"[SEND] Sending frame to server (size: {len(frame_base64)} bytes)")
            self.ws.send(frame_base64)
            print(f"[OK] Frame sent successfully")
            return True
        except Exception as e:
            print(f"[ERROR] Error sending frame: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return False

    def get_last_result(self) -> Optional[Dict[str, Any]]:
        """Get last verification result"""
        return self.last_result

    def get_status(self) -> Dict[str, Any]:
        """Get detailed connection status for debugging"""
        status = {
            "is_connected": self.is_connected,
            "ws_exists": self.ws is not None,
            "has_id_card": self.id_card_base64 is not None,
            "last_result": self.last_result is not None,
        }
        return status

    def is_healthy(self) -> bool:
        """Check if WebSocket connection is healthy"""
        return self.is_connected and self.ws is not None

    def disconnect(self):
        """Disconnect WebSocket (SYNC)"""
        print("[CONNECT] Disconnecting WebSocket...")
        self.is_connected = False
        
        if self.ws:
            try:
                self.ws.close()
            except Exception as e:
                print(f"[ERROR] Error closing WebSocket: {e}")
            self.ws = None

        self.last_result = None
        self.ignore_next_response = False
        print("[OK] WebSocket disconnected")


class FaceVerificationService:
    """Main service for face verification operations"""

    def __init__(self):
        self.batch_client = FaceVerificationClient()
        self.realtime_client: Optional[RealtimeFaceVerificationClient] = None

    async def verify_face_from_urls(self, id_card_image_url: str, selfie_image_url: str) -> Dict[str, Any]:
        """
        Verify face from image URLs

        Args:
            id_card_image_url: URL of ID card image
            selfie_image_url: URL of selfie image

        Returns:
            Dictionary containing verification result
        """
        result = await self.batch_client.verify_face(id_card_image_url, selfie_image_url)

        if result.get("success"):
            verification_result = VerificationResult.from_api_response(result.get("result", {}))
            return {
                "success": True,
                "result": verification_result.model_dump()
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "Unknown error")
            }

    def start_realtime_verification(self, id_card_image_url: str) -> Optional[RealtimeFaceVerificationClient]:
        """
        Start real-time face verification (SYNC method wrapped for async)

        Args:
            id_card_image_url: URL of ID card image

        Returns:
            RealtimeFaceVerificationClient instance or None if failed
        """
        try:
            print(f"[SERVICE] Creating new RealtimeFaceVerificationClient...")
            self.realtime_client = RealtimeFaceVerificationClient()
            print(f"[OK] Client created: {self.realtime_client}")

            # Set ID card image (SYNC)
            print(f"[DOWNLOAD] Loading ID card image from URL...")
            if not self.realtime_client.set_id_card_image(id_card_image_url):
                print("[ERROR] Failed to load ID card image")
                return None
            print(f"[OK] ID card image loaded successfully")

            # Connect (SYNC)
            print(f"[CONNECT] Attempting to connect to WebSocket...")
            if not self.realtime_client.connect():
                print("[ERROR] Failed to connect to WebSocket")
                return None
            
            print(f"[OK] Successfully connected to WebSocket")
            print(f"[DATA] Client status after connection:")
            status = self.realtime_client.get_status()
            print(json.dumps(status, indent=2))

            return self.realtime_client

        except Exception as e:
            print(f"[ERROR] Error starting realtime verification: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return None

    def stop_realtime_verification(self):
        """Stop real-time face verification (SYNC)"""
        if self.realtime_client:
            self.realtime_client.disconnect()
            self.realtime_client = None
