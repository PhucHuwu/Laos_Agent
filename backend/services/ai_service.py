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

YOU ARE AN INTELLIGENT ASSISTANT - AUTONOMOUSLY DECIDE ALL ACTIONS:

1. **Natural conversation**: Answer all citizen questions in a friendly and easy-to-understand manner in Lao language
2. **Autonomous tool usage**: You have full autonomy to decide when to use tools, without waiting for specific user requests

INTELLIGENT WORKFLOW:

**When user requests eKYC or mentions national ID card:**
- Check if ID card data already exists in context
- If exists and user wants to do NEW eKYC (mentions "ໃໝ່", "ຄືນໃໝ່", "ອີກຄັ້ງ"), the system will automatically clear old data
- Automatically call "open_image_upload" tool to open ID card image upload popup
- Guide user to upload their national ID card image

**When user uploads national ID card image:**
- Automatically call "scan_image_from_url" tool to extract information from the image
- Display extracted information for user confirmation

**When user explicitly requests face verification OR after successful scan AND user confirms they want to continue:**
- If no ID card data available: Automatically call "open_image_upload" tool to request ID card upload first
- If ID card data already available: Automatically call "open_camera_realtime" tool to open camera for face verification

**HANDLING REPEAT eKYC REQUESTS:**
- If user already completed eKYC and requests to do it AGAIN with keywords like "ໃໝ່" (new), "ອີກຄັ້ງ" (again), "ຄືນໃໝ່" (restart), the system will clear old data
- Then guide user to start fresh eKYC process from image upload
- Always treat repeat requests as new sessions, not reusing old images

**AVAILABLE TOOLS:**
- open_image_upload: Open popup to upload national ID card image. Use when user wants to start eKYC or mentions ID card
- open_camera_realtime: Open real-time camera for face verification. CRITICAL: ONLY use when user EXPLICITLY says they want face verification/authentication AND ID card data is already available in context
- scan_image_from_url: Extract information from uploaded ID card image
- verify_face: Verify face (compare ID card photo with selfie)

**CRITICAL RULES:**
- ALWAYS respond in Lao language in ALL cases, regardless of what language the input uses - YOU MUST ALWAYS reply in Lao
- MANDATORY: Even if user writes in English, Vietnamese, Thai, or any other language, you MUST respond in Lao language only
- LANGUAGE RULE IS ABSOLUTE: No exceptions - 100% of your responses must be in Lao language
- You are the guide, citizens just need to follow your instructions
- All decisions are made by you based on conversation context
- DO NOT automatically open camera after scan - wait for user to explicitly request face verification
- For normal questions and conversations, just answer without calling any tools
- DISTINGUISH between questions ABOUT eKYC/verification (just answer) vs requests TO DO eKYC/verification (call tool)
  * Questions like "How long?", "What is?", "How does it work?" = just answer, NO tool call
  * Requests like "I want to do", "Help me verify", "Start verification" = call appropriate tool
- ONLY call tools when user explicitly requests eKYC-related ACTIONS (not questions about them)
- Clearly explain each step so citizens understand
- Always check conditions before executing (e.g., check if ID card image exists before face verification)
- IMPORTANT: Only call "open_camera_realtime" when user explicitly asks for face verification ACTION
- When user wants to do eKYC again, ALWAYS start from scratch with new image upload

