"""
管理员数据管理接口
"""
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Header, Query
from pydantic import BaseModel
from typing import Optional, List
from app.database import SessionLocal
from app.models.user import User
from app.models.chat_history import ChatHistory, ChatMessage
from app.models.feedback import Feedback
from app.models.prompt_template import PromptTemplate
from app.api.admin_auth import get_current_admin

router = APIRouter(prefix="/admin", tags=["管理员数据"])


# ========== 统计数据 ==========

@router.get("/statistics")
async def get_statistics(authorization: str = Header(None)):
    """获取统计数据"""
    get_current_admin(authorization)

    db = SessionLocal()
    try:
        # 总用户数
        total_users = db.query(User).count()

        # 今日新增用户
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_users = db.query(User).filter(User.created_at >= today_start).count()

        # 昨日用户数
        yesterday_start = today_start - timedelta(days=1)
        yesterday_users = db.query(User).filter(
            User.created_at >= yesterday_start,
            User.created_at < today_start
        ).count()

        user_growth = ((today_users - yesterday_users) / max(yesterday_users, 1)) * 100

        # 总对话数
        total_chats = db.query(ChatHistory).count()

        # 今日对话数
        today_chats = db.query(ChatHistory).filter(
            ChatHistory.created_at >= today_start
        ).count()

        # 昨日对话数
        yesterday_chats = db.query(ChatHistory).filter(
            ChatHistory.created_at >= yesterday_start,
            ChatHistory.created_at < today_start
        ).count()

        chat_growth = ((today_chats - yesterday_chats) / max(yesterday_chats, 1)) * 100

        # 待处理反馈数
        pending_feedbacks = db.query(Feedback).filter(
            Feedback.status == "pending"
        ).count()

        return {
            "success": True,
            "data": {
                "totalUsers": total_users,
                "todayUsers": today_users,
                "userGrowth": round(user_growth, 1),
                "totalChats": total_chats,
                "todayChats": today_chats,
                "chatGrowth": round(chat_growth, 1),
                "pendingFeedbacks": pending_feedbacks,
            }
        }
    finally:
        db.close()


