"""
API路由模块
注册所有API路由
"""

from fastapi import APIRouter
from app.api.v1 import v1_router

# 创建主API路由
api_router = APIRouter(
    prefix="/api"
)

# 注册v1版本的路由
api_router.include_router(v1_router, tags=["v1"])

__all__ = ["api_router"]