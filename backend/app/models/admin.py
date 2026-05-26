from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text
from datetime import datetime
from app.database import Base


class Admin(Base):
    """管理员表"""
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(64), unique=True, nullable=False, index=True)
    password_hash = Column(String(256), nullable=False)
    nickname = Column(String(64), default="管理员")
    role = Column(String(32), default="admin")  # admin, super_admin
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AdminSession(Base):
    """管理员会话表"""
    __tablename__ = "admin_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    admin_id = Column(Integer, nullable=False, index=True)
    token = Column(String(512), nullable=False, index=True)
    expire_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
