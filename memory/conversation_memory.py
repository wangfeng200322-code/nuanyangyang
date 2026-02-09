import redis
import json
from config.settings import settings
from typing import List, Dict, Optional

class ConversationMemory:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            decode_responses=True
        )
        self.ttl = 3600  # 1小时过期
    
    def _get_key(self, user_id: str) -> str:
        return f"conversation:{user_id}"
    
    def add_message(self, user_id: str, role: str, content: str):
        """添加消息到会话记忆"""
        try:
            key = self._get_key(user_id)
            message = {"role": role, "content": content}
            
            # 获取现有消息
            messages = self.get_messages(user_id)
            messages.append(message)
            
            # 只保留最近10条
            if len(messages) > 10:
                messages = messages[-10:]
            
            # 存储
            self.redis_client.setex(
                key,
                self.ttl,
                json.dumps(messages, ensure_ascii=False)
            )
        except Exception as e:
            print(f"Error adding message to conversation memory: {e}")
    
    def get_messages(self, user_id: str) -> List[Dict]:
        """获取会话记忆"""
        try:
            key = self._get_key(user_id)
            data = self.redis_client.get(key)
            
            if data:
                return json.loads(data)
            return []
        except Exception as e:
            print(f"Error getting conversation memory: {e}")
            return []
    
    def clear(self, user_id: str):
        """清空会话记忆"""
        try:
            key = self._get_key(user_id)
            self.redis_client.delete(key)
        except Exception as e:
            print(f"Error clearing conversation memory: {e}")
