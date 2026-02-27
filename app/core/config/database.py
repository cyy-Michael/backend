"""
数据库配置管理模块
提供数据库连接和迁移相关的配置
"""

from typing import Dict, Any
from pydantic_settings import BaseSettings
from functools import lru_cache


class DatabaseSettings(BaseSettings):
    """数据库配置设置"""
    # MongoDB配置
    # 默认使用本地开发环境数据库
    # 生产环境可以通过环境变量 MONGO_URI 覆盖，格式为：mongodb://user:pass@host:port/dbname
    MONGO_URI: str = "mongodb+srv://0227_wx201383_db_user:hdkkdbdikwksbffkfjdwl645s87jwksadasfsafasf@cluster0.roe7na.mongodb.net/"
    DB_NAME: str = "teacher_query"
    
    # Alembic迁移配置
    ALEMBIC_CONFIG_PATH: str = "alembic.ini"
    ENABLE_AUTO_MIGRATION: bool = True
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"  # 新增：指定.env文件编码，避免中文乱码
        case_sensitive = True
        extra = "ignore"  # 忽略额外的环境变量


@lru_cache()
def get_database_settings() -> DatabaseSettings:
    """获取数据库配置（单例模式）"""
    try:
        return DatabaseSettings()
    except Exception as e:
        raise RuntimeError(f"加载数据库配置失败，请检查.env文件: {str(e)}") from e


def get_mongo_connection_params() -> Dict[str, Any]:
    """获取MongoDB连接参数"""
    settings = get_database_settings()
    return {
        "mongo_uri": settings.MONGO_URI,
        "db_name": settings.DB_NAME
    }


# 核心修复：实例化database_settings对象，供外部导入使用
database_settings = get_database_settings()