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
