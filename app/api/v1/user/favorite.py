"""
用户收藏管理接口
提供收藏/取消收藏导师、查询收藏列表等功能
"""

from fastapi import APIRouter, HTTPException, Depends, Request, Query
from typing import List, Optional
from datetime import datetime
import uuid

from app.models import User
from app.schemas.favorite_schema import (
    FavoriteToggleRequest,
    FavoriteToggleResponse,
    FavoriteTutorBrief,
    FavoriteListResponse,
    FavoriteStatusResponse,
    BatchFavoriteStatusRequest,
    BatchFavoriteStatusResponse
)
from app.api.v1.auth.login import get_current_user
from app.utils import (
    success_response,
    error_response,
    business_error_response,
    api_logger
)
from app.db.mongo import find_one, find_many, insert_one, delete_one, get_collection

router = APIRouter(
    prefix="/user",
    tags=["user", "favorite"]
)


@router.post(
    "/favorite/toggle",
    summary="收藏/取消收藏导师",
    description="切换导师的收藏状态，如果已收藏则取消收藏，如果未收藏则添加收藏"
)
async def toggle_favorite(
    request: Request,
    favorite_request: FavoriteToggleRequest,
    current_user: User = Depends(get_current_user)
):
    """
    收藏/取消收藏导师接口
    
    Args:
        request: 请求对象
        favorite_request: 收藏请求数据
        current_user: 当前登录用户（通过JWT token验证）
    
    Returns:
        操作结果，包括操作类型（collected/uncollected）和消息
    
    Raises:
        HTTPException: 当导师不存在或操作失败时抛出
    """
    try:
        tutor_id = favorite_request.tutor_id
        
        # 验证导师是否存在
        tutor = await find_one("tutors", {"id": tutor_id})
        if not tutor:
            api_logger.warning(
                f"导师不存在: {tutor_id}\n"
                f"User: {current_user.id}\n"
                f"Request ID: {request.state.request_id}"
            )
            raise HTTPException(
                status_code=404,
                detail=business_error_response(
                    code="TUTOR_NOT_FOUND",
                    message="导师不存在",
                    details={"tutor_id": tutor_id}
                )
            )
        
        # 检查是否已收藏
        existing_favorite = await find_one(
            "favorites",
            {
                "user_id": current_user.id,
                "target_type": "tutor",
                "target_id": tutor_id
            }
        )
        
        if existing_favorite:
            # 已收藏，执行取消收藏操作
            success = await delete_one(
                "favorites",
                {"id": existing_favorite["id"]}
            )
            
            if not success:
                raise HTTPException(
                    status_code=500,
                    detail=business_error_response(
                        code="UNCOLLECT_FAILED",
                        message="取消收藏失败"
                    )
                )
            
            api_logger.info(
                f"取消收藏成功: User {current_user.id} -> Tutor {tutor_id} ({tutor['name']})\n"
                f"Request ID: {request.state.request_id}"
            )
            
            return success_response(
                message="取消收藏成功",
                data=FavoriteToggleResponse(
                    action="uncollected",
                    tutor_id=tutor_id,
                    message="已取消收藏该导师"
                )
            )
        else:
            # 未收藏，执行收藏操作
            favorite_data = {
                "id": str(uuid.uuid4()),
                "user_id": current_user.id,
                "target_type": "tutor",
                "target_id": tutor_id,
                "created_at": datetime.now()
            }
            
            favorite_id = await insert_one("favorites", favorite_data)
            
            if not favorite_id:
                raise HTTPException(
                    status_code=500,
                    detail=business_error_response(
                        code="COLLECT_FAILED",
                        message="收藏失败"
                    )
                )
            
            api_logger.info(
                f"收藏成功: User {current_user.id} -> Tutor {tutor_id} ({tutor['name']})\n"
                f"Request ID: {request.state.request_id}"
            )
            
            return success_response(
                message="收藏成功",
                data=FavoriteToggleResponse(
                    action="collected",
                    tutor_id=tutor_id,
                    message="已收藏该导师"
                )
            )
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(
            f"收藏操作失败: {str(e)}\n"
            f"User: {current_user.id}\n"
            f"Tutor: {favorite_request.tutor_id}\n"
            f"Request ID: {request.state.request_id}"
        )
        raise HTTPException(
            status_code=500,
            detail=error_response(
                message="收藏操作失败",
                error={"request_id": request.state.request_id}
            )
        )


