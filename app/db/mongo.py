# backend/app/db/mongo.py
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure
from app.core.config.mongo_config import settings
from loguru import logger

# 单例模式：确保全局只有一个MongoDB连接池
class MongoDBClient:
    _instance = None
    _client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # 初始化MongoDB连接
            try:
                cls._client = MongoClient(
                    settings.MONGO_URI,
                    maxPoolSize=50,  # 连接池大小
                    minPoolSize=10,
                    serverSelectionTimeoutMS=5000  # 连接超时时间
                )
                # 测试连接是否成功
                cls._client.admin.command('ping')
                logger.info("MongoDB连接成功！")
            except ConnectionFailure as e:
                logger.error(f"MongoDB连接失败：{e}")
                raise e
        return cls._instance

    def get_db(self, db_name: str = None):
        """获取数据库实例"""
        db_name = db_name or settings.MONGO_DB_NAME
        return self._client[db_name]

    def get_collection(self, coll_name: str, db_name: str = None):
        """获取集合实例"""
        db = self.get_db(db_name)
        return db[coll_name]

# 全局实例：其他模块直接导入使用
mongo_client = MongoDBClient()

# 快捷获取常用集合
def get_tutor_collection():
    """获取导师集合"""
    return mongo_client.get_collection("tutors")

def get_user_collection():
    """获取用户集合"""
    return mongo_client.get_collection("users")

def get_order_collection():
    """获取订单集合"""
    return mongo_client.get_collection("orders")