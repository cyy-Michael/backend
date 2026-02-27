"""
用户认证接口
提供微信登录、注册等功能
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from typing import Optional
import httpx
import json
import uuid
from datetime import datetime, timedelta

from app.models import UserLogin, UserLoginResponse, User
from app.core import security_settings, app_settings
from app.utils import (
    success_response,
    error_response,
    business_error_response,
    get_password_hash,
    verify_password,
    create_access_token,
    api_logger
)
from app.db.mongo import get_db

router = APIRouter(
    prefix="/auth",
    tags=["authentication"]
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# 模拟微信API调用
async def verify_wechat_code(code: str) -> dict:
    """
    验证微信登录code
    注意：实际项目中需要调用微信官方API
    """
    # 这里模拟返回，实际需要调用：
    # https://api.weixin.qq.com/sns/jscode2session
    return {
        "openid": f"wx_{uuid.uuid4().hex[:16]}",
        "unionid": f"union_{uuid.uuid4().hex[:16]}",
        "session_key": uuid.uuid4().hex
    }


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
    
    db = get_db()
    user = db.users.find_one({"id": user_id})
    
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


@router.post(
    "/login",
    summary="微信登录",
    description="使用微信小程序登录凭证code获取用户信息和token",
    response_model=UserLoginResponse
)
async def login(
    request: Request,
    login_data: UserLogin
):
    """
    微信登录接口
    
    Args:
        request: 请求对象
        login_data: 登录数据，包含微信code
    
    Returns:
        UserLoginResponse: 包含token和用户信息
    """
    try:
        # 验证微信code
        wechat_result = await verify_wechat_code(login_data.code)
        openid = wechat_result.get("openid")
        
        if not openid:
            raise HTTPException(
                status_code=400,
                detail=business_error_response(
                    code="WECHAT_AUTH_FAILED",
                    message="微信授权失败",
                    details={"code": login_data.code}
                )
            )
        
        # 查询数据库中是否存在该用户
        db = get_db()
        existing_user = db.users.find_one({"openid": openid})
        
        if existing_user:
            # 用户已存在，生成token
            user = User(
                id=existing_user["id"],
                nickname=existing_user.get("nickname"),
                avatar=existing_user.get("avatar"),
                school=existing_user.get("school"),
                major=existing_user.get("major"),
                grade=existing_user.get("grade"),
                vip_status=existing_user.get("vip_status", False),
                vip_expire_date=existing_user.get("vip_expire_date"),
                created_at=existing_user["created_at"]
            )
        else:
            # 用户不存在，创建新用户
            new_user = {
                "id": str(uuid.uuid4()),
                "openid": openid,
                "unionid": wechat_result.get("unionid"),
                "nickname": f"用户_{openid[:8]}",
                "avatar": None,
                "school": None,
                "major": None,
                "grade": None,
                "vip_status": False,
                "vip_expire_date": None,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            result = db.users.insert_one(new_user)
            
            if not result.inserted_id:
                raise HTTPException(
                    status_code=500,
                    detail=error_response(
                        message="创建用户失败",
                        error={"type": "database_error"}
                    )
                )
            
            user = User(
                id=new_user["id"],
                nickname=new_user["nickname"],
                avatar=new_user.get("avatar"),
                school=new_user.get("school"),
                major=new_user.get("major"),
                grade=new_user.get("grade"),
                vip_status=new_user.get("vip_status", False),
                vip_expire_date=new_user.get("vip_expire_date"),
                created_at=new_user["created_at"]
            )
        
        # 生成JWT token
        access_token_expires = timedelta(
            minutes=security_settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )
        access_token = create_access_token(
            data={"sub": user.id},
            expires_delta=access_token_expires
        )
        
        api_logger.info(
            f"用户登录成功: {user.id} - {user.nickname}\n"
            f"Request ID: {request.state.request_id}"
        )
        
        return UserLoginResponse(
            token=access_token,
            user=user
        )
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(
            f"登录失败: {str(e)}\n"
            f"Request ID: {request.state.request_id}"
        )
        raise HTTPException(
            status_code=500,
            detail=error_response(
                message="登录过程中发生错误",
                error={"request_id": request.state.request_id}
            )
        )


@router.post(
    "/logout",
    summary="用户登出",
    description="用户退出登录"
)
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """
    用户登出接口
    
    Args:
        request: 请求对象
        current_user: 当前登录用户
    
    Returns:
        登出结果
    """
    # JWT是无状态的，服务端不需要特殊处理
    # 实际项目中可以将token加入黑名单
    
    api_logger.info(
        f"用户登出: {current_user.id} - {current_user.nickname}\n"
        f"Request ID: {request.state.request_id}"
    )
    
    return success_response(
        message="登出成功"
    )


@router.get(
    "/refresh",
    summary="刷新token",
    description="使用当前token刷新获取新的token"
)
async def refresh_token(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """
    刷新token接口
    
    Args:
        request: 请求对象
        current_user: 当前登录用户
    
    Returns:
        新的token
    """
    try:
        # 生成新的access token
        access_token_expires = timedelta(
            minutes=security_settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )
        access_token = create_access_token(
            data={"sub": current_user.id},
            expires_delta=access_token_expires
        )
        
        return success_response(
            data={"token": access_token},
            message="Token刷新成功"
        )
        
    except Exception as e:
        api_logger.error(
            f"Token刷新失败: {str(e)}\n"
            f"User: {current_user.id}\n"
            f"Request ID: {request.state.request_id}"
        )
        raise HTTPException(
            status_code=500,
            detail=error_response(
                message="Token刷新失败",
                error={"request_id": request.state.request_id}
            )
        )