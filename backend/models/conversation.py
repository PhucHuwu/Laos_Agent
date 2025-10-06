"""
Conversation and message models
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Message:
    """Represents a chat message"""
    role: str  # 'user', 'assistant', 'system', 'tool'
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None
    name: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
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


@dataclass
class Conversation:
    """Represents a conversation session"""
    messages: List[Message] = field(default_factory=list)
    session_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    context: Dict[str, Any] = field(default_factory=dict)  # Lưu trữ context và dữ liệu
    progress: str = "idle"  # Theo dõi tiến trình eKYC: idle, id_uploaded, id_scanned, face_verifying, completed

    def add_message(self, message: Message) -> None:
        """Add a message to the conversation"""
        self.messages.append(message)
        self.updated_at = datetime.now()

    def get_messages_for_api(self) -> List[Dict[str, Any]]:
        """Get messages formatted for API calls"""
        return [msg.to_dict() for msg in self.messages]

    def clear(self) -> None:
        """Clear all messages"""
        self.messages.clear()
        self.updated_at = datetime.now()

    def get_last_message(self) -> Optional[Message]:
        """Get the last message in the conversation"""
        return self.messages[-1] if self.messages else None

    def get_message_count(self) -> int:
        """Get the number of messages in the conversation"""
        return len(self.messages)

    def set_context(self, key: str, value: Any) -> None:
        """Set context data"""
        self.context[key] = value
        self.updated_at = datetime.now()

    def get_context(self, key: str, default: Any = None) -> Any:
        """Get context data"""
        return self.context.get(key, default)

    def has_id_card_data(self) -> bool:
        """Check if conversation has ID card data"""
        return self.context.get('id_card_url') is not None

    def get_id_card_url(self) -> Optional[str]:
        """Get ID card URL from context"""
        return self.context.get('id_card_url')

    def clear_ekyc_context(self) -> None:
        """Clear eKYC-related context data (ID card URL, scan result, verification result)"""
        keys_to_remove = ['id_card_url', 'scan_result', 'verification_result', 'verification_success']
        for key in keys_to_remove:
            if key in self.context:
                del self.context[key]
        self.progress = "idle"  # Reset progress
        self.updated_at = datetime.now()

    def set_progress(self, progress: str) -> None:
        """Set eKYC progress"""
        valid_progress = ["idle", "id_uploaded", "id_scanned", "face_verifying", "completed"]
        if progress in valid_progress:
            self.progress = progress
            self.updated_at = datetime.now()
        else:
            raise ValueError(f"Invalid progress value. Must be one of: {', '.join(valid_progress)}")

    def get_progress(self) -> str:
        """Get current eKYC progress"""
        return self.progress

    def get_progress_summary(self) -> Dict[str, Any]:
        """Get summary of current progress and context"""
        return {
            "progress": self.progress,
            "has_id_card": self.has_id_card_data(),
            "id_card_url": self.get_id_card_url(),
            "has_scan_result": self.context.get('scan_result') is not None,
            "verification_completed": self.context.get('verification_success', False)
        }
