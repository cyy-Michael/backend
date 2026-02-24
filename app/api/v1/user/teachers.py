"""
导师信息API接口
提供导师信息的CRUD操作
"""

from fastapi import APIRouter, HTTPException, Query, Request
from typing import Optional, List
from app.crud.teacher_crud import (
    get_teacher_by_email,
    get_all_teachers,
    create_teacher,
    update_teacher,
    delete_teacher
)
from app.schemas.teacher_schema import TeacherCreate, TeacherUpdate
from app.utils import (
    success_response,
    error_response,
    paginated_response,
    business_error_response,
    log_db_operation,
    validate_email,
    sanitize_input,
    db_logger,
    api_logger
)
import datetime
import time

# 创建路由实例
router = APIRouter(
    prefix="/teachers",
    tags=["teachers"],
    responses={
        404: {"description": "Not found"},
        400: {"description": "Bad request"},
        500: {"description": "Internal server error"}
    }
)


# 接口1：根据邮箱查询单个导师
@router.get(
    "/{email}",
    summary="查询单个导师信息",
    description="根据导师邮箱查询详细信息",
    response_description="导师详细信息"
)
def query_teacher(
    request: Request,
    email: str
):
    """
    根据邮箱查询单个导师信息
    
    Args:
        request: 请求对象
        email: 导师邮箱
    
    Returns:
        导师详细信息
    """
    # 验证邮箱格式
    if not validate_email(email):
        raise HTTPException(
            status_code=400,
            detail=error_response(
                message="邮箱格式不正确",
                error={"field": "email", "value": email}
            )
        )
    
    start_time = time.time()
    
    try:
        # 查询导师信息
        teacher = get_teacher_by_email(email)
        
        # 记录数据库操作日志
        log_db_operation(
            operation="find_one",
            collection="teachers",
            query={"email": email},
            execution_time=(time.time() - start_time) * 1000,
            success=True
        )
        
        if not teacher:
            raise HTTPException(
                status_code=404,
                detail=error_response(
                    message="未找到该导师信息",
                    error={"email": email}
                )
            )
        
        # 转换ObjectId为字符串
        if "_id" in teacher:
            teacher["_id"] = str(teacher["_id"])
        
        return success_response(
            data=teacher,
            message="导师信息查询成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db_logger.error(
            f"查询导师信息失败: {str(e)}\n"
            f"Email: {email}\n"
            f"Request ID: {request.state.request_id}"
        )
        raise HTTPException(
            status_code=500,
            detail=error_response(
                message="查询导师信息时发生错误",
                error={"request_id": request.state.request_id}
            )
        )


# 接口2：查询所有导师列表（支持分页）
@router.get(
    "/",
    summary="查询导师列表",
    description="查询所有导师信息，支持分页和简单过滤",
    response_description="导师信息列表"
)
def query_all_teachers(
    request: Request,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页大小"),
    name: Optional[str] = Query(None, description="导师姓名过滤"),
    academy: Optional[str] = Query(None, description="学院名称过滤")
):
    """
    查询所有导师列表
    
    Args:
        request: 请求对象
        page: 页码，从1开始
        page_size: 每页大小，1-100之间
        name: 导师姓名过滤（可选）
        academy: 学院名称过滤（可选）
    
    Returns:
        导师信息列表（分页）
    """
    start_time = time.time()
    
    try:
        # 查询所有导师
        all_teachers = get_all_teachers()
        
        # 应用过滤条件
        filtered_teachers = all_teachers
        if name:
            name = sanitize_input(name)
            filtered_teachers = [
                t for t in filtered_teachers 
                if t.get("basicInfo", {}).get("name", "").lower().find(name.lower()) != -1
            ]
        
        if academy:
            academy = sanitize_input(academy)
            filtered_teachers = [
                t for t in filtered_teachers
                if t.get("academy", {}).get("academyName", "").lower().find(academy.lower()) != -1
            ]
        
        # 计算分页
        total = len(filtered_teachers)
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        paginated_teachers = filtered_teachers[start_index:end_index]
        
        # 记录数据库操作日志
        log_db_operation(
            operation="find",
            collection="teachers",
            query={"filters": {"name": name, "academy": academy}},
            execution_time=(time.time() - start_time) * 1000,
            success=True
        )
        
        return paginated_response(
            data=paginated_teachers,
            total=total,
            page=page,
            page_size=page_size,
            message="导师列表查询成功"
        )
        
    except Exception as e:
        db_logger.error(
            f"查询导师列表失败: {str(e)}\n"
            f"Filters: name={name}, academy={academy}\n"
            f"Request ID: {request.state.request_id}"
        )
        raise HTTPException(
            status_code=500,
            detail=error_response(
                message="查询导师列表时发生错误",
                error={"request_id": request.state.request_id}
            )
        )


