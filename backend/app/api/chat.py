from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.chat_history import ChatHistory, ChatMessage
from app.auth import get_current_user

router = APIRouter(prefix="/chat", tags=["对话历史"])


class MessageItem(BaseModel):
    role: str
    content: str
    time: str = ""


class SaveChatRequest(BaseModel):
    messages: List[MessageItem]
    model_id: str = ""
    model_name: str = ""


class ChatListItem(BaseModel):
    id: int
    title: str
    preview: str
    model_id: Optional[str] = None
    model_name: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class ChatDetailResponse(BaseModel):
    id: int
    title: str
    preview: str
    model_id: Optional[str] = None
    model_name: Optional[str] = None
    messages: List[MessageItem]
    created_at: Optional[str] = None


@router.post("/save")
async def save_chat(
    req: SaveChatRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """保存或更新对话（根据chat_id）"""
    # 生成标题和预览
    title = "新对话"
    preview = ""
    for msg in req.messages:
        if msg.role == "user" and title == "新对话":
            title = msg.content[:20] + ("..." if len(msg.content) > 20 else "")
        if msg.role == "assistant":
            preview = msg.content[:50] + ("..." if len(msg.content) > 50 else "")

    # 查找是否有未删除的对话可以更新（简化逻辑：每次save都新建）
    chat = ChatHistory(
        user_id=user.id,
        title=title,
        preview=preview,
        model_id=req.model_id,
        model_name=req.model_name,
    )
    db.add(chat)
    db.flush()  # 获取chat.id

    for msg in req.messages:
        chat_msg = ChatMessage(
            chat_id=chat.id,
            role=msg.role,
            content=msg.content,
            time=msg.time,
        )
        db.add(chat_msg)

    db.commit()
    db.refresh(chat)

    return {"code": 0, "id": chat.id, "message": "保存成功"}


@router.put("/update/{chat_id}")
async def update_chat(
    chat_id: int,
    req: SaveChatRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新已有对话"""
    chat = db.query(ChatHistory).filter(
        ChatHistory.id == chat_id,
        ChatHistory.user_id == user.id,
        ChatHistory.is_deleted == False
    ).first()

    if not chat:
        raise HTTPException(status_code=404, detail="对话不存在")

    # 更新标题和预览
    title = chat.title
    preview = ""
    for msg in req.messages:
        if msg.role == "user" and title == "新对话":
            title = msg.content[:20] + ("..." if len(msg.content) > 20 else "")
        if msg.role == "assistant":
            preview = msg.content[:50] + ("..." if len(msg.content) > 50 else "")

    chat.title = title
    chat.preview = preview
    chat.model_id = req.model_id
    chat.model_name = req.model_name

    # 删除旧消息，重新插入
    db.query(ChatMessage).filter(ChatMessage.chat_id == chat_id).delete()

    for msg in req.messages:
        chat_msg = ChatMessage(
            chat_id=chat.id,
            role=msg.role,
            content=msg.content,
            time=msg.time,
        )
        db.add(chat_msg)

    db.commit()

    return {"code": 0, "id": chat.id, "message": "更新成功"}


@router.get("/list")
async def get_chat_list(
    page: int = 1,
    page_size: int = 20,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取对话历史列表"""
    query = db.query(ChatHistory).filter(
        ChatHistory.user_id == user.id,
        ChatHistory.is_deleted == False
    ).order_by(ChatHistory.updated_at.desc())

    total = query.count()
    chats = query.offset((page - 1) * page_size).limit(page_size).all()

    items = []
    for c in chats:
        items.append(ChatListItem(
            id=c.id,
            title=c.title,
            preview=c.preview,
            model_id=c.model_id,
            model_name=c.model_name,
            created_at=c.created_at.isoformat() if c.created_at else None,
            updated_at=c.updated_at.isoformat() if c.updated_at else None,
        ))

    return {
        "code": 0,
        "data": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/detail/{chat_id}")
async def get_chat_detail(
    chat_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取对话详情"""
    chat = db.query(ChatHistory).filter(
        ChatHistory.id == chat_id,
        ChatHistory.user_id == user.id,
        ChatHistory.is_deleted == False
    ).first()

    if not chat:
        raise HTTPException(status_code=404, detail="对话不存在")

    messages = db.query(ChatMessage).filter(
        ChatMessage.chat_id == chat_id
    ).order_by(ChatMessage.created_at.asc()).all()

    msg_list = [
        MessageItem(role=m.role, content=m.content, time=m.time or "")
        for m in messages
    ]

    return {
        "code": 0,
        "data": ChatDetailResponse(
            id=chat.id,
            title=chat.title,
            preview=chat.preview,
            model_id=chat.model_id,
            model_name=chat.model_name,
            messages=msg_list,
            created_at=chat.created_at.isoformat() if chat.created_at else None,
        )
    }


@router.delete("/delete/{chat_id}")
async def delete_chat(
    chat_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """软删除对话"""
    chat = db.query(ChatHistory).filter(
        ChatHistory.id == chat_id,
        ChatHistory.user_id == user.id,
        ChatHistory.is_deleted == False
    ).first()

    if not chat:
        raise HTTPException(status_code=404, detail="对话不存在")

    chat.is_deleted = True
    db.commit()

    return {"code": 0, "message": "删除成功"}


@router.delete("/clear")
async def clear_all_chats(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """清空所有对话历史"""
    count = db.query(ChatHistory).filter(
        ChatHistory.user_id == user.id,
        ChatHistory.is_deleted == False
    ).update({"is_deleted": True})

    db.commit()

    return {"code": 0, "message": "清空成功", "count": count}