@router.get(
    "/favorites",
    summary="获取收藏的导师列表",
    description="获取当前用户收藏的所有导师，支持分页"
)
async def get_favorite_list(
    request: Request,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    current_user: User = Depends(get_current_user)
):
    """
    获取收藏的导师列表接口
    
    Args:
        request: 请求对象
        page: 页码
        page_size: 每页数量
        current_user: 当前登录用户（通过JWT token验证）
    
    Returns:
        收藏的导师列表，包括分页信息
    
    Raises:
        HTTPException: 当查询失败时抛出
    """
    try:
        # 计算分页
        skip = (page - 1) * page_size
        
        # 获取用户的收藏记录
        favorites_collection = get_collection("favorites")
        
        # 获取总数
        total = await favorites_collection.count_documents({
            "user_id": current_user.id,
            "target_type": "tutor"
        })
        
        # 获取收藏记录（按收藏时间倒序）
        favorites_cursor = favorites_collection.find({
            "user_id": current_user.id,
            "target_type": "tutor"
        }).sort("created_at", -1).skip(skip).limit(page_size)
        
        favorites = await favorites_cursor.to_list(length=page_size)
        
        # 获取导师详细信息
        tutor_list = []
        for favorite in favorites:
            tutor_id = favorite["target_id"]
            tutor = await find_one("tutors", {"id": tutor_id})
            
            if tutor:
                # 构建导师简略信息
                tutor_brief = FavoriteTutorBrief(
                    id=tutor["id"],
                    name=tutor["name"],
                    title=tutor.get("title"),
                    school=tutor.get("school_name", ""),
                    department=tutor.get("department_name", ""),
                    avatar=tutor.get("avatar_url"),
                    research_direction=tutor.get("research_direction"),
                    tags=tutor.get("tags", []),
                    collected_at=favorite["created_at"]
                )
                tutor_list.append(tutor_brief)
        
        api_logger.info(
            f"获取收藏列表成功: User {current_user.id}\n"
            f"分页: page={page}, page_size={page_size}\n"
            f"结果: {len(tutor_list)}/{total}\n"
            f"Request ID: {request.state.request_id}"
        )
        
        return success_response(
            message="获取收藏列表成功",
            data={
                "list": tutor_list,
                "total": total,
                "page": page,
                "page_size": page_size
            }
        )
        
    except Exception as e:
        api_logger.error(
            f"获取收藏列表失败: {str(e)}\n"
            f"User: {current_user.id}\n"
            f"Request ID: {request.state.request_id}"
        )
        raise HTTPException(
            status_code=500,
            detail=error_response(
                message="获取收藏列表失败",
                error={"request_id": request.state.request_id}
            )
        )


