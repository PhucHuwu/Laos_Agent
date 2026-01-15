"""
Chat persistence service - save/load chat history from database
"""

from datetime import datetime
from uuid import UUID
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.models import ChatLog, User


class ChatPersistenceService:
    """Service to persist chat messages to database"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_chat_history(self, user_id: UUID) -> List[Dict[str, Any]]:
        """Load chat history for a user"""
        result = await self.db.execute(
            select(ChatLog).where(ChatLog.user_id == user_id)
        )
        chat_log = result.scalar_one_or_none()

        if chat_log and chat_log.messages:
            return chat_log.messages
        return []

    async def save_message(
        self,
        user_id: UUID,
        role: str,
        content: str,
        tool_calls: Optional[List] = None
    ) -> None:
        """Save a single message to chat history"""
        result = await self.db.execute(
            select(ChatLog).where(ChatLog.user_id == user_id)
        )
        chat_log = result.scalar_one_or_none()

        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
        }
        if tool_calls:
            message["tool_calls"] = tool_calls

        if chat_log:
            # Append to existing messages
            messages = chat_log.messages or []
            messages.append(message)
            chat_log.messages = messages
            chat_log.updated_at = datetime.utcnow()
        else:
            # Create new chat log
            chat_log = ChatLog(
                user_id=user_id,
                messages=[message]
            )
            self.db.add(chat_log)

        await self.db.commit()

    async def clear_history(self, user_id: UUID) -> None:
        """Clear chat history for a user"""
        result = await self.db.execute(
            select(ChatLog).where(ChatLog.user_id == user_id)
        )
        chat_log = result.scalar_one_or_none()

        if chat_log:
            chat_log.messages = []
            chat_log.updated_at = datetime.utcnow()
            await self.db.commit()
