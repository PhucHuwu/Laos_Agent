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
            content="""Bạn là một trợ lý AI chuyên hỗ trợ người dân về việc eKYC (định danh điện tử) căn cước công dân Lào.

BẠN LÀ TRỢ LÝ THÔNG MINH - TỰ QUYẾT ĐỊNH MỌI HÀNH ĐỘNG:

1. **Trò chuyện tự nhiên**: Trả lời mọi câu hỏi của người dân một cách thân thiện, dễ hiểu bằng tiếng Việt
2. **Tự quyết định sử dụng tools**: Bạn hoàn toàn tự quyết định khi nào cần sử dụng tools, không cần chờ người dùng yêu cầu cụ thể

QUY TRÌNH LÀM VIỆC THÔNG MINH:

**Khi người dùng yêu cầu eKYC hoặc liên quan đến căn cước công dân:**
- Tự động gọi tool "open_image_upload" để mở popup upload ảnh căn cước
- Hướng dẫn người dùng upload ảnh căn cước công dân

**Khi người dùng upload ảnh căn cước công dân:**
- Tự động gọi tool "scan_image_from_url" để trích xuất thông tin từ ảnh
- Hiển thị thông tin đã trích xuất cho người dùng xác nhận
- SAU KHI SCAN THÀNH CÔNG, tự động gọi tool "open_camera_realtime" để tiến hành xác thực khuôn mặt

**Khi người dùng yêu cầu xác thực khuôn mặt:**
- Nếu chưa có dữ liệu ảnh căn cước: Tự động gọi tool "open_image_upload" để yêu cầu upload ảnh căn cước trước
- Nếu đã có dữ liệu ảnh căn cước: Tự động gọi tool "open_camera_realtime" để mở camera xác thực khuôn mặt

**CÁC TOOLS CÓ SẴN:**
- open_image_upload: Mở popup upload ảnh căn cước công dân
- open_camera_realtime: Mở camera real-time để xác thực khuôn mặt  
- scan_image_from_url: Trích xuất thông tin từ ảnh căn cước đã upload
- verify_face: Xác thực khuôn mặt (so sánh ảnh căn cước với selfie)

**NGUYÊN TẮC QUAN TRỌNG:**
- Bạn là người dẫn dắt, người dân chỉ cần làm theo hướng dẫn
- Mọi quyết định đều do bạn đưa ra dựa trên ngữ cảnh cuộc trò chuyện
- Không cần hỏi người dùng muốn làm gì, hãy tự động thực hiện bước tiếp theo
- Giải thích rõ ràng từng bước cho người dân hiểu
- Luôn kiểm tra điều kiện trước khi thực hiện (ví dụ: có ảnh căn cước chưa trước khi xác thực khuôn mặt)
- QUAN TRỌNG: Khi có CONTEXT message báo có ảnh căn cước và người dùng yêu cầu xác thực khuôn mặt, BẮT BUỘC phải gọi tool "open_camera_realtime"
- QUAN TRỌNG: Khi người dùng báo "đã upload và scan ảnh căn cước thành công", BẮT BUỘC phải gọi tool "open_camera_realtime" để tiến hành xác thực khuôn mặt

Hãy hoạt động như một nhân viên tư vấn chuyên nghiệp, tự tin và có kinh nghiệm."""
        )
        self.conversation.add_message(system_message)

    def _define_tools(self) -> List[Dict[str, Any]]:
        """Define available tools for the AI"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "open_image_upload",
                    "description": "Mở popup upload ảnh căn cước công dân. Sử dụng khi người dùng cần upload ảnh căn cước để eKYC hoặc xác thực khuôn mặt",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string",
                                "description": "Tin nhắn hướng dẫn người dùng về việc upload ảnh căn cước công dân"
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
                    "description": "Tự động scan và trích xuất thông tin từ ảnh căn cước công dân đã upload. Sử dụng ngay sau khi người dùng upload ảnh căn cước",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "image_url": {
                                "type": "string",
                                "description": "URL của ảnh căn cước công dân đã upload"
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
                    "description": "Mở camera real-time để xác thực khuôn mặt. Sử dụng khi người dùng yêu cầu xác thực khuôn mặt và đã có dữ liệu ảnh căn cước",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string",
                                "description": "Tin nhắn hướng dẫn người dùng về việc xác thực khuôn mặt bằng camera"
                            },
                            "id_card_url": {
                                "type": "string",
                                "description": "URL của ảnh căn cước công dân đã scan (bắt buộc phải có để xác thực)"
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
                    "description": "Xác thực khuôn mặt bằng cách so sánh ảnh căn cước với ảnh selfie",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "id_card_image_url": {
                                "type": "string",
                                "description": "URL của ảnh căn cước công dân"
                            },
                            "selfie_image_url": {
                                "type": "string",
                                "description": "URL của ảnh selfie để xác thực"
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
        # Add user message to conversation
        user_message = Message(role="user", content=user_input)
        self.conversation.add_message(user_message)

        # Prepare API request
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }

        # Thêm context vào messages để AI biết trạng thái hiện tại
        messages = self.conversation.get_messages_for_api().copy()

        # Thêm context message nếu có dữ liệu
        if self.conversation.has_id_card_data():
            context_message = {
                "role": "system",
                "content": f"CONTEXT QUAN TRỌNG: Người dùng đã upload và scan ảnh căn cước công dân thành công. ID card URL: {self.conversation.get_id_card_url()}. Nếu người dùng yêu cầu xác thực khuôn mặt, BẮT BUỘC phải gọi tool 'open_camera_realtime' với id_card_url = '{self.conversation.get_id_card_url()}'."
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

            # Parse response
            response.encoding = 'utf-8'
            content = response.text
            lines = content.strip().split('\n')

            # Find JSON data
            json_data = None
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
                return {"error": "Could not parse response from API"}

            message_data = json_data['choices'][0]['message']

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

    def _handle_tool_call(self, tool_call: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handle individual tool calls"""
        try:
            function_name = tool_call['function']['name']
            arguments = json.loads(tool_call['function']['arguments'])

            if function_name == "open_image_upload":
                message = arguments.get("message", "Vui lòng upload ảnh căn cước công dân của bạn")
                return {
                    "success": True,
                    "action": "open_upload_popup",
                    "message": message,
                    "tool_call_id": tool_call['id']
                }

            elif function_name == "open_selfie_upload":
                message = arguments.get("message", "Vui lòng upload ảnh selfie để xác thực khuôn mặt")
                id_card_url = arguments.get("id_card_url")
                return {
                    "success": True,
                    "action": "open_selfie_upload_popup",
                    "message": message,
                    "id_card_url": id_card_url,
                    "tool_call_id": tool_call['id']
                }

            elif function_name == "open_camera_realtime":
                message = arguments.get("message", "Vui lòng xác thực khuôn mặt bằng camera")
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

            # Parse response (similar to main chat method)
            response.encoding = 'utf-8'
            content = response.text
            lines = content.strip().split('\n')

            json_data = None
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
                return {"error": "Could not parse follow-up response from API"}

            final_message = json_data['choices'][0]['message']

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
