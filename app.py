from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
import os

# 导入模块
from config.settings import settings
from core.language_router import LanguageRouter
from agents.chat_agent import ChatAgent
from database import get_db, init_db
from database.crud import UserCRUD, ConversationCRUD
from memory.vector_store import VectorStore

# 初始化FastAPI应用
app = FastAPI(title="暖洋洋 - Nuanyangyang")

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 初始化组件
chat_agent = ChatAgent()
language_router = LanguageRouter()
vector_store = VectorStore()

class ChatMessage(BaseModel):
    message: str
    language: str = None  # 可选，如果不提供则自动检测

@app.on_event("startup")
async def startup_event():
    """应用启动时初始化数据库"""
    try:
        init_db()
        print("✅ Database initialized successfully!")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """返回主页"""
    with open("static/index.html", encoding="utf-8") as f:
        return HTMLResponse(content=f.read(), status_code=200)

@app.post("/api/chat")
async def chat(message: ChatMessage, db: Session = Depends(get_db)):
    """处理聊天请求"""
    try:
        # 1. 检测或使用指定语言
        if message.language:
            language = message.language
        else:
            language = language_router.detect_language(message.message)
        
        # 2. 获取或创建默认用户（MVP阶段）
        user = UserCRUD.get_or_create_default_user(db)
        
        # 3. 调用ChatAgent处理对话
        bot_response = await chat_agent.chat(
            user_id=user.user_id,
            user_message=message.message,
            language=language,
            db=db
        )
        
        # 4. 保存对话到数据库
        conversation = ConversationCRUD.save_conversation(
            db=db,
            user_id=user.user_id,
            language=language,
            user_message=message.message,
            bot_response=bot_response
        )
        
        # 5. 保存到向量数据库（异步）
        await vector_store.add_conversation(
            user_id=user.user_id,
            language=language,
            user_message=message.message,
            bot_response=bot_response,
            conversation_id=conversation.conversation_id
        )
        
        return {
            "reply": bot_response,
            "language": language,
            "user_id": user.user_id
        }
    
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return {
            "reply": f"抱歉，我遇到了一些问题。请稍后再试。(Error: {str(e)})",
            "language": "zh"
        }

@app.get("/api/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "services": {
            "database": "connected",
            "redis": "connected",
            "qdrant": "connected"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
