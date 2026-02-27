"""
MongoDB 数据库连接与操作封装
提供连接池管理、异常处理和通用CRUD操作
"""

import time
from typing import Any, Dict, List, Optional, Union
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError, PyMongoError
from app.core.config.database import database_settings
from app.utils.logger import logger

class MongoDB:
    client: AsyncIOMotorClient = None
    db: AsyncIOMotorDatabase = None
    
    def __init__(self):
        self.connect()

    def connect(self):
        """建立MongoDB连接"""
        try:
            logger.info("正在连接MongoDB...")
            self.client = AsyncIOMotorClient(
                database_settings.MONGO_URI,
                maxPoolSize=100,
                minPoolSize=10,
                serverSelectionTimeoutMS=5000,  # 5秒超时
                connectTimeoutMS=10000,
                retryWrites=True
            )
            self.db = self.client[database_settings.DB_NAME]
            # 这里的ping是异步的，但为了初始化时不阻塞过久，我们在应用启动时进行真正的连接检查
            logger.info(f"MongoDB连接对象已创建，目标数据库: {database_settings.DB_NAME}")
        except Exception as e:
            logger.error(f"MongoDB初始化失败: {str(e)}")
            raise e

    async def ping(self):
        """检查数据库连接是否正常"""
        try:
            await self.client.admin.command('ping')
            logger.info("MongoDB连接状态: 正常")
            return True
        except Exception as e:
            logger.error(f"MongoDB连接异常: {str(e)}")
            return False

    def close(self):
        """关闭数据库连接"""
        if self.client:
            self.client.close()
            logger.info("MongoDB连接已关闭")

    def get_collection(self, collection_name: str):
        """获取集合对象"""
        return self.db[collection_name]

# 创建全局实例
db_client = MongoDB()

def get_db() -> AsyncIOMotorDatabase:
    """获取数据库实例（依赖注入用）"""
    return db_client.db

def get_collection(collection_name: str):
    """获取集合的快捷方式"""
    return db_client.get_collection(collection_name)

# ---------------------------------------------------------
# 通用 CRUD 操作封装
# ---------------------------------------------------------

async def find_one(collection_name: str, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    通用查询单条记录
    """
    try:
        coll = get_collection(collection_name)
        return await coll.find_one(query)
    except PyMongoError as e:
        logger.error(f"查询失败 ({collection_name}): {str(e)}")
        raise

async def find_many(
    collection_name: str, 
    query: Dict[str, Any] = None, 
    skip: int = 0, 
    limit: int = 20, 
    sort: List[tuple] = None
) -> List[Dict[str, Any]]:
    """
    通用查询多条记录（支持分页和排序）
    """
    if query is None:
        query = {}
    
    try:
        coll = get_collection(collection_name)
        cursor = coll.find(query).skip(skip).limit(limit)
        
        if sort:
            cursor = cursor.sort(sort)
            
        return await cursor.to_list(length=limit)
    except PyMongoError as e:
        logger.error(f"批量查询失败 ({collection_name}): {str(e)}")
        raise

async def insert_one(collection_name: str, document: Dict[str, Any]) -> str:
    """
    通用插入单条记录
    """
    try:
        coll = get_collection(collection_name)
        result = await coll.insert_one(document)
        return str(result.inserted_id)
    except PyMongoError as e:
        logger.error(f"插入失败 ({collection_name}): {str(e)}")
        raise

async def update_one(collection_name: str, query: Dict[str, Any], update_data: Dict[str, Any], upsert: bool = False) -> bool:
    """
    通用更新单条记录
    """
    try:
        coll = get_collection(collection_name)
        # 自动处理 $set 操作符，如果传入的数据没有 $set/$inc 等前缀，默认视为 $set
        if not any(k.startswith('$') for k in update_data.keys()):
            update_data = {"$set": update_data}
            
        result = await coll.update_one(query, update_data, upsert=upsert)
        return result.modified_count > 0 or result.upserted_id is not None
    except PyMongoError as e:
        logger.error(f"更新失败 ({collection_name}): {str(e)}")
        raise

async def delete_one(collection_name: str, query: Dict[str, Any]) -> bool:
    """
    通用删除单条记录
    """
    try:
        coll = get_collection(collection_name)
        result = await coll.delete_one(query)
        return result.deleted_count > 0
    except PyMongoError as e:
        logger.error(f"删除失败 ({collection_name}): {str(e)}")
        raise
