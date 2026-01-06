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

UNDERSTANDING eKYC PROCESS STATES:
You will receive context messages indicating current eKYC progress state:

1. "idle" - User has not started eKYC process yet
2. "id_uploaded" - User uploaded ID card image, waiting for scan
3. "id_scanned" - ID card scanned successfully, data extracted
4. "face_verifying" - User is in face verification process
5. "completed" - eKYC process completed successfully

INTENT RECOGNITION:
You have ONE powerful tool: start_ekyc_process

INTENT 1: INFORMATION SEEKING (Just answer, NO tool call)
- Questions about what eKYC is, how it works, security, requirements

INTENT 2: ACTION INITIATION (Call start_ekyc_process tool)
- User expresses readiness to begin, desire to start, willingness to proceed

KEY PRINCIPLES:
1. Use semantic understanding, not keyword matching
2. Consider conversation flow and current state
3. Understand natural language and implied meanings
4. Always respond in Lao language

Act as a professional, knowledgeable, and friendly eKYC consultant."""

        system_message = Message(role="system", content=system_content)
        self.conversation.add_message(system_message)

    def _define_tools(self) -> List[Dict[str, Any]]:
        """Define available tools for the AI"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "start_ekyc_process",
                    "description": "Initiates the complete eKYC verification flow (ID upload -> scan -> face verification). Use this when you recognize USER'S INTENT TO ACT - when they express readiness, desire to begin, or willingness to proceed with identity verification.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string",
                                "description": "Welcoming message in Lao language to guide user into the eKYC process"
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
            "idle": "User has not started eKYC process yet",
            "id_uploaded": "User has uploaded ID card image but not scanned yet",
            "id_scanned": "User has successfully scanned ID card, extracted information is available",
            "face_verifying": "User is currently in face verification process",
            "completed": "User has completed eKYC process successfully"
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
        # Auto-reset to idle if previous session was completed
        # This allows user to start new eKYC session naturally
        if self.conversation.progress == "completed":
            self.conversation.set_progress("idle")
            self.conversation.context = {}  # Clear old context
            print("[RESET] Previous eKYC completed - reset to idle for new session")
        
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
        # Auto-reset to idle if previous session was completed
        # This allows user to start new eKYC session naturally
        if self.conversation.progress == "completed":
            self.conversation.set_progress("idle")
            self.conversation.context = {}  # Clear old context
            print("[RESET] Previous eKYC completed - reset to idle for new session")
        
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
