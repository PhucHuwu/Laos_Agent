"""
Chat API routes
"""

import json
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse
from app.api.deps import get_session_id, get_bot
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
):
    """Handle chat messages (non-streaming)"""
    bot = get_bot(session_id)

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
):
    """Handle streaming chat messages with thinking/reasoning"""
    bot = get_bot(session_id)

    if not request.message:
        async def error_generator():
            yield {"event": "message", "data": json.dumps({"type": "error", "error": "Message cannot be empty"})}
        return EventSourceResponse(error_generator())

    async def generate():
        try:
            async for chunk in bot.chat_stream(request.message):
                yield {"event": "message", "data": json.dumps(chunk, ensure_ascii=False)}
            yield {"event": "message", "data": "[DONE]"}
        except Exception as e:
            error_data = {"type": "error", "error": f"Error processing message: {str(e)}"}
            yield {"event": "message", "data": json.dumps(error_data, ensure_ascii=False)}

    return EventSourceResponse(generate())


@router.post("/reset", response_model=ResetResponse)
async def reset_conversation(
    session_id: str = Depends(get_session_id),
):
    """Reset conversation"""
    try:
        bot = get_bot(session_id)
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
):
    """Get current conversation state for debugging"""
    try:
        bot = get_bot(session_id)
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
