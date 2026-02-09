from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from config.settings import settings
from typing import List, Dict
import uuid

class VectorStore:
    def __init__(self):
        self.client = QdrantClient(
            host=settings.qdrant_host,
            port=settings.qdrant_port
        )
        
        # 根据配置选择Embedding模型
        self.embeddings = None
        self.embedding_dim = 1024  # 默认维度
        
        if settings.embedding_model == "openai":
            # OpenAI Embeddings（需要API密钥）
            if settings.openai_api_key:
                self.embeddings = OpenAIEmbeddings(
                    openai_api_key=settings.openai_api_key,
                    model="text-embedding-3-small"
                )
                self.embedding_dim = 1536
                print("✅ 使用OpenAI Embeddings")
            else:
                print("⚠️  未配置OpenAI API密钥，将使用本地BGE-M3模型")
                settings.embedding_model = "bge-m3"  # 自动切换
        
        if settings.embedding_model == "bge-m3":
            # BGE-M3本地模型（开源，无需API）
            print("📦 加载BGE-M3本地Embedding模型（首次运行会下载模型，约2GB）...")
            self.embeddings = HuggingFaceEmbeddings(
                model_name="BAAI/bge-m3",
                model_kwargs={'device': 'cpu'},  # 使用CPU，如果有GPU可改为'cuda'
                encode_kwargs={'normalize_embeddings': True}
            )
            self.embedding_dim = 1024
            print("✅ BGE-M3模型加载完成！支持中文、英语、荷兰语等100+语言")
        
        # 为每种语言创建集合
        for lang in settings.supported_languages:
            self._ensure_collection(f"conversations_{lang}")
    
    def _ensure_collection(self, collection_name: str):
        """确保集合存在"""
        try:
            collections = self.client.get_collections().collections
            collection_names = [c.name for c in collections]
            
            if collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(
                        size=self.embedding_dim,
                        distance=Distance.COSINE
                    )
                )
                print(f"✅ 创建向量集合: {collection_name} (维度: {self.embedding_dim})")
        except Exception as e:
            print(f"❌ 创建集合 {collection_name} 失败: {e}")
    
    async def add_conversation(
        self,
        user_id: str,
        language: str,
        user_message: str,
        bot_response: str,
        conversation_id: str
    ):
        """添加对话到向量数据库"""
        # 如果没有配置embeddings，跳过向量存储
        if not self.embeddings:
            print("⚠️  未配置Embedding模型，跳过向量存储")
            return
            
        try:
            # 合并对话内容
            text = f"用户: {user_message}\n助手: {bot_response}"
            
            # 生成embedding
            embedding = await self.embeddings.aembed_query(text)
            
            # 存储到Qdrant
            self.client.upsert(
                collection_name=f"conversations_{language}",
                points=[
                    PointStruct(
                        id=str(uuid.uuid4()),
                        vector=embedding,
                        payload={
                            "user_id": user_id,
                            "conversation_id": conversation_id,
                            "user_message": user_message,
                            "bot_response": bot_response,
                            "text": text
                        }
                    )
                ]
            )
            print(f"✅ 对话已保存到向量数据库 (模型: {settings.embedding_model})")
        except Exception as e:
            print(f"❌ 保存对话到向量数据库失败: {e}")
    
    async def search_similar_conversations(
        self,
        user_id: str,
        language: str,
        query: str,
        limit: int = 3
    ) -> List[Dict]:
        """搜索相似对话"""
        # 如果没有配置embeddings，返回空列表
        if not self.embeddings:
            return []
            
        try:
            # 生成query embedding
            query_embedding = await self.embeddings.aembed_query(query)
            
            # 搜索
            results = self.client.search(
                collection_name=f"conversations_{language}",
                query_vector=query_embedding,
                query_filter={
                    "must": [
                        {"key": "user_id", "match": {"value": user_id}}
                    ]
                },
                limit=limit
            )
            
            similar_convs = [
                {
                    "text": hit.payload["text"],
                    "score": hit.score
                }
                for hit in results
            ]
            
            if similar_convs:
                print(f"🔍 找到 {len(similar_convs)} 条相似对话 (模型: {settings.embedding_model})")
            
            return similar_convs
        except Exception as e:
            print(f"❌ 搜索相似对话失败: {e}")
            return []
