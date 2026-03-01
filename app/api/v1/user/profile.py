"""
用户信息管理接口
提供用户信息查询和更新功能
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Dict, Any
from datetime import datetime

from app.models import User
from app.schemas.user_schema import (
    UserProfileResponse,
    UserProfileUpdate,
    UserProfileUpdateResponse
)
from app.api.v1.auth.login import get_current_user
from app.utils import (
    success_response,
    error_response,
    business_error_response,
    api_logger
)
from app.db.mongo import get_db, update_one, find_one

router = APIRouter(
    prefix="/user",
    tags=["user"]
)


@router.get(
    "/profile",
    summary="获取用户信息",
    description="获取当前登录用户的个人信息，包括昵称、头像、院校、专业等",
    response_model=UserProfileResponse
)
async def get_user_profile(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """
    获取用户信息接口
    
    Args:
        request: 请求对象
        current_user: 当前登录用户（通过JWT token验证）
    
    Returns:
        UserProfileResponse: 用户信息
    
    Raises:
        HTTPException: 当用户不存在或查询失败时抛出
    """
    try:
        # 从数据库查询完整的用户信息
        user_data = await find_one("users", {"id": current_user.id})
        
        if not user_data:
            api_logger.warning(
                f"用户信息不存在: {current_user.id}\n"
                f"Request ID: {request.state.request_id}"
            )
            raise HTTPException(
                status_code=404,
                detail=business_error_response(
                    code="USER_NOT_FOUND",
                    message="用户信息不存在",
                    details={"user_id": current_user.id}
                )
            )
        
        # 构建响应数据
        profile = UserProfileResponse(
            id=user_data["id"],
            nickname=user_data.get("nickname"),
            avatar=user_data.get("avatar"),
            school=user_data.get("school"),
            major=user_data.get("major"),
            grade=user_data.get("grade"),
            vip_status=user_data.get("vip_status", False),
            vip_expire_date=user_data.get("vip_expire_date"),
            created_at=user_data["created_at"]
        )
        
        api_logger.info(
            f"用户信息查询成功: {current_user.id}\n"
            f"Request ID: {request.state.request_id}"
        )
        
        return profile
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(
            f"获取用户信息失败: {str(e)}\n"
            f"User ID: {current_user.id}\n"
            f"Request ID: {request.state.request_id}"
        )
        raise HTTPException(
            status_code=500,
            detail=error_response(
                message="获取用户信息失败",
                error={"request_id": request.state.request_id}
            )
        )


@router.put(
    "/profile",
    summary="更新用户信息",
    description="更新当前登录用户的个人信息，支持更新昵称、头像、院校、专业、年级等字段"
)
async def update_user_profile(
    request: Request,
    profile_update: UserProfileUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    更新用户信息接口
    
    Args:
        request: 请求对象
        profile_update: 要更新的用户信息
        current_user: 当前登录用户（通过JWT token验证）
    
    Returns:
        更新结果，包括更新的字段列表和更新后的用户信息
    
    Raises:
        HTTPException: 当更新失败时抛出
    """
    try:
        # 构建更新数据（只包含非None的字段）
        update_data: Dict[str, Any] = {}
        updated_fields = []
        
        # 检查并添加要更新的字段
        if profile_update.nickname is not None:
            update_data["nickname"] = profile_update.nickname
            updated_fields.append("nickname")
        
        if profile_update.avatar is not None:
            update_data["avatar"] = profile_update.avatar
            updated_fields.append("avatar")
        
        if profile_update.school is not None:
            update_data["school"] = profile_update.school
            updated_fields.append("school")
        
        if profile_update.major is not None:
            update_data["major"] = profile_update.major
            updated_fields.append("major")
        
        if profile_update.grade is not None:
            update_data["grade"] = profile_update.grade
            updated_fields.append("grade")
        
        # 如果没有要更新的字段，返回提示
        if not update_data:
            return success_response(
                message="没有需要更新的字段",
                data={
                    "success": True,
                    "updated_fields": [],
                    "user": UserProfileResponse(
                        id=current_user.id,
                        nickname=current_user.nickname,
                        avatar=current_user.avatar,
                        school=current_user.school,
                        major=current_user.major,
                        grade=current_user.grade,
                        vip_status=current_user.vip_status,
                        vip_expire_date=current_user.vip_expire_date,
                        created_at=current_user.created_at
                    )
                }
            )
        
        # 添加更新时间
        update_data["updated_at"] = datetime.now()
        
        # 执行更新操作
        success = await update_one(
            "users",
            {"id": current_user.id},
            update_data
        )
        
        if not success:
            api_logger.warning(
                f"用户信息更新失败: {current_user.id}\n"
                f"Update data: {update_data}\n"
                f"Request ID: {request.state.request_id}"
            )
            raise HTTPException(
                status_code=500,
                detail=business_error_response(
                    code="UPDATE_FAILED",
                    message="用户信息更新失败",
                    details={"user_id": current_user.id}
                )
            )
        
        # 查询更新后的用户信息
        updated_user = await find_one("users", {"id": current_user.id})
        
        if not updated_user:
            raise HTTPException(
                status_code=500,
                detail=error_response(
                    message="更新后查询用户信息失败",
                    error={"request_id": request.state.request_id}
                )
            )
        
        # 构建响应
        user_profile = UserProfileResponse(
            id=updated_user["id"],
            nickname=updated_user.get("nickname"),
            avatar=updated_user.get("avatar"),
            school=updated_user.get("school"),
            major=updated_user.get("major"),
            grade=updated_user.get("grade"),
            vip_status=updated_user.get("vip_status", False),
            vip_expire_date=updated_user.get("vip_expire_date"),
            created_at=updated_user["created_at"]
        )
        
        api_logger.info(
            f"用户信息更新成功: {current_user.id}\n"
            f"Updated fields: {', '.join(updated_fields)}\n"
            f"Request ID: {request.state.request_id}"
        )
        
        return success_response(
            message="用户信息更新成功",
            data={
                "success": True,
                "updated_fields": updated_fields,
                "user": user_profile
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(
            f"更新用户信息失败: {str(e)}\n"
            f"User ID: {current_user.id}\n"
            f"Request ID: {request.state.request_id}"
        )
        raise HTTPException(
            status_code=500,
            detail=error_response(
                message="更新用户信息失败",
                error={"request_id": request.state.request_id}
            )
        )


@router.patch(
    "/profile",
    summary="部分更新用户信息",
    description="部分更新当前登录用户的个人信息（PATCH方法，与PUT方法功能相同）"
)
async def patch_user_profile(
    request: Request,
    profile_update: UserProfileUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    部分更新用户信息接口（PATCH方法）
    
    功能与PUT方法相同，提供RESTful API的完整支持
    
    Args:
        request: 请求对象
        profile_update: 要更新的用户信息
        current_user: 当前登录用户（通过JWT token验证）
    
    Returns:
        更新结果，包括更新的字段列表和更新后的用户信息
    """
    # 直接调用PUT方法的实现
    return await update_user_profile(request, profile_update, current_user)
