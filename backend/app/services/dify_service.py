"""
Dify API 集成服务
"""
import os
import httpx
import json
from typing import Optional, AsyncIterator, Dict, Any
from dotenv import load_dotenv

load_dotenv()


class DifyService:
    """Dify API 服务类"""
    
    def __init__(self):
        self.api_key = os.getenv("DIFY_API_KEY", "app-DoAn63W9Wck3bvEveCnwJZW1")
        self.base_url = os.getenv("DIFY_API_BASE_URL", "http://deepseek.zkyc-ai.cn/v1")
        self.app_id = os.getenv("DIFY_APP_ID", "e93105f7-fe7d-4563-afe1-4e17c380d87f")
        self.timeout = 60.0
    
    async def chat_streaming(
        self,
        query: str,
        conversation_id: Optional[str] = None,
        files: Optional[list] = None,
        user: str = "default_user"
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        流式对话接口
        
        Args:
            query: 用户问题
            conversation_id: Dify会话ID（可选，用于继续对话）
            files: 文件列表（可选）
            user: 用户标识
            
        Yields:
            流式响应数据块
        """
        url = f"{self.base_url}/chat-messages"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 硬编码的 token
        token = "eyJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE3Njk1MDIyNzgsImV4cCI6MTc2OTU0NTQ3OCwidG9QbGF0Zm9ybSI6IjEiLCJ0eXBlIjoiMiIsInVzZXJJZCI6IjE5MTE3MTgyMzE2MjkzMDc5MDQyMzE3MjgifQ.S7x8El59Tq4IXnA9nOtNz4kS-UbTF-rI9jKtpA5ZSXo"
        
        payload = {
            "conversation_id": conversation_id or "",
            "files": files or [],
            "inputs": {},
            "token": token,
            "parent_message_id": None,
            "query": query,
            "response_mode": "streaming",
            "user": user  # 添加 user 字段，Dify 要求必须提供
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream(
                "POST",
                url,
                headers=headers,
                json=payload
            ) as response:
                # 如果响应不是 2xx，打印详细错误信息
                if response.status_code >= 400:
                    error_body = await response.aread()
                    print(f"Dify API 错误响应 [{response.status_code}]:")
                    print(f"URL: {url}")
                    print(f"请求体: {json.dumps(payload, ensure_ascii=False, indent=2)}")
                    print(f"响应体: {error_body.decode('utf-8', errors='ignore')}")
                    response.raise_for_status()
                
                # 解析 SSE 流式响应
                async for line in response.aiter_lines():
                    if not line or not line.startswith("data:"):
                        continue
                    
                    # 提取 data: 后面的内容
                    data_str = line[5:].strip()
                    
                    if not data_str:
                        continue
                    
                    try:
                        data = json.loads(data_str)
                        yield data
                    except json.JSONDecodeError:
                        continue
    
    async def get_conversation_logs(
        self,
        conversation_id: str,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        获取对话历史记录
        
        Args:
            conversation_id: Dify会话ID
            limit: 获取的消息数量
            
        Returns:
            对话历史数据
        """
        # 使用普通 API 获取对话历史（不是控制台 API）
        url = f"{self.base_url}/messages"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        params = {
            "conversation_id": conversation_id,
            "user": "default_user",
            "limit": limit
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
    
    async def upload_file(
        self,
        file_path: str,
        user: str = "default_user"
    ) -> Dict[str, Any]:
        """
        上传文件到 Dify
        
        Args:
            file_path: 本地文件路径
            user: 用户标识
            
        Returns:
            文件信息（包含file_id）
        """
        url = f"{self.base_url}/files/upload"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            with open(file_path, "rb") as f:
                files = {
                    "file": (os.path.basename(file_path), f, "image/jpeg")
                }
                data = {
                    "user": user
                }
                response = await client.post(
                    url,
                    headers=headers,
                    files=files,
                    data=data
                )
                response.raise_for_status()
                return response.json()


# 全局 Dify 服务实例
dify_service = DifyService()

