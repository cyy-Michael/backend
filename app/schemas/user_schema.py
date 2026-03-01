"""
用户信息相关的数据校验模型
提供用户信息查询和更新的请求/响应模型
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime


class UserProfileResponse(BaseModel):
    """用户信息响应模型"""
    id: str = Field(..., description="用户ID")
    nickname: Optional[str] = Field(None, description="用户昵称")
    avatar: Optional[str] = Field(None, description="用户头像URL")
    school: Optional[str] = Field(None, description="所在院校")
    major: Optional[str] = Field(None, description="专业")
    grade: Optional[str] = Field(None, description="年级")
    vip_status: bool = Field(False, description="VIP状态")
    vip_expire_date: Optional[datetime] = Field(None, description="VIP到期时间")
    created_at: datetime = Field(..., description="账号创建时间")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "nickname": "张三",
                "avatar": "https://example.com/avatar.jpg",
                "school": "清华大学",
                "major": "计算机科学与技术",
                "grade": "2024级",
                "vip_status": True,
                "vip_expire_date": "2024-12-31T23:59:59",
                "created_at": "2024-01-01T00:00:00"
            }
        }


class UserProfileUpdate(BaseModel):
    """用户信息更新请求模型"""
    nickname: Optional[str] = Field(None, min_length=1, max_length=50, description="用户昵称")
    avatar: Optional[str] = Field(None, max_length=500, description="用户头像URL")
    school: Optional[str] = Field(None, max_length=100, description="所在院校")
    major: Optional[str] = Field(None, max_length=100, description="专业")
    grade: Optional[str] = Field(None, max_length=20, description="年级")
    
    @validator('nickname')
    def validate_nickname(cls, v):
        """验证昵称格式"""
        if v is not None:
            v = v.strip()
            if len(v) == 0:
                raise ValueError('昵称不能为空')
            if len(v) > 50:
                raise ValueError('昵称长度不能超过50个字符')
        return v
    
    @validator('avatar')
    def validate_avatar(cls, v):
        """验证头像URL格式"""
        if v is not None:
            v = v.strip()
            if len(v) > 0 and not (v.startswith('http://') or v.startswith('https://')):
                raise ValueError('头像必须是有效的HTTP/HTTPS URL')
        return v
    
    @validator('school', 'major')
    def validate_text_fields(cls, v):
        """验证文本字段"""
        if v is not None:
            v = v.strip()
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "nickname": "张三",
                "avatar": "https://example.com/avatar.jpg",
                "school": "清华大学",
                "major": "计算机科学与技术",
                "grade": "2024级"
            }
        }


class UserProfileUpdateResponse(BaseModel):
    """用户信息更新响应模型"""
    success: bool = Field(..., description="更新是否成功")
    updated_fields: list[str] = Field(..., description="已更新的字段列表")
    user: UserProfileResponse = Field(..., description="更新后的用户信息")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "updated_fields": ["nickname", "school"],
                "user": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "nickname": "张三",
                    "avatar": "https://example.com/avatar.jpg",
                    "school": "清华大学",
                    "major": "计算机科学与技术",
                    "grade": "2024级",
                    "vip_status": True,
                    "vip_expire_date": "2024-12-31T23:59:59",
                    "created_at": "2024-01-01T00:00:00"
                }
            }
        }
