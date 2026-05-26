"""
结构化日志配置 - 基于structlog
"""
import logging
import sys
import structlog
from app.config import get_settings

settings = get_settings()


def setup_logging():
    """配置结构化日志"""
    # 根据环境选择日志格式
    if settings.DEBUG:
        # 开发环境：彩色控制台输出
        processors = [
            structlog.contextvars.merge_contextvars,
            structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
            structlog.dev.ConsoleRenderer(colors=True)
        ]
    else:
        # 生产环境：JSON格式
        processors = [
            structlog.contextvars.merge_contextvars,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer()
        ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        cache_logger_on_first_use=True,
    )

    # 配置标准库日志
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """获取logger实例"""
    return structlog.get_logger(name)
