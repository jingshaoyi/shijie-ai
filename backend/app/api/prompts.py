# app/api/prompts.py
"""
提示词模板管理API
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import asyncio

from app.database import get_db
from app.services.prompt_service import PromptService
from app.models.prompt_template import PromptTemplate

router = APIRouter(prefix="/prompts", tags=["提示词模板"])


class PromptGenerateRequest(BaseModel):
    """生成提示词请求"""
    category: str
    variables: Dict[str, Any]
    sub_key: Optional[str] = None


class PromptGenerateResponse(BaseModel):
    """生成提示词响应"""
    success: bool
    prompt: str
    cache_key: Optional[str] = None


class TemplateUpdateRequest(BaseModel):
    """更新模板请求"""
    category: str
    sub_key: Optional[str] = None


class TemplateStatsResponse(BaseModel):
    """模板统计响应"""
    total_templates: int
    active_templates: int
    total_usage: int
    cached_prompts: int
    expired_cache: int
    categories: Dict[str, Any]


@router.post("/generate", response_model=PromptGenerateResponse)
def generate_prompt(
    request: PromptGenerateRequest,
    db: Session = Depends(get_db)
):
    """生成提示词"""
    service = PromptService(db)
    
    try:
        prompt = service.generate_prompt(
            category=request.category,
            variables=request.variables,
            sub_key=request.sub_key
        )
        
        return PromptGenerateResponse(
            success=True,
            prompt=prompt,
            cache_key=service._generate_cache_key(
                request.category, 
                request.variables, 
                request.sub_key
            )
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/regenerate")
async def regenerate_template(
    request: TemplateUpdateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """重新生成指定模板"""
    service = PromptService(db)
    
    result = await service.regenerate_template(
        category=request.category,
        sub_key=request.sub_key
    )
    
    if result:
        return {
            "success": True,
            "message": f"模板 {request.category}/{request.sub_key or 'base'} 已更新",
            "version": result.version
        }
    else:
        raise HTTPException(status_code=500, detail="模板更新失败")


@router.post("/regenerate-all")
async def regenerate_all_templates(
    categories: Optional[List[str]] = None,
    db: Session = Depends(get_db)
):
    """重新生成所有模板"""
    service = PromptService(db)
    
    results = await service.regenerate_all_templates(categories)
    
    success_count = sum(1 for r in results if r["success"])
    
    return {
        "success": True,
        "message": f"已更新 {success_count}/{len(results)} 个模板",
        "results": results
    }


@router.get("/stats", response_model=TemplateStatsResponse)
def get_template_stats(db: Session = Depends(get_db)):
    """获取模板统计信息"""
    service = PromptService(db)
    stats = service.get_template_stats()
    return TemplateStatsResponse(**stats)


@router.get("/templates")
def list_templates(
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """列出所有模板"""
    query = db.query(PromptTemplate)
    
    if category:
        query = query.filter(PromptTemplate.category == category)
    
    templates = query.order_by(
        PromptTemplate.category,
        PromptTemplate.template_key,
        PromptTemplate.version.desc()
    ).all()
    
    return {
        "success": True,
        "templates": [
            {
                "id": t.id,
                "template_key": t.template_key,
                "category": t.category,
                "sub_key": t.sub_key,
                "version": t.version,
                "description": t.description,
                "usage_count": t.usage_count,
                "is_active": t.is_active,
                "created_at": t.created_at.isoformat() if t.created_at else None,
                "updated_at": t.updated_at.isoformat() if t.updated_at else None
            }
            for t in templates
        ]
    }


@router.post("/initialize")
def initialize_templates(db: Session = Depends(get_db)):
    """初始化默认模板"""
    service = PromptService(db)
    service.initialize_default_templates()
    
    return {
        "success": True,
        "message": "默认模板初始化完成"
    }


@router.post("/clear-cache")
def clear_cache(db: Session = Depends(get_db)):
    """清除过期缓存"""
    service = PromptService(db)
    deleted = service.clear_expired_cache()
    
    return {
        "success": True,
        "message": f"已清除 {deleted} 条过期缓存"
    }
