"""
测试 Dify API 响应格式
"""
import httpx
import json

# Dify API 配置
API_KEY = "app-DoAn63W9Wck3bvEveCnwJZW1"
BASE_URL = "http://deepseek.zkyc-ai.cn/v1"
TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE3Njk1MDIyNzgsImV4cCI6MTc2OTU0NTQ3OCwidG9QbGF0Zm9ybSI6IjEiLCJ0eXBlIjoiMiIsInVzZXJJZCI6IjE5MTE3MTgyMzE2MjkzMDc5MDQyMzE3MjgifQ.S7x8El59Tq4IXnA9nOtNz4kS-UbTF-rI9jKtpA5ZSXo"

def test_dify_streaming():
    """测试流式响应"""
    url = f"{BASE_URL}/chat-messages"
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "conversation_id": "",
        "files": [],
        "inputs": {},
        "token": TOKEN,
        "parent_message_id": None,
        "query": "你好",
        "response_mode": "streaming",
        "user": "test_user"
    }
    
    print("=" * 80)
    print("发送请求:")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    print("=" * 80)
    print("\n接收到的响应数据块：\n")
    
    with httpx.Client(timeout=60.0) as client:
        with client.stream("POST", url, headers=headers, json=payload) as response:
            print(f"HTTP 状态码: {response.status_code}\n")
            
            if response.status_code != 200:
                print("错误响应:")
                print(response.text)
                return
            
            chunk_count = 0
            for line in response.iter_lines():
                if not line or not line.startswith("data:"):
                    continue
                
                chunk_count += 1
                data_str = line[5:].strip()
                
                if not data_str:
                    continue
                
                try:
                    data = json.loads(data_str)
                    print(f"\n【数据块 {chunk_count}】")
                    print(json.dumps(data, ensure_ascii=False, indent=2))
                    print("-" * 80)
                except json.JSONDecodeError as e:
                    print(f"JSON 解析失败: {e}")
                    print(f"原始数据: {data_str}")

if __name__ == "__main__":
    test_dify_streaming()

