"""
数据校验模型模块
提供所有API的请求和响应数据校验
"""

from .user_schema import (
    UserProfileResponse,
    UserProfileUpdate,
    UserProfileUpdateResponse
)

from .teacher_schema import (
    TeacherCreate,
    TeacherUpdate
)

from .favorite_schema import (
    FavoriteToggleRequest,
    FavoriteToggleResponse,
    FavoriteTutorBrief,
    FavoriteListResponse,
    FavoriteStatusResponse,
    BatchFavoriteStatusRequest,
    BatchFavoriteStatusResponse
)

from .tutor_schema import (
    PaperInput,
    ProjectInput,
    TutorCreateRequest,
    TutorUpdateRequest,
    TutorResponse,
    TutorDeleteResponse,
    TutorBatchDeleteRequest,
    TutorBatchDeleteResponse
)

from .tutor_query_schema import (
    TutorQueryParams,
    TutorListResponse,
    TutorFilterOptions,
    SortField,
    SortOrder,
    RecruitmentType
)

__all__ = [
    # 用户相关
    "UserProfileResponse",
    "UserProfileUpdate",
    "UserProfileUpdateResponse",
    
    # 导师相关（旧）
    "TeacherCreate",
    "TeacherUpdate",
    
    # 导师CRUD相关（新）
    "PaperInput",
    "ProjectInput",
    "TutorCreateRequest",
    "TutorUpdateRequest",
    "TutorResponse",
    "TutorDeleteResponse",
    "TutorBatchDeleteRequest",
    "TutorBatchDeleteResponse",
    
    # 收藏相关
    "FavoriteToggleRequest",
    "FavoriteToggleResponse",
    "FavoriteTutorBrief",
    "FavoriteListResponse",
    "FavoriteStatusResponse",
    "BatchFavoriteStatusRequest",
    "BatchFavoriteStatusResponse",
    
    # 导师查询相关
    "TutorQueryParams",
    "TutorListResponse",
    "TutorFilterOptions",
    "SortField",
    "SortOrder",
    "RecruitmentType",
]
