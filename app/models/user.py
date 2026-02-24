"""
用户数据模型
定义用户相关的数据结构
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime


class UserBase(BaseModel):
    """用户基础模型"""
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    school: Optional[str] = None
    major: Optional[str] = None
    grade: Optional[str] = None


class UserCreate(UserBase):
    """用户创建模型"""
    openid: str
    unionid: Optional[str] = None


class UserUpdate(UserBase):
    """用户更新模型"""
    vip_status: Optional[bool] = None
    vip_expire_date: Optional[datetime] = None


class UserInDB(UserBase):
    """数据库中的用户模型"""
    id: str
    openid: str
    unionid: Optional[str] = None
    vip_status: bool = False
    vip_expire_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class User(UserBase):
    """用户响应模型"""
    id: str
    vip_status: bool
    vip_expire_date: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """用户登录请求模型"""
    code: str = Field(..., description="微信登录凭证code")


class UserLoginResponse(BaseModel):
    """用户登录响应模型"""
    token: str
    user: User


class Favorite(BaseModel):
    """收藏模型"""
    id: str
    user_id: str
    target_type: str = Field(..., pattern="^(tutor|project)$")
    target_id: str
    created_at: datetime

    class Config:
        from_attributes = True


class FavoriteCreate(BaseModel):
    """创建收藏请求模型"""
    target_type: str = Field(..., pattern="^(tutor|project)$")
    target_id: str


class FavoriteResponse(BaseModel):
    """收藏响应模型"""
    status: str = Field(..., description="collected 或 uncollected")


class Booking(BaseModel):
    """预约模型"""
    id: str
    user_id: str
    tutor_id: str
    date: datetime
    message: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BookingCreate(BaseModel):
    """创建预约请求模型"""
    tutor_id: str
    date: datetime
    message: str


class BookingResponse(BaseModel):
    """预约响应模型"""
    booking_id: str
    status: str