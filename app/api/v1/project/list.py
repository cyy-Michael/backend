"""
合作项目接口
提供项目列表查询、详情展示和申请功能
"""

from fastapi import APIRouter, HTTPException, Depends, Request, Query
from typing import List, Optional
import uuid
from datetime import datetime

from app.models import (
    User, Project, ProjectBrief, ProjectDetail,
    ProjectApplication, ProjectApplicationCreate, ProjectApplicationResponse
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
    prefix="/project",
    tags=["project"]
)


@router.get(
    "/list",
    summary="项目列表",
    description="获取合作项目列表，支持分页和类型筛选",
)
async def get_project_list(
    request: Request,
    type: str = Query("all", description="项目类型: ai/bigdata/iot/all"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    项目列表接口
    
    Args:
        request: 请求对象
        type: 项目类型
        page: 页码
        page_size: 每页数量
        current_user: 当前登录用户（可选）
    
    Returns:
        项目列表
    """
    try:
        if type not in ["ai", "bigdata", "iot", "all"]:
            raise HTTPException(
                status_code=400,
                detail=business_error_response(
                    code="INVALID_TYPE",
                    message="无效的项目类型"
                )
            )
        
        db = get_db()
        
        # 构建查询条件
        query = {}
        if type != "all":
            query["type"] = type
        
        # 计算分页
        skip = (page - 1) * page_size
        
        # 获取总数
        total = db.projects.count_documents(query)
        
        # 获取数据
        projects = db.projects.find(query).sort("created_at", -1).skip(skip).limit(page_size)
        
        # 转换为响应模型
        project_list = []
        for project in projects:
            project_brief = ProjectBrief(
                id=project["id"],
                title=project["title"],
                type=project["type"],
                tags=project.get("tags", []),
                description=project.get("description"),
                members=project.get("members", [])
            )
            project_list.append(project_brief)
        
        api_logger.info(
            f"获取项目列表成功\n"
            f"类型: {type}, 分页: page={page}, page_size={page_size}\n"
            f"结果: {len(project_list)}/{total}\n"
            f"Request ID: {request.state.request_id}"
        )
        
        return success_response(
            data={
                "list": project_list,
                "total": total,
                "page": page,
                "pageSize": page_size
            },
            message="获取项目列表成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(
            f"获取项目列表失败: {str(e)}\n"
            f"Type: {type}\n"
            f"Request ID: {request.state.request_id}"
        )
        raise HTTPException(
            status_code=500,
            detail=error_response(
                message="获取项目列表失败",
                error={"request_id": request.state.request_id}
            )
        )


@router.get(
    "/detail/{project_id}",
    summary="项目详情",
    description="获取项目详细信息",
)
async def get_project_detail(
    request: Request,
    project_id: str,
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    项目详情接口
    
    Args:
        request: 请求对象
        project_id: 项目ID
        current_user: 当前登录用户（可选）
    
    Returns:
        项目详细信息
    """
    try:
        db = get_db()
        
        # 获取项目信息
        project = db.projects.find_one({"id": project_id})
        
        if not project:
            raise HTTPException(
                status_code=404,
                detail=business_error_response(
                    code="PROJECT_NOT_FOUND",
                    message="项目不存在"
                )
            )
        
        # 构建响应数据
        detail_data = ProjectDetail(
            id=project["id"],
            title=project["title"],
            type=project["type"],
            tags=project.get("tags", []),
            description=project.get("description"),
            requirements=project.get("requirements"),
            members=project.get("members", []),
            contact_info=project.get("contact_info"),
            created_at=project["created_at"]
        )
        
        # 检查用户是否已申请
        if current_user:
            application = db.project_applications.find_one({
                "user_id": current_user.id,
                "project_id": project_id
            })
            detail_data.__dict__["is_applied"] = application is not None
        
        api_logger.info(
            f"获取项目详情成功: {project_id} - {project['title']}\n"
            f"Request ID: {request.state.request_id}"
        )
        
        return success_response(
            data=detail_data,
            message="获取项目详情成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(
            f"获取项目详情失败: {str(e)}\n"
            f"Project ID: {project_id}\n"
            f"Request ID: {request.state.request_id}"
        )
        raise HTTPException(
            status_code=500,
            detail=error_response(
                message="获取项目详情失败",
                error={"request_id": request.state.request_id}
            )
        )


@router.post(
    "/apply",
    summary="申请加入项目",
    description="申请加入合作项目",
    response_model=ProjectApplicationResponse
)
async def apply_project(
    request: Request,
    application_data: ProjectApplicationCreate,
    current_user: User = Depends(get_current_user)
):
    """
    申请加入项目接口
    
    Args:
        request: 请求对象
        application_data: 申请数据
        current_user: 当前登录用户
    
    Returns:
        ProjectApplicationResponse: 申请结果
    """
    try:
        db = get_db()
        
        # 检查项目是否存在
        project = db.projects.find_one({"id": application_data.project_id})
        if not project:
            raise HTTPException(
                status_code=404,
                detail=business_error_response(
                    code="PROJECT_NOT_FOUND",
                    message="项目不存在"
                )
            )
        
        # 检查是否已经申请过
        existing_application = db.project_applications.find_one({
            "user_id": current_user.id,
            "project_id": application_data.project_id
        })
        
        if existing_application:
            raise HTTPException(
                status_code=400,
                detail=business_error_response(
                    code="ALREADY_APPLIED",
                    message="您已经申请过该项目"
                )
            )
        
        # 创建申请记录
        new_application = {
            "id": str(uuid.uuid4()),
            "user_id": current_user.id,
            "project_id": application_data.project_id,
            "reason": application_data.reason,
            "resume": application_data.resume,
            "status": "pending",  # pending, approved, rejected
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        result = db.project_applications.insert_one(new_application)
        
        if not result.inserted_id:
            raise HTTPException(
                status_code=500,
                detail=error_response(
                    message="创建申请失败",
                    error={"type": "database_error"}
                )
            )
        
        api_logger.info(
            f"项目申请成功: {current_user.id} - {project['title']}\n"
            f"Application ID: {new_application['id']}\n"
            f"Request ID: {request.state.request_id}"
        )
        
        return ProjectApplicationResponse(
            application_id=new_application["id"],
            status=new_application["status"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(
            f"项目申请失败: {str(e)}\n"
            f"User: {current_user.id}\n"
            f"Project ID: {application_data.project_id}\n"
            f"Request ID: {request.state.request_id}"
        )
        raise HTTPException(
            status_code=500,
            detail=error_response(
                message="项目申请失败",
                error={"request_id": request.state.request_id}
            )
        )


@router.get(
    "/applications",
    summary="获取申请列表",
    description="获取用户的项目申请列表"
)
async def get_project_applications(
    request: Request,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    获取项目申请列表接口
    
    Args:
        request: 请求对象
        status: 申请状态筛选
        current_user: 当前登录用户
    
    Returns:
        申请列表
    """
    try:
        db = get_db()
        
        # 构建查询条件
        query = {"user_id": current_user.id}
        
        if status:
            query["status"] = status
        
        # 获取申请列表
        applications = db.project_applications.find(query).sort("created_at", -1)
        
        application_list = []
        for application in applications:
            # 获取项目信息
            project = db.projects.find_one({"id": application["project_id"]})
            
            application_info = {
                "id": application["id"],
                "project": {
                    "id": project["id"] if project else application["project_id"],
                    "title": project["title"] if project else "未知项目",
                    "type": project["type"] if project else "unknown"
                },
                "reason": application["reason"],
                "status": application["status"],
                "created_at": application["created_at"],
                "updated_at": application["updated_at"]
            }
            
            application_list.append(application_info)
        
        return success_response(
            data={"list": application_list},
            message="获取申请列表成功"
        )
        
    except Exception as e:
        api_logger.error(
            f"获取申请列表失败: {str(e)}\n"
            f"User: {current_user.id}\n"
            f"Status: {status}\n"
            f"Request ID: {request.state.request_id}"
        )
        raise HTTPException(
            status_code=500,
            detail=error_response(
                message="获取申请列表失败",
                error={"request_id": request.state.request_id}
            )
        )