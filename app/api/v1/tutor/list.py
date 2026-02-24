"""
导师列表接口
提供导师信息的查询和筛选功能
"""

from fastapi import APIRouter, HTTPException, Depends, Request, Query
from typing import List, Optional
from datetime import datetime

from app.models import User, TutorBrief
from app.api.v1.auth.login import get_current_user
from app.utils import (
    success_response,
    error_response,
    business_error_response,
    api_logger
)
from app.db.mongo import get_db

router = APIRouter(
    prefix="/tutor",
    tags=["tutor"]
)


@router.get(
    "/list",
    summary="导师列表",
    description="获取导师列表，支持分页、搜索和筛选",
)
async def get_tutor_list(
    request: Request,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    keyword: Optional[str] = Query(None, description="搜索关键词(姓名/研究方向)"),
    school: Optional[str] = Query(None, description="学校筛选"),
    department: Optional[str] = Query(None, description="学院筛选"),
    city: Optional[str] = Query(None, description="城市筛选"),
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    导师列表接口
    
    Args:
        request: 请求对象
        page: 页码
        page_size: 每页数量
        keyword: 搜索关键词
        school: 学校筛选
        department: 学院筛选
        city: 城市筛选
        current_user: 当前登录用户（可选）
    
    Returns:
        导师列表
    """
    try:
        db = get_db()
        
        # 构建查询条件
        query = {}
        
        if keyword:
            # 搜索姓名或研究方向
            query["$or"] = [
                {"name": {"$regex": keyword, "$options": "i"}},
                {"research_direction": {"$regex": keyword, "$options": "i"}}
            ]
        
        if school:
            query["school_name"] = {"$regex": school, "$options": "i"}
        
        if department:
            query["department_name"] = {"$regex": department, "$options": "i"}
        
        if city:
            query["city"] = {"$regex": city, "$options": "i"}
        
        # 计算分页
        skip = (page - 1) * page_size
        
        # 获取总数
        total = db.tutors.count_documents(query)
        
        # 获取数据
        tutors = db.tutors.find(query).sort("created_at", -1).skip(skip).limit(page_size)
        
        # 转换为响应模型
        tutor_list = []
        for tutor in tutors:
            tutor_brief = TutorBrief(
                id=tutor["id"],
                name=tutor["name"],
                title=tutor.get("title"),
                school=tutor.get("school_name", ""),
                department=tutor.get("department_name", ""),
                tags=tutor.get("tags", []),
                avatar=tutor.get("avatar_url")
            )
            tutor_list.append(tutor_brief)
        
        api_logger.info(
            f"获取导师列表成功\n"
            f"条件: keyword={keyword}, school={school}, department={department}, city={city}\n"
            f"分页: page={page}, page_size={page_size}\n"
            f"结果: {len(tutor_list)}/{total}\n"
            f"Request ID: {request.state.request_id}"
        )
        
        return success_response(
            data={
                "list": tutor_list,
                "total": total,
                "page": page,
                "pageSize": page_size
            },
            message="获取导师列表成功"
        )
        
    except Exception as e:
        api_logger.error(
            f"获取导师列表失败: {str(e)}\n"
            f"Request ID: {request.state.request_id}"
        )
        raise HTTPException(
            status_code=500,
            detail=error_response(
                message="获取导师列表失败",
                error={"request_id": request.state.request_id}
            )
        )


@router.get(
    "/detail/{tutor_id}",
    summary="导师详情",
    description="获取导师详细信息",
)
async def get_tutor_detail(
    request: Request,
    tutor_id: str,
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    导师详情接口
    
    Args:
        request: 请求对象
        tutor_id: 导师ID
        current_user: 当前登录用户（可选）
    
    Returns:
        导师详细信息
    """
    try:
        db = get_db()
        
        # 获取导师基本信息
        tutor = db.tutors.find_one({"id": tutor_id})
        
        if not tutor:
            raise HTTPException(
                status_code=404,
                detail=business_error_response(
                    code="TUTOR_NOT_FOUND",
                    message="导师不存在"
                )
            )
        
        # 获取导师详细信息（从tutor_details表）
        tutor_detail = db.tutor_details.find_one({"tutor_id": tutor_id})
        
        # 构建响应数据
        detail_data = {
            "id": tutor["id"],
            "name": tutor["name"],
            "title": tutor.get("title"),
            "school": tutor.get("school_name", ""),
            "department": tutor.get("department_name", ""),
            "avatar": tutor.get("avatar_url"),
            "bio": tutor_detail.get("bio") if tutor_detail else None,
            "email": tutor.get("email"),
            "phone": tutor.get("phone"),
            "personal_page": tutor.get("personal_page_url"),
            "research_direction": tutor.get("research_direction"),
            "papers": tutor_detail.get("papers", []) if tutor_detail else [],
            "projects": tutor_detail.get("projects", []) if tutor_detail else [],
            "coops": tutor_detail.get("coops", []) if tutor_detail else [],
            "students": tutor_detail.get("students", []) if tutor_detail else [],
            "risks": tutor_detail.get("risks", []) if tutor_detail else [],
            "socials": tutor_detail.get("socials", []) if tutor_detail else [],
            "achievements_summary": tutor_detail.get("achievements_summary") if tutor_detail else None,
            "is_collected": False
        }
        
        # 检查是否已收藏
        if current_user:
            favorite = db.favorites.find_one({
                "user_id": current_user.id,
                "target_type": "tutor",
                "target_id": tutor_id
            })
            detail_data["is_collected"] = favorite is not None
        
        api_logger.info(
            f"获取导师详情成功: {tutor_id} - {tutor['name']}\n"
            f"Request ID: {request.state.request_id}"
        )
        
        return success_response(
            data=detail_data,
            message="获取导师详情成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(
            f"获取导师详情失败: {str(e)}\n"
            f"Tutor ID: {tutor_id}\n"
            f"Request ID: {request.state.request_id}"
        )
        raise HTTPException(
            status_code=500,
            detail=error_response(
                message="获取导师详情失败",
                error={"request_id": request.state.request_id}
            )
        )


@router.get(
    "/search/suggestions",
    summary="搜索建议",
    description="获取搜索关键词建议"
)
async def get_search_suggestions(
    request: Request,
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    field: str = Query("all", description="搜索字段: all, name, school, department")
):
    """
    搜索建议接口
    
    Args:
        request: 请求对象
        keyword: 搜索关键词
        field: 搜索字段
    
    Returns:
        搜索建议列表
    """
    try:
        db = get_db()
        
        if not keyword:
            return success_response(
                data={"suggestions": []},
                message="获取搜索建议成功"
            )
        
        suggestions = []
        
        if field in ["all", "name"]:
            # 获取姓名建议
            name_suggestions = db.tutors.find(
                {"name": {"$regex": keyword, "$options": "i"}},
                {"name": 1}
            ).limit(5)
            
            for s in name_suggestions:
                suggestions.append({
                    "type": "name",
                    "value": s["name"],
                    "label": f"导师: {s['name']}"
                })
        
        if field in ["all", "school"]:
            # 获取学校建议
            school_suggestions = db.schools.find(
                {"name": {"$regex": keyword, "$options": "i"}},
                {"name": 1}
            ).limit(3)
            
            for s in school_suggestions:
                suggestions.append({
                    "type": "school",
                    "value": s["name"],
                    "label": f"学校: {s['name']}"
                })
        
        if field in ["all", "department"]:
            # 获取学院建议
            department_suggestions = db.departments.find(
                {"name": {"$regex": keyword, "$options": "i"}},
                {"name": 1}
            ).limit(3)
            
            for s in department_suggestions:
                suggestions.append({
                    "type": "department",
                    "value": s["name"],
                    "label": f"学院: {s['name']}"
                })
        
        # 去重
        seen = set()
        unique_suggestions = []
        for s in suggestions:
            key = f"{s['type']}:{s['value']}"
            if key not in seen:
                seen.add(key)
                unique_suggestions.append(s)
        
        return success_response(
            data={"suggestions": unique_suggestions[:10]},  # 最多返回10个建议
            message="获取搜索建议成功"
        )
        
    except Exception as e:
        api_logger.error(
            f"获取搜索建议失败: {str(e)}\n"
            f"Keyword: {keyword}, Field: {field}\n"
            f"Request ID: {request.state.request_id}"
        )
        raise HTTPException(
            status_code=500,
            detail=error_response(
                message="获取搜索建议失败",
                error={"request_id": request.state.request_id}
            )
        )