"""
内存数据存储 - 对话和消息（带文件持久化）
"""
from datetime import datetime
from typing import Dict, List, Optional
import uuid
import json
import os
from pathlib import Path


class MemoryStore:
    """内存数据存储类（支持文件持久化对话元数据）"""
    
    def __init__(self):
        self.conversations: Dict[str, dict] = {}
        self.messages: Dict[str, List[dict]] = {}  # conversation_id -> messages
        self.storage_file = Path(__file__).parent / "conversation_storage.json"
        
        # 启动时加载持久化的对话数据
        self._load_from_file()
    
    def _load_from_file(self):
        """从文件加载对话数据"""
        try:
            if self.storage_file.exists():
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 转换 datetime 字符串回对象
                    for conv_id, conv in data.get("conversations", {}).items():
                        if isinstance(conv.get("created_at"), str):
                            conv["created_at"] = datetime.fromisoformat(conv["created_at"])
                        if isinstance(conv.get("updated_at"), str):
                            conv["updated_at"] = datetime.fromisoformat(conv["updated_at"])
                        self.conversations[conv_id] = conv
                        self.messages[conv_id] = []  # 消息不持久化，只保存对话元数据
                    print(f"[INFO] 加载了 {len(self.conversations)} 个对话")
        except Exception as e:
            print(f"[WARN] 加载对话数据失败: {e}")
    
    def _save_to_file(self):
        """保存对话数据到文件"""
        try:
            # 只保存对话元数据，不保存消息（消息从 Dify 拉取）
            data = {
                "conversations": {},
                "last_updated": datetime.now().isoformat()
            }
            for conv_id, conv in self.conversations.items():
                conv_copy = conv.copy()
                # 转换 datetime 为字符串
                if isinstance(conv_copy.get("created_at"), datetime):
                    conv_copy["created_at"] = conv_copy["created_at"].isoformat()
                if isinstance(conv_copy.get("updated_at"), datetime):
                    conv_copy["updated_at"] = conv_copy["updated_at"].isoformat()
                data["conversations"][conv_id] = conv_copy
            
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[WARN] 保存对话数据失败: {e}")
    
    # ==================== Conversations ====================
    
    def create_conversation(self, title: str = "新对话", user_id: Optional[str] = None) -> dict:
        """创建新对话"""
        conv_id = f"conv_{uuid.uuid4().hex[:12]}"
        now = datetime.now()
        
        conversation = {
            "id": conv_id,
            "user_id": user_id,
            "title": title,
            "dify_conversation_id": None,
            "last_message": None,
            "message_count": 0,
            "created_at": now,
            "updated_at": now
        }
        
        self.conversations[conv_id] = conversation
        self.messages[conv_id] = []
        
        # 保存到文件
        self._save_to_file()
        
        return conversation
    
    def get_conversation(self, conversation_id: str) -> Optional[dict]:
        """获取对话"""
        return self.conversations.get(conversation_id)
    
    def get_all_conversations(self, user_id: Optional[str] = None) -> List[dict]:
        """获取所有对话"""
        convs = list(self.conversations.values())
        if user_id:
            convs = [c for c in convs if c.get("user_id") == user_id]
        # 按更新时间倒序
        convs.sort(key=lambda x: x["updated_at"], reverse=True)
        return convs
    
    def update_conversation(self, conversation_id: str, **kwargs) -> Optional[dict]:
        """更新对话"""
        conv = self.conversations.get(conversation_id)
        if not conv:
            return None
        
        for key, value in kwargs.items():
            if value is not None:
                conv[key] = value
        
        conv["updated_at"] = datetime.now()
        
        # 保存到文件
        self._save_to_file()
        
        return conv
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """删除对话"""
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
            if conversation_id in self.messages:
                del self.messages[conversation_id]
            
            # 保存到文件
            self._save_to_file()
            
            return True
        return False
    
    # ==================== Messages ====================
    
    def create_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        image_url: Optional[str] = None,
        dify_message_id: Optional[str] = None
    ) -> dict:
        """创建消息"""
        if conversation_id not in self.conversations:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        msg_id = f"msg_{uuid.uuid4().hex[:12]}"
        now = datetime.now()
        
        message = {
            "id": msg_id,
            "conversation_id": conversation_id,
            "role": role,
            "content": content,
            "image_url": image_url,
            "dify_message_id": dify_message_id,
            "created_at": now
        }
        
        if conversation_id not in self.messages:
            self.messages[conversation_id] = []
        
        self.messages[conversation_id].append(message)
        
        # 更新对话的最后消息和消息数量
        conv = self.conversations[conversation_id]
        conv["last_message"] = content[:50]  # 只保存前50个字符
        conv["message_count"] = len(self.messages[conversation_id])
        conv["updated_at"] = now
        
        return message
    
    def get_messages(self, conversation_id: str, limit: Optional[int] = None) -> List[dict]:
        """获取对话的消息列表"""
        messages = self.messages.get(conversation_id, [])
        if limit:
            messages = messages[-limit:]  # 获取最后N条
        return messages
    
    def get_message(self, message_id: str) -> Optional[dict]:
        """获取单条消息"""
        for msgs in self.messages.values():
            for msg in msgs:
                if msg["id"] == message_id:
                    return msg
        return None


# 全局内存存储实例
memory_store = MemoryStore()

