"""
Camera service for handling camera operations
"""

from typing import Callable, Optional


class CameraService:
    """Service for camera operations"""

    def __init__(self):
        self.stream: Optional['MediaStream'] = None
        self.videoElement: Optional['HTMLVideoElement'] = None
        self.canvasElement: Optional['HTMLCanvasElement'] = None
        self.onCameraStart: Optional[Callable] = None
        self.onCameraStop: Optional[Callable] = None
        self.onCameraError: Optional[Callable[[str], None]] = None
        self.isActive = False

    def setVideoElement(self, videoElement: 'HTMLVideoElement'):
        """Set video element for camera stream"""
        self.videoElement = videoElement

    def setCanvasElement(self, canvasElement: 'HTMLCanvasElement'):
        """Set canvas element for frame capture"""
        self.canvasElement = canvasElement

    def setCallbacks(self, onStart: Optional[Callable] = None,
                     onStop: Optional[Callable] = None,
                     onError: Optional[Callable[[str], None]] = None):
        """Set camera event callbacks"""
        self.onCameraStart = onStart
        self.onCameraStop = onStop
        self.onCameraError = onError

    async def startCamera(self) -> bool:
        """
        Start camera stream

        Returns:
            bool: Success status
        """
        try:
            if not self.videoElement:
                raise Exception("Video element not set")

            # Get user media
            self.stream = await navigator.mediaDevices.getUserMedia({
                "video": {
                    "width": {"ideal": 640},
                    "height": {"ideal": 480},
                    "facingMode": "user"
                }
            })

            # Set video source
            self.videoElement.srcObject = self.stream
            await self.videoElement.play()

            self.isActive = True

            if self.onCameraStart:
                self.onCameraStart()

            return True

        except Exception as e:
            errorMsg = f"Không thể truy cập camera: {str(e)}"
            if self.onCameraError:
                self.onCameraError(errorMsg)
            return False

    def stopCamera(self):
        """Stop camera stream"""
        try:
            if self.stream:
                self.stream.getTracks().forEach(lambda track: track.stop())
                self.stream = None

            if self.videoElement:
                self.videoElement.srcObject = None

            self.isActive = False

            if self.onCameraStop:
                self.onCameraStop()

        except Exception as e:
            print(f"Error stopping camera: {e}")

    def captureFrame(self) -> Optional[str]:
        """
        Capture frame from video as base64

        Returns:
            str: Base64 encoded frame or None if failed
        """
        if not self.videoElement or not self.canvasElement or not self.isActive:
            return None

        try:
            context = self.canvasElement.getContext("2d")
            self.canvasElement.width = self.videoElement.videoWidth
            self.canvasElement.height = self.videoElement.videoHeight
            context.drawImage(self.videoElement, 0, 0)
            
            # Convert to base64
            return self.canvasElement.toDataURL("image/jpeg", 0.8)

        except Exception as e:
            print(f"Error capturing frame: {e}")
            return None

    def isCameraActive(self) -> bool:
        """Check if camera is active"""
        return self.isActive
