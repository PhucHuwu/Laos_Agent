import time
from typing import Dict, Optional
from uuid import UUID
from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.bot import LaosEKYCBot
from app.config import settings
from app.api.deps_auth import get_current_user_id
from app.database.connection import get_db
from app.services.chat_persistence import ChatPersistenceService

# Store bot instances per USER ID (with cleanup)
bot_sessions: Dict[str, LaosEKYCBot] = {}
session_timestamps: Dict[str, float] = {}


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
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> LaosEKYCBot:
    """
    Get or create bot instance for authenticated user.
    Restores state from database if creating new instance.
    """
    # Cleanup old sessions periodically
    cleanup_old_sessions()

    # Get or create bot for this user
    if user_id not in bot_sessions:
        print(f"Creating/Restoring bot for user: {user_id}")
        bot = LaosEKYCBot()

        # Restore state from DB
        try:
            persistence = ChatPersistenceService(db)
            state = await persistence.get_chat_history(UUID(user_id))
            await bot.restore_conversation(state)
        except Exception as e:
            print(f"Failed to restore bot state: {e}")
            # Continue with empty bot if restore fails

        bot_sessions[user_id] = bot
    else:
        print(f"Using cached bot for user: {user_id}")

    # Update timestamp
    session_timestamps[user_id] = time.time()

    return bot_sessions[user_id]


def delete_bot_session(user_id: str) -> bool:
    """
    Delete a bot session completely.
    Use this after successful verification to ensure next session starts fresh.
    """
    if user_id in bot_sessions:
        del bot_sessions[user_id]
        if user_id in session_timestamps:
            del session_timestamps[user_id]
        print(f"Deleted bot session for user: {user_id}")
        return True
    return False

# Legacy support/Helper for endpoints explicitly needing session_id string


def get_session_id(user_id: str = Depends(get_current_user_id)) -> str:
    return user_id
