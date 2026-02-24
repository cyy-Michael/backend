from typing import List, Optional
from pydantic import BaseModel, Field

# 个人基本信息子模型
class BasicInfo(BaseModel):
    name: str
    gender: str = Field(..., pattern="^(男|女)$")  # 限制性别只能是男/女
    age: int
    phone: Optional[str] = None  # 可选字段
    title: Optional[str] = None  # 职称：教授/副教授等

# 院校信息子模型
class AcademyInfo(BaseModel):
    academyId: str
    academyName: str
    department: str

# 履历子模型
class ResumeItem(BaseModel):
    period: str  # 时间段：如2010-2015
    experience: str  # 履历内容

# 科研成果子模型
class ResearchItem(BaseModel):
    type: str = Field(..., pattern="^(论文|专利|项目)$")  # 限制成果类型
    title: str
    time: str
    description: Optional[str] = None

# 导师主模型
class Teacher(BaseModel):
    email: str  # 主键（唯一索引）
    basicInfo: BasicInfo
    academy: AcademyInfo
    resume: List[ResumeItem] = []  # 默认空数组
    researchAchievements: List[ResearchItem] = []
    createTime: Optional[str] = None
    updateTime: Optional[str] = None