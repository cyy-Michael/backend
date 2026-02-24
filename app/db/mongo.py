from pymongo import MongoClient
from dotenv import load_dotenv
import os

# 加载.env文件中的环境变量
load_dotenv()

# 获取MongoDB连接信息
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "teacher_query")

# 创建MongoDB客户端和数据库实例
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# 定义获取数据库实例的函数，供其他模块调用
def get_db():
    return db