"""
导师CRUD相关的数据校验模型
提供导师信息新增、更新、删除的请求/响应模型
"""

from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import datetime


class PaperInput(BaseModel):
    """论文输入模型"""
    title: str = Field(..., min_length=1, max_length=500, description="论文标题")
    authors: List[str] = Field(..., min_items=1, description="作者列表")
    journal: Optional[str] = Field(None, max_length=200, description="期刊名称")
    year: int = Field(..., ge=1900, le=2100, description="发表年份")
    doi: Optional[str] = Field(None, max_length=100, description="DOI")
    abstract: Optional[str] = Field(None, max_length=2000, description="摘要")
    
    @validator('title', 'journal')
    def validate_text_fields(cls, v):
        """验证文本字段"""
        if v is not None:
            v = v.strip()
            if len(v) == 0:
                raise ValueError('字段不能为空')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "基于深度学习的图像识别研究",
                "authors": ["张三", "李四"],
                "journal": "计算机学报",
                "year": 2024,
                "doi": "10.1234/example.2024.001",
                "abstract": "本文研究了..."
            }
        }


class ProjectInput(BaseModel):
    """项目输入模型"""
    title: str = Field(..., min_length=1, max_length=500, description="项目名称")
    funding: Optional[str] = Field(None, max_length=200, description="资助来源")
    start_date: Optional[str] = Field(None, description="开始日期（YYYY-MM-DD）")
    end_date: Optional[str] = Field(None, description="结束日期（YYYY-MM-DD）")
    description: Optional[str] = Field(None, max_length=2000, description="项目描述")
    
    @validator('title', 'funding', 'description')
    def validate_text_fields(cls, v):
        """验证文本字段"""
        if v is not None:
            v = v.strip()
            if len(v) == 0:
                raise ValueError('字段不能为空')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "国家自然科学基金项目",
                "funding": "国家自然科学基金委员会",
                "start_date": "2024-01-01",
                "end_date": "2026-12-31",
                "description": "研究人工智能在医疗领域的应用"
            }
        }


class TutorCreateRequest(BaseModel):
    """导师创建请求模型"""
    name: str = Field(..., min_length=1, max_length=50, description="导师姓名")
    school: str = Field(..., min_length=1, max_length=100, description="所在院校")
    department: str = Field(..., min_length=1, max_length=100, description="所在院系/专业")
    title: Optional[str] = Field(None, max_length=50, description="职称（教授、副教授等）")
    research_direction: Optional[str] = Field(None, max_length=500, description="研究方向")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    phone: Optional[str] = Field(None, max_length=20, description="联系电话")
    avatar_url: Optional[str] = Field(None, max_length=500, description="头像URL")
    personal_page_url: Optional[str] = Field(None, max_length=500, description="个人主页URL")
    bio: Optional[str] = Field(None, max_length=2000, description="个人简介")
    papers: List[PaperInput] = Field(default_factory=list, description="论文列表")
    projects: List[ProjectInput] = Field(default_factory=list, description="项目列表")
    tags: List[str] = Field(default_factory=list, max_items=20, description="标签列表")
    
    @validator('name', 'school', 'department', 'title', 'research_direction', 'bio')
    def validate_text_fields(cls, v):
        """验证文本字段"""
        if v is not None:
            v = v.strip()
            if len(v) == 0:
                raise ValueError('字段不能为空')
        return v
    
    @validator('phone')
    def validate_phone(cls, v):
        """验证电话号码格式"""
        if v is not None:
            v = v.strip()
            # 简单验证：只包含数字、空格、短横线、括号
            import re
            if not re.match(r'^[\d\s\-\(\)\+]+$', v):
                raise ValueError('电话号码格式不正确')
        return v
    
    @validator('avatar_url', 'personal_page_url')
    def validate_url(cls, v):
        """验证URL格式"""
        if v is not None:
            v = v.strip()
            if len(v) > 0 and not (v.startswith('http://') or v.startswith('https://')):
                raise ValueError('URL必须是有效的HTTP/HTTPS地址')
        return v
    
    @validator('tags')
    def validate_tags(cls, v):
        """验证标签"""
        if v:
            # 去重
            v = list(set(v))
            # 去除空标签
            v = [tag.strip() for tag in v if tag.strip()]
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "张三",
                "school": "清华大学",
                "department": "计算机科学与技术系",
                "title": "教授",
                "research_direction": "人工智能、机器学习、计算机视觉",
                "email": "zhangsan@example.edu.cn",
                "phone": "010-12345678",
                "avatar_url": "https://example.com/avatar.jpg",
                "personal_page_url": "https://example.com/~zhangsan",
                "bio": "张三教授，博士生导师，主要研究方向为人工智能...",
                "papers": [
                    {
                        "title": "基于深度学习的图像识别研究",
                        "authors": ["张三", "李四"],
                        "journal": "计算机学报",
                        "year": 2024,
                        "doi": "10.1234/example.2024.001"
                    }
                ],
                "projects": [
                    {
                        "title": "国家自然科学基金项目",
                        "funding": "国家自然科学基金委员会",
                        "start_date": "2024-01-01",
                        "end_date": "2026-12-31"
                    }
                ],
                "tags": ["AI", "深度学习", "计算机视觉"]
            }
        }


