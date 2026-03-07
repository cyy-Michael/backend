"""
外部服务配置
包含第三方服务的 API Key 和配置信息
"""

from pydantic_settings import BaseSettings

class ServiceSettings(BaseSettings):
    # Baidu OCR
    BAIDU_API_KEY: str = "ZPA1nlXx9BmrOgTWxo70NjPW"
    BAIDU_SECRET_KEY: str = "0CVc5WM9QT4z7kVGg5plrCrvVFVVbKGv"
    
    # DeepSeek
    DEEPSEEK_API_KEY: str = "sk-e42acdb8f235474ba583c116faf8de4e"
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"

    class Config:
        env_file = ".env"
        extra = "ignore"

service_settings = ServiceSettings()
