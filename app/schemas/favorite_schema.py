"""
收藏相关的数据校验模型
提供收藏操作和查询的请求/响应模型
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime


class FavoriteToggleRequest(BaseModel):
    """收藏/取消收藏请求模型"""
    tutor_id: str = Field(..., min_length=1, description="导师ID")
    
    @validator('tutor_id')
    def validate_tutor_id(cls, v):
        """验证导师ID格式"""
        if v is not None:
            v = v.strip()
            if len(v) == 0:
                raise ValueError('导师ID不能为空')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "tutor_id": "tutor_123456789"
            }
        }


class FavoriteToggleResponse(BaseModel):
    """收藏/取消收藏响应模型"""
    action: str = Field(..., description="操作类型: collected(已收藏) 或 uncollected(已取消收藏)")
    tutor_id: str = Field(..., description="导师ID")
    message: str = Field(..., description="操作结果消息")
    
    class Config:
        json_schema_extra = {
            "example": {
                "action": "collected",
                "tutor_id": "tutor_123456789",
                "message": "收藏成功"
            }
        }


class FavoriteTutorBrief(BaseModel):
    """收藏的导师简略信息模型"""
    id: str = Field(..., description="导师ID")
    name: str = Field(..., description="导师姓名")
    title: Optional[str] = Field(None, description="职称")
    school: str = Field(..., description="所在学校")
    department: str = Field(..., description="所在院系")
    avatar: Optional[str] = Field(None, description="头像URL")
    research_direction: Optional[str] = Field(None, description="研究方向")
    tags: List[str] = Field(default_factory=list, description="标签列表")
    collected_at: datetime = Field(..., description="收藏时间")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "tutor_123456789",
                "name": "张三",
                "title": "教授",
                "school": "清华大学",
                "department": "计算机科学与技术系",
                "avatar": "https://example.com/avatar.jpg",
                "research_direction": "人工智能、机器学习",
                "tags": ["AI", "深度学习", "计算机视觉"],
                "collected_at": "2024-03-01T12:00:00"
            }
        }


class FavoriteListResponse(BaseModel):
    """收藏列表响应模型"""
    list: List[FavoriteTutorBrief] = Field(..., description="收藏的导师列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")
    
    class Config:
        json_schema_extra = {
            "example": {
                "list": [
                    {
                        "id": "tutor_123456789",
                        "name": "张三",
                        "title": "教授",
                        "school": "清华大学",
                        "department": "计算机科学与技术系",
                        "avatar": "https://example.com/avatar.jpg",
                        "research_direction": "人工智能、机器学习",
                        "tags": ["AI", "深度学习"],
                        "collected_at": "2024-03-01T12:00:00"
                    }
                ],
                "total": 1,
                "page": 1,
                "page_size": 10
            }
        }


class FavoriteStatusResponse(BaseModel):
    """收藏状态响应模型"""
    is_collected: bool = Field(..., description="是否已收藏")
    tutor_id: str = Field(..., description="导师ID")
    
    class Config:
        json_schema_extra = {
            "example": {
                "is_collected": True,
                "tutor_id": "tutor_123456789"
            }
        }


class BatchFavoriteStatusRequest(BaseModel):
    """批量查询收藏状态请求模型"""
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


class BatchFavoriteStatusResponse(BaseModel):
    """批量查询收藏状态响应模型"""
    favorites: dict = Field(..., description="收藏状态字典，key为导师ID，value为是否收藏")
    
    class Config:
        json_schema_extra = {
            "example": {
                "favorites": {
                    "tutor_123": True,
                    "tutor_456": False,
                    "tutor_789": True
                }
            }
        }
