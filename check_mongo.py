import sys
import os

# 添加当前目录 to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

try:
    # 尝试连接本地MongoDB
    client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
    client.admin.command('ping')
    print("MongoDB is running")
except ConnectionFailure:
    print("MongoDB is NOT running")
    sys.exit(1)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
