"""
安全工具模块
提供密码加密、JWT令牌生成、数据验证等安全相关功能
"""

import os
import secrets
import hashlib
import hmac
import base64
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT配置
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32))
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
JWT_REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7"))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码
    
    Args:
        plain_password: 明文密码
        hashed_password: 哈希密码
    
    Returns:
        bool: 密码是否正确
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    获取密码哈希值
    
    Args:
        password: 明文密码
    
    Returns:
        str: 哈希后的密码
    """
    return pwd_context.hash(password)


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    创建访问令牌
    
    Args:
        data: 要编码的数据
        expires_delta: 过期时间增量
    
    Returns:
        str: JWT令牌
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    
    return encoded_jwt


def create_refresh_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    创建刷新令牌
    
    Args:
        data: 要编码的数据
        expires_delta: 过期时间增量
    
    Returns:
        str: JWT刷新令牌
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    
    return encoded_jwt


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """
    解码JWT令牌
    
    Args:
        token: JWT令牌
    
    Returns:
        Optional[Dict[str, Any]]: 解码后的数据，如果令牌无效则返回None
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        return None


def verify_token(token: str, token_type: str = "access") -> bool:
    """
    验证令牌
    
    Args:
        token: JWT令牌
        token_type: 令牌类型（access或refresh）
    
    Returns:
        bool: 令牌是否有效
    """
    payload = decode_token(token)
    
    if not payload:
        return False
    
    # 检查令牌类型
    if payload.get("type") != token_type:
        return False
    
    # 检查是否过期
    exp = payload.get("exp")
    if not exp or datetime.utcnow().timestamp() > exp:
        return False
    
    return True


def generate_api_key(user_id: str, email: str) -> str:
    """
    生成API密钥
    
    Args:
        user_id: 用户ID
        email: 用户邮箱
    
    Returns:
        str: API密钥
    """
    # 使用HMAC-SHA256生成API密钥
    message = f"{user_id}:{email}:{datetime.utcnow().isoformat()}"
    h = hmac.new(
        JWT_SECRET_KEY.encode(),
        message.encode(),
        hashlib.sha256
    )
    api_key = base64.urlsafe_b64encode(h.digest()).decode()
    
    return f"api_{api_key}"


def validate_api_key(api_key: str) -> bool:
    """
    验证API密钥格式
    
    Args:
        api_key: API密钥
    
    Returns:
        bool: 格式是否正确
    """
    if not api_key.startswith("api_"):
        return False
    
    # 检查base64格式
    try:
        key_part = api_key[4:]  # 移除"api_"前缀
        decoded = base64.urlsafe_b64decode(key_part)
        return len(decoded) == 32  # SHA256输出32字节
    except:
        return False


def generate_random_token(length: int = 32) -> str:
    """
    生成随机令牌
    
    Args:
        length: 令牌长度
    
    Returns:
        str: 随机令牌
    """
    return secrets.token_urlsafe(length)


def hash_data(data: Union[str, bytes]) -> str:
    """
    对数据进行哈希处理
    
    Args:
        data: 要哈希的数据
    
    Returns:
        str: 哈希值（十六进制字符串）
    """
    if isinstance(data, str):
        data = data.encode('utf-8')
    
    return hashlib.sha256(data).hexdigest()


def sanitize_input(input_string: Optional[str]) -> Optional[str]:
    """
    清理用户输入，防止XSS攻击
    
    Args:
        input_string: 用户输入字符串
    
    Returns:
        Optional[str]: 清理后的字符串
    """
    if input_string is None:
        return None
    
    # 基本的HTML字符转义
    replacements = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#x27;',
        '/': '&#x2F;'
    }
    
    result = input_string
    for char, replacement in replacements.items():
        result = result.replace(char, replacement)
    
    return result


def validate_email(email: str) -> bool:
    """
    简单的邮箱格式验证
    
    Args:
        email: 邮箱地址
    
    Returns:
        bool: 格式是否正确
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """
    简单的手机号格式验证（中国大陆）
    
    Args:
        phone: 手机号码
    
    Returns:
        bool: 格式是否正确
    """
    import re
    pattern = r'^1[3-9]\d{9}$'
    return bool(re.match(pattern, phone))


def mask_sensitive_data(data: Dict[str, Any], sensitive_fields: list = None) -> Dict[str, Any]:
    """
    屏蔽敏感数据
    
    Args:
        data: 数据字典
        sensitive_fields: 敏感字段列表
    
    Returns:
        Dict[str, Any]: 屏蔽后的数据
    """
    if sensitive_fields is None:
        sensitive_fields = ['password', 'token', 'secret', 'key', 'credential']
    
    masked_data = data.copy()
    
    for key, value in masked_data.items():
        # 检查是否为敏感字段
        if any(sensitive in key.lower() for sensitive in sensitive_fields):
            if isinstance(value, str) and len(value) > 8:
                masked_data[key] = value[:4] + '*' * (len(value) - 8) + value[-4:]
            elif isinstance(value, str):
                masked_data[key] = '*' * len(value)
            else:
                masked_data[key] = '***'
    
    return masked_data