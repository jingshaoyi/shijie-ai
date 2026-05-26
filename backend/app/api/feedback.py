"""
意见反馈路由
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.user import User
from app.models.feedback import Feedback
from app.auth import get_current_user
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/feedback", tags=["意见反馈"])


class FeedbackCreate(BaseModel):
    type: str = Field(..., description="反馈类型: feature/bug/experience/other")
    content: str = Field(..., min_length=10, max_length=500, description="反馈内容")
    contact: Optional[str] = Field(None, max_length=100, description="联系方式")
    images: Optional[List[str]] = Field(None, description="图片URL列表")


class FeedbackResponse(BaseModel):
    id: int
    type: str
    content: str
    status: str
    created_at: Optional[str] = None


@router.post("/submit")
async def submit_feedback(
    req: FeedbackCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """提交意见反馈"""
    # 验证反馈类型
    valid_types = ["feature", "bug", "experience", "other"]
    if req.type not in valid_types:
        raise HTTPException(status_code=400, detail=f"无效的反馈类型，可选: {', '.join(valid_types)}")
    
    # 创建反馈记录
    feedback = Feedback(
        user_id=user.id,
        type=req.type,
        content=req.content,
        contact=req.contact,
        images=req.images or []
    )
    
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    
    logger.info("feedback_submitted", user_id=user.id, feedback_id=feedback.id, type=req.type)
    
    return {
        "code": 0,
        "message": "反馈提交成功",
        "id": feedback.id
    }


@router.get("/list")
async def get_feedback_list(
    page: int = 1,
    page_size: int = 10,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户的反馈列表"""
    query = db.query(Feedback).filter(Feedback.user_id == user.id).order_by(Feedback.created_at.desc())
    
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return {
        "code": 0,
        "data": [
            {
                "id": item.id,
                "type": item.type,
                "content": item.content[:100] + "..." if len(item.content) > 100 else item.content,
                "status": item.status,
                "created_at": item.created_at.isoformat() if item.created_at else None
            }
            for item in items
        ],
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.get("/detail/{feedback_id}")
async def get_feedback_detail(
    feedback_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取反馈详情"""
    feedback = db.query(Feedback).filter(
        Feedback.id == feedback_id,
        Feedback.user_id == user.id
    ).first()
    
    if not feedback:
        raise HTTPException(status_code=404, detail="反馈不存在")
    
    return {
        "code": 0,
        "data": {
            "id": feedback.id,
            "type": feedback.type,
            "content": feedback.content,
            "contact": feedback.contact,
            "images": feedback.images,
            "status": feedback.status,
            "reply": feedback.reply,
            "created_at": feedback.created_at.isoformat() if feedback.created_at else None
        }
    }


@router.get("/stats")
async def get_feedback_stats(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户反馈统计"""
    total = db.query(Feedback).filter(Feedback.user_id == user.id).count()
    pending = db.query(Feedback).filter(
        Feedback.user_id == user.id,
        Feedback.status == "pending"
    ).count()
    resolved = db.query(Feedback).filter(
        Feedback.user_id == user.id,
        Feedback.status == "resolved"
    ).count()
    
    return {
        "code": 0,
        "data": {
            "total": total,
            "pending": pending,
            "resolved": resolved
        }
    }
