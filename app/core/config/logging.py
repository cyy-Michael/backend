"""
日志配置模块
管理应用的日志配置
"""

import os
from typing import Optional, Dict, Any, List
from pydantic_settings import BaseSettings
from functools import lru_cache


class LoggingSettings(BaseSettings):
    """日志配置设置"""
    # 日志级别
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
    DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"
    
    # 日志文件配置
    LOG_DIR: str = os.getenv("LOG_DIR", "logs")
    LOG_FILE: Optional[str] = os.getenv("LOG_FILE")
    ERROR_LOG_FILE: str = os.path.join(LOG_DIR, "error.log")
    API_LOG_FILE: str = os.path.join(LOG_DIR, "api.log")
    DB_LOG_FILE: str = os.path.join(LOG_DIR, "database.log")
    
    # 日志轮转配置
    LOG_ROTATION: str = "size"  # size, time
    LOG_MAX_BYTES: int = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT: int = 5
    LOG_ROTATION_WHEN: str = "D"  # S, M, H, D, W0-W6
    LOG_ROTATION_INTERVAL: int = 1
    
    # 控制台日志配置
    CONSOLE_LOG_ENABLED: bool = True
    CONSOLE_LOG_COLORIZED: bool = True
    
    # 文件日志配置
    FILE_LOG_ENABLED: bool = True
    
    # 第三方库日志配置
    THIRD_PARTY_LOG_LEVEL: str = "WARNING"
    
    # 日志处理器配置
    LOG_HANDLERS: List[str] = ["console", "file"]
    
    # 日志过滤器配置
    SENSITIVE_KEYWORDS: List[str] = [
        "password", "token", "secret", "key", "credential",
        "password_hash", "api_key", "jwt", "auth"
    ]
    
    # 性能日志配置
    PERFORMANCE_LOG_ENABLED: bool = False
    PERFORMANCE_LOG_THRESHOLD: float = 1.0  # 秒
    
    # 访问日志配置
    ACCESS_LOG_ENABLED: bool = True
    ACCESS_LOG_FORMAT: str = (
        "%(asctime)s - %(client_ip)s - %(method)s %(path)s "
        "%(status_code)s - %(response_time).2fms - %(user_agent)s"
    )
    
    # 异常日志配置
    EXCEPTION_LOG_ENABLED: bool = True
    EXCEPTION_LOG_VERBOSE: bool = True
    
    @property
    def log_level_int(self) -> int:
        """获取日志级别对应的整数值"""
        import logging
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "WARN": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
        return level_map.get(self.LOG_LEVEL, logging.INFO)
    
    @property
    def third_party_log_level_int(self) -> int:
        """获取第三方库日志级别对应的整数值"""
        import logging
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "WARN": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
        return level_map.get(self.THIRD_PARTY_LOG_LEVEL, logging.WARNING)
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


@lru_cache()
def get_logging_settings() -> LoggingSettings:
    """获取日志配置（单例模式）"""
    return LoggingSettings()


# 创建全局日志配置实例
logging_settings = get_logging_settings()


def setup_logging() -> None:
    """设置全局日志配置"""
    import logging
    import sys
    from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
    
    settings = get_logging_settings()
    
    # 确保日志目录存在
    if not os.path.exists(settings.LOG_DIR):
        os.makedirs(settings.LOG_DIR)
    
    # 获取根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.log_level_int)
    root_logger.handlers.clear()
    
    # 创建格式化器
    formatter = logging.Formatter(settings.LOG_FORMAT, settings.DATE_FORMAT)
    
    # 添加控制台处理器
    if settings.CONSOLE_LOG_ENABLED:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(settings.log_level_int)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # 添加文件处理器
    if settings.FILE_LOG_ENABLED and settings.LOG_FILE:
        if settings.LOG_ROTATION == "size":
            file_handler = RotatingFileHandler(
                settings.LOG_FILE,
                maxBytes=settings.LOG_MAX_BYTES,
                backupCount=settings.LOG_BACKUP_COUNT,
                encoding='utf-8'
            )
        else:
            file_handler = TimedRotatingFileHandler(
                settings.LOG_FILE,
                when=settings.LOG_ROTATION_WHEN,
                interval=settings.LOG_ROTATION_INTERVAL,
                backupCount=settings.LOG_BACKUP_COUNT,
                encoding='utf-8'
            )
        
        file_handler.setLevel(settings.log_level_int)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # 配置第三方库日志级别
    third_party_loggers = [
        "uvicorn", "uvicorn.error", "uvicorn.access",
        "fastapi", "sqlalchemy", "pymongo",
        "httpx", "requests", "urllib3"
    ]
    
    for logger_name in third_party_loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(settings.third_party_log_level_int)


def get_log_config() -> Dict[str, Any]:
    """获取Uvicorn日志配置"""
    settings = get_logging_settings()
    
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "()": "uvicorn.logging.DefaultFormatter",
                "fmt": settings.LOG_FORMAT,
                "datefmt": settings.DATE_FORMAT,
            },
            "access": {
                "()": "uvicorn.logging.AccessFormatter",
                "fmt": settings.ACCESS_LOG_FORMAT,
                "datefmt": settings.DATE_FORMAT,
            },
        },
        "handlers": {
            "default": {
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stderr",
            },
            "access": {
                "formatter": "access",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "uvicorn": {"handlers": ["default"], "level": settings.LOG_LEVEL},
            "uvicorn.error": {"level": settings.LOG_LEVEL},
            "uvicorn.access": {
                "handlers": ["access"],
                "level": settings.LOG_LEVEL,
                "propagate": False,
            },
        },
    }