from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class ChatHistory(Base):
    """对话历史表"""
    __tablename__ = "chat_histories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(256), default="新对话")
    preview = Column(String(512), default="")
    model_id = Column(String(64), nullable=True)
    model_name = Column(String(128), nullable=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    messages = relationship("ChatMessage", back_populates="chat_history", cascade="all, delete-orphan")


class ChatMessage(Base):
    """对话消息表"""
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(Integer, ForeignKey("chat_histories.id"), nullable=False, index=True)
    role = Column(String(16), nullable=False)
    content = Column(Text, nullable=False)
    time = Column(String(16), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    chat_history = relationship("ChatHistory", back_populates="messages")
