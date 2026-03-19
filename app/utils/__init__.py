"""
后端通用工具模块
提供响应格式化、日志记录、安全加密等通用功能
"""

from .response import (
    success_response,
    error_response,
    paginated_response,
    validation_error_response,
    business_error_response,
    StandardResponse
)

from .logger import (
    get_logger,
    app_logger,
    api_logger,
    db_logger,
    error_logger,
    log_request,
    log_db_operation
)

from .security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_token,
    generate_api_key,
    validate_api_key,
    generate_random_token,
    hash_data,
    sanitize_input,
    validate_email,
    validate_phone,
    mask_sensitive_data
)

<<<<<<< Updated upstream
=======
# 不在顶层导出 admin，避免循环导入：login → utils → admin → login
# 需要管理员相关时请使用: from app.utils.admin import get_current_admin 等

>>>>>>> Stashed changes
__all__ = [
    # response
    'success_response',
    'error_response',
    'paginated_response',
    'validation_error_response',
    'business_error_response',
    'StandardResponse',
    
    # logger
    'get_logger',
    'app_logger',
    'api_logger',
    'db_logger',
    'error_logger',
    'log_request',
    'log_db_operation',
    
    # security
    'verify_password',
    'get_password_hash',
    'create_access_token',
    'create_refresh_token',
    'decode_token',
    'verify_token',
    'generate_api_key',
    'validate_api_key',
    'generate_random_token',
    'hash_data',
    'sanitize_input',
    'validate_email',
    'validate_phone',
<<<<<<< Updated upstream
    'mask_sensitive_data'
=======
    'mask_sensitive_data',
>>>>>>> Stashed changes
]