from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text
from datetime import datetime
from app.database import Base


class User(Base):
    """用户表"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    openid = Column(String(64), unique=True, nullable=False, index=True)
    union_id = Column(String(64), unique=True, nullable=True, index=True)
    session_key = Column(String(64), nullable=True)
    nickname = Column(String(64), default="")
    avatar = Column(String(512), default="")
    phone = Column(String(20), nullable=True)
    token = Column(String(256), nullable=True, index=True)
    token_expire = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
