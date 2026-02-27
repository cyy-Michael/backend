"""
智能匹配数据模型
定义匹配相关的数据结构
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class MatchPreference(BaseModel):
    """匹配偏好设置"""
    cross_school: bool = False
    high_output: bool = False
    young_scholar: bool = False


class MatchRequest(BaseModel):
    """匹配请求模型"""
    discipline: str = Field(..., description="学科方向")
    keywords: str = Field(..., description="研究兴趣关键词，逗号分隔")
    preferences: MatchPreference = Field(default_factory=MatchPreference)


class MatchResult(BaseModel):
    """匹配结果模型"""
    tutor_id: str
    match_score: float
    match_reason: str
    tutor_info: Dict[str, Any]


class MatchResponse(BaseModel):
    """匹配响应模型"""
    match_id: str
    results: List[MatchResult]


class MatchHistory(BaseModel):
    """匹配历史记录模型"""
    id: str
    user_id: str
    discipline: str
    keywords: str
    preferences: MatchPreference
    result_json: str
    created_at: datetime

    class Config:
        from_attributes = True


class MatchHistoryResponse(BaseModel):
    """匹配历史响应模型"""
    id: str
    discipline: str
    keywords: str
    preferences: MatchPreference
    created_at: datetime
    result_count: int