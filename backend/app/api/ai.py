"""
AI对话API路由 - SSE流式输出
使用LiteLLM统一调用，无需数据库模型配置
"""
import json
import asyncio
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Literal
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.auth import get_current_user
from app.models.user import User
from app.services.ai_service import stream_chat, chat_completion
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/ai", tags=["AI对话"])

# 系统提示词
SYSTEM_PROMPT = "你是识界AI助手，一个专业、友好、helpful的AI助手。请用中文回答用户的问题，回答要简洁明了、有条理。"


class ChatMessageItem(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    message: str
    history: List[ChatMessageItem] = []
    model_id: Optional[str] = None
    images: Optional[List[str]] = None  # 图片URL列表


class TextGenRequest(BaseModel):
    prompt: str
    model_id: Optional[str] = None
    max_tokens: int = 1500


class TranslateRequest(BaseModel):
    text: str
    source_lang: str = "auto"
    target_lang: str = "en"
    model_id: Optional[str] = None


def _get_limiter(request: Request) -> Limiter:
    """获取全局 limiter 实例"""
    return request.app.state.limiter


@router.post("/chat/stream")
async def chat_stream(
    request: Request,
    req: ChatRequest,
    user: User = Depends(get_current_user),
):
    """AI对话 - SSE流式输出（支持图片）"""
    if not req.message.strip() and not req.images:
        raise HTTPException(status_code=400, detail="消息内容或图片不能为空")

    # 构建消息列表
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in req.history:
        messages.append({"role": msg.role, "content": msg.content})
    
    # 构建用户消息（支持图片）
    user_message = {"role": "user", "content": req.message}
    if req.images and len(req.images) > 0:
        # 多模态格式：content 为数组
        content = [{"type": "text", "text": req.message or "请描述这张图片"}]
        for img_url in req.images:
            content.append({
                "type": "image_url",
                "image_url": {"url": img_url}
            })
        user_message["content"] = content
    
    messages.append(user_message)

    logger.info("chat_stream_start", user_id=user.id, model=req.model_id, 
                message_length=len(req.message), has_images=bool(req.images))

    async def event_generator():
        try:
            async for chunk in stream_chat(messages, model=req.model_id):
                data = json.dumps({"content": chunk}, ensure_ascii=False)
                yield f"data: {data}\n\n"
                # 关键：强制 flush，确保数据立即发送到客户端
                await asyncio.sleep(0)
            yield "data: [DONE]\n\n"
        except Exception as e:
            logger.error("chat_stream_error", user_id=user.id, error=str(e))
            error_data = json.dumps({"error": "AI服务暂时不可用，请稍后重试"}, ensure_ascii=False)
            yield f"data: {error_data}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/chat")
async def chat(
    request: Request,
    req: ChatRequest,
    user: User = Depends(get_current_user),
):
    """AI对话 - 非流式"""
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="消息内容不能为空")

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in req.history:
        messages.append({"role": msg.role, "content": msg.content})
    messages.append({"role": "user", "content": req.message})

    full_text = await chat_completion(messages, model=req.model_id)
    full_text = full_text or ""

    logger.info("chat_complete", user_id=user.id, model=req.model_id, response_length=len(full_text))
    return {"code": 0, "data": full_text}


@router.post("/text-gen")
async def text_generate(
    request: Request,
    req: TextGenRequest,
    user: User = Depends(get_current_user),
):
    """文本生成"""
    messages = [{"role": "user", "content": req.prompt}]
    full_text = await chat_completion(messages, model=req.model_id, max_tokens=req.max_tokens)
    full_text = full_text or ""

    return {"code": 0, "data": full_text}


@router.post("/translate")
async def translate(
    request: Request,
    req: TranslateRequest,
    user: User = Depends(get_current_user),
):
    """智能翻译"""
    lang_map = {
        "zh": "中文", "en": "英文", "ja": "日文", "ko": "韩文",
        "fr": "法文", "de": "德文", "es": "西班牙文", "ru": "俄文",
        "auto": "自动检测"
    }
    source_name = lang_map.get(req.source_lang, req.source_lang)
    target_name = lang_map.get(req.target_lang, req.target_lang)

    messages = [
        {"role": "system", "content": f"你是一个专业翻译。请将以下文本从{source_name}翻译为{target_name}。只输出翻译结果，不要添加解释。"},
        {"role": "user", "content": req.text}
    ]

    full_text = await chat_completion(messages, model=req.model_id)
    full_text = full_text or ""

    return {"code": 0, "data": full_text}
