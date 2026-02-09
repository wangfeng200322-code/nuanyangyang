from sqlalchemy import Column, String, Integer, DateTime, JSON, Float, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"
    
    user_id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String(100))
    age = Column(Integer)
    gender = Column(String(10))
    preferred_language = Column(String(5), nullable=False, default="zh")
    dialect = Column(String(20))
    voice_gender = Column(String(10), default="female")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    conversations = relationship("Conversation", back_populates="user")
    health_records = relationship("HealthRecord", back_populates="user")

class UserProfile(Base):
    __tablename__ = "user_profiles"
    
    profile_id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.user_id"))
    family_members = Column(JSON)
    interests = Column(JSON)
    medical_history = Column(JSON)
    medications = Column(JSON)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Conversation(Base):
    __tablename__ = "conversations"
    
    conversation_id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.user_id"))
    language = Column(String(5), nullable=False)
    user_message = Column(Text)
    bot_response = Column(Text)
    emotion_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="conversations")

class HealthRecord(Base):
    __tablename__ = "health_records"
    
    record_id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.user_id"))
    record_type = Column(String(50))  # sleep, pain, appetite, etc.
    value = Column(JSON)
    extracted_from_conversation_id = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="health_records")
