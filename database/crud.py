from sqlalchemy.orm import Session
from . import models
from typing import Optional, List
from datetime import datetime

class UserCRUD:
    @staticmethod
    def create_user(db: Session, name: str, age: int, gender: str, language: str = "zh"):
        user = models.User(
            name=name,
            age=age,
            gender=gender,
            preferred_language=language
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def get_user(db: Session, user_id: str) -> Optional[models.User]:
        return db.query(models.User).filter(models.User.user_id == user_id).first()
    
    @staticmethod
    def get_or_create_default_user(db: Session) -> models.User:
        """获取或创建默认用户（用于MVP测试）"""
        user = db.query(models.User).first()
        if not user:
            user = UserCRUD.create_user(db, "测试用户", 70, "female", "zh")
        return user

class ConversationCRUD:
    @staticmethod
    def save_conversation(
        db: Session,
        user_id: str,
        language: str,
        user_message: str,
        bot_response: str,
        emotion_score: Optional[float] = None
    ):
        conversation = models.Conversation(
            user_id=user_id,
            language=language,
            user_message=user_message,
            bot_response=bot_response,
            emotion_score=emotion_score
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        return conversation
    
    @staticmethod
    def get_recent_conversations(
        db: Session,
        user_id: str,
        limit: int = 10
    ) -> List[models.Conversation]:
        return db.query(models.Conversation)\
            .filter(models.Conversation.user_id == user_id)\
            .order_by(models.Conversation.created_at.desc())\
            .limit(limit)\
            .all()

class HealthRecordCRUD:
    @staticmethod
    def create_record(
        db: Session,
        user_id: str,
        record_type: str,
        value: dict,
        conversation_id: Optional[str] = None
    ):
        record = models.HealthRecord(
            user_id=user_id,
            record_type=record_type,
            value=value,
            extracted_from_conversation_id=conversation_id
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
