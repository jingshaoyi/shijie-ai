from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.config import get_settings
from app.database import get_db
from app.models.user import User

settings = get_settings()
security = HTTPBearer(auto_error=False)


def create_token(user_id: int) -> str:
    """生成JWT token"""
    expire = datetime.now(timezone.utc) + timedelta(days=settings.JWT_EXPIRE_DAYS)
    payload = {
        "user_id": user_id,
        "exp": expire,
        "iat": datetime.now(timezone.utc)
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")


def verify_token(token: str) -> Optional[int]:
    """验证JWT token，返回user_id"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        user_id = payload.get("user_id")
        if user_id is None:
            return None
        return user_id
    except jwt.PyJWTError:
        return None


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """获取当前登录用户（依赖注入）"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未登录或token已过期",
            headers={"WWW-Authenticate": "Bearer"}
        )

    token = credentials.credentials
    user_id = verify_token(token)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="token无效或已过期",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user = db.query(User).filter(User.id == user_id, User.is_active.is_(True)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在"
        )

    return user
