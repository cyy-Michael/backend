from pydantic import BaseModel
from typing import Optional

# 新增导师的请求参数校验
class TeacherCreate(BaseModel):
    email: str
    basicInfo: dict
    academy: dict
    resume: Optional[list] = []
    researchAchievements: Optional[list] = []

# 更新导师的请求参数校验（仅可选字段）
class TeacherUpdate(BaseModel):
    basicInfo: Optional[dict] = None
    academy: Optional[dict] = None
    resume: Optional[list] = None
    researchAchievements: Optional[list] = None