"""
日志工具模块
提供统一的日志配置和使用方式
"""

import os
import logging
import sys
from typing import Optional
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 日志级别映射
LOG_LEVEL_MAP = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "WARN": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL
}

# 默认日志配置
DEFAULT_LOG_LEVEL = LOG_LEVEL_MAP.get(
    os.getenv("LOG_LEVEL", "INFO").upper(),
    logging.INFO
)
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class Logger:
    """自定义日志类"""
    
    def __init__(
        self,
        name: str,
        level: int = DEFAULT_LOG_LEVEL,
        log_file: Optional[str] = None,
        max_bytes: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5,
        use_rotating: bool = True
    ):
        """
        初始化日志器
        
        Args:
            name: 日志器名称
            level: 日志级别
            log_file: 日志文件路径
            max_bytes: 单个日志文件最大字节数
            backup_count: 保留的日志文件数量
            use_rotating: 是否使用轮转日志
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.propagate = False
        
        # 清除已有的处理器
        self.logger.handlers.clear()
        
        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
        self.logger.addHandler(console_handler)
        
        # 文件处理器（如果指定了日志文件）
        if log_file:
            self._setup_file_handler(
                log_file, level, max_bytes, backup_count, use_rotating
            )
    
    def _setup_file_handler(
        self,
        log_file: str,
        level: int,
        max_bytes: int,
        backup_count: int,
        use_rotating: bool
    ):
        """设置文件处理器"""
        # 确保日志目录存在
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        if use_rotating:
            # 按大小轮转
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding='utf-8'
            )
        else:
            # 按时间轮转（每天）
            file_handler = TimedRotatingFileHandler(
                log_file,
                when='D',
                interval=1,
                backupCount=backup_count,
                encoding='utf-8'
            )
        
        file_handler.setLevel(level)
        file_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
        self.logger.addHandler(file_handler)
    
    def debug(self, message: str, *args, **kwargs):
        """调试日志"""
        self.logger.debug(message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs):
        """信息日志"""
        self.logger.info(message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs):
        """警告日志"""
        self.logger.warning(message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs):
        """错误日志"""
        self.logger.error(message, *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs):
        """严重错误日志"""
        self.logger.critical(message, *args, **kwargs)
    
    def exception(self, message: str, *args, exc_info=True, **kwargs):
        """异常日志"""
        self.logger.exception(message, *args, exc_info=exc_info, **kwargs)


# 创建全局日志器实例
def get_logger(
    name: str,
    log_file: Optional[str] = None
) -> Logger:
    """
    获取日志器实例
    
    Args:
        name: 日志器名称
        log_file: 日志文件路径（可选）
    
    Returns:
        Logger实例
    """
    # 如果没有指定日志文件，使用默认路径
    if not log_file:
        log_dir = os.getenv("LOG_DIR", "logs")
        log_file = os.path.join(log_dir, f"{name}.log")
    
    return Logger(name, log_file=log_file)


# 创建应用默认日志器
app_logger = get_logger("app")
api_logger = get_logger("api")
db_logger = get_logger("database")
error_logger = get_logger("error", os.path.join("logs", "error.log"))


def log_request(
    request_id: str,
    method: str,
    path: str,
    status_code: int,
    processing_time: float,
    client_ip: str,
    user_agent: Optional[str] = None
):
    """
    记录API请求日志
    
    Args:
        request_id: 请求ID
        method: HTTP方法
        path: 请求路径
        status_code: 响应状态码
        processing_time: 处理时间（毫秒）
        client_ip: 客户端IP
        user_agent: 用户代理（可选）
    """
    log_message = (
        f"Request ID: {request_id} | "
        f"Method: {method} | "
        f"Path: {path} | "
        f"Status: {status_code} | "
        f"Time: {processing_time:.2f}ms | "
        f"IP: {client_ip}"
    )
    
    if user_agent:
        log_message += f" | UA: {user_agent}"
    
    if status_code >= 500:
        api_logger.error(log_message)
    elif status_code >= 400:
        api_logger.warning(log_message)
    else:
        api_logger.info(log_message)


def log_db_operation(
    operation: str,
    collection: str,
    query: Optional[dict] = None,
    execution_time: Optional[float] = None,
    success: bool = True,
    error: Optional[str] = None
):
    """
    记录数据库操作日志
    
    Args:
        operation: 操作类型（insert, update, delete, find等）
        collection: 集合名称
        query: 查询条件（可选）
        execution_time: 执行时间（毫秒，可选）
        success: 是否成功
        error: 错误信息（可选）
    """
    log_message = (
        f"Operation: {operation} | "
        f"Collection: {collection}"
    )
    
    if query:
        log_message += f" | Query: {query}"
    
    if execution_time is not None:
        log_message += f" | Time: {execution_time:.2f}ms"
    
    if success:
        db_logger.info(log_message)
    else:
        log_message += f" | Error: {error}"
        db_logger.error(log_message)