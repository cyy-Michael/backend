"""
导师管理接口（管理员）
提供导师信息的新增、更新、删除等管理功能
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from typing import List
from datetime import datetime
import uuid

from app.models import User
from app.schemas.tutor_schema import (
    TutorCreateRequest,
    TutorUpdateRequest,
    TutorResponse,
    TutorDeleteResponse,
    TutorBatchDeleteRequest,
    TutorBatchDeleteResponse
)
from app.utils import (
    get_current_admin,
    success_response,
    error_response,
    business_error_response,
    api_logger
)
from app.db.mongo import find_one, insert_one, update_one, delete_one, get_collection

router = APIRouter(
    prefix="/tutor",
    tags=["tutor", "admin"]
)


@router.post(
    "/admin/create",
    summary="新增导师信息（管理员）",
    description="管理员新增导师信息，包括基本信息、论文、项目等"
)
async def create_tutor(
    request: Request,
    tutor_data: TutorCreateRequest,
    current_admin: User = Depends(get_current_admin)
):
    """
    新增导师信息接口（管理员权限）
    
    Args:
        request: 请求对象
        tutor_data: 导师信息数据
        current_admin: 当前管理员用户（通过JWT token和管理员权限验证）
    
    Returns:
        创建的导师信息
    
    Raises:
        HTTPException: 当创建失败时抛出
    """
    try:
        # 生成导师ID
        tutor_id = f"tutor_{uuid.uuid4().hex[:12]}"
        
        # 构建导师基本信息
        tutor_doc = {
            "id": tutor_id,
            "name": tutor_data.name,
            "school_name": tutor_data.school,
            "department_name": tutor_data.department,
            "title": tutor_data.title,
            "research_direction": tutor_data.research_direction,
            "email": tutor_data.email,
            "phone": tutor_data.phone,
            "avatar_url": tutor_data.avatar_url,
            "personal_page_url": tutor_data.personal_page_url,
            "bio": tutor_data.bio,
            "tags": tutor_data.tags,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "created_by": current_admin.id  # 记录创建者
        }
        
        # 插入导师基本信息
        result = await insert_one("tutors", tutor_doc)
        
        if not result:
            raise HTTPException(
                status_code=500,
                detail=business_error_response(
                    code="CREATE_FAILED",
                    message="创建导师信息失败"
                )
            )
        
        # 如果有论文信息，插入论文数据
        if tutor_data.papers:
            papers_collection = get_collection("papers")
            papers_to_insert = []
            for paper in tutor_data.papers:
                paper_doc = {
                    "id": f"paper_{uuid.uuid4().hex[:12]}",
                    "tutor_id": tutor_id,
                    "title": paper.title,
                    "authors": paper.authors,
                    "journal": paper.journal,
                    "year": paper.year,
                    "doi": paper.doi,
                    "abstract": paper.abstract,
                    "created_at": datetime.now()
                }
                papers_to_insert.append(paper_doc)
            
            if papers_to_insert:
                await papers_collection.insert_many(papers_to_insert)
        
        # 如果有项目信息，插入项目数据
        if tutor_data.projects:
            projects_collection = get_collection("projects")
            projects_to_insert = []
            for project in tutor_data.projects:
                project_doc = {
                    "id": f"project_{uuid.uuid4().hex[:12]}",
                    "tutor_id": tutor_id,
                    "title": project.title,
                    "funding": project.funding,
                    "start_date": project.start_date,
                    "end_date": project.end_date,
                    "description": project.description,
                    "created_at": datetime.now()
                }
                projects_to_insert.append(project_doc)
            
            if projects_to_insert:
                await projects_collection.insert_many(projects_to_insert)
        
        # 查询完整的导师信息（包括论文和项目）
        created_tutor = await get_tutor_with_details(tutor_id)
        
        api_logger.info(
            f"导师信息创建成功: {tutor_id} - {tutor_data.name}\n"
            f"创建者: {current_admin.id} - {current_admin.nickname}\n"
            f"论文数量: {len(tutor_data.papers)}\n"
            f"项目数量: {len(tutor_data.projects)}\n"
            f"Request ID: {request.state.request_id}"
        )
        
        return success_response(
            message="导师信息创建成功",
            data=created_tutor
        )
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(
            f"创建导师信息失败: {str(e)}\n"
            f"管理员: {current_admin.id}\n"
            f"Request ID: {request.state.request_id}"
        )
        raise HTTPException(
            status_code=500,
            detail=error_response(
                message="创建导师信息失败",
                error={"request_id": request.state.request_id}
            )
        )


@router.put(
    "/admin/update/{tutor_id}",
    summary="更新导师信息（管理员）",
    description="管理员更新导师信息，支持部分字段更新"
)
async def update_tutor(
    request: Request,
    tutor_id: str,
    tutor_data: TutorUpdateRequest,
    current_admin: User = Depends(get_current_admin)
):
    """
    更新导师信息接口（管理员权限）
    
    Args:
        request: 请求对象
        tutor_id: 导师ID
        tutor_data: 要更新的导师信息
        current_admin: 当前管理员用户
    
    Returns:
        更新后的导师信息
    
    Raises:
        HTTPException: 当导师不存在或更新失败时抛出
    """
    try:
        # 验证导师是否存在
        existing_tutor = await find_one("tutors", {"id": tutor_id})
        if not existing_tutor:
            api_logger.warning(
                f"导师不存在: {tutor_id}\n"
                f"管理员: {current_admin.id}\n"
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
        
        # 构建更新数据
        update_data = {}
        updated_fields = []
        
        if tutor_data.name is not None:
            update_data["name"] = tutor_data.name
            updated_fields.append("name")
        
        if tutor_data.school is not None:
            update_data["school_name"] = tutor_data.school
            updated_fields.append("school")
        
        if tutor_data.department is not None:
            update_data["department_name"] = tutor_data.department
            updated_fields.append("department")
        
        if tutor_data.title is not None:
            update_data["title"] = tutor_data.title
            updated_fields.append("title")
        
        if tutor_data.research_direction is not None:
            update_data["research_direction"] = tutor_data.research_direction
            updated_fields.append("research_direction")
        
        if tutor_data.email is not None:
            update_data["email"] = tutor_data.email
            updated_fields.append("email")
        
        if tutor_data.phone is not None:
            update_data["phone"] = tutor_data.phone
            updated_fields.append("phone")
        
        if tutor_data.avatar_url is not None:
            update_data["avatar_url"] = tutor_data.avatar_url
            updated_fields.append("avatar_url")
        
        if tutor_data.personal_page_url is not None:
            update_data["personal_page_url"] = tutor_data.personal_page_url
            updated_fields.append("personal_page_url")
        
        if tutor_data.bio is not None:
            update_data["bio"] = tutor_data.bio
            updated_fields.append("bio")
        
        if tutor_data.tags is not None:
            update_data["tags"] = tutor_data.tags
            updated_fields.append("tags")
        
        # 如果没有要更新的字段
        if not update_data and tutor_data.papers is None and tutor_data.projects is None:
            return success_response(
                message="没有需要更新的字段",
                data=await get_tutor_with_details(tutor_id)
            )
        
        # 更新导师基本信息
        if update_data:
            update_data["updated_at"] = datetime.now()
            update_data["updated_by"] = current_admin.id  # 记录更新者
            
            success = await update_one("tutors", {"id": tutor_id}, update_data)
            
            if not success:
                raise HTTPException(
                    status_code=500,
                    detail=business_error_response(
                        code="UPDATE_FAILED",
                        message="更新导师信息失败"
                    )
                )
        
        # 更新论文信息（完全替换）
        if tutor_data.papers is not None:
            papers_collection = get_collection("papers")
            # 删除旧的论文
            await papers_collection.delete_many({"tutor_id": tutor_id})
            # 插入新的论文
            if tutor_data.papers:
                papers_to_insert = []
                for paper in tutor_data.papers:
                    paper_doc = {
                        "id": f"paper_{uuid.uuid4().hex[:12]}",
                        "tutor_id": tutor_id,
                        "title": paper.title,
                        "authors": paper.authors,
                        "journal": paper.journal,
                        "year": paper.year,
                        "doi": paper.doi,
                        "abstract": paper.abstract,
                        "created_at": datetime.now()
                    }
                    papers_to_insert.append(paper_doc)
                
                if papers_to_insert:
                    await papers_collection.insert_many(papers_to_insert)
            updated_fields.append("papers")
        
        # 更新项目信息（完全替换）
        if tutor_data.projects is not None:
            projects_collection = get_collection("projects")
            # 删除旧的项目
            await projects_collection.delete_many({"tutor_id": tutor_id})
            # 插入新的项目
            if tutor_data.projects:
                projects_to_insert = []
                for project in tutor_data.projects:
                    project_doc = {
                        "id": f"project_{uuid.uuid4().hex[:12]}",
                        "tutor_id": tutor_id,
                        "title": project.title,
                        "funding": project.funding,
                        "start_date": project.start_date,
                        "end_date": project.end_date,
                        "description": project.description,
                        "created_at": datetime.now()
                    }
                    projects_to_insert.append(project_doc)
                
                if projects_to_insert:
                    await projects_collection.insert_many(projects_to_insert)
            updated_fields.append("projects")
        
        # 查询更新后的导师信息
        updated_tutor = await get_tutor_with_details(tutor_id)
        
        api_logger.info(
            f"导师信息更新成功: {tutor_id} - {existing_tutor['name']}\n"
            f"更新者: {current_admin.id} - {current_admin.nickname}\n"
            f"更新字段: {', '.join(updated_fields)}\n"
            f"Request ID: {request.state.request_id}"
        )
        
        return success_response(
            message="导师信息更新成功",
            data={
                "updated_fields": updated_fields,
                "tutor": updated_tutor
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(
            f"更新导师信息失败: {str(e)}\n"
            f"导师ID: {tutor_id}\n"
            f"管理员: {current_admin.id}\n"
            f"Request ID: {request.state.request_id}"
        )
        raise HTTPException(
            status_code=500,
            detail=error_response(
                message="更新导师信息失败",
                error={"request_id": request.state.request_id}
            )
        )


@router.delete(
    "/admin/delete/{tutor_id}",
    summary="删除导师信息（管理员）- 软删除",
    description="管理员软删除指定的导师信息，标记为已删除状态而不是物理删除"
)
async def delete_tutor(
    request: Request,
    tutor_id: str,
    current_admin: User = Depends(get_current_admin)
):
    """
    软删除导师信息接口（管理员权限）
    
    使用软删除策略，只标记删除状态，不物理删除数据
    
    Args:
        request: 请求对象
        tutor_id: 导师ID
        current_admin: 当前管理员用户
    
    Returns:
        删除结果
    
    Raises:
        HTTPException: 当导师不存在或删除失败时抛出
    """
    try:
        # 验证导师是否存在且未被删除
        existing_tutor = await find_one("tutors", {"id": tutor_id})
        if not existing_tutor:
            api_logger.warning(
                f"导师不存在: {tutor_id}\n"
                f"管理员: {current_admin.id}\n"
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
        
        # 检查是否已经被删除
        if existing_tutor.get("is_deleted", False):
            raise HTTPException(
                status_code=400,
                detail=business_error_response(
                    code="ALREADY_DELETED",
                    message="导师已被删除",
                    details={"tutor_id": tutor_id}
                )
            )
        
        # 软删除：标记删除状态
        delete_data = {
            "is_deleted": True,
            "deleted_at": datetime.now(),
            "deleted_by": current_admin.id,
            "updated_at": datetime.now()
        }
        
        success = await update_one("tutors", {"id": tutor_id}, delete_data)
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail=business_error_response(
                    code="DELETE_FAILED",
                    message="删除导师信息失败"
                )
            )
        
        api_logger.info(
            f"导师信息软删除成功: {tutor_id} - {existing_tutor['name']}\n"
            f"删除者: {current_admin.id} - {current_admin.nickname}\n"
            f"Request ID: {request.state.request_id}"
        )
        
        return success_response(
            message="导师信息删除成功",
            data=TutorDeleteResponse(
                success=True,
                tutor_id=tutor_id,
                message=f"已删除导师 {existing_tutor['name']}（软删除）"
            )
        )
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(
            f"删除导师信息失败: {str(e)}\n"
            f"导师ID: {tutor_id}\n"
            f"管理员: {current_admin.id}\n"
            f"Request ID: {request.state.request_id}"
        )
        raise HTTPException(
            status_code=500,
            detail=error_response(
                message="删除导师信息失败",
                error={"request_id": request.state.request_id}
            )
        )


@router.post(
    "/admin/batch-delete",
    summary="批量删除导师信息（管理员）- 软删除",
    description="管理员批量软删除多个导师信息"
)
async def batch_delete_tutors(
    request: Request,
    batch_request: TutorBatchDeleteRequest,
    current_admin: User = Depends(get_current_admin)
):
    """
    批量软删除导师信息接口（管理员权限）
    
    Args:
        request: 请求对象
        batch_request: 批量删除请求数据
        current_admin: 当前管理员用户
    
    Returns:
        批量删除结果
    """
    try:
        tutor_ids = batch_request.tutor_ids
        success_count = 0
        failed_count = 0
        failed_ids = []
        
        for tutor_id in tutor_ids:
            try:
                # 验证导师是否存在且未被删除
                existing_tutor = await find_one("tutors", {"id": tutor_id})
                if not existing_tutor:
                    failed_count += 1
                    failed_ids.append(tutor_id)
                    continue
                
                # 如果已经被删除，跳过
                if existing_tutor.get("is_deleted", False):
                    failed_count += 1
                    failed_ids.append(tutor_id)
                    continue
                
                # 软删除：标记删除状态
                delete_data = {
                    "is_deleted": True,
                    "deleted_at": datetime.now(),
                    "deleted_by": current_admin.id,
                    "updated_at": datetime.now()
                }
                
                success = await update_one("tutors", {"id": tutor_id}, delete_data)
                
                if success:
                    success_count += 1
                else:
                    failed_count += 1
                    failed_ids.append(tutor_id)
                    
            except Exception as e:
                api_logger.error(f"删除导师失败: {tutor_id} - {str(e)}")
                failed_count += 1
                failed_ids.append(tutor_id)
        
        api_logger.info(
            f"批量软删除导师: 成功{success_count}个，失败{failed_count}个\n"
            f"管理员: {current_admin.id} - {current_admin.nickname}\n"
            f"Request ID: {request.state.request_id}"
        )
        
        return success_response(
            message=f"批量删除完成：成功{success_count}个，失败{failed_count}个",
            data=TutorBatchDeleteResponse(
                success_count=success_count,
                failed_count=failed_count,
                total_count=len(tutor_ids),
                failed_ids=failed_ids
            )
        )
        
    except Exception as e:
        api_logger.error(
            f"批量删除导师失败: {str(e)}\n"
            f"管理员: {current_admin.id}\n"
            f"Request ID: {request.state.request_id}"
        )
        raise HTTPException(
            status_code=500,
            detail=error_response(
                message="批量删除导师失败",
                error={"request_id": request.state.request_id}
            )
        )


@router.post(
    "/admin/batch-update",
    summary="批量修改导师信息（管理员）",
    description="管理员批量修改多个导师的相同字段"
)
async def batch_update_tutors(
    request: Request,
    batch_data: dict,
    current_admin: User = Depends(get_current_admin)
):
    """
    批量修改导师信息接口（管理员权限）
    
    Args:
        request: 请求对象
        batch_data: 批量修改数据，格式：{"tutor_ids": [...], "update_fields": {...}}
        current_admin: 当前管理员用户
    
    Returns:
        批量修改结果
    """
    try:
        tutor_ids = batch_data.get("tutor_ids", [])
        update_fields = batch_data.get("update_fields", {})
        
        if not tutor_ids or not update_fields:
            raise HTTPException(
                status_code=400,
                detail=business_error_response(
                    code="INVALID_REQUEST",
                    message="导师ID列表和更新字段不能为空"
                )
            )
        
        if len(tutor_ids) > 100:
            raise HTTPException(
                status_code=400,
                detail=business_error_response(
                    code="TOO_MANY_IDS",
                    message="最多支持100个导师ID"
                )
            )
        
        success_count = 0
        failed_count = 0
        failed_ids = []
        
        # 构建更新数据
        update_data = {}
        if "title" in update_fields:
            update_data["title"] = update_fields["title"]
        if "research_direction" in update_fields:
            update_data["research_direction"] = update_fields["research_direction"]
        if "email" in update_fields:
            update_data["email"] = update_fields["email"]
        if "phone" in update_fields:
            update_data["phone"] = update_fields["phone"]
        if "tags" in update_fields:
            update_data["tags"] = update_fields["tags"]
        
        if not update_data:
            raise HTTPException(
                status_code=400,
                detail=business_error_response(
                    code="NO_VALID_FIELDS",
                    message="没有有效的更新字段"
                )
            )
        
        update_data["updated_at"] = datetime.now()
        update_data["updated_by"] = current_admin.id
        
        for tutor_id in tutor_ids:
            try:
                # 验证导师是否存在且未被删除
                existing_tutor = await find_one("tutors", {"id": tutor_id})
                if not existing_tutor or existing_tutor.get("is_deleted", False):
                    failed_count += 1
                    failed_ids.append(tutor_id)
                    continue
                
                # 更新导师信息
                success = await update_one("tutors", {"id": tutor_id}, update_data)
                
                if success:
                    success_count += 1
                else:
                    failed_count += 1
                    failed_ids.append(tutor_id)
                    
            except Exception as e:
                api_logger.error(f"批量更新导师失败: {tutor_id} - {str(e)}")
                failed_count += 1
                failed_ids.append(tutor_id)
        
        api_logger.info(
            f"批量修改导师: 成功{success_count}个，失败{failed_count}个\n"
            f"管理员: {current_admin.id} - {current_admin.nickname}\n"
            f"更新字段: {list(update_data.keys())}\n"
            f"Request ID: {request.state.request_id}"
        )
        
        return success_response(
            message=f"批量修改完成：成功{success_count}个，失败{failed_count}个",
            data={
                "success_count": success_count,
                "failed_count": failed_count,
                "total_count": len(tutor_ids),
                "failed_ids": failed_ids,
                "updated_fields": list(update_data.keys())
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(
            f"批量修改导师失败: {str(e)}\n"
            f"管理员: {current_admin.id}\n"
            f"Request ID: {request.state.request_id}"
        )
        raise HTTPException(
            status_code=500,
            detail=error_response(
                message="批量修改导师失败",
                error={"request_id": request.state.request_id}
            )
        )


@router.post(
    "/admin/restore/{tutor_id}",
    summary="恢复已删除的导师（管理员）",
    description="管理员恢复软删除的导师信息"
)
async def restore_tutor(
    request: Request,
    tutor_id: str,
    current_admin: User = Depends(get_current_admin)
):
    """
    恢复已删除的导师信息接口（管理员权限）
    
    Args:
        request: 请求对象
        tutor_id: 导师ID
        current_admin: 当前管理员用户
    
    Returns:
        恢复结果
    """
    try:
        # 查找导师（包括已删除的）
        existing_tutor = await find_one("tutors", {"id": tutor_id})
        if not existing_tutor:
            raise HTTPException(
                status_code=404,
                detail=business_error_response(
                    code="TUTOR_NOT_FOUND",
                    message="导师不存在",
                    details={"tutor_id": tutor_id}
                )
            )
        
        # 检查是否已被删除
        if not existing_tutor.get("is_deleted", False):
            raise HTTPException(
                status_code=400,
                detail=business_error_response(
                    code="NOT_DELETED",
                    message="导师未被删除，无需恢复",
                    details={"tutor_id": tutor_id}
                )
            )
        
        # 恢复：移除删除标记
        restore_data = {
            "is_deleted": False,
            "deleted_at": None,
            "deleted_by": None,
            "restored_at": datetime.now(),
            "restored_by": current_admin.id,
            "updated_at": datetime.now()
        }
        
        success = await update_one("tutors", {"id": tutor_id}, restore_data)
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail=business_error_response(
                    code="RESTORE_FAILED",
                    message="恢复导师信息失败"
                )
            )
        
        api_logger.info(
            f"导师信息恢复成功: {tutor_id} - {existing_tutor['name']}\n"
            f"恢复者: {current_admin.id} - {current_admin.nickname}\n"
            f"Request ID: {request.state.request_id}"
        )
        
        return success_response(
            message="导师信息恢复成功",
            data={
                "success": True,
                "tutor_id": tutor_id,
                "message": f"已恢复导师 {existing_tutor['name']}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(
            f"恢复导师信息失败: {str(e)}\n"
            f"导师ID: {tutor_id}\n"
            f"管理员: {current_admin.id}\n"
            f"Request ID: {request.state.request_id}"
        )
        raise HTTPException(
            status_code=500,
            detail=error_response(
                message="恢复导师信息失败",
                error={"request_id": request.state.request_id}
            )
        )


async def get_tutor_with_details(tutor_id: str) -> dict:
    """
    获取导师完整信息（包括论文和项目）
    
    Args:
        tutor_id: 导师ID
    
    Returns:
        dict: 导师完整信息
    """
    # 获取导师基本信息
    tutor = await find_one("tutors", {"id": tutor_id})
    if not tutor:
        return None
    
    # 获取论文列表
    papers_collection = get_collection("papers")
    papers_cursor = papers_collection.find({"tutor_id": tutor_id})
    papers = await papers_cursor.to_list(length=100)
    
    # 获取项目列表
    projects_collection = get_collection("projects")
    projects_cursor = projects_collection.find({"tutor_id": tutor_id})
    projects = await projects_cursor.to_list(length=100)
    
    # 构建响应数据
    return {
        "id": tutor["id"],
        "name": tutor["name"],
        "school": tutor.get("school_name", ""),
        "department": tutor.get("department_name", ""),
        "title": tutor.get("title"),
        "research_direction": tutor.get("research_direction"),
        "email": tutor.get("email"),
        "phone": tutor.get("phone"),
        "avatar_url": tutor.get("avatar_url"),
        "personal_page_url": tutor.get("personal_page_url"),
        "bio": tutor.get("bio"),
        "papers": [
            {
                "id": p["id"],
                "title": p["title"],
                "authors": p["authors"],
                "journal": p.get("journal"),
                "year": p["year"],
                "doi": p.get("doi"),
                "abstract": p.get("abstract")
            }
            for p in papers
        ],
        "projects": [
            {
                "id": proj["id"],
                "title": proj["title"],
                "funding": proj.get("funding"),
                "start_date": proj.get("start_date"),
                "end_date": proj.get("end_date"),
                "description": proj.get("description")
            }
            for proj in projects
        ],
        "tags": tutor.get("tags", []),
        "created_at": tutor["created_at"],
        "updated_at": tutor["updated_at"]
    }
