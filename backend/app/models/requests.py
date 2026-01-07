"""
API Request and Response schemas
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel


# Chat schemas
class ChatRequest(BaseModel):
    """Chat request body"""
    message: str


class ChatResponse(BaseModel):
    """Chat response body"""
    success: bool = True
    response: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None


class StreamChunk(BaseModel):
    """Streaming response chunk"""
    type: str  # thinking, thinking_done, content, tool_calls, done, error
    content: Optional[str] = None
    full_content: Optional[str] = None
    full_thinking: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    finish_reason: Optional[str] = None
    error: Optional[str] = None


# Upload schemas
class UploadResponse(BaseModel):
    """Upload response body"""
    success: bool = True
    image_url: Optional[str] = None
    scan_result: Optional[Dict[str, Any]] = None
    formatted_html: Optional[str] = None
    message: Optional[str] = None
    id_card_url: Optional[str] = None
    tool_call: Optional[Dict[str, Any]] = None  # Tool call for frontend to execute
    error: Optional[str] = None


# Verification schemas
class VerifyFaceRequest(BaseModel):
    """Face verification request body"""
    id_card_image_url: str
    selfie_image_url: str


class VerifyFaceResponse(BaseModel):
    """Face verification response body"""
    success: bool = True
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class StartVerificationRequest(BaseModel):
    """Start WebSocket verification request"""
    id_card_image_url: str


class FrameRequest(BaseModel):
    """Send frame request body"""
    frame_base64: str


class FrameResponse(BaseModel):
    """Send frame response body"""
    success: bool = True
    message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# Reset schemas
class ResetResponse(BaseModel):
    """Reset response body"""
    success: bool = True
    message: str = "Conversation reset successfully"
    context: Optional[Dict[str, Any]] = None
    progress: Optional[str] = None
    messages_count: int = 0


# Conversation state schemas
class ConversationStateResponse(BaseModel):
    """Conversation state response body"""
    success: bool = True
    context: Dict[str, Any] = {}
    progress: str = "idle"
    messages_count: int = 0
    messages: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None
