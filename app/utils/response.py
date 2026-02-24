"""
统一响应格式工具
提供标准化的API响应格式
"""

from typing import Any, Optional, Dict, List, Union
from pydantic import BaseModel


class StandardResponse(BaseModel):
    """标准响应模型"""
    success: bool
    message: Optional[str] = None
    data: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
    meta: Optional[Dict[str, Any]] = None


def success_response(
    data: Any = None,
    message: str = "操作成功",
    meta: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    成功响应
    
    Args:
        data: 响应数据
        message: 响应消息
        meta: 元数据（如分页信息）
    
    Returns:
        标准成功响应格式
    """
    response = {
        "success": True,
        "message": message,
        "data": data
    }
    if meta:
        response["meta"] = meta
    return response


def error_response(
    message: str = "操作失败",
    error: Optional[Dict[str, Any]] = None,
    data: Any = None
) -> Dict[str, Any]:
    """
    错误响应
    
    Args:
        message: 错误消息
        error: 错误详情
        data: 响应数据（可选）
    
    Returns:
        标准错误响应格式
    """
    response = {
        "success": False,
        "message": message,
        "data": data
    }
    if error:
        response["error"] = error
    return response


def paginated_response(
    data: List[Any],
    total: int,
    page: int,
    page_size: int,
    message: str = "查询成功"
) -> Dict[str, Any]:
    """
    分页响应
    
    Args:
        data: 分页数据列表
        total: 总记录数
        page: 当前页码
        page_size: 每页大小
        message: 响应消息
    
    Returns:
        标准分页响应格式
    """
    total_pages = (total + page_size - 1) // page_size
    
    meta = {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1
    }
    
    return success_response(
        data=data,
        message=message,
        meta=meta
    )


def validation_error_response(
    errors: Union[List[Dict[str, Any]], Dict[str, Any]],
    message: str = "请求参数验证失败"
) -> Dict[str, Any]:
    """
    参数验证错误响应
    
    Args:
        errors: 验证错误详情
        message: 错误消息
    
    Returns:
        标准验证错误响应格式
    """
    error_details = {
        "type": "validation_error",
        "details": errors
    }
    
    return error_response(
        message=message,
        error=error_details
    )


def business_error_response(
    code: str,
    message: str,
    details: Optional[Any] = None
) -> Dict[str, Any]:
    """
    业务错误响应
    
    Args:
        code: 错误码
        message: 错误消息
        details: 错误详情
    
    Returns:
        标准业务错误响应格式
    """
    error_details = {
        "type": "business_error",
        "code": code
    }
    
    if details:
        error_details["details"] = details
    
    return error_response(
        message=message,
        error=error_details
    )