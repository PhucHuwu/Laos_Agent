"""
AI Service for chatbot functionality
"""

import json
import requests
from typing import Dict, Any, List, Optional
from ..config import settings
from ..models.conversation import Conversation, Message


class AIService:
    """Service for AI chatbot operations"""

    def __init__(self):
        self.api_url = settings.API_URL
        self.api_key = settings.API_KEY
        self.model = settings.MODEL
        self.conversation = Conversation()

        # Initialize with system message
        self._initialize_system_message()

        # Define available tools
        self.tools = self._define_tools()

    def _initialize_system_message(self):
        """Initialize system message"""
        system_message = Message(
            role="system",
            content="""You are an AI assistant specialized in supporting Lao citizens with eKYC (electronic Know Your Customer) for Lao national ID cards.

YOU ARE AN INTELLIGENT ASSISTANT - SIMPLIFIED WORKFLOW:

1. **Natural conversation**: Answer all citizen questions in a friendly and easy-to-understand manner in Lao language
2. **Single tool approach**: You have ONE simple tool to handle complete eKYC verification

INTELLIGENT WORKFLOW - SIMPLIFIED:

**When user wants to do eKYC verification:**
- Detect keywords: "ekyc", "ຢັ້ງຢືນ", "ບັດປະຈໍາຕົວ", "ຢັ້ງຢືນໃບໜ້າ", "ສະແກນບັດ", "ອັບໂຫຼດ", "ລົງທະບຽນ", "ຢາກເຮັດ", etc.
- Simply call "start_ekyc_process" tool with a welcoming message in Lao
- The tool will handle the entire flow automatically: upload → scan → face verification
- You don't need to manage individual steps

**When user has already completed eKYC:**
- If they want to do it AGAIN (mentions "ໃໝ່", "ຄືນໃໝ່", "ອີກຄັ້ງ"), the system auto-clears old data
- Then call "start_ekyc_process" again for fresh verification

**AVAILABLE TOOL:**
- start_ekyc_process: Start complete eKYC process from beginning to end. Use this ONLY tool when user requests eKYC verification.

**CRITICAL RULES:**
- ALWAYS respond in Lao language in ALL cases, regardless of input language - YOU MUST ALWAYS reply in Lao
- MANDATORY: Even if user writes in English, Vietnamese, Thai, or any language, you MUST respond in Lao only
- LANGUAGE RULE IS ABSOLUTE: No exceptions - 100% of your responses must be in Lao language
- DISTINGUISH between questions ABOUT eKYC (just answer) vs requests TO DO eKYC (call tool):
  * Questions like "ນານປານໃດ?" (How long?), "ແມ່ນຫຍັງ?" (What is?), "ເຮັດແນວໃດ?" (How?) = just answer, NO tool
  * Requests like "ຢາກເຮັດ eKYC" (I want to do eKYC), "ຊ່ວຍຢັ້ງຢືນ" (Help verify) = call start_ekyc_process tool
- For normal conversations and questions, just answer without calling tools
- Be professional, confident, and experienced consultant

Act as a helpful guide for Lao citizens."""
        )
        self.conversation.add_message(system_message)

    def _define_tools(self) -> List[Dict[str, Any]]:
        """Define available tools for the AI - Only expose start_ekyc_process to simplify AI decision-making"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "start_ekyc_process",
                    "description": "Start complete eKYC verification process. This single tool initiates the entire flow: ID card upload → scan → face verification. Use this when user wants to do eKYC, verify identity, or mentions ID card/verification in Lao language.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string",
                                "description": "Welcome message to guide user through eKYC process (must be in Lao language)"
                            }
                        },
                        "required": ["message"]
                    }
                }
            }
        ]

    def chat(self, user_input: str) -> Dict[str, Any]:
        """
        Process user input and return AI response

        Args:
            user_input: User's message

        Returns:
            Dictionary containing AI response or tool calls
        """
        # Add user message to conversation
        user_message = Message(role="user", content=user_input)
        self.conversation.add_message(user_message)

        # Prepare API request
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }

        # Add context to messages so AI knows current state
        messages = self.conversation.get_messages_for_api().copy()

        # Add progress context message to help AI understand current state
        progress_summary = self.conversation.get_progress_summary()
        progress_descriptions = {
            "idle": "User has not started eKYC process yet",
            "id_uploaded": "User has uploaded ID card image but not scanned yet",
            "id_scanned": "User has successfully scanned ID card, extracted information is available",
            "face_verifying": "User is currently in face verification process",
            "completed": "User has completed eKYC process successfully"
        }

        context_parts = [
            f"CURRENT eKYC PROGRESS: {progress_summary['progress'].upper()} - {progress_descriptions.get(progress_summary['progress'], '')}",
        ]

        if progress_summary['has_id_card']:
            context_parts.append(f"ID card URL available: {progress_summary['id_card_url']}")

        if progress_summary['has_scan_result']:
            context_parts.append("ID card information has been extracted and available")

        if progress_summary['verification_completed']:
            context_parts.append("Face verification completed successfully")

        # Add simplified guidance based on current progress
        if progress_summary['progress'] == 'idle':
            context_parts.append("GUIDANCE: If user wants to start eKYC verification, call 'start_ekyc_process' tool")
        elif progress_summary['progress'] == 'completed':
            context_parts.append("GUIDANCE: eKYC completed. If user wants to do it again, call 'start_ekyc_process' tool (system will auto-clear old data)")

        context_parts.append("REMEMBER: Your response must be in Lao language.")

        context_message = {
            "role": "system",
            "content": "\n".join(context_parts)
        }
        messages.append(context_message)

        data = {
            "model": self.model,
            "messages": messages,
            "tools": self.tools,
            "tool_choice": "auto",
            "stream": False
        }

        try:
            # Make API call
            response = requests.post(self.api_url, headers=headers, json=data)
            response.raise_for_status()

            # Parse response - handle both streaming and non-streaming
            response.encoding = 'utf-8'
            content = response.text.strip()

            json_data = None

            # Try to parse as regular JSON first
            try:
                json_data = json.loads(content)
            except json.JSONDecodeError:
                # If not regular JSON, try streaming format
                lines = content.split('\n')
                for line in lines:
                    if line.startswith('data:'):
                        data_content = line[5:].strip()
                        if data_content and data_content != '[DONE]':
                            try:
                                json_data = json.loads(data_content)
                                break
                            except json.JSONDecodeError:
                                continue

            if not json_data:
                # Log the actual response for debugging
                print(f"Debug - API Response: {content}")
                print(f"Debug - Response status: {response.status_code}")
                print(f"Debug - Response headers: {response.headers}")
                return {"error": "Could not parse response from API"}

            # Handle different response structures
            if 'choices' in json_data:
                message_data = json_data['choices'][0]['message']
            elif 'message' in json_data:
                message_data = json_data['message']
            else:
                return {"error": "Unexpected API response format"}

            # Create assistant message
            assistant_message = Message(
                role="assistant",
                content=message_data.get('content', ''),
                tool_calls=message_data.get('tool_calls')
            )
            self.conversation.add_message(assistant_message)

            # Handle tool calls
            if message_data.get('tool_calls'):
                # Return tool calls for frontend handling
                return {
                    'tool_calls': message_data['tool_calls']
                }

            return {"response": assistant_message.content}

        except requests.exceptions.RequestException as e:
            return {"error": f"API request error: {str(e)}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}

    def chat_stream(self, user_input: str):
        """
        Process user input and return streaming AI response with thinking/reasoning

        Args:
            user_input: User's message

        Yields:
            Dictionary containing streaming data chunks
        """
        # Add user message to conversation
        user_message = Message(role="user", content=user_input)
        self.conversation.add_message(user_message)

        # Prepare API request
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }

        # Add context to messages so AI knows current state
        messages = self.conversation.get_messages_for_api().copy()

        # Add progress context message to help AI understand current state
        progress_summary = self.conversation.get_progress_summary()
        progress_descriptions = {
            "idle": "User has not started eKYC process yet",
            "id_uploaded": "User has uploaded ID card image but not scanned yet",
            "id_scanned": "User has successfully scanned ID card, extracted information is available",
            "face_verifying": "User is currently in face verification process",
            "completed": "User has completed eKYC process successfully"
        }

        context_parts = [
            f"CURRENT eKYC PROGRESS: {progress_summary['progress'].upper()} - {progress_descriptions.get(progress_summary['progress'], '')}",
        ]

        if progress_summary['has_id_card']:
            context_parts.append(f"ID card URL available: {progress_summary['id_card_url']}")

        if progress_summary['has_scan_result']:
            context_parts.append("ID card information has been extracted and available")

        if progress_summary['verification_completed']:
            context_parts.append("Face verification completed successfully")

        # Add simplified guidance based on current progress
        if progress_summary['progress'] == 'idle':
            context_parts.append("GUIDANCE: If user wants to start eKYC verification, call 'start_ekyc_process' tool")
        elif progress_summary['progress'] == 'completed':
            context_parts.append("GUIDANCE: eKYC completed. If user wants to do it again, call 'start_ekyc_process' tool (system will auto-clear old data)")

        context_parts.append("REMEMBER: Your response must be in Lao language.")

        context_message = {
            "role": "system",
            "content": "\n".join(context_parts)
        }
        messages.append(context_message)

        data = {
            "model": self.model,
            "messages": messages,
            "tools": self.tools,
            "tool_choice": "auto",
            "stream": True  # Enable streaming
        }

        try:
            # Make streaming API call
            response = requests.post(self.api_url, headers=headers, json=data, stream=True)
            response.raise_for_status()

            # Variables để lưu trữ response
            content_buffer = ""
            tool_calls_buffer = []
            thinking_content = ""
            is_thinking = False

            # Process streaming response
            for line in response.iter_lines():
                if not line:
                    continue

                line = line.decode('utf-8').strip()

                # Skip empty lines
                if not line:
                    continue

                # Parse SSE format
                if line.startswith('data: '):
                    data_content = line[6:].strip()

                    # Check for end of stream
                    if data_content == '[DONE]':
                        break

                    try:
                        chunk_data = json.loads(data_content)

                        # Handle different chunk structures
                        if 'choices' in chunk_data and len(chunk_data['choices']) > 0:
                            choice = chunk_data['choices'][0]
                            delta = choice.get('delta', {})

                            # Check for reasoning/thinking content
                            if 'reasoning_content' in delta:
                                reasoning = delta['reasoning_content']
                                thinking_content += reasoning
                                is_thinking = True
                                yield {
                                    'type': 'thinking',
                                    'content': reasoning,
                                    'full_thinking': thinking_content
                                }

                            # Check for regular content
                            if 'content' in delta and delta['content']:
                                content_chunk = delta['content']
                                content_buffer += content_chunk

                                # If we were thinking, mark end of thinking
                                if is_thinking:
                                    yield {
                                        'type': 'thinking_done',
                                        'full_thinking': thinking_content
                                    }
                                    is_thinking = False

                                yield {
                                    'type': 'content',
                                    'content': content_chunk,
                                    'full_content': content_buffer
                                }

                            # Check for tool calls
                            if 'tool_calls' in delta:
                                tool_calls = delta['tool_calls']
                                if tool_calls:
                                    for tool_call in tool_calls:
                                        # Buffer tool calls
                                        index = tool_call.get('index', 0)
                                        if index >= len(tool_calls_buffer):
                                            tool_calls_buffer.append({
                                                'id': tool_call.get('id', ''),
                                                'type': 'function',
                                                'function': {
                                                    'name': '',
                                                    'arguments': ''
                                                }
                                            })

                                        if 'function' in tool_call:
                                            func = tool_call['function']
                                            if 'name' in func:
                                                tool_calls_buffer[index]['function']['name'] = func['name']
                                            if 'arguments' in func:
                                                tool_calls_buffer[index]['function']['arguments'] += func['arguments']

                                        if 'id' in tool_call:
                                            tool_calls_buffer[index]['id'] = tool_call['id']

                                    yield {
                                        'type': 'tool_calls',
                                        'tool_calls': tool_calls_buffer
                                    }

                            # Check for finish reason
                            if 'finish_reason' in choice and choice['finish_reason']:
                                finish_reason = choice['finish_reason']

                                # Save message to conversation
                                if tool_calls_buffer:
                                    assistant_message = Message(
                                        role="assistant",
                                        content=content_buffer,
                                        tool_calls=tool_calls_buffer
                                    )
                                    self.conversation.add_message(assistant_message)

                                    yield {
                                        'type': 'done',
                                        'finish_reason': finish_reason,
                                        'tool_calls': tool_calls_buffer,
                                        'thinking': thinking_content
                                    }
                                else:
                                    assistant_message = Message(
                                        role="assistant",
                                        content=content_buffer
                                    )
                                    self.conversation.add_message(assistant_message)

                                    yield {
                                        'type': 'done',
                                        'finish_reason': finish_reason,
                                        'content': content_buffer,
                                        'thinking': thinking_content
                                    }

                                break

                    except json.JSONDecodeError as e:
                        print(f"Error parsing streaming chunk: {e}")
                        print(f"Chunk data: {data_content}")
                        continue

        except requests.exceptions.RequestException as e:
            yield {
                'type': 'error',
                'error': f"API request error: {str(e)}"
            }
        except Exception as e:
            yield {
                'type': 'error',
                'error': f"Unexpected error: {str(e)}"
            }

    def _handle_tool_call(self, tool_call: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handle tool calls - only start_ekyc_process is exposed to AI"""
        try:
            function_name = tool_call['function']['name']
            arguments = json.loads(tool_call['function']['arguments'])

            if function_name == "start_ekyc_process":
                message = arguments.get("message", "ຍິນດີຕ້ອນຮັບສູ່ລະບົບ eKYC! ກະລຸນາອັບໂຫຼດຮູບບັດປະຈໍາຕົວຂອງທ່ານເພື່ອເລີ່ມຕົ້ນ")
                return {
                    "success": True,
                    "action": "start_ekyc_flow",
                    "message": message,
                    "tool_call_id": tool_call['id']
                }

        except Exception as e:
            print(f"Error handling tool {tool_call['function']['name']}: {e}")
            return {
                "success": False,
                "message": f"Error: {str(e)}"
            }

    def _get_follow_up_response(self) -> Dict[str, Any]:
        """Get follow-up response after tool execution"""
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }

        data = {
            "model": self.model,
            "messages": self.conversation.get_messages_for_api(),
            "stream": False
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=data)
            response.raise_for_status()

            # Parse response - handle both streaming and non-streaming
            response.encoding = 'utf-8'
            content = response.text.strip()

            json_data = None

            # Try to parse as regular JSON first
            try:
                json_data = json.loads(content)
            except json.JSONDecodeError:
                # If not regular JSON, try streaming format
                lines = content.split('\n')
                for line in lines:
                    if line.startswith('data:'):
                        data_content = line[5:].strip()
                        if data_content and data_content != '[DONE]':
                            try:
                                json_data = json.loads(data_content)
                                break
                            except json.JSONDecodeError:
                                continue

            if not json_data:
                # Log the actual response for debugging
                print(f"Debug - Follow-up API Response: {content[:500]}...")
                return {"error": "Could not parse follow-up response from API"}

            # Handle different response structures
            if 'choices' in json_data:
                final_message = json_data['choices'][0]['message']
            elif 'message' in json_data:
                final_message = json_data['message']
            else:
                return {"error": "Unexpected follow-up API response format"}

            # Add final message to conversation
            assistant_message = Message(
                role="assistant",
                content=final_message.get('content', '')
            )
            self.conversation.add_message(assistant_message)

            return {"response": assistant_message.content}

        except Exception as e:
            return {"error": f"Follow-up response error: {str(e)}"}

    def reset_conversation(self):
        """Reset the conversation to initial state"""
        print("="*80)
        print("🔄 RESETTING CONVERSATION")
        print(f"Before reset - Messages count: {len(self.conversation.messages)}")
        print(f"Before reset - Context: {self.conversation.context}")
        print(f"Before reset - Progress: {self.conversation.progress}")
        
        self.conversation.clear()
        self._initialize_system_message()
        
        print(f"After reset - Messages count: {len(self.conversation.messages)}")
        print(f"After reset - Context: {self.conversation.context}")
        print(f"After reset - Progress: {self.conversation.progress}")
        print("✅ CONVERSATION RESET COMPLETE")
        print("="*80)

    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get conversation history"""
        return self.conversation.get_messages_for_api()
