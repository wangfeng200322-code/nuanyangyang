from core.llm_manager import LLMManager
from core.prompts import SYSTEM_PROMPTS
from memory.vector_store import VectorStore
from memory.conversation_memory import ConversationMemory
from database.crud import UserCRUD
from sqlalchemy.orm import Session
from typing import Optional

class ChatAgent:
    def __init__(self):
        self.llm_manager = LLMManager()
        self.vector_store = VectorStore()
        self.conversation_memory = ConversationMemory()
    
    async def chat(
        self,
        user_id: str,
        user_message: str,
        language: str,
        db: Session
    ) -> str:
        """处理对话"""
        
        # 1. 获取用户信息
        user = UserCRUD.get_user(db, user_id)
        if user:
            if language == "zh":
                user_info = f"姓名: {user.name}, 年龄: {user.age}"
            elif language == "nl":
                user_info = f"Naam: {user.name}, Leeftijd: {user.age}"
            else:
                user_info = f"Name: {user.name}, Age: {user.age}"
        else:
            user_info = "新用户" if language == "zh" else ("Nieuwe gebruiker" if language == "nl" else "New user")
        
        # 2. 检索相似对话（RAG）
        similar_convs = await self.vector_store.search_similar_conversations(
            user_id, language, user_message, limit=2
        )
        
        if similar_convs:
            context = "\n".join([conv["text"] for conv in similar_convs])
        else:
            if language == "zh":
                context = "无历史对话"
            elif language == "nl":
                context = "Geen eerdere gesprekken"
            else:
                context = "No previous conversations"
        
        # 3. 获取会话记忆
        history = self.conversation_memory.get_messages(user_id)
        
        # 4. 构建系统提示词
        system_prompt = SYSTEM_PROMPTS[language].format(
            context=context,
            user_info=user_info
        )
        
        # 5. 调用LLM
        bot_response = await self.llm_manager.chat(
            language=language,
            system_prompt=system_prompt,
            user_message=user_message,
            history=history
        )
        
        # 6. 更新记忆
        self.conversation_memory.add_message(user_id, "user", user_message)
        self.conversation_memory.add_message(user_id, "assistant", bot_response)
        
        return bot_response
