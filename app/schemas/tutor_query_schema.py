"""
导师查询参数模型
定义导师查询和筛选的请求参数
"""

from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class SortField(str, Enum):
    """排序字段枚举"""
    CREATED_AT = "created_at"  # 创建时间
    UPDATED_AT = "updated_at"  # 更新时间
    NAME = "name"  # 姓名
    PAPER_COUNT = "paper_count"  # 论文数量
    PROJECT_COUNT = "project_count"  # 项目数量


class SortOrder(str, Enum):
    """排序方向枚举"""
    ASC = "asc"  # 升序
    DESC = "desc"  # 降序


class RecruitmentType(str, Enum):
    """招生类型枚举"""
    ACADEMIC = "academic"  # 学硕
    PROFESSIONAL = "professional"  # 专硕
    BOTH = "both"  # 两者都招


class TutorQueryParams(BaseModel):
    """导师查询参数模型"""
    
    # 基础查询参数
    keyword: Optional[str] = Field(None, description="搜索关键词（姓名/研究方向/院校/专业）")
    name: Optional[str] = Field(None, description="导师姓名（模糊匹配）")
    school: Optional[str] = Field(None, description="学校名称（模糊匹配）")
    department: Optional[str] = Field(None, description="院系名称（模糊匹配）")
    
    # 高级筛选参数
    research_direction: Optional[str] = Field(None, description="研究方向（模糊匹配）")
    title: Optional[str] = Field(None, description="职称（精确匹配或模糊匹配）")
    recruitment_type: Optional[RecruitmentType] = Field(None, description="招生类型：academic(学硕)/professional(专硕)/both(都招)")
    has_projects: Optional[bool] = Field(None, description="是否有课题/项目")
    has_funding: Optional[bool] = Field(None, description="是否有科研经费")
    tags: Optional[List[str]] = Field(None, description="标签列表（任意匹配）")
    
    # 论文和项目筛选
    min_papers: Optional[int] = Field(None, ge=0, description="最少论文数量")
    max_papers: Optional[int] = Field(None, ge=0, description="最多论文数量")
    min_projects: Optional[int] = Field(None, ge=0, description="最少项目数量")
    max_projects: Optional[int] = Field(None, ge=0, description="最多项目数量")
    
    # 分页参数
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(10, ge=1, le=100, description="每页数量")
    
    # 排序参数
    sort_by: SortField = Field(SortField.CREATED_AT, description="排序字段")
    sort_order: SortOrder = Field(SortOrder.DESC, description="排序方向")


class TutorListResponse(BaseModel):
    """导师列表响应模型"""
    list: List[dict]  # 导师列表
    total: int  # 总数
    page: int  # 当前页码
    page_size: int  # 每页数量
    total_pages: int  # 总页数
    
    class Config:
        from_attributes = True


class TutorFilterOptions(BaseModel):
    """导师筛选选项模型（用于前端展示筛选条件）"""
    schools: List[str] = Field([], description="学校列表")
    departments: List[str] = Field([], description="院系列表")
    titles: List[str] = Field([], description="职称列表")
    research_directions: List[str] = Field([], description="研究方向列表")
    tags: List[str] = Field([], description="标签列表")
    recruitment_types: List[dict] = Field(
        [
            {"value": "academic", "label": "学硕"},
            {"value": "professional", "label": "专硕"},
            {"value": "both", "label": "学硕+专硕"}
        ],
        description="招生类型列表"
    )
