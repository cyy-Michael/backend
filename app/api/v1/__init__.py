"""
API v1 版本模块
注册所有v1版本的API路由
"""

from fastapi import APIRouter
from app.api.v1.auth.login import router as auth_router
from app.api.v1.user.profile import router as user_profile_router
from app.api.v1.user.favorite import router as user_favorite_router
from app.api.v1.tutor.list import router as tutor_router
from app.api.v1.tutor.manage import router as tutor_manage_router
from app.api.v1.tutor.search import router as tutor_search_router
from app.api.v1.tutor.export import router as tutor_export_router
from app.api.v1.interaction.book import router as booking_router
from app.api.v1.match.submit import router as match_router
from app.api.v1.project.list import router as project_router

# 创建v1版本的主路由
v1_router = APIRouter(
    prefix="/v1"
)

# 注册各个模块的路由
v1_router.include_router(auth_router, prefix="/auth", tags=["authentication"])
v1_router.include_router(user_profile_router, tags=["user"])
v1_router.include_router(user_favorite_router, tags=["user", "favorite"])
v1_router.include_router(tutor_router, prefix="/tutor", tags=["tutor"])
v1_router.include_router(tutor_search_router, tags=["tutor", "search"])
v1_router.include_router(tutor_manage_router, tags=["tutor", "admin"])
v1_router.include_router(tutor_export_router, tags=["tutor", "export", "admin"])
v1_router.include_router(booking_router, prefix="/service", tags=["service"])
v1_router.include_router(match_router, prefix="/match", tags=["match"])
v1_router.include_router(project_router, prefix="/project", tags=["project"])

__all__ = ["v1_router"]