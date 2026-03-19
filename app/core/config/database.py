"""
数据库配置管理模块
提供数据库连接和迁移相关的配置
"""

from typing import Dict, Any
from pydantic_settings import BaseSettings
from functools import lru_cache


class DatabaseSettings(BaseSettings):
<<<<<<< Updated upstream
    """数据库配置设置"""
    # MongoDB配置
    MONGO_URI: str
    DB_NAME: str = "teacher_query"
    
=======
    """数据库配置设置

    说明：
    - 为了避免系统环境变量中已有的 `MONGO_URI` 产生冲突，这里统一使用
      `BACKEND_MONGO_URI` 和 `BACKEND_DB_NAME` 作为环境变量名。
    - 代码内部仍然通过属性 `MONGO_URI` 和 `DB_NAME` 访问，方便兼容原有代码。
    """

    # 环境变量名：BACKEND_MONGO_URI
    BACKEND_MONGO_URI: str = (
        "mongodb+srv://0227_wx201383_db_user:"
        "hdkkdbdikwksbffkfjdwl645s87jwksadasfsafasf"
        "@cluster0.roe7na.mongodb.net/"
    )
    # 环境变量名：BACKEND_DB_NAME
    BACKEND_DB_NAME: str = "teacher_query"

>>>>>>> Stashed changes
    # Alembic迁移配置
    ALEMBIC_CONFIG_PATH: str = "alembic.ini"
    ENABLE_AUTO_MIGRATION: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"  # 指定.env文件编码，避免中文乱码
        case_sensitive = True
        extra = "ignore"  # 忽略额外的环境变量

    # 向外暴露与旧代码兼容的属性
    @property
    def MONGO_URI(self) -> str:
        return self.BACKEND_MONGO_URI

    @property
    def DB_NAME(self) -> str:
        return self.BACKEND_DB_NAME


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