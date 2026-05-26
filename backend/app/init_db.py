"""
数据库初始化脚本 - 创建必要的数据库表
用法: python -m app.init_db
"""
import logging
from app.database import SessionLocal, engine, Base
from app.models import User, ChatHistory, ChatMessage
from app.config import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_db():
    """初始化数据库"""
    Base.metadata.create_all(bind=engine)
    logger.info("数据库表创建完成 (users, chat_histories, chat_messages)")
    logger.info("AI模型配置使用 LiteLLM + 环境变量，无需数据库表")


if __name__ == "__main__":
    init_db()
