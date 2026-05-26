"""
管理员认证模块
"""
import hashlib
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import Optional
from app.database import SessionLocal
from app.models.admin import Admin, AdminSession

router = APIRouter(prefix="/auth", tags=["管理员认证"])


def hash_password(password: str) -> str:
    """密码哈希"""
    return hashlib.sha256(password.encode()).hexdigest()


def create_token(admin_id: int) -> str:
    """创建会话token"""
    import secrets
    token = secrets.token_urlsafe(32)
    expire_at = datetime.utcnow() + timedelta(days=7)

    db = SessionLocal()
    try:
        # 创建会话记录
        session = AdminSession(
            admin_id=admin_id,
            token=token,
            expire_at=expire_at
        )
        db.add(session)
        db.commit()
    finally:
        db.close()

    return token


def verify_token(token: str) -> Optional[int]:
    """验证token并返回admin_id"""
    db = SessionLocal()
    try:
        session = db.query(AdminSession).filter(
            AdminSession.token == token,
            AdminSession.expire_at > datetime.utcnow()
        ).first()

        if session:
            return session.admin_id
        return None
    finally:
        db.close()


def get_current_admin(authorization: str = Header(None)) -> dict:
    """获取当前管理员"""
    if not authorization:
        raise HTTPException(status_code=401, detail="未登录")

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="无效的认证格式")

    token = authorization[7:]
    admin_id = verify_token(token)

    if not admin_id:
        raise HTTPException(status_code=401, detail="登录已过期")

    db = SessionLocal()
    try:
        admin = db.query(Admin).filter(Admin.id == admin_id).first()
        if not admin or not admin.is_active:
            raise HTTPException(status_code=401, detail="管理员不存在或已禁用")

        return {
            "id": admin.id,
            "username": admin.username,
            "nickname": admin.nickname,
            "role": admin.role
        }
    finally:
        db.close()


# 请求/响应模型
class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    success: bool
    token: Optional[str] = None
    user: Optional[dict] = None
    message: Optional[str] = None


class UserInfoResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
    message: Optional[str] = None


@router.post("/admin/login", response_model=LoginResponse)
async def admin_login(request: LoginRequest):
    """管理员登录"""
    db = SessionLocal()
    try:
        admin = db.query(Admin).filter(
            Admin.username == request.username,
            Admin.is_active == True
        ).first()

        if not admin:
            return LoginResponse(success=False, message="用户名或密码错误")

        # 验证密码
        if admin.password_hash != hash_password(request.password):
            return LoginResponse(success=False, message="用户名或密码错误")

        # 更新最后登录时间
        admin.last_login = datetime.utcnow()
        db.commit()

        # 创建token
        token = create_token(admin.id)

        return LoginResponse(
            success=True,
            token=token,
            user={
                "id": admin.id,
                "username": admin.username,
                "nickname": admin.nickname,
                "role": admin.role
            }
        )
    finally:
        db.close()


@router.get("/admin/info", response_model=UserInfoResponse)
async def get_admin_info(authorization: str = Header(None)):
    """获取管理员信息"""
    try:
        admin = get_current_admin(authorization)
        return UserInfoResponse(success=True, data=admin)
    except HTTPException as e:
        return UserInfoResponse(success=False, message=e.detail)


@router.post("/admin/logout")
async def admin_logout(authorization: str = Header(None)):
    """管理员登出"""
    if not authorization or not authorization.startswith("Bearer "):
        return {"success": True, "message": "已登出"}

    token = authorization[7:]

    db = SessionLocal()
    try:
        db.query(AdminSession).filter(AdminSession.token == token).delete()
        db.commit()
    finally:
        db.close()

    return {"success": True, "message": "已登出"}


def init_default_admin():
    """初始化默认管理员"""
    db = SessionLocal()
    try:
        # 检查是否已存在
        existing = db.query(Admin).filter(Admin.username == "admin").first()
        if not existing:
            admin = Admin(
                username="admin",
                password_hash=hash_password("admin123"),
                nickname="超级管理员",
                role="super_admin"
            )
            db.add(admin)
            db.commit()
            print("✅ 默认管理员已创建: admin / admin123")
    finally:
        db.close()
