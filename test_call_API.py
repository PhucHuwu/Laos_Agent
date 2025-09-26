import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()
DATA = os.getenv("DATA")
Authorization = os.getenv("Authorization")
Url = os.getenv("Url")

def test_api_call():
    url = Url

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {Authorization}"
    }

    data = {
        "model": "google/gemini-2.5-flash-lite",
        "messages": [
            {
                "role": "system",
                "content": "Bạn là AI hỗ trợ. Sử dụng tools nếu cần."
            },
            {
                "role": "user",
                "content": "Viết 1 đoạn văn mô tả về thời tiết hôm nay ở hà nội"
            },

            {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": "1",
                        "type": "function",
                        "function": {
                            "name": "get_weather",
                            "arguments": "{\"location\": \"Hà Nội\"}"
                        }
                    }
                ]
            },
            {
                "role": "tool",
                "name": "get_weather",
                "tool_call_id": "1",
                "content": "{ \"tool\": \"get_weather\", \"location\": \"Hà Nội\", \"status\": \"Trời nắng\" }"
            }
        ],
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Lấy thời tiết hiện tại cho một location.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "Tên thành phố, ví dụ: 'Hà Nội'."
                            }
                        },
                        "required": [
                            "location"
                        ]
                    }
                }
            }
        ],
        "tool_choice": "auto",
        "stream": True
    }

    try:
        print("Đang gọi API...")
        print(f"URL: {url}")
        print(f"Headers: {json.dumps(headers, indent=2)}")
        print(f"Data: {json.dumps(data, indent=2, ensure_ascii=False)}")
        print("-" * 50)

        response = requests.post(url, headers=headers, json=data, stream=True)

        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print("-" * 50)

        if response.status_code == 200:
            print("Response (streaming):")
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    print(line_str)
                    if line_str.startswith('data: '):
                        try:
                            json_data = json.loads(line_str[6:])
                            print(f"Parsed JSON: {json.dumps(json_data, indent=2, ensure_ascii=False)}")
                        except json.JSONDecodeError:
                            pass
        else:
            print(f"Error: {response.status_code}")
            print(f"Response: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    test_api_call()
