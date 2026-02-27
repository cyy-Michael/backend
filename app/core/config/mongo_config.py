# backend/app/core/config/mongo_config.py
import os
from dotenv import load_dotenv

# 加载环境变量（.env文件）
load_dotenv()

class MongoSettings:
    # 开发环境：本地MongoDB
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    # 生产环境：替换为云MongoDB地址（如阿里云/腾讯云）
    # MONGO_URI = os.getenv("MONGO_URI", "mongodb://username:password@xxx.mongodb.aliyuncs.com:27017/")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "ai_edu_admission")  # 数据库名

# 全局配置实例
settings = MongoSettings()