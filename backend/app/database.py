from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import get_settings

settings = get_settings()

# SQLite配置：check_same_thread=False 允许多线程访问
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """获取数据库会话（依赖注入用）"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
