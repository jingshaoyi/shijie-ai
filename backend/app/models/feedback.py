"""
意见反馈模型
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.sql import func
from app.database import Base


class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, comment="用户ID")
    type = Column(String(20), nullable=False, comment="反馈类型: feature/bug/experience/other")
    content = Column(Text, nullable=False, comment="反馈内容")
    contact = Column(String(100), nullable=True, comment="联系方式")
    images = Column(JSON, nullable=True, comment="图片URL列表")
    status = Column(String(20), default="pending", comment="状态: pending/processing/resolved")
    reply = Column(Text, nullable=True, comment="回复内容")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
