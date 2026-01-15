"""
Chat API routes
"""

import json
from uuid import UUID
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.api.deps import get_session_id, get_bot
from app.api.deps_auth import get_current_user_id
from app.database import get_db
from app.database.models import User
from app.services.chat_persistence import ChatPersistenceService
from app.core.bot import LaosEKYCBot
from app.models.requests import (
    ChatRequest,
    ChatResponse,
    ResetResponse,
    ConversationStateResponse,
)


router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    session_id: str = Depends(get_session_id),
    bot: LaosEKYCBot = Depends(get_bot),
):
    """Handle chat messages (non-streaming)"""
    if not request.message:
        return ChatResponse(success=False, error="Message cannot be empty")

    try:
        result = await bot.chat(request.message)

        if "tool_calls" in result:
            return ChatResponse(success=True, tool_calls=result["tool_calls"])
        elif "error" in result:
            return ChatResponse(success=False, error=result["error"])
        else:
            return ChatResponse(success=True, response=result.get("response", ""))

    except Exception as e:
        return ChatResponse(success=False, error=f"Error processing message: {str(e)}")


@router.post("/chat-stream")
async def chat_stream(
    request: ChatRequest,
    session_id: str = Depends(get_session_id),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    bot: LaosEKYCBot = Depends(get_bot),
):
    """Handle streaming chat messages with thinking/reasoning and DB persistence"""
    chat_service = ChatPersistenceService(db)

    if not request.message:
        async def error_generator():
            yield {"event": "message", "data": json.dumps({"type": "error", "error": "Message cannot be empty"})}
        return EventSourceResponse(error_generator())

    # Save user message to DB
    try:
        await chat_service.save_message(UUID(user_id), "user", request.message)
    except Exception as e:
        print(f"Error saving user message: {e}")
        # Continue even if save fails? verify later.

    async def generate():
        full_content = ""
        full_tool_calls = []

        try:
            async for chunk in bot.chat_stream(request.message):
                # Accumulate content for history
                if isinstance(chunk, dict):
                    if chunk.get("type") == "content":
                        full_content += chunk.get("content", "")
                    elif chunk.get("type") == "tool_calls":
                        # Assume complete tool calls are yielded or handle merging
                        # For simplicity, we assume the chunk contains tool_calls list
                        tc = chunk.get("tool_calls", [])
                        if isinstance(tc, list):
                            full_tool_calls.extend(tc)

                yield {"event": "message", "data": json.dumps(chunk, ensure_ascii=False)}

            yield {"event": "message", "data": "[DONE]"}

            # Save assistant message to DB
            if full_content or full_tool_calls:
                await chat_service.save_message(
                    UUID(user_id),
                    "assistant",
                    full_content,
                    tool_calls=full_tool_calls if full_tool_calls else None
                )

        except Exception as e:
            error_data = {"type": "error", "error": f"Error processing message: {str(e)}"}
            yield {"event": "message", "data": json.dumps(error_data, ensure_ascii=False)}

    return EventSourceResponse(generate())


@router.post("/reset", response_model=ResetResponse)
async def reset_conversation(
    session_id: str = Depends(get_session_id),
    bot: LaosEKYCBot = Depends(get_bot),
):
    """Reset conversation"""
    try:
        bot.reset_conversation()
        return ResetResponse(
            success=True,
            message="Conversation reset successfully",
            context=bot.conversation.context,
            progress=bot.conversation.progress,
            messages_count=len(bot.conversation.messages),
        )
    except Exception as e:
        return ResetResponse(success=False, message=f"Error resetting: {str(e)}")


@router.get("/conversation-state", response_model=ConversationStateResponse)
async def get_conversation_state(
    session_id: str = Depends(get_session_id),
    bot: LaosEKYCBot = Depends(get_bot),
):
    """Get current conversation state for debugging"""
    try:
        return ConversationStateResponse(
            success=True,
            context=bot.conversation.context,
            progress=bot.conversation.progress,
            messages_count=len(bot.conversation.messages),
            messages=[
                {
                    "role": msg.role,
                    "content": msg.content[:100] if msg.content else None,
                    "has_tool_calls": bool(msg.tool_calls),
                }
                for msg in bot.conversation.messages
            ],
        )
    except Exception as e:
        return ConversationStateResponse(success=False, error=f"Error: {str(e)}")


# ============ Chat History Endpoints (Database) ============

class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: Optional[str] = None


class ChatHistoryResponse(BaseModel):
    success: bool
    messages: List[dict] = []
    context: Optional[dict] = {}
    progress: Optional[str] = "idle"
    error: Optional[str] = None


class SaveMessageRequest(BaseModel):
    role: str
    content: str


@router.get("/chat/history", response_model=ChatHistoryResponse)
async def get_chat_history(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get chat history for authenticated user"""
    try:
        service = ChatPersistenceService(db)
        # Returns dict with messages, context, progress
        data = await service.get_chat_history(UUID(user_id))

        return ChatHistoryResponse(
            success=True,
            messages=data.get("messages", []),
            context=data.get("context", {}),
            progress=data.get("progress", "idle")
        )
    except Exception as e:
        return ChatHistoryResponse(success=False, error=str(e))


@router.post("/chat/history")
async def save_chat_message(
    request: SaveMessageRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Save a message to chat history"""
    try:
        service = ChatPersistenceService(db)
        await service.save_message(
            user_id=UUID(user_id),
            role=request.role,
            content=request.content,
        )
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.delete("/chat/history")
async def clear_chat_history(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Clear chat history for authenticated user"""
    try:
        service = ChatPersistenceService(db)
        await service.clear_history(UUID(user_id))
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}
