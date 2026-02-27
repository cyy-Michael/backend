"""
应用配置模块
管理应用的基本配置信息
"""

import os
from typing import Optional, List
from pydantic_settings import BaseSettings
from functools import lru_cache


class AppSettings(BaseSettings):
    """应用配置设置"""
    # 应用基本信息
    APP_NAME: str = "导师资料查询小程序后端"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "提供导师信息的查询、新增、更新、删除等接口"
    APP_ENVIRONMENT: str = os.getenv("APP_ENVIRONMENT", "development")  # development, production, testing
    
    # 服务配置
    HOST: str = "0.0.0.0"
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = APP_ENVIRONMENT == "development"
    RELOAD: bool = APP_ENVIRONMENT == "development"
    
    # API配置
    API_V1_STR: str = "/api/v1"
    API_PREFIX: str = "/api"
    PROJECT_NAME: str = APP_NAME
    
    # CORS配置
    # 开发环境允许的来源
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
    ]
    # 生产环境CORS配置（可以为空，通过环境变量设置）
    # 示例: BACKEND_CORS_ORIGINS=["https://api.example.com", "https://admin.example.com"]
    
    # 限流配置 (Rate Limiting)
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60      # 全局每分钟请求限制
    RATE_LIMIT_PER_HOUR: int = 1000      # 全局每小时请求限制
    RATE_LIMIT_BURST: int = 5            # 突发请求允许数量
    
    # 特定接口限流配置 (可选)
    # 格式: {"/api/v1/auth/login": "5/minute"}
    SPECIFIC_ENDPOINT_LIMITS: dict = {
        "/api/v1/auth/login": "5/minute",
        "/api/v1/recharge/create_order": "10/minute"
    }
    
    # 请求体大小限制（MB）
    MAX_REQUEST_BODY_SIZE: int = 10
    
    # 健康检查配置
    HEALTH_CHECK_ENABLED: bool = True
    HEALTH_CHECK_ENDPOINT: str = "/"
    
    # 性能监控配置
    PERFORMANCE_MONITORING_ENABLED: bool = False
    
    # 数据验证配置
    STRICT_VALIDATION: bool = True
    
    # 缓存配置
    CACHE_ENABLED: bool = False
    CACHE_TTL: int = 300  # 5分钟
    
    # 清理配置
    CLEANUP_INTERVAL: int = 3600  # 1小时
    
    @property
    def is_development(self) -> bool:
        """是否为开发环境"""
        return self.APP_ENVIRONMENT == "development"
    
    @property
    def is_production(self) -> bool:
        """是否为生产环境"""
        return self.APP_ENVIRONMENT == "production"
    
    @property
    def is_testing(self) -> bool:
        """是否为测试环境"""
        return self.APP_ENVIRONMENT == "testing"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


@lru_cache()
def get_app_settings() -> AppSettings:
    """获取应用配置（单例模式）"""
    return AppSettings()


# 创建全局配置实例
app_settings = get_app_settings()