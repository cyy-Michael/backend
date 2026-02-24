"""
项目数据模型
定义合作项目相关的数据结构
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class ProjectMember(BaseModel):
    """项目成员模型"""
    name: str
    school: str
    role: Optional[str] = None


class ProjectBase(BaseModel):
    """项目基础模型"""
    title: str
    type: str = Field(..., pattern="^(ai|bigdata|iot|all)$")
    tags: List[str] = []
    description: Optional[str] = None
    requirements: Optional[str] = None


class ProjectCreate(ProjectBase):
    """项目创建模型"""
    members: List[ProjectMember] = []


class ProjectUpdate(ProjectBase):
    """项目更新模型"""
    title: Optional[str] = None
    type: Optional[str] = None


class ProjectInDB(ProjectBase):
    """数据库中的项目模型"""
    id: str
    members: List[ProjectMember] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Project(ProjectBase):
    """项目响应模型"""
    id: str
    members: List[ProjectMember] = []

    class Config:
        from_attributes = True


class ProjectBrief(BaseModel):
    """项目简略信息模型（用于列表展示）"""
    id: str
    title: str
    type: str
    tags: List[str] = []
    description: Optional[str] = None
    members: List[Dict[str, str]] = []

    class Config:
        from_attributes = True


class ProjectDetail(Project):
    """项目详细信息模型"""
    requirements: Optional[str] = None
    contact_info: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ProjectApplication(BaseModel):
    """项目申请模型"""
    id: str
    user_id: str
    project_id: str
    reason: str
    resume: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProjectApplicationCreate(BaseModel):
    """创建项目申请请求模型"""
    project_id: str
    reason: str
    resume: Optional[str] = None


class ProjectApplicationResponse(BaseModel):
    """项目申请响应模型"""
    application_id: str
    status: str