class TutorUpdateRequest(BaseModel):
    """导师更新请求模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="导师姓名")
    school: Optional[str] = Field(None, min_length=1, max_length=100, description="所在院校")
    department: Optional[str] = Field(None, min_length=1, max_length=100, description="所在院系/专业")
    title: Optional[str] = Field(None, max_length=50, description="职称")
    research_direction: Optional[str] = Field(None, max_length=500, description="研究方向")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    phone: Optional[str] = Field(None, max_length=20, description="联系电话")
    avatar_url: Optional[str] = Field(None, max_length=500, description="头像URL")
    personal_page_url: Optional[str] = Field(None, max_length=500, description="个人主页URL")
    bio: Optional[str] = Field(None, max_length=2000, description="个人简介")
    papers: Optional[List[PaperInput]] = Field(None, description="论文列表（完全替换）")
    projects: Optional[List[ProjectInput]] = Field(None, description="项目列表（完全替换）")
    tags: Optional[List[str]] = Field(None, max_items=20, description="标签列表（完全替换）")
    
    @validator('name', 'school', 'department', 'title', 'research_direction', 'bio')
    def validate_text_fields(cls, v):
        """验证文本字段"""
        if v is not None:
            v = v.strip()
            if len(v) == 0:
                raise ValueError('字段不能为空')
        return v
    
    @validator('phone')
    def validate_phone(cls, v):
        """验证电话号码格式"""
        if v is not None:
            v = v.strip()
            import re
            if not re.match(r'^[\d\s\-\(\)\+]+$', v):
                raise ValueError('电话号码格式不正确')
        return v
    
    @validator('avatar_url', 'personal_page_url')
    def validate_url(cls, v):
        """验证URL格式"""
        if v is not None:
            v = v.strip()
            if len(v) > 0 and not (v.startswith('http://') or v.startswith('https://')):
                raise ValueError('URL必须是有效的HTTP/HTTPS地址')
        return v
    
    @validator('tags')
    def validate_tags(cls, v):
        """验证标签"""
        if v is not None:
            # 去重
            v = list(set(v))
            # 去除空标签
            v = [tag.strip() for tag in v if tag.strip()]
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "教授、博士生导师",
                "research_direction": "人工智能、深度学习、自然语言处理",
                "email": "zhangsan_new@example.edu.cn",
                "tags": ["AI", "NLP", "深度学习"]
            }
        }


class TutorResponse(BaseModel):
    """导师响应模型"""
    id: str = Field(..., description="导师ID")
    name: str = Field(..., description="导师姓名")
    school: str = Field(..., description="所在院校")
    department: str = Field(..., description="所在院系/专业")
    title: Optional[str] = Field(None, description="职称")
    research_direction: Optional[str] = Field(None, description="研究方向")
    email: Optional[str] = Field(None, description="邮箱")
    phone: Optional[str] = Field(None, description="联系电话")
    avatar_url: Optional[str] = Field(None, description="头像URL")
    personal_page_url: Optional[str] = Field(None, description="个人主页URL")
    bio: Optional[str] = Field(None, description="个人简介")
    papers: List[Dict[str, Any]] = Field(default_factory=list, description="论文列表")
    projects: List[Dict[str, Any]] = Field(default_factory=list, description="项目列表")
    tags: List[str] = Field(default_factory=list, description="标签列表")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    class Config:
        from_attributes = True


class TutorDeleteResponse(BaseModel):
    """导师删除响应模型"""
    success: bool = Field(..., description="是否删除成功")
    tutor_id: str = Field(..., description="被删除的导师ID")
    message: str = Field(..., description="操作结果消息")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "tutor_id": "tutor_123456789",
                "message": "导师信息已删除"
            }
        }


class TutorBatchDeleteRequest(BaseModel):
    """批量删除导师请求模型"""
    tutor_ids: List[str] = Field(..., min_items=1, max_items=100, description="导师ID列表（最多100个）")
    
    @validator('tutor_ids')
    def validate_tutor_ids(cls, v):
        """验证导师ID列表"""
        if not v:
            raise ValueError('导师ID列表不能为空')
        if len(v) > 100:
            raise ValueError('导师ID列表最多100个')
        # 去重
        return list(set(v))
    
    class Config:
        json_schema_extra = {
            "example": {
                "tutor_ids": ["tutor_123", "tutor_456", "tutor_789"]
            }
        }


class TutorBatchDeleteResponse(BaseModel):
    """批量删除导师响应模型"""
    success_count: int = Field(..., description="成功删除的数量")
    failed_count: int = Field(..., description="失败的数量")
    total_count: int = Field(..., description="总数量")
    failed_ids: List[str] = Field(default_factory=list, description="删除失败的导师ID列表")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success_count": 2,
                "failed_count": 1,
                "total_count": 3,
                "failed_ids": ["tutor_789"]
            }
        }
