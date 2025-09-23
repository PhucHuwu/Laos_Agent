import os
import json
import requests
from dotenv import load_dotenv

# Load biến môi trường từ file .env
load_dotenv()
API_KEY = os.getenv("API_KEY")

if not API_KEY:
    raise ValueError("❌ API_KEY chưa được cấu hình trong file .env")

# Cấu hình MCP server
MCP_SERVER_URL = "http://172.16.5.10:3009/mcp"  # Document MCP server
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

def call_mcp(method: str, params: dict = None):
    """
    Gửi request JSON-RPC 2.0 đến MCP server
    """
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params or {}
    }

    try:
        response = requests.post(MCP_SERVER_URL, headers=HEADERS, data=json.dumps(payload), timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print("❌ Lỗi khi gọi MCP server:", e)
        return None

if __name__ == "__main__":
    # Test gọi 1 function có sẵn trên MCP server, ví dụ: list_functions
    result = call_mcp("list_functions")

    print("✅ Kết quả từ MCP server:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
