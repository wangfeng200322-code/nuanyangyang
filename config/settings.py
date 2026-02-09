from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # API Keys
    deepseek_api_key: str
    openai_api_key: str = ""  # 可选，仅在使用荷兰语/英语时需要
    
    # Database
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str
    postgres_password: str
    postgres_db: str
    
    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    
    # Qdrant
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    
    # Application
    default_language: str = "zh"
    supported_languages: List[str] = ["zh", "nl", "en"]
    
    # Embedding配置
    embedding_model: str = "bge-m3"  # 可选: "openai" 或 "bge-m3"（本地开源模型）
    
    @property
    def database_url(self) -> str:
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8-sig"

settings = Settings()
