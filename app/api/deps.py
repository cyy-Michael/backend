from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app.models import User
from app.core import security_settings
from app.utils import error_response

# OAuth2 方案配置
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    获取当前登录用户
    """
    credentials_exception = HTTPException(
        status_code=401,
        detail=error_response(
            message="无效的认证凭证",
            error={"type": "authentication_error"}
        ),
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token, 
            security_settings.JWT_SECRET_KEY, 
            algorithms=[security_settings.JWT_ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # 使用异步的数据库查询
    from app.db.mongo import find_one
    user = await find_one("users", {"id": user_id})
    
    if user is None:
        raise credentials_exception
    
    # 转换为User模型
    return User(
        id=user["id"],
        nickname=user.get("nickname"),
        avatar=user.get("avatar"),
        school=user.get("school"),
        major=user.get("major"),
        grade=user.get("grade"),
        vip_status=user.get("vip_status", False),
        vip_expire_date=user.get("vip_expire_date"),
        created_at=user["created_at"]
    )
