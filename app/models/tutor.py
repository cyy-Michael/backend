"""
导师数据模型
定义导师相关的数据结构
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class TutorBase(BaseModel):
    """导师基础模型"""
    name: str
    title: Optional[str] = None
    school_id: str
    department_id: str
    bio: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    personal_page_url: Optional[str] = None
    research_direction: Optional[str] = None


class TutorCreate(TutorBase):
    """导师创建模型"""
    pass


class TutorUpdate(TutorBase):
    """导师更新模型"""
    name: Optional[str] = None
    school_id: Optional[str] = None
    department_id: Optional[str] = None


class TutorInDB(TutorBase):
    """数据库中的导师模型"""
    id: str
    crawled_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Tutor(TutorBase):
    """导师响应模型"""
    id: str

    class Config:
        from_attributes = True


class TutorBrief(BaseModel):
    """导师简略信息模型（用于列表展示）"""
    id: str
    name: str
    title: Optional[str] = None
    school: str
    department: str
    tags: List[str] = []
    avatar: Optional[str] = None

    class Config:
        from_attributes = True


class TutorDetail(Tutor):
    """导师详细信息模型"""
    school: str
    department: str
    achievements_summary: Optional[str] = None
    papers: List[Dict[str, Any]] = []
    projects: List[Dict[str, Any]] = []
    students: List[Dict[str, Any]] = []
    socials: List[Dict[str, Any]] = []
    risks: List[Dict[str, Any]] = []
    is_collected: bool = False

    class Config:
        from_attributes = True


class Paper(BaseModel):
    """论文模型"""
    id: str
    tutor_id: str
    title: str
    authors: List[str]
    journal: Optional[str] = None
    year: int
    doi: Optional[str] = None
    abstract: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class Project(BaseModel):
    """项目模型"""
    id: str
    tutor_id: str
    title: str
    funding: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    description: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class School(BaseModel):
    """学校模型"""
    id: str
    name: str
    location: Optional[str] = None
    level: Optional[str] = None
    logo_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Department(BaseModel):
    """院系模型"""
    id: str
    school_id: str
    name: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ScoreLine(BaseModel):
    """分数线模型"""
    id: str
    school_id: str
    department_id: str
    year: int
    category: str
    score: float
    rank: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True