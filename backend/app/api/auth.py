import httpx
import logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.config import get_settings
from app.database import get_db
from app.models.user import User
from app.auth import create_token, get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["认证"])
settings = get_settings()


class WxLoginRequest(BaseModel):
    code: str
    nickname: str = ""
    avatar: str = ""


class WxLoginResponse(BaseModel):
    token: str
    user_id: int
    nickname: str
    avatar: str


class UserInfoResponse(BaseModel):
    id: int
    nickname: str
    avatar: str
    openid: str = ""


class UpdateUserRequest(BaseModel):
    nickname: str = ""
    avatar: str = ""


@router.post("/wx-login", response_model=WxLoginResponse)
async def wx_login(req: WxLoginRequest, db: Session = Depends(get_db)):
    """微信小程序登录 - 后端代理code2session"""
    # 1. 调用微信API换取openid
    wx_url = "https://api.weixin.qq.com/sns/jscode2session"
    params = {
        "appid": settings.WX_APPID,
        "secret": settings.WX_APPSECRET,
        "js_code": req.code,
        "grant_type": "authorization_code"
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            wx_res = await client.get(wx_url, params=params)
            wx_data = wx_res.json()
        except httpx.RequestError as e:
            logger.error(f"微信API请求失败: {e}")
            raise HTTPException(status_code=500, detail="微信服务连接失败")

    if "errcode" in wx_data and wx_data["errcode"] != 0:
        logger.error(f"微信登录失败: {wx_data}")
        raise HTTPException(status_code=400, detail=f"微信登录失败: {wx_data.get('errmsg', '未知错误')}")

    openid = wx_data.get("openid")
    session_key = wx_data.get("session_key")
    union_id = wx_data.get("unionid")

    if not openid:
        raise HTTPException(status_code=400, detail="获取openid失败")

    # 2. 查找或创建用户
    user = db.query(User).filter(User.openid == openid).first()
    if not user:
        user = User(
            openid=openid,
            union_id=union_id,
            session_key=session_key,
            nickname=req.nickname or "微信用户",
            avatar=req.avatar or ""
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        # 更新session_key和用户信息
        user.session_key = session_key
        if union_id:
            user.union_id = union_id
        if req.nickname:
            user.nickname = req.nickname
        if req.avatar:
            user.avatar = req.avatar
        db.commit()

    # 3. 生成token
    token = create_token(user.id)
    user.token = token
    db.commit()

    return WxLoginResponse(
        token=token,
        user_id=user.id,
        nickname=user.nickname,
        avatar=user.avatar
    )


@router.get("/me", response_model=UserInfoResponse)
async def get_my_info(user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return UserInfoResponse(
        id=user.id,
        nickname=user.nickname,
        avatar=user.avatar,
        openid=""  # 不返回openid
    )


@router.put("/me")
async def update_my_info(
    req: UpdateUserRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新当前用户信息"""
    if req.nickname:
        user.nickname = req.nickname
    if req.avatar:
        user.avatar = req.avatar
    db.commit()
    return {"code": 0, "message": "更新成功"}