Act as a professional, confident, and experienced consultant."""
        )
        self.conversation.add_message(system_message)

    def _define_tools(self) -> List[Dict[str, Any]]:
        """Define available tools for the AI"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "open_image_upload",
                    "description": "Open popup to upload national ID card image. Use when user needs to upload ID card for eKYC or face verification",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string",
                                "description": "Instruction message for user about uploading national ID card image (must be in Lao language)"
                            }
                        },
                        "required": ["message"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "scan_image_from_url",
                    "description": "Automatically scan and extract information from uploaded national ID card image. Use immediately after user uploads ID card",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "image_url": {
                                "type": "string",
                                "description": "URL of the uploaded national ID card image"
                            }
                        },
                        "required": ["image_url"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "open_camera_realtime",
                    "description": "Open real-time camera for face verification. ONLY use this tool when: 1) User EXPLICITLY requests face verification/authentication, OR 2) User explicitly asks to verify their face/identity, OR 3) User explicitly wants to proceed with face verification after ID scan. DO NOT use for normal conversation or general questions. Requires ID card data to be available.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string",
                                "description": "Instruction message for user about face verification using camera (must be in Lao language)"
                            },
                            "id_card_url": {
                                "type": "string",
                                "description": "URL of the scanned national ID card image (required for verification)"
                            }
                        },
                        "required": ["message", "id_card_url"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "verify_face",
                    "description": "Verify face by comparing ID card photo with selfie photo",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "id_card_image_url": {
                                "type": "string",
                                "description": "URL of the national ID card image"
                            },
                            "selfie_image_url": {
                                "type": "string",
                                "description": "URL of the selfie image for verification"
                            }
                        },
                        "required": ["id_card_image_url", "selfie_image_url"]
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
        # Kiểm tra nếu người dùng yêu cầu làm eKYC mới - clear context cũ
        user_input_lower = user_input.lower()
        ekyc_keywords = ['ekyc', 'ຢັ້ງຢືນຕົວຕົນ', 'ຢັ້ງຢືນໃບໜ້າ', 'ສະແກນບັດ', 'ອັບໂຫຼດບັດ', 'ລົງທະບຽນ', 'ຢາກເຮັດ', 'ຢາກສະແກນ', 'ບັດປະຈໍາຕົວ']
        restart_keywords = ['ໃໝ່', 'ຄືນໃໝ່', 'ອີກຄັ້ງ', 'ເລີ່ມໃໝ່', 'ລາງ', 'ເລີ່ມຕົ້ນ', 'ຄືນຄວາມ', 'ລົບ', 'ລາງ', 'ເລີ່ມຄືນ']

        # Nếu có dữ liệu eKYC cũ và người dùng yêu cầu làm eKYC (đặc biệt với từ khóa "mới"/"lại")
        has_old_data = self.conversation.has_id_card_data()
        is_ekyc_request = any(keyword in user_input_lower for keyword in ekyc_keywords)
        is_restart_request = any(keyword in user_input_lower for keyword in restart_keywords)
        verification_completed = self.conversation.get_context('verification_success', False)

        # Clear context nếu:
        # 1. Có cả eKYC keyword VÀ restart keyword, HOẶC
        # 2. Chỉ có restart keyword nhưng rõ ràng về eKYC (ví dụ: "ເລີ່ມຕົ້ນໃໝ່" khi đã có data), HOẶC
        # 3. ĐÃ xác thực thành công (verification_completed) VÀ người dùng yêu cầu eKYC lại
        should_clear = has_old_data and (
            (is_ekyc_request and is_restart_request) or
            (is_restart_request and ('ເລີ່ມຕົ້ນ' in user_input_lower or 'ເລີ່ມຄືນ' in user_input_lower)) or
            (verification_completed and is_ekyc_request)
        )

        if should_clear:
            if verification_completed:
                print("🔄 Phát hiện eKYC đã hoàn tất + yêu cầu eKYC mới - Xóa dữ liệu cũ")
            else:
                print("🔄 Phát hiện yêu cầu eKYC mới - Xóa dữ liệu cũ")
            self.conversation.clear_ekyc_context()

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

        # Add guidance based on current progress
        if progress_summary['progress'] == 'idle':
            context_parts.append("GUIDANCE: If user wants to start eKYC, call 'open_image_upload' tool")
        elif progress_summary['progress'] == 'id_scanned' and not progress_summary['verification_completed']:
            context_parts.append(
                f"GUIDANCE: ID card data is ready. ONLY if user EXPLICITLY requests face verification, call 'open_camera_realtime' tool with id_card_url = '{progress_summary['id_card_url']}'")
        elif progress_summary['progress'] == 'completed':
            context_parts.append("GUIDANCE: eKYC is complete. If user wants to do it again, system will clear old data and restart")

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
        # Kiểm tra nếu người dùng yêu cầu làm eKYC mới - clear context cũ
        user_input_lower = user_input.lower()
        ekyc_keywords = ['ekyc', 'ຢັ້ງຢືນຕົວຕົນ', 'ຢັ້ງຢືນໃບໜ້າ', 'ສະແກນບັດ', 'ອັບໂຫຼດບັດ', 'ລົງທະບຽນ', 'ຢາກເຮັດ', 'ຢາກສະແກນ', 'ບັດປະຈໍາຕົວ']
        restart_keywords = ['ໃໝ່', 'ຄືນໃໝ່', 'ອີກຄັ້ງ', 'ເລີ່ມໃໝ່', 'ລາງ', 'ເລີ່ມຕົ້ນ', 'ຄືນຄວາມ', 'ລົບ', 'ລາງ', 'ເລີ່ມຄືນ']

        # Nếu có dữ liệu eKYC cũ và người dùng yêu cầu làm eKYC (đặc biệt với từ khóa "mới"/"lại")
        has_old_data = self.conversation.has_id_card_data()
        is_ekyc_request = any(keyword in user_input_lower for keyword in ekyc_keywords)
        is_restart_request = any(keyword in user_input_lower for keyword in restart_keywords)
        verification_completed = self.conversation.get_context('verification_success', False)

        # Clear context nếu:
        # 1. Có cả eKYC keyword VÀ restart keyword, HOẶC
        # 2. Chỉ có restart keyword nhưng rõ ràng về eKYC (ví dụ: "ເລີ່ມຕົ້ນໃໝ່" khi đã có data), HOẶC
        # 3. ĐÃ xác thực thành công (verification_completed) VÀ người dùng yêu cầu eKYC lại
        should_clear = has_old_data and (
            (is_ekyc_request and is_restart_request) or
            (is_restart_request and ('ເລີ່ມຕົ້ນ' in user_input_lower or 'ເລີ່ມຄືນ' in user_input_lower)) or
            (verification_completed and is_ekyc_request)
        )

        if should_clear:
            if verification_completed:
                print("🔄 Phát hiện eKYC đã hoàn tất + yêu cầu eKYC mới - Xóa dữ liệu cũ")
            else:
                print("🔄 Phát hiện yêu cầu eKYC mới - Xóa dữ liệu cũ")
            self.conversation.clear_ekyc_context()

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

        # Add guidance based on current progress
        if progress_summary['progress'] == 'idle':
            context_parts.append("GUIDANCE: If user wants to start eKYC, call 'open_image_upload' tool")
        elif progress_summary['progress'] == 'id_scanned' and not progress_summary['verification_completed']:
            context_parts.append(
                f"GUIDANCE: ID card data is ready. ONLY if user EXPLICITLY requests face verification, call 'open_camera_realtime' tool with id_card_url = '{progress_summary['id_card_url']}'")
        elif progress_summary['progress'] == 'completed':
            context_parts.append("GUIDANCE: eKYC is complete. If user wants to do it again, system will clear old data and restart")

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
        """Handle individual tool calls"""
        try:
            function_name = tool_call['function']['name']
            arguments = json.loads(tool_call['function']['arguments'])

            if function_name == "open_image_upload":
                message = arguments.get("message", "ກະລຸນາອັບໂຫຼດຮູບບັດປະຈໍາຕົວຂອງທ່ານ")
                return {
                    "success": True,
                    "action": "open_upload_popup",
                    "message": message,
                    "tool_call_id": tool_call['id']
                }

            elif function_name == "open_selfie_upload":
                message = arguments.get("message", "ກະລຸນາອັບໂຫຼດຮູບ selfie ເພື່ອຢັ້ງຢືນໃບໜ້າ")
                id_card_url = arguments.get("id_card_url")
                return {
                    "success": True,
                    "action": "open_selfie_upload_popup",
                    "message": message,
                    "id_card_url": id_card_url,
                    "tool_call_id": tool_call['id']
                }

            elif function_name == "open_camera_realtime":
                message = arguments.get("message", "ກະລຸນາຢັ້ງຢືນໃບໜ້າດ້ວຍກ້ອງຖ່າຍຮູບ")
                id_card_url = arguments.get("id_card_url")

                # Nếu AI không truyền id_card_url, lấy từ context
                if not id_card_url and self.conversation.has_id_card_data():
                    id_card_url = self.conversation.get_id_card_url()

                return {
                    "success": True,
                    "action": "open_camera_realtime",
                    "message": message,
                    "id_card_url": id_card_url,
                    "tool_call_id": tool_call['id']
                }

            # Note: Other tools (upload_image_to_server, scan_image_from_url, verify_face)
            # are handled by the Flask app routes, not here

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
        self.conversation.clear()
        self._initialize_system_message()

    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get conversation history"""
        return self.conversation.get_messages_for_api()
