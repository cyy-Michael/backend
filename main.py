"""
导师资料查询小程序后端服务入口
"""

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from app.api.api import api_router
from app.core import (
    app_settings, 
    security_settings, 
    logging_settings,
    setup_logging,
    get_log_config
)

from app.utils import (
    success_response,
    error_response,
    log_request,
    app_logger,
    api_logger
)
import time
import uuid
import traceback

# 设置全局日志
setup_logging()

# 创建FastAPI应用实例
app = FastAPI(
    title=app_settings.APP_NAME,
    description=app_settings.APP_DESCRIPTION,
    version=app_settings.APP_VERSION,
    debug=app_settings.DEBUG,
    docs_url="/docs" if app_settings.is_development else None,
    redoc_url="/redoc" if app_settings.is_development else None,
    openapi_url="/api/openapi.json" if app_settings.is_development else None
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    **security_settings.cors_config
)

# 添加Gzip压缩中间件
app.add_middleware(GZipMiddleware, minimum_size=1000)


# 请求ID和日志中间件
@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    """请求日志中间件"""
    # 生成请求ID
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    # 设置请求开始时间
    start_time = time.time()
    
    # 添加请求ID到响应头
    response = Response("Internal server error", status_code=500)
    
    try:
        # 处理请求
        response = await call_next(request)
        
        # 计算处理时间
        processing_time = (time.time() - start_time) * 1000
        
        # 记录请求日志
        log_request(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            processing_time=processing_time,
            client_ip=request.client.host,
            user_agent=request.headers.get("user-agent")
        )
        
        # 添加请求ID到响应头
        response.headers["X-Request-ID"] = request_id
        
    except Exception as e:
        # 记录异常日志
        error_message = f"Request processing error: {str(e)}"
        error_logger = app_logger.error if app_settings.is_development else app_logger.exception
        error_logger(
            f"{error_message}\n"
            f"Request ID: {request_id}\n"
            f"Path: {request.url.path}\n"
            f"Method: {request.method}\n"
            f"Client IP: {request.client.host}\n"
            f"Traceback: {traceback.format_exc()}"
        )
        
        # 返回标准错误响应
        response = JSONResponse(
            status_code=500,
            content=error_response(
                message="Internal server error",
                error={"request_id": request_id}
            ),
            headers={"X-Request-ID": request_id}
        )
    
    return response


# 挂载所有API路由
app.include_router(api_router, prefix=app_settings.API_PREFIX)


# 根路径健康检查接口
@app.get(app_settings.HEALTH_CHECK_ENDPOINT, tags=["health"])
def health_check():
    """健康检查接口"""
    return success_response(
        message=f"{app_settings.APP_NAME} 服务运行正常",
        data={
            "version": app_settings.APP_VERSION,
            "environment": app_settings.APP_ENVIRONMENT,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    )

from app.api.recharge import router as recharge_router

app.include_router(recharge_router)
# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理器"""
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    
    # 记录异常日志
    error_logger = app_logger.error if app_settings.is_development else app_logger.exception
    error_logger(
        f"Global exception: {str(exc)}\n"
        f"Request ID: {request_id}\n"
        f"Path: {request.url.path}\n"
        f"Method: {request.method}\n"
        f"Traceback: {traceback.format_exc()}"
    )
    
    return JSONResponse(
        status_code=500,
        content=error_response(
            message="Internal server error",
            error={"request_id": request_id}
        ),
        headers={"X-Request-ID": request_id}
    )


# 启动服务
if __name__ == "__main__":
    import uvicorn
    
    app_logger.info(
        f"Starting {app_settings.APP_NAME} v{app_settings.APP_VERSION}\n"
        f"Environment: {app_settings.APP_ENVIRONMENT}\n"
        f"Host: {app_settings.HOST}\n"
        f"Port: {app_settings.PORT}\n"
        f"Debug: {app_settings.DEBUG}"
    )
    
    # 启动服务
    uvicorn.run(
        "main:app",
        host=app_settings.HOST,
        port=app_settings.PORT,
        reload=app_settings.RELOAD,
        log_config=get_log_config() if app_settings.is_development else None
    )