# app/models/prompt_template.py
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Index
from sqlalchemy.sql import func
from app.database import Base

class PromptTemplate(Base):
    """提示词模板表"""
    __tablename__ = "prompt_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    template_key = Column(String(100), nullable=False, index=True, comment="模板唯一标识")
    category = Column(String(50), nullable=False, index=True, comment="分类：work_summary, science, poetry, hot_recommend等")
    sub_key = Column(String(100), nullable=True, comment="子分类key，如岗位类型、诗歌体裁等")
    
    # 模板内容
    template_content = Column(Text, nullable=False, comment="提示词模板内容，支持{变量}格式")
    variables = Column(JSON, default=list, comment="模板变量列表")
    
    # 版本控制
    version = Column(Integer, default=1, comment="版本号")
    is_active = Column(Integer, default=1, comment="是否启用：1启用，0禁用")
    
    # 生成参数
    generation_params = Column(JSON, default=dict, comment="生成参数：temperature, model等")
    
    # 元数据
    description = Column(String(500), nullable=True, comment="模板描述")
    usage_count = Column(Integer, default=0, comment="使用次数")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_generated_at = Column(DateTime(timezone=True), nullable=True, comment="上次生成时间")
    
    __table_args__ = (
        Index('idx_category_subkey', 'category', 'sub_key'),
        Index('idx_template_key_version', 'template_key', 'version'),
    )


class PromptTemplateHistory(Base):
    """提示词模板历史记录表"""
    __tablename__ = "prompt_template_history"
    
    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, nullable=False, index=True, comment="关联的模板ID")
    template_key = Column(String(100), nullable=False, comment="模板key")
    
    # 历史内容
    old_content = Column(Text, nullable=False, comment="旧模板内容")
    new_content = Column(Text, nullable=False, comment="新模板内容")
    
    # 变更信息
    change_reason = Column(String(500), nullable=True, comment="变更原因")
    generated_by = Column(String(50), default="system", comment="生成方式：system, manual, scheduled")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class DynamicPrompt(Base):
    """动态生成的提示词缓存表"""
    __tablename__ = "dynamic_prompts"
    
    id = Column(Integer, primary_key=True, index=True)
    cache_key = Column(String(200), nullable=False, unique=True, index=True, comment="缓存key")
    category = Column(String(50), nullable=False, index=True, comment="分类")
    
    # 生成的提示词
    prompt_content = Column(Text, nullable=False, comment="生成的完整提示词")
    
    # 上下文信息
    context = Column(JSON, default=dict, comment="生成上下文：variables, params等")
    
    # 过期时间
    expires_at = Column(DateTime(timezone=True), nullable=False, comment="过期时间")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        Index('idx_category_expires', 'category', 'expires_at'),
    )
