"""
API Dependencies - Session management without authentication
"""

import time
import uuid
from typing import Dict
from uuid import UUID
from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.bot import LaosEKYCBot
from app.config import settings
from app.database.connection import get_db
from app.services.chat_persistence import ChatPersistenceService

# Store bot instances per session ID (with cleanup)
bot_sessions: Dict[str, LaosEKYCBot] = {}
session_timestamps: Dict[str, float] = {}


def get_session_id(x_session_id: str = Header(default=None)) -> str:
    """
    Get session ID from header or generate a new one.
    No authentication - just session tracking.
    """
    if x_session_id:
        return x_session_id
    # Generate new session ID if not provided
    return str(uuid.uuid4())


def cleanup_old_sessions():
    """Remove sessions older than timeout"""
    current_time = time.time()
    expired_sessions = [
        sid for sid, timestamp in session_timestamps.items()
        if current_time - timestamp > settings.SESSION_TIMEOUT
    ]
    for sid in expired_sessions:
        if sid in bot_sessions:
            del bot_sessions[sid]
            del session_timestamps[sid]
            print(f"Cleaned up expired session: {sid}")


async def get_bot(
    session_id: str = Depends(get_session_id),
    db: AsyncSession = Depends(get_db)
) -> LaosEKYCBot:
    """
    Get or create bot instance for session.
    Restores state from database if creating new instance.
    """
    # Cleanup old sessions periodically
    cleanup_old_sessions()

    # Get or create bot for this session
    if session_id not in bot_sessions:
        print(f"Creating/Restoring bot for session: {session_id}")
        bot = LaosEKYCBot()

        # Try to restore state from DB
        try:
            persistence = ChatPersistenceService(db)
            state = await persistence.get_chat_history(UUID(session_id))
            await bot.restore_conversation(state)
        except Exception as e:
            print(f"Failed to restore bot state: {e}")
            # Continue with empty bot if restore fails

        bot_sessions[session_id] = bot
    else:
        print(f"Using cached bot for session: {session_id}")

    # Update timestamp
    session_timestamps[session_id] = time.time()

    return bot_sessions[session_id]


def delete_bot_session(session_id: str) -> bool:
    """
    Delete a bot session completely.
    Use this after successful verification to ensure next session starts fresh.
    """
    if session_id in bot_sessions:
        del bot_sessions[session_id]
        if session_id in session_timestamps:
            del session_timestamps[session_id]
        print(f"Deleted bot session: {session_id}")
        return True
    return False