# 接口3：新增导师
@router.post(
    "/",
    summary="新增导师信息",
    description="添加新的导师信息",
    response_description="新增结果"
)
def add_teacher(
    request: Request,
    teacher: TeacherCreate
):
    """
    新增导师信息
    
    Args:
        request: 请求对象
        teacher: 导师信息
    
    Returns:
        新增结果
    """
    # 验证邮箱格式
    if not validate_email(teacher.email):
        raise HTTPException(
            status_code=400,
            detail=error_response(
                message="邮箱格式不正确",
                error={"field": "email", "value": teacher.email}
            )
        )
    
    start_time = time.time()
    
    try:
        # 检查邮箱是否已存在
        existing_teacher = get_teacher_by_email(teacher.email)
        if existing_teacher:
            raise HTTPException(
                status_code=400,
                detail=business_error_response(
                    code="TEACHER_EXISTS",
                    message="该导师邮箱已存在",
                    details={"email": teacher.email}
                )
            )
        
        # 转换为字典并添加时间字段
        teacher_data = teacher.model_dump()
        current_time = datetime.datetime.now().isoformat()
        teacher_data["createTime"] = current_time
        teacher_data["updateTime"] = current_time
        
        # 插入数据库
        result = create_teacher(teacher_data)
        
        # 记录数据库操作日志
        log_db_operation(
            operation="insert_one",
            collection="teachers",
            query={"email": teacher.email},
            execution_time=(time.time() - start_time) * 1000,
            success=True
        )
        
        api_logger.info(
            f"新增导师成功: {teacher.email}\n"
            f"Request ID: {request.state.request_id}"
        )
        
        return success_response(
            data=result,
            message="导师信息新增成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db_logger.error(
            f"新增导师失败: {str(e)}\n"
            f"Email: {teacher.email}\n"
            f"Request ID: {request.state.request_id}"
        )
        raise HTTPException(
            status_code=500,
            detail=error_response(
                message="新增导师信息时发生错误",
                error={"request_id": request.state.request_id}
            )
        )


# 接口4：更新导师信息
@router.put(
    "/{email}",
    summary="更新导师信息",
    description="更新指定导师的信息",
    response_description="更新结果"
)
def modify_teacher(
    request: Request,
    email: str,
    update_data: TeacherUpdate
):
    """
    更新导师信息
    
    Args:
        request: 请求对象
        email: 导师邮箱
        update_data: 更新数据
    
    Returns:
        更新结果
    """
    # 验证邮箱格式
    if not validate_email(email):
        raise HTTPException(
            status_code=400,
            detail=error_response(
                message="邮箱格式不正确",
                error={"field": "email", "value": email}
            )
        )
    
    start_time = time.time()
    
    try:
        # 检查导师是否存在
        existing_teacher = get_teacher_by_email(email)
        if not existing_teacher:
            raise HTTPException(
                status_code=404,
                detail=error_response(
                    message="未找到该导师信息",
                    error={"email": email}
                )
            )
        
        # 过滤掉None值（只更新传入的字段）
        update_dict = {
            k: v for k, v in update_data.model_dump().items() 
            if v is not None
        }
        
        if not update_dict:
            return success_response(
                message="没有需要更新的字段"
            )
        
        # 更新时间戳
        update_dict["updateTime"] = datetime.datetime.now().isoformat()
        
        # 执行更新
        success = update_teacher(email, update_dict)
        
        # 记录数据库操作日志
        log_db_operation(
            operation="update_one",
            collection="teachers",
            query={"email": email, "update_fields": list(update_dict.keys())},
            execution_time=(time.time() - start_time) * 1000,
            success=success
        )
        
        if success:
            api_logger.info(
                f"更新导师成功: {email}\n"
                f"更新字段: {list(update_dict.keys())}\n"
                f"Request ID: {request.state.request_id}"
            )
            
            return success_response(
                message="导师信息更新成功"
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=error_response(
                    message="导师信息更新失败",
                    error={"email": email}
                )
            )
            
    except HTTPException:
        raise
    except Exception as e:
        db_logger.error(
            f"更新导师失败: {str(e)}\n"
            f"Email: {email}\n"
            f"Update fields: {list(update_dict.keys()) if 'update_dict' in locals() else []}\n"
            f"Request ID: {request.state.request_id}"
        )
        raise HTTPException(
            status_code=500,
            detail=error_response(
                message="更新导师信息时发生错误",
                error={"request_id": request.state.request_id}
            )
        )


# 接口5：删除导师
@router.delete(
    "/{email}",
    summary="删除导师信息",
    description="删除指定的导师信息",
    response_description="删除结果"
)
def remove_teacher(
    request: Request,
    email: str
):
    """
    删除导师信息
    
    Args:
        request: 请求对象
        email: 导师邮箱
    
    Returns:
        删除结果
    """
    # 验证邮箱格式
    if not validate_email(email):
        raise HTTPException(
            status_code=400,
            detail=error_response(
                message="邮箱格式不正确",
                error={"field": "email", "value": email}
            )
        )
    
    start_time = time.time()
    
    try:
        # 检查导师是否存在
        existing_teacher = get_teacher_by_email(email)
        if not existing_teacher:
            raise HTTPException(
                status_code=404,
                detail=error_response(
                    message="未找到该导师信息",
                    error={"email": email}
                )
            )
        
        # 执行删除
        success = delete_teacher(email)
        
        # 记录数据库操作日志
        log_db_operation(
            operation="delete_one",
            collection="teachers",
            query={"email": email},
            execution_time=(time.time() - start_time) * 1000,
            success=success
        )
        
        if success:
            api_logger.info(
                f"删除导师成功: {email}\n"
                f"Request ID: {request.state.request_id}"
            )
            
            return success_response(
                message="导师信息删除成功"
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=error_response(
                    message="导师信息删除失败",
                    error={"email": email}
                )
            )
            
    except HTTPException:
        raise
    except Exception as e:
        db_logger.error(
            f"删除导师失败: {str(e)}\n"
            f"Email: {email}\n"
            f"Request ID: {request.state.request_id}"
        )
        raise HTTPException(
            status_code=500,
            detail=error_response(
                message="删除导师信息时发生错误",
                error={"request_id": request.state.request_id}
            )
        )