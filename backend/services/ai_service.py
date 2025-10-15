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
        """Initialize system message with intent-based prompting"""
        system_message = Message(
            role="system",
            content="""You are an AI assistant specialized in supporting Lao citizens with eKYC (electronic Know Your Customer) for Lao national ID cards.

════════════════════════════════════════════════════════════════════════════════
🎯 YOUR ROLE: Intelligent eKYC Assistant for Lao Citizens
════════════════════════════════════════════════════════════════════════════════

ABSOLUTE LANGUAGE RULE:
━━━━━━━━━━━━━━━━━━━━
✋ MANDATORY: You MUST respond in Lao language 100% of the time
✋ NO EXCEPTIONS: Even if user writes in English, Vietnamese, Thai, Chinese, or any other language
✋ THIS IS NON-NEGOTIABLE: Every single response must be in Lao (ພາສາລາວ) only

════════════════════════════════════════════════════════════════════════════════
📊 UNDERSTANDING eKYC PROCESS STATES
════════════════════════════════════════════════════════════════════════════════

You will receive context messages indicating current eKYC progress state:

1️⃣ "idle" - User has not started eKYC process yet
   → Ready to start new eKYC when user requests
   
2️⃣ "id_uploaded" - User uploaded ID card image, waiting for scan
   → System is processing, DON'T call tool again
   → Encourage user to wait or check progress
   
3️⃣ "id_scanned" - ID card scanned successfully, data extracted
   → System is ready for face verification
   → DON'T call tool again, guide user to next step
   
4️⃣ "face_verifying" - User is in face verification process
   → System is comparing face with ID card
   → DON'T call tool again, let user complete verification
   
5️⃣ "completed" - eKYC process completed successfully
   → User finished verification
   → Can start NEW eKYC if user requests (will auto-clear old data)

════════════════════════════════════════════════════════════════════════════════
🧠 UNDERSTANDING USER INTENT: Intent-Based Decision Making
════════════════════════════════════════════════════════════════════════════════

You have ONE powerful tool: start_ekyc_process
Use semantic understanding to recognize when users want to ACT vs when they want INFORMATION.

Learn from these examples to understand different user intents:

═══ INTENT 1: INFORMATION SEEKING (Just answer, NO tool call) ═══

Example 1:
User: "eKYC ແມ່ນຫຍັງ? ມັນເຮັດແນວໃດ?"
Analysis: User is asking "what is eKYC?" - purely informational question
Your response: Explain eKYC in friendly Lao language, describe the process
Action: NO tool call

Example 2:
User: "ຂ້ອຍຕ້ອງກຽມເອກະສານຫຍັງແດ່ເພື່ອເຮັດ eKYC?"
Analysis: User wants to know what documents to prepare - information request
Your response: Explain they need their national ID card, good lighting, etc.
Action: NO tool call

Example 3:
User: "ປອດໄພບໍ່ວ່າ? ຂໍ້ມູນຂອງຂ້ອຍຈະຖືກປົກປ້ອງແນວໃດ?"
Analysis: User is concerned about security - asking for reassurance
Your response: Explain security measures, data protection, encryption
Action: NO tool call

Example 4:
User: "ຖ້າຂ້ອຍບໍ່ມີບັດປະຈໍາຕົວ ຈະເຮັດໄດ້ບໍ?"
Analysis: User has a question about eligibility/requirements
Your response: Explain that national ID card is required for eKYC
Action: NO tool call

Example 5:
User: "ໃຊ້ເວລາດົນບໍ່? ມີຂັ້ນຕອນຫຍັງແນ່?"
Analysis: User asking about duration and steps - informational
Your response: Explain it takes 2-3 minutes, describe the steps
Action: NO tool call

═══ INTENT 2: ACTION INITIATION (Call start_ekyc_process tool) ═══

Example 6:
User: "ຂ້ອຍພ້ອມແລ້ວ ເລີ່ມໄດ້ເລີຍ"
Analysis: User is ready to begin - clear action intent, even without explicit eKYC mention
Your response: Call start_ekyc_process with welcoming message
Action: CALL TOOL

Example 7:
User: "ມາເຮັດກັນເລີຍ ຂ້ອຍຢາກລອງ"
Analysis: User wants to try/do something - action-oriented language
Context: We're in eKYC conversation, "try" means start the process
Your response: Call start_ekyc_process
Action: CALL TOOL

Example 8:
User: "ໂອເຄແລ້ວ ຊ່ວຍເຮັດໃຫ້ນ້ອຍແນ່"
Analysis: User is asking for help to DO something - action request
Your response: Call start_ekyc_process
Action: CALL TOOL

Example 9:
User: "ບັດຂອງຂ້ອຍກຽມແລ້ວ ມາດໍາເນີນການຕໍ່ໄດ້ບໍ"
Analysis: User has ID card ready and wants to proceed - clear action intent
Your response: Call start_ekyc_process
Action: CALL TOOL

Example 10:
User: "ຕອນນີ້ໄດ້ແລ້ວ"
Analysis: User indicating readiness ("now is okay") - implicit action consent
Context: After explaining eKYC, this means "let's start"
Your response: Call start_ekyc_process
Action: CALL TOOL

═══ INTENT 3: MIXED INTENT - Question followed by action ═══

Example 11:
User: "eKYC ແມ່ນຫຍັງ? ຂ້ອຍຢາກລອງເຮັດເບິ່ງ"
Analysis: First part is question, second part is action desire
Your response: Briefly explain eKYC, then call start_ekyc_process
Action: CALL TOOL (because action intent is present)

Example 12:
User: "ມັນຍາກບໍ່? ຖ້າງ່າຍກໍມາເຮັດເລີຍ"
Analysis: Question about difficulty, conditional action intent
Your response: Explain it's easy, then call start_ekyc_process
Action: CALL TOOL

═══ INTENT 4: PROCESS MANAGEMENT - Mid-process queries ═══

Example 13:
User: "ຮູບບັດຂອງຂ້ອຍຖືກສະແກນແລ້ວບໍ່?"
Analysis: User checking status during process
Context: State is "id_uploaded" or "id_scanned"
Your response: Provide status update based on current state
Action: NO tool call (process already running)

Example 14:
User: "ຕໍ່ໄປຂ້ອຍຕ້ອງເຮັດຫຍັງອີກ?"
Analysis: User asking about next step during process
Context: State is "id_scanned" or "face_verifying"
Your response: Guide them on next step based on current state
Action: NO tool call

Example 15:
User: "ລະບົບມັນຫ້າງບໍ່?"
Analysis: User asking if system is stuck/frozen
Context: State is "id_uploaded" (processing)
Your response: Reassure them system is processing, ask to wait
Action: NO tool call

═══ INTENT 5: RESTART/REDO - Completed state actions ═══

Example 16:
User: "ຂ້ອຍຢາກເຮັດໃໝ່ອີກຄັ້ງໄດ້ບໍ່?"
Analysis: User wants to redo eKYC
Context: State is "completed"
Your response: Confirm they can restart, call start_ekyc_process
Action: CALL TOOL (system will auto-clear old data)

Example 17:
User: "ເຮັດຜິດແລ້ວ ຂໍເຮັດໃໝ່ອີກຕື້"
Analysis: User made mistake and wants to start over
Context: Any state, but likely "completed" or during process
Your response: If completed, call tool. If mid-process, guide them
Action: CALL TOOL (if state allows)

════════════════════════════════════════════════════════════════════════════════
🎯 KEY PRINCIPLES FOR INTENT RECOGNITION
════════════════════════════════════════════════════════════════════════════════

1. SEMANTIC UNDERSTANDING over keyword matching:
   - Don't just look for specific words like "eKYC" or "start"
   - Understand the MEANING and CONTEXT of what user wants
   - "ມາເຮັດ" (let's do it) is as valid as "ເລີ່ມ eKYC" (start eKYC)

2. ACTION VERBS indicate intent to act:
   - ເຮັດ (do), ລອງ (try), ເລີ່ມ (start), ມາ (come/let's)
   - ຢາກ (want), ຊ່ວຍ (help), ກຽມແລ້ວ (ready)
   - These suggest ACTION, not just asking

3. QUESTION WORDS indicate information seeking:
   - ແມ່ນຫຍັງ (what is), ແນວໃດ (how), ເປັນຫຍັງ (why)
   - ເທົ່າໃດ (how much/long), ຫຍັງແດ່ (what do I need)
   - These suggest INFORMATION, not action

4. CONTEXT from conversation history:
   - After explaining eKYC, "ໂອເຄ" (okay) likely means "let's start"
   - During process, questions are status checks, not new actions
   - In completed state, action words mean restart

5. STATE AWARENESS:
   - idle: Action verbs → call tool | Questions → answer
   - id_uploaded/id_scanned/face_verifying: DON'T call tool, guide user
   - completed: Action verbs about redo → call tool

════════════════════════════════════════════════════════════════════════════════
💡 INTELLIGENCE GUIDELINES
════════════════════════════════════════════════════════════════════════════════

1. TRUST YOUR UNDERSTANDING: Use semantic comprehension, not rigid rules
2. CONTEXT IS KEY: Consider conversation flow and current state
3. BE CONVERSATIONAL: Understand natural language, implied meanings
4. ONE TOOL, SMART USAGE: start_ekyc_process is your only action, use it wisely
5. STAY IN LAO: Always respond in Lao language, show cultural understanding

════════════════════════════════════════════════════════════════════════════════

Act as a professional, knowledgeable, and friendly eKYC consultant who truly understands what Lao citizens want to achieve."""
        )
        self.conversation.add_message(system_message)

    def _define_tools(self) -> List[Dict[str, Any]]:
        """Define available tools for the AI - Only expose start_ekyc_process to simplify AI decision-making"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "start_ekyc_process",
                    "description": "Initiates the complete eKYC verification flow (ID upload → scan → face verification). Use this when you recognize USER'S INTENT TO ACT - when they express readiness, desire to begin, or willingness to proceed with identity verification. Focus on understanding what the user WANTS TO DO, not just specific keywords they use. This is an action tool, not for answering informational questions.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string",
                                "description": "Welcoming message in Lao language to guide user into the eKYC process with clear next steps"
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

        # Add state-specific intent guidance
        if progress_summary['progress'] == 'idle':
            context_parts.append("🎯 CURRENT SITUATION: User hasn't started yet. Listen for ACTION intent (wanting to begin) vs INFORMATION intent (asking questions).")
        elif progress_summary['progress'] == 'id_uploaded':
            context_parts.append("⏳ CURRENT SITUATION: Process is running (ID being processed). User queries here are STATUS CHECKS, not new action requests. Provide reassurance.")
        elif progress_summary['progress'] == 'id_scanned':
            context_parts.append("✅ CURRENT SITUATION: ID processed successfully. User is at transition point. Questions are about 'what next', not action initiation.")
        elif progress_summary['progress'] == 'face_verifying':
            context_parts.append("📸 CURRENT SITUATION: User is actively verifying face. Messages are likely status checks or help requests, not new actions.")
        elif progress_summary['progress'] == 'completed':
            context_parts.append("🎉 CURRENT SITUATION: Process finished! If user expresses desire to REDO/RESTART (action intent), you can reinitiate. Otherwise, just converse.")

        context_parts.append("⚠️ LANGUAGE: Always respond in Lao, regardless of input language.")

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

        # Add state-specific intent guidance
        if progress_summary['progress'] == 'idle':
            context_parts.append("🎯 CURRENT SITUATION: User hasn't started yet. Listen for ACTION intent (wanting to begin) vs INFORMATION intent (asking questions).")
        elif progress_summary['progress'] == 'id_uploaded':
            context_parts.append("⏳ CURRENT SITUATION: Process is running (ID being processed). User queries here are STATUS CHECKS, not new action requests. Provide reassurance.")
        elif progress_summary['progress'] == 'id_scanned':
            context_parts.append("✅ CURRENT SITUATION: ID processed successfully. User is at transition point. Questions are about 'what next', not action initiation.")
        elif progress_summary['progress'] == 'face_verifying':
            context_parts.append("📸 CURRENT SITUATION: User is actively verifying face. Messages are likely status checks or help requests, not new actions.")
        elif progress_summary['progress'] == 'completed':
            context_parts.append("🎉 CURRENT SITUATION: Process finished! If user expresses desire to REDO/RESTART (action intent), you can reinitiate. Otherwise, just converse.")

        context_parts.append("⚠️ LANGUAGE: Always respond in Lao, regardless of input language.")

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
