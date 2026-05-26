from sqlalchemy import Column, String, Integer, Text, DateTime, JSON
from sqlalchemy.sql import func
from app.database import Base


class SystemConfig(Base):
    """系统配置表"""
    __tablename__ = "system_configs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    config_key = Column(String(100), unique=True, nullable=False, index=True, comment="配置键")
    config_value = Column(Text, nullable=True, comment="配置值")
    config_type = Column(String(32), default="string", comment="类型: string, json, number, boolean")
    description = Column(String(256), nullable=True, comment="配置描述")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
