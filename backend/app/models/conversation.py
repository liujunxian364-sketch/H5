"""
考点答疑 - 对话会话和消息数据模型
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class ConversationCreate(BaseModel):
    """创建对话请求"""
    title: Optional[str] = "新对话"


class ConversationUpdate(BaseModel):
    """更新对话请求"""
    title: Optional[str] = None
    last_message: Optional[str] = None


class Conversation(BaseModel):
    """对话会话模型"""
    id: str
    user_id: Optional[str] = None
    title: str
    dify_conversation_id: Optional[str] = None  # Dify侧的会话ID
    last_message: Optional[str] = None
    message_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "id": "conv_123",
                "title": "数学问题求解",
                "dify_conversation_id": "e5b9dd45-a79e-4ac2-aebe-a994454f57a4",
                "last_message": "好的，我明白了",
                "message_count": 5,
                "created_at": "2024-01-27T10:30:00",
                "updated_at": "2024-01-27T10:35:00"
            }
        }


class MessageCreate(BaseModel):
    """创建消息请求"""
    content: str = Field(..., min_length=1, max_length=5000)
    image_url: Optional[str] = None


class Message(BaseModel):
    """消息模型"""
    id: str
    conversation_id: str
    role: str  # user | assistant | system
    content: str
    image_url: Optional[str] = None
    dify_message_id: Optional[str] = None
    created_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "id": "msg_123",
                "conversation_id": "conv_123",
                "role": "user",
                "content": "这道题怎么做？",
                "image_url": None,
                "created_at": "2024-01-27T10:30:00"
            }
        }


class ConversationWithMessages(Conversation):
    """带消息的对话会话"""
    messages: List[Message] = []

