"""
导师高级查询接口
提供基础查询和高级筛选功能
"""

from fastapi import APIRouter, HTTPException, Depends, Request, Query
from typing import List, Optional
from datetime import datetime
import math

from app.models import User, TutorBrief
from app.schemas import (
    TutorQueryParams,
    TutorListResponse,
    TutorFilterOptions,
    SortField,
    SortOrder,
    RecruitmentType
)
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
    tags=["tutor_search"]
)


@router.get(
    "/search",
    summary="导师高级查询",
    description="支持基础查询和高级筛选的导师搜索接口",
    response_model=TutorListResponse
)
async def search_tutors(
    request: Request,
    # 基础查询参数
    keyword: Optional[str] = Query(None, description="搜索关键词（姓名/研究方向/院校/专业）"),
    name: Optional[str] = Query(None, description="导师姓名（模糊匹配）"),
    school: Optional[str] = Query(None, description="学校名称（模糊匹配）"),
    department: Optional[str] = Query(None, description="院系名称（模糊匹配）"),
    
    # 高级筛选参数
    research_direction: Optional[str] = Query(None, description="研究方向（模糊匹配）"),
    title: Optional[str] = Query(None, description="职称（模糊匹配）"),
    recruitment_type: Optional[RecruitmentType] = Query(None, description="招生类型：academic(学硕)/professional(专硕)/both(都招)"),
    has_projects: Optional[bool] = Query(None, description="是否有课题/项目"),
    has_funding: Optional[bool] = Query(None, description="是否有科研经费"),
    tags: Optional[str] = Query(None, description="标签列表（逗号分隔，任意匹配）"),
    
    # 论文和项目筛选
    min_papers: Optional[int] = Query(None, ge=0, description="最少论文数量"),
    max_papers: Optional[int] = Query(None, ge=0, description="最多论文数量"),
    min_projects: Optional[int] = Query(None, ge=0, description="最少项目数量"),
    max_projects: Optional[int] = Query(None, ge=0, description="最多项目数量"),
    
    # 分页参数
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    
    # 排序参数
    sort_by: SortField = Query(SortField.CREATED_AT, description="排序字段"),
    sort_order: SortOrder = Query(SortOrder.DESC, description="排序方向"),
    
    # 用户认证（可选）
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    导师高级查询接口
    
    支持：
    1. 基础模糊查询：姓名、院校、专业
    2. 高级筛选：研究方向、职称、招生类型、是否有课题等
    3. 分页和排序
    
    Args:
        request: 请求对象
        keyword: 搜索关键词
        name: 导师姓名
        school: 学校名称
        department: 院系名称
        research_direction: 研究方向
        title: 职称
        recruitment_type: 招生类型
        has_projects: 是否有课题
        has_funding: 是否有科研经费
        tags: 标签列表
        min_papers: 最少论文数
        max_papers: 最多论文数
        min_projects: 最少项目数
        max_projects: 最多项目数
        page: 页码
        page_size: 每页数量
        sort_by: 排序字段
        sort_order: 排序方向
        current_user: 当前用户（可选）
    
    Returns:
        导师列表
    """
    try:
        db = get_db()
        
        # 构建查询条件
        query = {
            "$or": [
                {"is_deleted": {"$exists": False}},
                {"is_deleted": False}
            ]
        }
        
        # 基础关键词查询（搜索姓名、研究方向、学校、院系）
        if keyword:
            query["$and"] = query.get("$and", [])
            query["$and"].append({
                "$or": [
                    {"name": {"$regex": keyword, "$options": "i"}},
                    {"research_direction": {"$regex": keyword, "$options": "i"}},
                    {"school_name": {"$regex": keyword, "$options": "i"}},
                    {"department_name": {"$regex": keyword, "$options": "i"}}
                ]
            })
        
        # 姓名模糊查询
        if name:
            query["name"] = {"$regex": name, "$options": "i"}
        
        # 学校模糊查询
        if school:
            query["school_name"] = {"$regex": school, "$options": "i"}
        
        # 院系模糊查询
        if department:
            query["department_name"] = {"$regex": department, "$options": "i"}
        
        # 研究方向模糊查询
        if research_direction:
            query["research_direction"] = {"$regex": research_direction, "$options": "i"}
        
        # 职称筛选（支持模糊匹配）
        if title:
            query["title"] = {"$regex": title, "$options": "i"}
        
        # 招生类型筛选
        if recruitment_type:
            query["recruitment_type"] = recruitment_type.value
        
        # 是否有课题/项目
        if has_projects is not None:
            if has_projects:
                query["project_count"] = {"$gt": 0}
            else:
                query["$or"] = query.get("$or", [])
                query["$or"].append({"project_count": {"$exists": False}})
                query["$or"].append({"project_count": 0})
        
        # 是否有科研经费
        if has_funding is not None:
            query["has_funding"] = has_funding
        
        # 标签筛选（任意匹配）
        if tags:
            tag_list = [t.strip() for t in tags.split(",") if t.strip()]
            if tag_list:
                query["tags"] = {"$in": tag_list}
        
        # 论文数量筛选
        if min_papers is not None or max_papers is not None:
            paper_query = {}
            if min_papers is not None:
                paper_query["$gte"] = min_papers
            if max_papers is not None:
                paper_query["$lte"] = max_papers
            if paper_query:
                query["paper_count"] = paper_query
        
        # 项目数量筛选
        if min_projects is not None or max_projects is not None:
            project_query = {}
            if min_projects is not None:
                project_query["$gte"] = min_projects
            if max_projects is not None:
                project_query["$lte"] = max_projects
            if project_query:
                query["project_count"] = project_query
        
        # 获取总数
        total = await db.tutors.count_documents(query)
        
        # 计算总页数
        total_pages = math.ceil(total / page_size) if total > 0 else 0
        
        # 构建排序条件
        sort_direction = -1 if sort_order == SortOrder.DESC else 1
        sort_field = sort_by.value
        
        # 计算分页
        skip = (page - 1) * page_size
        
        # 获取数据
        tutors_cursor = db.tutors.find(query).sort(sort_field, sort_direction).skip(skip).limit(page_size)
        tutors = await tutors_cursor.to_list(length=page_size)
        
        # 转换为响应模型
        tutor_list = []
        for tutor in tutors:
            tutor_brief = {
                "id": tutor["id"],
                "name": tutor["name"],
                "title": tutor.get("title"),
                "school": tutor.get("school_name", ""),
                "department": tutor.get("department_name", ""),
                "research_direction": tutor.get("research_direction"),
                "tags": tutor.get("tags", []),
                "avatar": tutor.get("avatar_url"),
                "paper_count": tutor.get("paper_count", 0),
                "project_count": tutor.get("project_count", 0),
                "recruitment_type": tutor.get("recruitment_type"),
                "has_funding": tutor.get("has_funding", False)
            }
            tutor_list.append(tutor_brief)
        
        api_logger.info(
            f"导师高级查询成功\n"
            f"查询条件: keyword={keyword}, name={name}, school={school}, department={department}\n"
            f"高级筛选: research_direction={research_direction}, title={title}, recruitment_type={recruitment_type}\n"
            f"分页: page={page}, page_size={page_size}, sort_by={sort_by}, sort_order={sort_order}\n"
            f"结果: {len(tutor_list)}/{total}\n"
            f"Request ID: {request.state.request_id}"
        )
        
        return success_response(
            data={
                "list": tutor_list,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages
            },
            message="查询导师列表成功"
        )
        
    except Exception as e:
        api_logger.error(
            f"导师高级查询失败: {str(e)}\n"
            f"Request ID: {request.state.request_id}"
        )
        raise HTTPException(
            status_code=500,
            detail=error_response(
                message="查询导师列表失败",
                error={"request_id": request.state.request_id}
            )
        )


@router.get(
    "/filter-options",
    summary="获取筛选选项",
    description="获取导师筛选的可选项（学校、院系、职称等）",
    response_model=TutorFilterOptions
)
async def get_filter_options(
    request: Request,
    school: Optional[str] = Query(None, description="学校筛选（获取该学校的院系列表）")
):
    """
    获取筛选选项接口
    
    返回可用的筛选选项，用于前端展示筛选条件
    
    Args:
        request: 请求对象
        school: 学校名称（可选，用于获取该学校的院系列表）
    
    Returns:
        筛选选项
    """
    try:
        db = get_db()
        
        # 获取学校列表（去重）
        schools_cursor = db.tutors.distinct("school_name", {
            "$or": [
                {"is_deleted": {"$exists": False}},
                {"is_deleted": False}
            ]
        })
        schools = await schools_cursor
        schools = sorted([s for s in schools if s])  # 过滤空值并排序
        
        # 获取院系列表
        department_query = {
            "$or": [
                {"is_deleted": {"$exists": False}},
                {"is_deleted": False}
            ]
        }
        if school:
            department_query["school_name"] = school
        
        departments_cursor = db.tutors.distinct("department_name", department_query)
        departments = await departments_cursor
        departments = sorted([d for d in departments if d])
        
        # 获取职称列表
        titles_cursor = db.tutors.distinct("title", {
            "$or": [
                {"is_deleted": {"$exists": False}},
                {"is_deleted": False}
            ]
        })
        titles = await titles_cursor
        titles = sorted([t for t in titles if t])
        
        # 获取研究方向列表（取前50个最常见的）
        research_directions_pipeline = [
            {
                "$match": {
                    "$or": [
                        {"is_deleted": {"$exists": False}},
                        {"is_deleted": False}
                    ],
                    "research_direction": {"$exists": True, "$ne": None, "$ne": ""}
                }
            },
            {
                "$group": {
                    "_id": "$research_direction",
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"count": -1}},
            {"$limit": 50},
            {"$project": {"_id": 1}}
        ]
        research_directions_cursor = db.tutors.aggregate(research_directions_pipeline)
        research_directions = [doc["_id"] for doc in await research_directions_cursor.to_list(length=50)]
        
        # 获取标签列表（取前30个最常见的）
        tags_pipeline = [
            {
                "$match": {
                    "$or": [
                        {"is_deleted": {"$exists": False}},
                        {"is_deleted": False}
                    ],
                    "tags": {"$exists": True, "$ne": []}
                }
            },
            {"$unwind": "$tags"},
            {
                "$group": {
                    "_id": "$tags",
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"count": -1}},
            {"$limit": 30},
            {"$project": {"_id": 1}}
        ]
        tags_cursor = db.tutors.aggregate(tags_pipeline)
        tags = [doc["_id"] for doc in await tags_cursor.to_list(length=30)]
        
        api_logger.info(
            f"获取筛选选项成功\n"
            f"学校数: {len(schools)}, 院系数: {len(departments)}, 职称数: {len(titles)}\n"
            f"研究方向数: {len(research_directions)}, 标签数: {len(tags)}\n"
            f"Request ID: {request.state.request_id}"
        )
        
        return success_response(
            data={
                "schools": schools,
                "departments": departments,
                "titles": titles,
                "research_directions": research_directions,
                "tags": tags,
                "recruitment_types": [
                    {"value": "academic", "label": "学硕"},
                    {"value": "professional", "label": "专硕"},
                    {"value": "both", "label": "学硕+专硕"}
                ]
            },
            message="获取筛选选项成功"
        )
        
    except Exception as e:
        api_logger.error(
            f"获取筛选选项失败: {str(e)}\n"
            f"Request ID: {request.state.request_id}"
        )
        raise HTTPException(
            status_code=500,
            detail=error_response(
                message="获取筛选选项失败",
                error={"request_id": request.state.request_id}
            )
        )
