"""
配置管理 - 从.env文件加载配置
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置"""

    # 应用
    APP_ENV: str = "development"
    DEBUG: bool = True

    # 服务器
    HOST: str = "0.0.0.0"
    PORT: int = 9090

    # 数据库
    DB_PATH: str = "data/shijie_ai.db"
    
    @property
    def DATABASE_URL(self) -> str:
        """生成SQLAlchemy数据库URL"""
        return f"sqlite:///{self.DB_PATH}"

    # JWT
    JWT_SECRET: str = "your-secret-key-change-in-production"
    JWT_EXPIRE_DAYS: int = 7

    # 微信小程序
    WX_APPID: str = ""
    WX_APPSECRET: str = ""

    # 默认AI模型 (LiteLLM格式)
    DEFAULT_MODEL: str = "dashscope/qwen-plus"

    # 速率限制
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60

    # LiteLLM API Keys
    DASHSCOPE_API_KEY: str = ""      # 阿里云通义千问 (推荐)
    ALIBABA_API_KEY: str = ""        # 阿里云通义千问 (兼容旧版)
    DEEPSEEK_API_KEY: str = ""       # DeepSeek
    OPENAI_API_KEY: str = ""         # OpenAI
    ANTHROPIC_API_KEY: str = ""      # Anthropic Claude
    GEMINI_API_KEY: str = ""         # Google Gemini
    ZHIPU_API_KEY: str = ""          # 智谱AI
    MOONSHOT_API_KEY: str = ""       # Moonshot

    # 图片上传配置
    UPLOAD_DIR: str = "uploads"      # 上传文件存储目录
    MAX_IMAGE_SIZE: int = 10 * 1024 * 1024  # 最大图片大小 10MB
    ALLOWED_IMAGE_TYPES: list = ["image/jpeg", "image/png", "image/webp", "image/gif"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # 允许.env中有未定义的字段


@lru_cache()
def get_settings() -> Settings:
    """获取配置（缓存）"""
    return Settings()
