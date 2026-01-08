"""
Conversation and message models
"""

from datetime import datetime
from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field


class Message(BaseModel):
    """Represents a chat message"""
    role: Literal["user", "assistant", "system", "tool"]
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None
    name: Optional[str] = None

    def to_api_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API calls"""
        data = {
            "role": self.role,
            "content": self.content
        }
        if self.tool_calls:
            data["tool_calls"] = self.tool_calls
        if self.tool_call_id:
            data["tool_call_id"] = self.tool_call_id
        if self.name:
            data["name"] = self.name
        return data


class Conversation(BaseModel):
    """Represents a conversation session"""
    messages: List[Message] = Field(default_factory=list)
    session_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    context: Dict[str, Any] = Field(default_factory=dict)
    progress: Literal["idle", "id_uploading", "id_scanned", "face_verifying"] = "idle"

    def add_message(self, message: Message) -> None:
        """Add a message to the conversation"""
        self.messages.append(message)
        self.updated_at = datetime.now()

    def get_messages_for_api(self) -> List[Dict[str, Any]]:
        """Get messages formatted for API calls"""
        return [msg.to_api_dict() for msg in self.messages]

    def clear(self) -> None:
        """Clear all messages and reset state"""
        self.messages.clear()
        self.context.clear()
        self.progress = "idle"
        self.updated_at = datetime.now()

    def get_last_message(self) -> Optional[Message]:
        """Get the last message in the conversation"""
        return self.messages[-1] if self.messages else None

    def set_context(self, key: str, value: Any) -> None:
        """Set context data"""
        self.context[key] = value
        self.updated_at = datetime.now()

    def get_context(self, key: str, default: Any = None) -> Any:
        """Get context data"""
        return self.context.get(key, default)

    def has_id_card_data(self) -> bool:
        """Check if conversation has ID card data"""
        return self.context.get("id_card_url") is not None

    def get_id_card_url(self) -> Optional[str]:
        """Get ID card URL from context"""
        return self.context.get("id_card_url")

    def set_progress(self, progress: str) -> None:
        """Set eKYC progress"""
        valid_progress = ["idle", "id_uploading", "id_scanned", "face_verifying"]
        if progress in valid_progress:
            self.progress = progress
            self.updated_at = datetime.now()
        else:
            raise ValueError(f"Invalid progress value. Must be one of: {', '.join(valid_progress)}")

    def reset_ekyc_state(self) -> None:
        """
        Reset eKYC-related state after successful verification.
        This clears ALL conversation data (messages + context) so that
        the next eKYC session starts completely fresh.
        """
        # Clear all messages (will be re-initialized with system message by AIService)
        self.messages.clear()

        # Clear all context
        self.context.clear()

        # Reset progress to idle
        self.progress = "idle"
        self.updated_at = datetime.now()

    def get_progress_summary(self) -> Dict[str, Any]:
        """Get summary of current progress and context"""
        return {
            "progress": self.progress,
            "has_id_card": self.has_id_card_data(),
            "id_card_url": self.get_id_card_url(),
            "has_scan_result": self.context.get("scan_result") is not None,
            "verification_completed": self.context.get("verification_success", False)
        }
