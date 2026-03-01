"""
管理员权限验证模块
提供管理员身份验证和权限检查功能
"""

from fastapi import HTTPException, Depends
from typing import Optional
from app.models import User
from app.api.v1.auth.login import get_current_user
from app.utils import business_error_response, api_logger
from app.db.mongo import find_one


# 管理员邮箱白名单（可以从配置文件或数据库读取）
ADMIN_EMAILS = [
    "admin@example.com",
    "superadmin@example.com"
]

# 管理员用户ID白名单（可以从配置文件或数据库读取）
ADMIN_USER_IDS = [
    "admin_user_001",
    "admin_user_002"
]


async def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    获取当前管理员用户
    
    验证当前用户是否具有管理员权限
    
    Args:
        current_user: 当前登录用户（通过JWT token验证）
    
    Returns:
        User: 管理员用户对象
    
    Raises:
        HTTPException: 当用户不是管理员时抛出403错误
    """
    # 方法1: 通过用户ID验证（推荐用于生产环境）
    if current_user.id in ADMIN_USER_IDS:
        api_logger.info(f"管理员访问: {current_user.id} - {current_user.nickname}")
        return current_user
    
    # 方法2: 通过数据库中的is_admin字段验证
    user_data = await find_one("users", {"id": current_user.id})
    if user_data and user_data.get("is_admin", False):
        api_logger.info(f"管理员访问（数据库验证）: {current_user.id} - {current_user.nickname}")
        return current_user
    
    # 方法3: 通过邮箱白名单验证（备用方案）
    # 注意：User模型中可能没有email字段，需要从数据库查询
    if user_data and user_data.get("email") in ADMIN_EMAILS:
        api_logger.info(f"管理员访问（邮箱验证）: {current_user.id} - {user_data.get('email')}")
        return current_user
    
    # 如果都不满足，拒绝访问
    api_logger.warning(
        f"非管理员尝试访问管理接口: {current_user.id} - {current_user.nickname}"
    )
    raise HTTPException(
        status_code=403,
        detail=business_error_response(
            code="FORBIDDEN",
            message="权限不足，仅管理员可访问",
            details={"user_id": current_user.id}
        )
    )


async def check_admin_permission(user_id: str) -> bool:
    """
    检查用户是否具有管理员权限
    
    Args:
        user_id: 用户ID
    
    Returns:
        bool: 是否具有管理员权限
    """
    # 检查用户ID白名单
    if user_id in ADMIN_USER_IDS:
        return True
    
    # 检查数据库中的is_admin字段
    user_data = await find_one("users", {"id": user_id})
    if user_data and user_data.get("is_admin", False):
        return True
    
    # 检查邮箱白名单
    if user_data and user_data.get("email") in ADMIN_EMAILS:
        return True
    
    return False


def add_admin_user(user_id: str):
    """
    将用户ID添加到管理员白名单
    
    注意：这是内存中的操作，重启后会失效
    生产环境应该使用数据库存储
    
    Args:
        user_id: 用户ID
    """
    if user_id not in ADMIN_USER_IDS:
        ADMIN_USER_IDS.append(user_id)
        api_logger.info(f"添加管理员: {user_id}")


def remove_admin_user(user_id: str):
    """
    从管理员白名单中移除用户ID
    
    Args:
        user_id: 用户ID
    """
    if user_id in ADMIN_USER_IDS:
        ADMIN_USER_IDS.remove(user_id)
        api_logger.info(f"移除管理员: {user_id}")


def get_admin_list() -> list:
    """
    获取管理员列表
    
    Returns:
        list: 管理员用户ID列表
    """
    return ADMIN_USER_IDS.copy()