@router.get("/trend")
async def get_trend_data(days: int = Query(7, ge=1, le=30), authorization: str = Header(None)):
    """获取趋势数据"""
    get_current_admin(authorization)

    db = SessionLocal()
    try:
        result = []
        for i in range(days - 1, -1, -1):
            day_start = (datetime.utcnow() - timedelta(days=i)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            day_end = day_start + timedelta(days=1)

            user_count = db.query(User).filter(
                User.created_at >= day_start,
                User.created_at < day_end
            ).count()

            chat_count = db.query(ChatHistory).filter(
                ChatHistory.created_at >= day_start,
                ChatHistory.created_at < day_end
            ).count()

            result.append({
                "date": day_start.strftime("%m-%d"),
                "users": user_count,
                "chats": chat_count
            })

        return {"success": True, "data": result}
    finally:
        db.close()


@router.get("/model-stats")
async def get_model_stats(authorization: str = Header(None)):
    """获取模型使用统计"""
    get_current_admin(authorization)

    # 模拟数据
    return {
        "success": True,
        "data": [
            {"name": "GPT-4", "value": 45, "percentage": 45},
            {"name": "Claude", "value": 30, "percentage": 30},
            {"name": "文心一言", "value": 15, "percentage": 15},
            {"name": "通义千问", "value": 10, "percentage": 10},
        ]
    }


@router.get("/activities")
async def get_recent_activities(limit: int = Query(10, ge=1, le=50), authorization: str = Header(None)):
    """获取最近活动"""
    get_current_admin(authorization)

    db = SessionLocal()
    try:
        # 获取最近的用户注册
        recent_users = db.query(User).order_by(
            User.created_at.desc()
        ).limit(limit // 2).all()

        activities = []
        for user in recent_users:
            activities.append({
                "content": f"新用户注册: {user.nickname or user.openid[:8]}",
                "time": user.created_at.strftime("%Y-%m-%d %H:%M"),
                "type": "user"
            })

        # 获取最近的对话
        recent_chats = db.query(ChatHistory).order_by(
            ChatHistory.created_at.desc()
        ).limit(limit // 2).all()

        for chat in recent_chats:
            activities.append({
                "content": f"新建对话: {chat.title or '未命名对话'}",
                "time": chat.created_at.strftime("%Y-%m-%d %H:%M"),
                "type": "chat"
            })

        # 按时间排序
        activities.sort(key=lambda x: x["time"], reverse=True)

        return {"success": True, "data": activities[:limit]}
    finally:
        db.close()


# ========== 用户管理 ==========

class UserStatusUpdate(BaseModel):
    status: str


@router.get("/users")
async def get_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    keyword: Optional[str] = None,
    status: Optional[str] = None,
    authorization: str = Header(None)
):
    """获取用户列表"""
    get_current_admin(authorization)

    db = SessionLocal()
    try:
        query = db.query(User)

        # 搜索过滤
        if keyword:
            query = query.filter(
                User.nickname.contains(keyword) |
                User.openid.contains(keyword)
            )

        # 状态过滤
        if status == "active":
            query = query.filter(User.is_active == True)
        elif status == "inactive":
            query = query.filter(User.is_active == False)

        # 总数
        total = query.count()

        # 分页
        users = query.order_by(User.created_at.desc()).offset(
            (page - 1) * page_size
        ).limit(page_size).all()

        return {
            "success": True,
            "data": [
                {
                    "id": u.id,
                    "username": u.openid[:12] + "...",
                    "nickname": u.nickname or "未设置",
                    "email": u.phone or "-",
                    "avatar": u.avatar,
                    "status": "active" if u.is_active else "inactive",
                    "created_at": u.created_at.strftime("%Y-%m-%d %H:%M")
                }
                for u in users
            ],
            "total": total,
            "page": page,
            "pageSize": page_size
        }
    finally:
        db.close()


@router.get("/users/{user_id}")
async def get_user_detail(user_id: int, authorization: str = Header(None)):
    """获取用户详情"""
    get_current_admin(authorization)

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")

        # 获取用户的对话数
        chat_count = db.query(ChatHistory).filter(
            ChatHistory.user_id == user.id
        ).count()

        return {
            "success": True,
            "data": {
                "id": user.id,
                "openid": user.openid,
                "nickname": user.nickname or "未设置",
                "avatar": user.avatar,
                "phone": user.phone,
                "is_active": user.is_active,
                "chat_count": chat_count,
                "created_at": user.created_at.strftime("%Y-%m-%d %H:%M:%S")
            }
        }
    finally:
        db.close()


@router.put("/users/{user_id}/status")
async def update_user_status(
    user_id: int,
    request: UserStatusUpdate,
    authorization: str = Header(None)
):
    """更新用户状态"""
    get_current_admin(authorization)

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")

        user.is_active = (request.status == "active")
        db.commit()

        return {"success": True, "message": "状态更新成功"}
    finally:
        db.close()


@router.delete("/users/{user_id}")
async def delete_user(user_id: int, authorization: str = Header(None)):
    """删除用户"""
    get_current_admin(authorization)

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")

        db.delete(user)
        db.commit()

        return {"success": True, "message": "删除成功"}
    finally:
        db.close()


# ========== 对话管理 ==========

@router.get("/chats")
async def get_chats(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    user_id: Optional[int] = None,
    authorization: str = Header(None)
):
    """获取对话列表"""
    get_current_admin(authorization)

    db = SessionLocal()
    try:
        query = db.query(ChatHistory).filter(ChatHistory.is_deleted == False)

        if user_id:
            query = query.filter(ChatHistory.user_id == user_id)

        total = query.count()

        chats = query.order_by(ChatHistory.created_at.desc()).offset(
            (page - 1) * page_size
        ).limit(page_size).all()

        result = []
        for chat in chats:
            # 获取用户信息
            user = db.query(User).filter(User.id == chat.user_id).first()

            # 统计消息数
            message_count = db.query(ChatMessage).filter(ChatMessage.chat_id == chat.id).count()

            result.append({
                "id": chat.id,
                "user_id": chat.user_id,
                "username": user.nickname if user and user.nickname else (user.openid[:8] if user else "未知用户"),
                "title": chat.title or "未命名对话",
                "model": chat.model_name or chat.model_id or "GPT-4",
                "message_count": message_count,
                "created_at": chat.created_at.strftime("%Y-%m-%d %H:%M") if chat.created_at else ""
            })

        return {
            "success": True,
            "data": result,
            "total": total,
            "page": page,
            "pageSize": page_size
        }
    finally:
        db.close()


@router.get("/chats/{chat_id}")
async def get_chat_detail(chat_id: int, authorization: str = Header(None)):
    """获取对话详情"""
    get_current_admin(authorization)

    db = SessionLocal()
    try:
        chat = db.query(ChatHistory).filter(
            ChatHistory.id == chat_id,
            ChatHistory.is_deleted == False
        ).first()
        if not chat:
            raise HTTPException(status_code=404, detail="对话不存在")

        user = db.query(User).filter(User.id == chat.user_id).first()

        # 获取消息列表
        messages = db.query(ChatMessage).filter(ChatMessage.chat_id == chat.id).order_by(ChatMessage.created_at).all()
        messages_data = [
            {
                "role": msg.role,
                "content": msg.content,
                "time": msg.time,
                "created_at": msg.created_at.strftime("%Y-%m-%d %H:%M:%S") if msg.created_at else ""
            }
            for msg in messages
        ]

        return {
            "success": True,
            "data": {
                "id": chat.id,
                "user_id": chat.user_id,
                "username": user.nickname if user and user.nickname else (user.openid[:8] if user else "未知用户"),
                "title": chat.title or "未命名对话",
                "model": chat.model_name or chat.model_id or "GPT-4",
                "messages": messages_data,
                "message_count": len(messages),
                "created_at": chat.created_at.strftime("%Y-%m-%d %H:%M:%S") if chat.created_at else ""
            }
        }
    finally:
        db.close()


# ========== 反馈管理 ==========

@router.get("/feedbacks")
async def get_feedbacks(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: Optional[str] = None,
    authorization: str = Header(None)
):
    """获取反馈列表"""
    get_current_admin(authorization)

    db = SessionLocal()
    try:
        query = db.query(Feedback)

        if status:
            query = query.filter(Feedback.status == status)

        total = query.count()

        feedbacks = query.order_by(Feedback.created_at.desc()).offset(
            (page - 1) * page_size
        ).limit(page_size).all()

        result = []
        for fb in feedbacks:
            user = db.query(User).filter(User.id == fb.user_id).first()

            result.append({
                "id": fb.id,
                "user_id": fb.user_id,
                "username": user.nickname if user else "未知用户",
                "type": fb.type,
                "content": fb.content,
                "status": fb.status,
                "reply": fb.reply,
                "created_at": fb.created_at.strftime("%Y-%m-%d %H:%M")
            })

        return {
            "success": True,
            "data": result,
            "total": total,
            "page": page,
            "pageSize": page_size
        }
    finally:
        db.close()


class FeedbackReply(BaseModel):
    reply: str


@router.put("/feedbacks/{feedback_id}/reply")
async def reply_feedback(
    feedback_id: int,
    request: FeedbackReply,
    authorization: str = Header(None)
):
    """回复反馈"""
    get_current_admin(authorization)

    db = SessionLocal()
    try:
        feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
        if not feedback:
            raise HTTPException(status_code=404, detail="反馈不存在")

        feedback.reply = request.reply
        feedback.status = "resolved"
        feedback.updated_at = datetime.utcnow()
        db.commit()

        return {"success": True, "message": "回复成功"}
    finally:
        db.close()


# ========== 提示词管理 ==========

class PromptTemplateCreate(BaseModel):
    template_key: str
    category: str
    sub_key: Optional[str] = None
    template_content: str
    description: Optional[str] = ""
    variables: Optional[list] = None


class PromptTemplateUpdate(BaseModel):
    template_key: Optional[str] = None
    category: Optional[str] = None
    sub_key: Optional[str] = None
    template_content: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[int] = None


@router.get("/prompts")
async def get_prompts(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    authorization: str = Header(None)
):
    """获取提示词模板列表"""
    get_current_admin(authorization)

    db = SessionLocal()
    try:
        total = db.query(PromptTemplate).count()

        prompts = db.query(PromptTemplate).order_by(
            PromptTemplate.created_at.desc()
        ).offset((page - 1) * page_size).limit(page_size).all()

        return {
            "success": True,
            "data": [
                {
                    "id": p.id,
                    "template_key": p.template_key,
                    "category": p.category,
                    "sub_key": p.sub_key or "",
                    "template_content": p.template_content,  # 返回完整内容用于编辑
                    "template_content_preview": p.template_content[:100] + "..." if len(p.template_content) > 100 else p.template_content,
                    "description": p.description or "",
                    "is_active": p.is_active == 1,
                    "version": p.version,
                    "usage_count": p.usage_count or 0,
                    "created_at": p.created_at.strftime("%Y-%m-%d %H:%M") if p.created_at else "",
                    "updated_at": p.updated_at.strftime("%Y-%m-%d %H:%M") if p.updated_at else ""
                }
                for p in prompts
            ],
            "total": total,
            "page": page,
            "pageSize": page_size
        }
    finally:
        db.close()


@router.get("/prompts/{prompt_id}")
async def get_prompt_detail(prompt_id: int, authorization: str = Header(None)):
    """获取提示词模板详情"""
    get_current_admin(authorization)

    db = SessionLocal()
    try:
        p = db.query(PromptTemplate).filter(PromptTemplate.id == prompt_id).first()
        if not p:
            raise HTTPException(status_code=404, detail="模板不存在")

        return {
            "success": True,
            "data": {
                "id": p.id,
                "template_key": p.template_key,
                "category": p.category,
                "sub_key": p.sub_key or "",
                "template_content": p.template_content,
                "description": p.description or "",
                "is_active": p.is_active == 1,
                "version": p.version,
                "usage_count": p.usage_count or 0,
                "variables": p.variables or [],
                "created_at": p.created_at.strftime("%Y-%m-%d %H:%M:%S") if p.created_at else "",
                "updated_at": p.updated_at.strftime("%Y-%m-%d %H:%M:%S") if p.updated_at else ""
            }
        }
    finally:
        db.close()


@router.post("/prompts")
async def create_prompt(
    request: PromptTemplateCreate,
    authorization: str = Header(None)
):
    """创建提示词模板"""
    get_current_admin(authorization)

    db = SessionLocal()
    try:
        prompt = PromptTemplate(
            template_key=request.template_key,
            category=request.category,
            sub_key=request.sub_key,
            template_content=request.template_content,
            description=request.description,
            variables=request.variables or [],
            is_active=1
        )
        db.add(prompt)
        db.commit()
        db.refresh(prompt)

        return {"success": True, "message": "创建成功", "data": {"id": prompt.id}}
    finally:
        db.close()


@router.put("/prompts/{prompt_id}")
async def update_prompt(
    prompt_id: int,
    request: PromptTemplateUpdate,
    authorization: str = Header(None)
):
    """更新提示词模板"""
    get_current_admin(authorization)

    db = SessionLocal()
    try:
        prompt = db.query(PromptTemplate).filter(PromptTemplate.id == prompt_id).first()
        if not prompt:
            raise HTTPException(status_code=404, detail="模板不存在")

        if request.template_key is not None:
            prompt.template_key = request.template_key
        if request.category is not None:
            prompt.category = request.category
        if request.sub_key is not None:
            prompt.sub_key = request.sub_key
        if request.template_content is not None:
            prompt.template_content = request.template_content
        if request.description is not None:
            prompt.description = request.description
        if request.is_active is not None:
            prompt.is_active = 1 if request.is_active else 0

        db.commit()

        return {"success": True, "message": "更新成功"}
    finally:
        db.close()


@router.delete("/prompts/{prompt_id}")
async def delete_prompt(prompt_id: int, authorization: str = Header(None)):
    """删除提示词模板"""
    get_current_admin(authorization)

    db = SessionLocal()
    try:
        prompt = db.query(PromptTemplate).filter(PromptTemplate.id == prompt_id).first()
        if not prompt:
            raise HTTPException(status_code=404, detail="模板不存在")

        db.delete(prompt)
        db.commit()

        return {"success": True, "message": "删除成功"}
    finally:
        db.close()


# ========== 系统设置 ==========

from app.models.system_config import SystemConfig

# LLM模型列表
LLM_MODELS = [
    {"id": "qwen-plus", "name": "通义千问 Plus", "provider": "阿里云"},
    {"id": "qwen-turbo", "name": "通义千问 Turbo", "provider": "阿里云"},
    {"id": "qwen-max", "name": "通义千问 Max", "provider": "阿里云"},
    {"id": "gpt-4", "name": "GPT-4", "provider": "OpenAI"},
    {"id": "gpt-4-turbo", "name": "GPT-4 Turbo", "provider": "OpenAI"},
    {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "provider": "OpenAI"},
    {"id": "claude-3-opus", "name": "Claude 3 Opus", "provider": "Anthropic"},
    {"id": "claude-3-sonnet", "name": "Claude 3 Sonnet", "provider": "Anthropic"},
    {"id": "glm-4", "name": "智谱GLM-4", "provider": "智谱AI"},
    {"id": "glm-3-turbo", "name": "智谱GLM-3 Turbo", "provider": "智谱AI"},
    {"id": "ernie-4.0", "name": "文心一言 4.0", "provider": "百度"},
    {"id": "ernie-3.5", "name": "文心一言 3.5", "provider": "百度"},
    {"id": "moonshot-v1-8k", "name": "Kimi", "provider": "月之暗面"},
    {"id": "deepseek-chat", "name": "DeepSeek Chat", "provider": "DeepSeek"},
]


class SystemConfigUpdate(BaseModel):
    config_key: str
    config_value: str


@router.get("/models")
async def get_llm_models(authorization: str = Header(None)):
    """获取LLM模型列表"""
    get_current_admin(authorization)

    # 获取当前默认模型
    db = SessionLocal()
    try:
        default_model_config = db.query(SystemConfig).filter(
            SystemConfig.config_key == "default_model"
        ).first()
        default_model = default_model_config.config_value if default_model_config else "qwen-plus"
    finally:
        db.close()

    return {
        "success": True,
        "data": LLM_MODELS,
        "default_model": default_model
    }


@router.get("/settings")
async def get_system_settings(authorization: str = Header(None)):
    """获取系统设置"""
    get_current_admin(authorization)

    db = SessionLocal()
    try:
        # 获取所有配置
        configs = db.query(SystemConfig).all()
        config_dict = {c.config_key: c.config_value for c in configs}

        return {
            "success": True,
            "data": {
                "system_name": config_dict.get("system_name", "识界AI"),
                "system_version": "1.1.0",
                "maintenance": config_dict.get("maintenance", "false") == "true",
                "default_model": config_dict.get("default_model", "qwen-plus"),
                "max_context": int(config_dict.get("max_context", "4000")),
                "temperature": float(config_dict.get("temperature", "0.7")),
            }
        }
    finally:
        db.close()


@router.put("/settings")
async def update_system_settings(
    request: SystemConfigUpdate,
    authorization: str = Header(None)
):
    """更新系统设置"""
    get_current_admin(authorization)

    db = SessionLocal()
    try:
        config = db.query(SystemConfig).filter(
            SystemConfig.config_key == request.config_key
        ).first()

        if config:
            config.config_value = request.config_value
        else:
            config = SystemConfig(
                config_key=request.config_key,
                config_value=request.config_value
            )
            db.add(config)

        db.commit()

        return {"success": True, "message": "设置已保存"}
    finally:
        db.close()


@router.put("/settings/batch")
async def batch_update_settings(
    settings: dict,
    authorization: str = Header(None)
):
    """批量更新系统设置"""
    get_current_admin(authorization)

    db = SessionLocal()
    try:
        for key, value in settings.items():
            config = db.query(SystemConfig).filter(
                SystemConfig.config_key == key
            ).first()

            if config:
                config.config_value = str(value)
            else:
                config = SystemConfig(
                    config_key=key,
                    config_value=str(value)
                )
                db.add(config)

        db.commit()

        return {"success": True, "message": "设置已保存"}
    finally:
        db.close()


# ========== 消息通知 ==========

@router.get("/notifications")
async def get_notifications(
    limit: int = Query(5, ge=1, le=20),
    authorization: str = Header(None)
):
    """获取真实消息通知"""
    get_current_admin(authorization)

    db = SessionLocal()
    try:
        notifications = []

        # 1. 新用户注册通知
        new_users = db.query(User).order_by(User.created_at.desc()).limit(3).all()
        for user in new_users:
            notifications.append({
                "type": "user",
                "content": f"新用户注册: {user.nickname or user.openid[:8]}",
                "time": user.created_at.strftime("%Y-%m-%d %H:%M") if user.created_at else "",
                "color": "blue"
            })

        # 2. 待处理反馈通知
        pending_feedbacks = db.query(Feedback).filter(
            Feedback.status == "pending"
        ).count()
        if pending_feedbacks > 0:
            notifications.append({
                "type": "feedback",
                "content": f"您有 {pending_feedbacks} 条待处理的用户反馈",
                "time": "刚刚",
                "color": "orange"
            })

        # 3. 今日对话统计
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_chats = db.query(ChatHistory).filter(
            ChatHistory.created_at >= today_start
        ).count()
        notifications.append({
            "type": "stats",
            "content": f"今日新增对话: {today_chats} 条",
            "time": "今日",
            "color": "green"
        })

        # 按时间排序，限制数量
        notifications = notifications[:limit]

        return {
            "success": True,
            "data": notifications,
            "total": len(notifications)
        }
    finally:
        db.close()
