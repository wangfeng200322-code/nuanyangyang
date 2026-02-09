from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from config.settings import settings
from typing import List, Dict

class LLMManager:
    def __init__(self):
        # 中文模型：DeepSeek
        self.deepseek = ChatOpenAI(
            model="deepseek-chat",
            openai_api_key=settings.deepseek_api_key,
            openai_api_base="https://api.deepseek.com/v1",
            temperature=0.7
        )
        
        # 荷兰语/英语模型：GPT-4o-mini（仅在配置了OpenAI密钥时初始化）
        self.gpt4o_mini = None
        if settings.openai_api_key:
            self.gpt4o_mini = ChatOpenAI(
                model="gpt-4o-mini",
                openai_api_key=settings.openai_api_key,
                temperature=0.7
            )
    
    def get_model(self, language: str):
        """根据语言选择模型"""
        if language == "zh":
            return self.deepseek
        else:
            if not self.gpt4o_mini:
                raise ValueError(
                    f"OpenAI API密钥未配置，无法使用{language}语言。"
                    "请在.env文件中添加OPENAI_API_KEY，或只使用中文对话。"
                )
            return self.gpt4o_mini
    
    async def chat(
        self,
        language: str,
        system_prompt: str,
        user_message: str,
        history: List[Dict] = None
    ) -> str:
        """执行对话"""
        model = self.get_model(language)
        
        messages = [SystemMessage(content=system_prompt)]
        
        # 添加历史对话
        if history:
            for msg in history:
                if msg["role"] == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    messages.append(AIMessage(content=msg["content"]))
        
        # 添加当前用户消息
        messages.append(HumanMessage(content=user_message))
        
        # 调用模型
        response = await model.ainvoke(messages)
        return response.content
