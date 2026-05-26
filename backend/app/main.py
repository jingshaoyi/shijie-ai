"""
识界AI FastAPI后端 - 生产级配置
"""
import sys
import os
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.api import auth, ai, models, chat, upload, feedback, prompts
from app.api import admin_auth, admin_data
from app.database import engine, Base
from app.config import get_settings
from app.core.logging import setup_logging, get_logger
from app.api.admin_auth import init_default_admin

# 导入所有模型以确保表创建
from app.models import User, ChatHistory, ChatMessage, Feedback, PromptTemplate, Admin, AdminSession, SystemConfig

# uvloop 仅在 Linux/macOS 上可用，Windows 跳过
if sys.platform != "win32":
    import uvloop
    uvloop.install()

# 初始化
settings = get_settings()
setup_logging()
logger = get_logger(__name__)

# 速率限制器（全局唯一实例）
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动
    await asyncio.to_thread(Base.metadata.create_all, bind=engine)
    logger.info("app_startup", message="数据库表创建/检查完成")

    # 初始化默认管理员
    init_default_admin()

    yield
    # 关闭
    logger.info("app_shutdown", message="应用关闭")


# 创建应用
app = FastAPI(
    title="识界AI API",
    description="识界AI微信小程序后端服务 - 生产级FastAPI模板",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# 速率限制中间件
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 速率限制异常处理
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "请求过于频繁，请稍后再试"},
    )


# 注册路由
app.include_router(auth.router, prefix="/api")
app.include_router(ai.router, prefix="/api")
app.include_router(models.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(upload.router, prefix="/api")
app.include_router(feedback.router, prefix="/api")
app.include_router(prompts.router, prefix="/api")

# 管理员路由
app.include_router(admin_auth.router, prefix="/api")
app.include_router(admin_data.router, prefix="/api")

# 静态文件服务 - 上传的图片
# 确保上传目录存在
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")


@app.get("/health")
@limiter.limit("100/minute")
async def health_check(request: Request):
    """健康检查"""
    return {
        "status": "ok",
        "service": "识界AI",
        "env": settings.APP_ENV
    }


@app.get("/")
@limiter.limit("100/minute")
async def root(request: Request):
    """根路径"""
    return {
        "message": "识界AI API 服务运行中",
        "docs": "/docs" if settings.DEBUG else "disabled",
        "health": "/health"
    }
