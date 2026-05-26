"""
文件上传路由 - 处理图片上传
"""
import os
import uuid
import shutil
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from typing import Optional

from app.auth import get_current_user
from app.models.user import User
from app.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/upload", tags=["文件上传"])
settings = get_settings()

# 确保上传目录存在
UPLOAD_DIR = settings.UPLOAD_DIR
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 按日期创建子目录
def get_upload_path() -> str:
    """获取上传目录路径（按日期组织）"""
    today = datetime.now().strftime("%Y%m%d")
    path = os.path.join(UPLOAD_DIR, today)
    os.makedirs(path, exist_ok=True)
    return path

def get_file_extension(filename: str) -> str:
    """获取文件扩展名"""
    return os.path.splitext(filename)[1].lower()

def generate_filename(original_filename: str) -> str:
    """生成唯一文件名"""
    ext = get_file_extension(original_filename)
    unique_id = uuid.uuid4().hex[:16]
    timestamp = datetime.now().strftime("%H%M%S")
    return f"{timestamp}_{unique_id}{ext}"

@router.post("/image")
async def upload_image(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user)
):
    """
    上传图片
    - 支持格式: jpg, png, webp, gif
    - 最大大小: 10MB
    - 返回图片访问URL
    """
    # 检查文件类型
    content_type = file.content_type or ""
    if content_type not in settings.ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400, 
            detail=f"不支持的图片格式: {content_type}。支持的格式: jpeg, png, webp, gif"
        )
    
    # 检查文件大小（通过读取内容）
    contents = await file.read()
    if len(contents) > settings.MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=400, 
            detail=f"图片大小超过限制: {settings.MAX_IMAGE_SIZE / 1024 / 1024}MB"
        )
    
    # 生成文件名和路径
    upload_path = get_upload_path()
    filename = generate_filename(file.filename or "image.jpg")
    file_path = os.path.join(upload_path, filename)
    
    try:
        # 保存文件
        with open(file_path, "wb") as f:
            f.write(contents)
        
        # 构建访问URL
        # 格式: /uploads/20250125/143052_abc123.jpg
        relative_path = os.path.relpath(file_path, ".").replace("\\", "/")
        # 移除 uploads/ 前缀，因为静态文件路由已经配置了前缀
        url_path = relative_path.replace("uploads/", "")
        
        logger.info("image_uploaded", 
                   user_id=user.id, 
                   filename=filename, 
                   size=len(contents),
                   path=relative_path)
        
        return {
            "code": 0,
            "url": f"/uploads/{url_path}",
            "filename": filename,
            "size": len(contents)
        }
        
    except Exception as e:
        logger.error("image_upload_failed", user_id=user.id, error=str(e))
        raise HTTPException(status_code=500, detail=f"图片上传失败: {str(e)}")

@router.get("/images/{date}/{filename}")
async def get_image(date: str, filename: str):
    """
    获取上传的图片
    - date: 日期目录 (如 20250125)
    - filename: 文件名
    """
    file_path = os.path.join(UPLOAD_DIR, date, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="图片不存在")
    
    # 根据文件扩展名确定 media_type
    ext = get_file_extension(filename)
    media_type_map = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
        ".gif": "image/gif"
    }
    media_type = media_type_map.get(ext, "image/jpeg")
    
    return FileResponse(file_path, media_type=media_type)

@router.delete("/image/{date}/{filename}")
async def delete_image(
    date: str, 
    filename: str,
    user: User = Depends(get_current_user)
):
    """
    删除上传的图片
    """
    file_path = os.path.join(UPLOAD_DIR, date, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="图片不存在")
    
    try:
        os.remove(file_path)
        logger.info("image_deleted", user_id=user.id, filename=filename)
        return {"code": 0, "message": "删除成功"}
    except Exception as e:
        logger.error("image_delete_failed", user_id=user.id, error=str(e))
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")
