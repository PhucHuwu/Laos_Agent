"""
AI Service for chatbot functionality with async support
"""

import json
import httpx
from typing import Dict, Any, List, Optional, AsyncGenerator
from app.config import settings
from app.models.conversation import Conversation, Message


class AIService:
    """Service for AI chatbot operations"""

    def __init__(self):
        self.api_url = settings.API_URL
        self.api_key = settings.API_KEY
        self.model = settings.MODEL
        self.conversation = Conversation()
        self.tools = self._define_tools()

        # Initialize with system message
        self._initialize_system_message()

    def _initialize_system_message(self):
        """Initialize system message with intent-based prompting"""
        system_content = """You are an AI assistant specialized in supporting Lao citizens with eKYC (electronic Know Your Customer) for Lao national ID cards.

ABSOLUTE LANGUAGE RULE:
- MANDATORY: You MUST respond in Lao language 100% of the time
- NO EXCEPTIONS: Even if user writes in English, Vietnamese, Thai, Chinese, or any other language
- THIS IS NON-NEGOTIABLE: Every single response must be in Lao only

eKYC PROGRESS STATES:
1. "idle" - User has not started OR just completed eKYC
2. "id_uploading" - User is uploading ID card image  
3. "id_scanned" - ID card scanned successfully, ready for face verification
4. "face_verifying" - User is in face verification process

TOOL USAGE RULES:
You have 2 tools to manage the eKYC flow:

1. open_id_scan - Opens ID card upload modal
   USE WHEN: progress is "idle" AND user wants to start/restart eKYC
   
2. open_face_verification - Opens camera for face verification  
   USE WHEN: progress is "id_scanned" AND user wants to:
   - Continue face verification (e.g., closed camera accidentally)
   - Retry face verification

EXCEPTION HANDLING:
- If user at "id_scanned" wants to re-scan ID: use open_id_scan
- If user closed camera popup: use open_face_verification when asked
- If user wants to start over: use open_id_scan

KEY PRINCIPLES:
1. Use semantic understanding, not keyword matching
2. Always check current progress state before calling tools
3. Provide helpful guidance in Lao language
4. Be professional and friendly

Act as a professional eKYC consultant."""

        system_message = Message(role="system", content=system_content)
        self.conversation.add_message(system_message)

    def _define_tools(self) -> List[Dict[str, Any]]:
        """Define available tools for the AI"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "open_id_scan",
                    "description": "Opens the ID card upload/scan modal. Use when: (1) progress is 'idle' and user wants to START eKYC, OR (2) user explicitly wants to re-scan/re-upload their ID card.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string",
                                "description": "Guidance message in Lao language for uploading ID card"
                            }
                        },
                        "required": ["message"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "open_face_verification",
                    "description": "Opens the camera modal for face verification. Use when: (1) progress is 'id_scanned' and user wants to proceed with face matching, OR (2) user closed camera accidentally and wants to continue.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string",
                                "description": "Guidance message in Lao language for face verification"
                            }
                        },
                        "required": ["message"]
                    }
                }
            }
        ]

    def _get_context_message(self) -> Dict[str, str]:
        """Generate context message based on current state"""
        progress_summary = self.conversation.get_progress_summary()
        progress_descriptions = {
            "idle": "User has not started eKYC process yet (or just completed and reset)",
            "id_uploading": "User is uploading ID card image",
            "id_scanned": "User has successfully scanned ID card, extracted information is available",
            "face_verifying": "User is currently in face verification process"
        }

        context_parts = [
            f"CURRENT eKYC PROGRESS: {progress_summary['progress'].upper()} - {progress_descriptions.get(progress_summary['progress'], '')}"
        ]

        if progress_summary['has_id_card']:
            context_parts.append(f"ID card URL available: {progress_summary['id_card_url']}")

        if progress_summary['has_scan_result']:
            context_parts.append("ID card information has been extracted and available")

        if progress_summary['verification_completed']:
            context_parts.append("Face verification completed successfully")

        context_parts.append("LANGUAGE: Always respond in Lao, regardless of input language.")

        return {
            "role": "system",
            "content": "\n".join(context_parts)
        }

    async def chat(self, user_input: str) -> Dict[str, Any]:
        """Process user input and return AI response (non-streaming)"""
        # Add user message to conversation
        user_message = Message(role="user", content=user_input)
        self.conversation.add_message(user_message)

        # Prepare messages with context
        messages = self.conversation.get_messages_for_api().copy()
        messages.append(self._get_context_message())

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        data = {
            "model": self.model,
            "messages": messages,
            "tools": self.tools,
            "tool_choice": "auto",
            "stream": False
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(self.api_url, headers=headers, json=data)
                response.raise_for_status()

                json_data = response.json()

                if "choices" in json_data:
                    message_data = json_data["choices"][0]["message"]
                else:
                    return {"error": "Unexpected API response format"}

                # Create assistant message
                assistant_message = Message(
                    role="assistant",
                    content=message_data.get("content", ""),
                    tool_calls=message_data.get("tool_calls")
                )
                self.conversation.add_message(assistant_message)

                # Handle tool calls
                if message_data.get("tool_calls"):
                    return {"tool_calls": message_data["tool_calls"]}

                return {"response": assistant_message.content}

        except httpx.RequestError as e:
            return {"error": f"API request error: {str(e)}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}

    async def chat_stream(self, user_input: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Process user input and return streaming AI response"""
        # Add user message to conversation
        user_message = Message(role="user", content=user_input)
        self.conversation.add_message(user_message)

        # Prepare messages with context
        messages = self.conversation.get_messages_for_api().copy()
        messages.append(self._get_context_message())

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        data = {
            "model": self.model,
            "messages": messages,
            "tools": self.tools,
            "tool_choice": "auto",
            "stream": True
        }

        content_buffer = ""
        thinking_content = ""
        tool_calls_buffer = []
        is_thinking = False

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                async with client.stream("POST", self.api_url, headers=headers, json=data) as response:
                    response.raise_for_status()

                    async for line in response.aiter_lines():
                        if not line or not line.startswith("data: "):
                            continue

                        data_content = line[6:].strip()

                        if data_content == "[DONE]":
                            break

                        try:
                            chunk_data = json.loads(data_content)

                            if "choices" in chunk_data and len(chunk_data["choices"]) > 0:
                                choice = chunk_data["choices"][0]
                                delta = choice.get("delta", {})

                                # Check for reasoning/thinking content
                                if "reasoning_content" in delta:
                                    reasoning = delta["reasoning_content"]
                                    thinking_content += reasoning
                                    is_thinking = True
                                    yield {
                                        "type": "thinking",
                                        "content": reasoning,
                                        "full_thinking": thinking_content
                                    }

                                # Check for regular content
                                if "content" in delta and delta["content"]:
                                    content_chunk = delta["content"]
                                    content_buffer += content_chunk

                                    if is_thinking:
                                        yield {
                                            "type": "thinking_done",
                                            "full_thinking": thinking_content
                                        }
                                        is_thinking = False

                                    yield {
                                        "type": "content",
                                        "content": content_chunk,
                                        "full_content": content_buffer
                                    }

                                # Check for tool calls
                                if "tool_calls" in delta:
                                    tool_calls = delta["tool_calls"]
                                    if tool_calls:
                                        for tool_call in tool_calls:
                                            index = tool_call.get("index", 0)
                                            if index >= len(tool_calls_buffer):
                                                tool_calls_buffer.append({
                                                    "id": tool_call.get("id", ""),
                                                    "type": "function",
                                                    "function": {"name": "", "arguments": ""}
                                                })

                                            if "function" in tool_call:
                                                func = tool_call["function"]
                                                if "name" in func:
                                                    tool_calls_buffer[index]["function"]["name"] = func["name"]
                                                if "arguments" in func:
                                                    tool_calls_buffer[index]["function"]["arguments"] += func["arguments"]

                                            if "id" in tool_call:
                                                tool_calls_buffer[index]["id"] = tool_call["id"]

                                        yield {
                                            "type": "tool_calls",
                                            "tool_calls": tool_calls_buffer
                                        }

                                # Check for finish reason
                                if "finish_reason" in choice and choice["finish_reason"]:
                                    # Save message to conversation
                                    assistant_message = Message(
                                        role="assistant",
                                        content=content_buffer,
                                        tool_calls=tool_calls_buffer if tool_calls_buffer else None
                                    )
                                    self.conversation.add_message(assistant_message)

                                    yield {
                                        "type": "done",
                                        "finish_reason": choice["finish_reason"],
                                        "tool_calls": tool_calls_buffer if tool_calls_buffer else None,
                                        "content": content_buffer,
                                        "thinking": thinking_content
                                    }
                                    break

                        except json.JSONDecodeError:
                            continue

        except httpx.RequestError as e:
            yield {"type": "error", "error": f"API request error: {str(e)}"}
        except Exception as e:
            yield {"type": "error", "error": f"Unexpected error: {str(e)}"}

    def reset_conversation(self):
        """Reset the conversation to initial state"""
        self.conversation.clear()
        self._initialize_system_message()

    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get conversation history"""
        return self.conversation.get_messages_for_api()
