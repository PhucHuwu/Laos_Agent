import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")


def call_mcp_api(method="tools/list", params=None, tool_name=None):
    url = "http://172.16.5.10:3009/mcp/"

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json,text/event-stream',
        'mcp-session-id': '7fcdb6f9974749188ee117ed6e22201c'
    }

    if tool_name:
        data = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "id": 2,
            "params": {
                "name": tool_name,
                "arguments": params or {}
            }
        }
    else:
        data = {
            "jsonrpc": "2.0",
            "method": method,
            "id": 2,
            "params": params or {}
        }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()

        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"Error calling API: {e}")
        return None


def use_tool(tool_name, arguments=None):
    result = call_mcp_api(tool_name=tool_name, params=arguments)

    if result and "result" in result:
        return result["result"]
    else:
        print(f"Lỗi khi sử dụng tool {tool_name}")
        return None


mcp_response = call_mcp_api()

if mcp_response:
    tools = mcp_response.get("result", {}).get("tools", [])

    if tools:
        extract_tool = None
        for tool in tools:
            if tool['name'] == 'extract_document_from_url':
                extract_tool = tool
                break

        if extract_tool:
            test_url = "https://docx.com.vn/tai-lieu/bao-cao-bai-tap-lon-mon-lap-trinh-web-1-1569"

            result = use_tool('extract_document_from_url', {'url': test_url})

            if result:
                with open('result.json', 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
            else:
                print("Thất bại!")

else:
    print("Failed to call MCP API")
