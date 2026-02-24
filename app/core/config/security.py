"""
安全配置模块
管理应用的安全相关配置
"""

import os
import secrets
from typing import Optional, List, Dict, Any
from pydantic_settings import BaseSettings
from functools import lru_cache


class SecuritySettings(BaseSettings):
    """安全配置设置"""
    # JWT配置
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32))
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    JWT_BLACKLIST_ENABLED: bool = True
    JWT_BLACKLIST_TOKEN_PREFIX: str = "bl_token:"
    
    # 密码配置
    PASSWORD_SCHEME: str = "bcrypt"
    PASSWORD_HASH_ROUNDS: int = 12
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_MAX_LENGTH: int = 128
    PASSWORD_COMPLEXITY_REQUIRED: bool = True
    PASSWORD_COMPLEXITY_RULES: Dict[str, Any] = {
        "require_uppercase": True,
        "require_lowercase": True,
        "require_digit": True,
        "require_special": True,
        "special_chars": "!@#$%^&*()_+-=[]{}|;:,.<>?/"
    }
    
    # API密钥配置
    API_KEY_ENABLED: bool = False
    API_KEY_HEADER_NAME: str = "X-API-Key"
    API_KEY_PREFIX: str = "api_"
    API_KEY_EXPIRE_DAYS: int = 365
    
    # 速率限制配置
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    RATE_LIMIT_PER_DAY: int = 10000
    RATE_LIMIT_WHITELIST: List[str] = ["127.0.0.1", "localhost", "::1"]
    
    # CORS配置
    CORS_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
    ]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]
    CORS_EXPOSE_HEADERS: List[str] = ["Content-Length", "X-Request-ID"]
    CORS_MAX_AGE: int = 600  # 10分钟
    
    # CSRF配置
    CSRF_PROTECTION_ENABLED: bool = True
    CSRF_TOKEN_LENGTH: int = 32
    CSRF_TOKEN_EXPIRE_MINUTES: int = 30
    CSRF_COOKIE_NAME: str = "csrf_token"
    CSRF_HEADER_NAME: str = "X-CSRF-Token"
    
    # 内容安全策略配置
    CSP_ENABLED: bool = False
    CSP_DIRECTIVES: Dict[str, List[str]] = {
        "default-src": ["'self'"],
        "script-src": ["'self'", "'unsafe-inline'"],
        "style-src": ["'self'", "'unsafe-inline'"],
        "img-src": ["'self'", "data:", "https:"],
        "font-src": ["'self'", "data:"],
        "connect-src": ["'self'"],
        "frame-src": [],
        "object-src": ["'none'"],
        "base-uri": ["'self'"],
        "form-action": ["'self'"],
        "frame-ancestors": ["'self'"],
        "upgrade-insecure-requests": [],
        "block-all-mixed-content": []
    }
    
    # HTTP安全头部配置
    SECURE_HEADERS_ENABLED: bool = True
    SECURE_HEADERS_CONFIG: Dict[str, Any] = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains"
    }
    
    # 敏感数据处理配置
    SENSITIVE_FIELDS: List[str] = [
        "password", "token", "secret", "key", "credential",
        "password_hash", "api_key", "jwt", "auth", "credit_card",
        "social_security", "passport", "bank_account"
    ]
    SENSITIVE_DATA_MASK_CHAR: str = "*"
    SENSITIVE_DATA_MASK_KEEP_LENGTH: int = 4
    
    # 输入验证配置
    INPUT_VALIDATION_ENABLED: bool = True
    MAX_REQUEST_BODY_SIZE: int = 10 * 1024 * 1024  # 10MB
    MAX_UPLOAD_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_UPLOAD_EXTENSIONS: List[str] = [
        ".jpg", ".jpeg", ".png", ".gif", ".pdf",
        ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx"
    ]
    
    # 审计日志配置
    AUDIT_LOG_ENABLED: bool = True
    AUDIT_LOG_ACTIONS: List[str] = ["create", "update", "delete", "login", "logout", "password_change"]
    AUDIT_LOG_EXCLUDE_PATHS: List[str] = ["/health", "/metrics", "/docs", "/redoc"]
    
    # 会话配置
    SESSION_ENABLED: bool = False
    SESSION_COOKIE_NAME: str = "session_id"
    SESSION_COOKIE_SECURE: bool = True
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SAMESITE: str = "Lax"
    SESSION_EXPIRE_MINUTES: int = 180  # 3小时
    
    @property
    def cors_config(self) -> Dict[str, Any]:
        """获取CORS配置"""
        return {
            "allow_origins": self.CORS_ORIGINS,
            "allow_credentials": self.CORS_ALLOW_CREDENTIALS,
            "allow_methods": self.CORS_ALLOW_METHODS,
            "allow_headers": self.CORS_ALLOW_HEADERS,
            "expose_headers": self.CORS_EXPOSE_HEADERS,
            "max_age": self.CORS_MAX_AGE
        }
    
    @property
    def password_regex_pattern(self) -> str:
        """生成密码复杂度正则表达式"""
        if not self.PASSWORD_COMPLEXITY_REQUIRED:
            return f"^.{{{self.PASSWORD_MIN_LENGTH},{self.PASSWORD_MAX_LENGTH}}}$"
        
        rules = []
        if self.PASSWORD_COMPLEXITY_RULES.get("require_uppercase"):
            rules.append(r"(?=.*[A-Z])")
        if self.PASSWORD_COMPLEXITY_RULES.get("require_lowercase"):
            rules.append(r"(?=.*[a-z])")
        if self.PASSWORD_COMPLEXITY_RULES.get("require_digit"):
            rules.append(r"(?=.*\d)")
        if self.PASSWORD_COMPLEXITY_RULES.get("require_special"):
            special_chars = re.escape(self.PASSWORD_COMPLEXITY_RULES.get("special_chars", "!@#$%^&*()_+-=[]{}|;:,.<>?/"))
            rules.append(f"(?=.*[{special_chars}])")
        
        rules.append(f"^.{{{self.PASSWORD_MIN_LENGTH},{self.PASSWORD_MAX_LENGTH}}}$")
        return "".join(rules)
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


@lru_cache()
def get_security_settings() -> SecuritySettings:
    """获取安全配置（单例模式）"""
    return SecuritySettings()


# 创建全局安全配置实例
security_settings = get_security_settings()


# 导入re用于密码正则表达式
import re