"""
数据模型模块
导出所有数据模型类
"""

from .user import (
    User, UserCreate, UserUpdate, UserLogin, UserLoginResponse,
    Favorite, FavoriteCreate, FavoriteResponse,
    Booking, BookingCreate, BookingResponse
)

from .tutor import (
    Tutor, TutorCreate, TutorUpdate, TutorBrief, TutorDetail,
    Paper, Project as TutorProject,
    School, Department, ScoreLine
)

from .match import (
    MatchRequest, MatchResponse, MatchResult,
    MatchPreference, MatchHistory, MatchHistoryResponse
)

from .project import (
    Project, ProjectCreate, ProjectUpdate, ProjectBrief, ProjectDetail,
    ProjectMember, ProjectApplication, 
    ProjectApplicationCreate, ProjectApplicationResponse
)

__all__ = [
    # User models
    'User', 'UserCreate', 'UserUpdate', 'UserLogin', 'UserLoginResponse',
    'Favorite', 'FavoriteCreate', 'FavoriteResponse',
    'Booking', 'BookingCreate', 'BookingResponse',
    
    # Tutor models
    'Tutor', 'TutorCreate', 'TutorUpdate', 'TutorBrief', 'TutorDetail',
    'Paper', 'TutorProject',
    'School', 'Department', 'ScoreLine',
    
    # Match models
    'MatchRequest', 'MatchResponse', 'MatchResult',
    'MatchPreference', 'MatchHistory', 'MatchHistoryResponse',
    
    # Project models
    'Project', 'ProjectCreate', 'ProjectUpdate', 'ProjectBrief', 'ProjectDetail',
    'ProjectMember', 'ProjectApplication',
    'ProjectApplicationCreate', 'ProjectApplicationResponse'
]