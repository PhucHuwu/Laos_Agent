"""
Dependencies for FastAPI routes
"""

import time
from typing import Dict
from fastapi import Request, Header
from app.core.bot import LaosEKYCBot
from app.config import settings


# Store bot instances per session (with cleanup for old sessions)
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


def get_session_id(x_session_id: str = Header(None, alias="X-Session-ID")) -> str:
    """Get session ID from header"""
    if not x_session_id:
        # Generate a new session ID if not provided
        import uuid
        x_session_id = str(uuid.uuid4())
        print(f"Generated new session ID: {x_session_id}")
    return x_session_id


def get_bot(session_id: str) -> LaosEKYCBot:
    """Get or create bot instance for session"""
    # Cleanup old sessions periodically
    cleanup_old_sessions()

    # Get or create bot for this session
    if session_id not in bot_sessions:
        bot_sessions[session_id] = LaosEKYCBot()
        print(f"Created new bot instance for session: {session_id}")

    # Update timestamp
    session_timestamps[session_id] = time.time()

    return bot_sessions[session_id]


def delete_bot_session(session_id: str) -> bool:
    """
    Delete a bot session completely.
    Use this after successful verification to ensure next session starts fresh.
    Returns True if session was deleted, False if not found.
    """
    if session_id in bot_sessions:
        del bot_sessions[session_id]
        if session_id in session_timestamps:
            del session_timestamps[session_id]
        print(f"Deleted bot session: {session_id}")
        return True
    print(f"Session not found for deletion: {session_id}")
    return False