@router.get(
    "/favorite/status/{tutor_id}",
    summary="查询导师收藏状态",
    description="查询指定导师是否已被当前用户收藏"
)
async def get_favorite_status(
    request: Request,
    tutor_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    查询导师收藏状态接口
    
    Args:
        request: 请求对象
        tutor_id: 导师ID
        current_user: 当前登录用户（通过JWT token验证）
    
    Returns:
        收藏状态信息
    
    Raises:
        HTTPException: 当查询失败时抛出
    """
    try:
        # 查询收藏记录
        favorite = await find_one(
            "favorites",
            {
                "user_id": current_user.id,
                "target_type": "tutor",
                "target_id": tutor_id
            }
        )
        
        is_collected = favorite is not None
        
        api_logger.info(
            f"查询收藏状态: User {current_user.id} -> Tutor {tutor_id}: {is_collected}\n"
            f"Request ID: {request.state.request_id}"
        )
        
        return success_response(
            message="查询成功",
            data=FavoriteStatusResponse(
                is_collected=is_collected,
                tutor_id=tutor_id
            )
        )
        
    except Exception as e:
        api_logger.error(
            f"查询收藏状态失败: {str(e)}\n"
            f"User: {current_user.id}\n"
            f"Tutor: {tutor_id}\n"
            f"Request ID: {request.state.request_id}"
        )
        raise HTTPException(
            status_code=500,
            detail=error_response(
                message="查询收藏状态失败",
                error={"request_id": request.state.request_id}
            )
        )


@router.post(
    "/favorite/batch-status",
    summary="批量查询导师收藏状态",
    description="批量查询多个导师是否已被当前用户收藏"
)
async def get_batch_favorite_status(
    request: Request,
    batch_request: BatchFavoriteStatusRequest,
    current_user: User = Depends(get_current_user)
):
    """
    批量查询导师收藏状态接口
    
    Args:
        request: 请求对象
        batch_request: 批量查询请求数据
        current_user: 当前登录用户（通过JWT token验证）
    
    Returns:
        收藏状态字典，key为导师ID，value为是否收藏
    
    Raises:
        HTTPException: 当查询失败时抛出
    """
    try:
        tutor_ids = batch_request.tutor_ids
        
        # 查询所有相关的收藏记录
        favorites_collection = get_collection("favorites")
        favorites_cursor = favorites_collection.find({
            "user_id": current_user.id,
            "target_type": "tutor",
            "target_id": {"$in": tutor_ids}
        })
        
        favorites = await favorites_cursor.to_list(length=len(tutor_ids))
        
        # 构建收藏状态字典
        collected_ids = {fav["target_id"] for fav in favorites}
        favorites_dict = {
            tutor_id: (tutor_id in collected_ids)
            for tutor_id in tutor_ids
        }
        
        api_logger.info(
            f"批量查询收藏状态: User {current_user.id}\n"
            f"查询数量: {len(tutor_ids)}\n"
            f"已收藏数量: {len(collected_ids)}\n"
            f"Request ID: {request.state.request_id}"
        )
        
        return success_response(
            message="批量查询成功",
            data=BatchFavoriteStatusResponse(
                favorites=favorites_dict
            )
        )
        
    except Exception as e:
        api_logger.error(
            f"批量查询收藏状态失败: {str(e)}\n"
            f"User: {current_user.id}\n"
            f"Request ID: {request.state.request_id}"
        )
        raise HTTPException(
            status_code=500,
            detail=error_response(
                message="批量查询收藏状态失败",
                error={"request_id": request.state.request_id}
            )
        )


@router.delete(
    "/favorite/{tutor_id}",
    summary="取消收藏导师（DELETE方法）",
    description="使用DELETE方法取消收藏指定的导师"
)
async def delete_favorite(
    request: Request,
    tutor_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    取消收藏导师接口（DELETE方法）
    
    Args:
        request: 请求对象
        tutor_id: 导师ID
        current_user: 当前登录用户（通过JWT token验证）
    
    Returns:
        操作结果
    
    Raises:
        HTTPException: 当导师未收藏或操作失败时抛出
    """
    try:
        # 查询收藏记录
        favorite = await find_one(
            "favorites",
            {
                "user_id": current_user.id,
                "target_type": "tutor",
                "target_id": tutor_id
            }
        )
        
        if not favorite:
            api_logger.warning(
                f"导师未收藏: User {current_user.id} -> Tutor {tutor_id}\n"
                f"Request ID: {request.state.request_id}"
            )
            raise HTTPException(
                status_code=404,
                detail=business_error_response(
                    code="NOT_COLLECTED",
                    message="该导师未收藏",
                    details={"tutor_id": tutor_id}
                )
            )
        
        # 删除收藏记录
        success = await delete_one("favorites", {"id": favorite["id"]})
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail=business_error_response(
                    code="DELETE_FAILED",
                    message="取消收藏失败"
                )
            )
        
        api_logger.info(
            f"取消收藏成功（DELETE）: User {current_user.id} -> Tutor {tutor_id}\n"
            f"Request ID: {request.state.request_id}"
        )
        
        return success_response(
            message="取消收藏成功",
            data={
                "tutor_id": tutor_id,
                "action": "deleted"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(
            f"取消收藏失败（DELETE）: {str(e)}\n"
            f"User: {current_user.id}\n"
            f"Tutor: {tutor_id}\n"
            f"Request ID: {request.state.request_id}"
        )
        raise HTTPException(
            status_code=500,
            detail=error_response(
                message="取消收藏失败",
                error={"request_id": request.state.request_id}
            )
        )
