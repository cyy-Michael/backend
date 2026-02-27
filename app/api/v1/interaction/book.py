"""
预约咨询接口
提供VIP用户预约导师咨询的功能
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Optional
import uuid
from datetime import datetime

from app.models import User, Booking, BookingCreate, BookingResponse
from app.api.v1.auth.login import get_current_user
from app.utils import (
    success_response,
    error_response,
    business_error_response,
    api_logger
)
from app.db.mongo import get_db

router = APIRouter(
    prefix="/service",
    tags=["service"]
)


@router.post(
    "/book",
    summary="预约咨询",
    description="VIP用户预约导师咨询",
    response_model=BookingResponse
)
async def book_consultation(
    request: Request,
    booking_data: BookingCreate,
    current_user: User = Depends(get_current_user)
):
    """
    预约咨询接口
    
    Args:
        request: 请求对象
        booking_data: 预约数据
        current_user: 当前登录用户
    
    Returns:
        BookingResponse: 预约结果
    """
    try:
        db = get_db()
        
        # 检查用户是否为VIP
        user_data = db.users.find_one({"id": current_user.id})
        if not user_data.get("vip_status", False):
            raise HTTPException(
                status_code=403,
                detail=business_error_response(
                    code="VIP_REQUIRED",
                    message="只有VIP用户才能预约咨询"
                )
            )
        
        # 检查VIP是否过期
        if user_data.get("vip_expire_date"):
            if user_data["vip_expire_date"] < datetime.now():
                raise HTTPException(
                    status_code=403,
                    detail=business_error_response(
                        code="VIP_EXPIRED",
                        message="VIP会员已过期"
                    )
                )
        
        # 检查导师是否存在
        tutor = db.tutors.find_one({"id": booking_data.tutor_id})
        if not tutor:
            raise HTTPException(
                status_code=404,
                detail=business_error_response(
                    code="TUTOR_NOT_FOUND",
                    message="导师不存在"
                )
            )
        
        # 检查是否已经有相同时间的预约
        existing_booking = db.bookings.find_one({
            "tutor_id": booking_data.tutor_id,
            "date": booking_data.date,
            "status": {"$in": ["pending", "confirmed"]}
        })
        
        if existing_booking:
            raise HTTPException(
                status_code=400,
                detail=business_error_response(
                    code="TIME_CONFLICT",
                    message="该时间段已被预约"
                )
            )
        
        # 检查用户是否已经预约过该导师
        user_booking = db.bookings.find_one({
            "user_id": current_user.id,
            "tutor_id": booking_data.tutor_id,
            "date": booking_data.date,
            "status": {"$in": ["pending", "confirmed"]}
        })
        
        if user_booking:
            raise HTTPException(
                status_code=400,
                detail=business_error_response(
                    code="DUPLICATE_BOOKING",
                    message="您已经预约过该时间段"
                )
            )
        
        # 创建预约记录
        new_booking = {
            "id": str(uuid.uuid4()),
            "user_id": current_user.id,
            "tutor_id": booking_data.tutor_id,
            "date": booking_data.date,
            "message": booking_data.message,
            "status": "pending",  # pending, confirmed, cancelled, completed
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        result = db.bookings.insert_one(new_booking)
        
        if not result.inserted_id:
            raise HTTPException(
                status_code=500,
                detail=error_response(
                    message="创建预约失败",
                    error={"type": "database_error"}
                )
            )
        
        api_logger.info(
            f"预约咨询成功: {current_user.id} - {tutor['name']} - {booking_data.date}\n"
            f"Booking ID: {new_booking['id']}\n"
            f"Request ID: {request.state.request_id}"
        )
        
        return BookingResponse(
            booking_id=new_booking["id"],
            status=new_booking["status"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(
            f"预约咨询失败: {str(e)}\n"
            f"User: {current_user.id}\n"
            f"Tutor ID: {booking_data.tutor_id}\n"
            f"Date: {booking_data.date}\n"
            f"Request ID: {request.state.request_id}"
        )
        raise HTTPException(
            status_code=500,
            detail=error_response(
                message="预约咨询失败",
                error={"request_id": request.state.request_id}
            )
        )


@router.get(
    "/bookings",
    summary="获取预约列表",
    description="获取用户的预约列表"
)
async def get_bookings(
    request: Request,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    获取预约列表接口
    
    Args:
        request: 请求对象
        status: 预约状态筛选
        current_user: 当前登录用户
    
    Returns:
        预约列表
    """
    try:
        db = get_db()
        
        # 构建查询条件
        query = {"user_id": current_user.id}
        
        if status:
            query["status"] = status
        
        # 获取预约列表
        bookings = db.bookings.find(query).sort("created_at", -1)
        
        booking_list = []
        for booking in bookings:
            # 获取导师信息
            tutor = db.tutors.find_one({"id": booking["tutor_id"]})
            
            booking_info = {
                "id": booking["id"],
                "tutor": {
                    "id": tutor["id"] if tutor else booking["tutor_id"],
                    "name": tutor["name"] if tutor else "未知导师",
                    "avatar": tutor.get("avatar_url") if tutor else None
                },
                "date": booking["date"],
                "message": booking["message"],
                "status": booking["status"],
                "created_at": booking["created_at"],
                "updated_at": booking["updated_at"]
            }
            
            booking_list.append(booking_info)
        
        return success_response(
            data={"list": booking_list},
            message="获取预约列表成功"
        )
        
    except Exception as e:
        api_logger.error(
            f"获取预约列表失败: {str(e)}\n"
            f"User: {current_user.id}\n"
            f"Status: {status}\n"
            f"Request ID: {request.state.request_id}"
        )
        raise HTTPException(
            status_code=500,
            detail=error_response(
                message="获取预约列表失败",
                error={"request_id": request.state.request_id}
            )
        )


@router.post(
    "/booking/{booking_id}/cancel",
    summary="取消预约",
    description="取消待确认的预约"
)
async def cancel_booking(
    request: Request,
    booking_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    取消预约接口
    
    Args:
        request: 请求对象
        booking_id: 预约ID
        current_user: 当前登录用户
    
    Returns:
        取消结果
    """
    try:
        db = get_db()
        
        # 查找预约记录
        booking = db.bookings.find_one({
            "id": booking_id,
            "user_id": current_user.id
        })
        
        if not booking:
            raise HTTPException(
                status_code=404,
                detail=business_error_response(
                    code="BOOKING_NOT_FOUND",
                    message="预约记录不存在"
                )
            )
        
        # 检查是否可以取消
        if booking["status"] != "pending":
            raise HTTPException(
                status_code=400,
                detail=business_error_response(
                    code="CANNOT_CANCEL",
                    message="只能取消待确认的预约"
                )
            )
        
        # 更新预约状态
        db.bookings.update_one(
            {"id": booking_id},
            {"$set": {
                "status": "cancelled",
                "updated_at": datetime.now()
            }}
        )
        
        api_logger.info(
            f"取消预约成功: {booking_id}\n"
            f"User: {current_user.id}\n"
            f"Request ID: {request.state.request_id}"
        )
        
        return success_response(
            message="取消预约成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(
            f"取消预约失败: {str(e)}\n"
            f"User: {current_user.id}\n"
            f"Booking ID: {booking_id}\n"
            f"Request ID: {request.state.request_id}"
        )
        raise HTTPException(
            status_code=500,
            detail=error_response(
                message="取消预约失败",
                error={"request_id": request.state.request_id}
            )
        )