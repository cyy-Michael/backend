"""
MongoDB 数据库迁移脚本
用于管理数据库版本和变更

使用方法：
python -m app.db.migrations.migrate
"""

import os
import sys
import importlib.util
import asyncio
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config.database import database_settings
from app.utils.logger import logger

# 迁移记录集合名称
MIGRATION_COLLECTION = "_migrations"
# 迁移脚本目录
MIGRATION_DIR = os.path.dirname(os.path.abspath(__file__))

async def get_applied_migrations(db):
    """获取已应用的迁移列表"""
    cursor = db[MIGRATION_COLLECTION].find().sort("name", 1)
    return [doc["name"] async for doc in cursor]

async def record_migration(db, name):
    """记录迁移执行情况"""
    await db[MIGRATION_COLLECTION].insert_one({
        "name": name,
        "applied_at": datetime.utcnow()
    })
    logger.info(f"已记录迁移: {name}")

def load_migration_module(file_path):
    """加载迁移脚本模块"""
    spec = importlib.util.spec_from_file_location("migration_module", file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

async def run_migrations():
    """运行所有未执行的迁移"""
    logger.info("开始数据库迁移检查...")
    
    # 连接数据库
    client = AsyncIOMotorClient(database_settings.MONGO_URI)
    db = client[database_settings.DB_NAME]
    
    try:
        # 获取已应用的迁移
        applied_migrations = await get_applied_migrations(db)
        logger.info(f"已应用的迁移: {applied_migrations}")
        
        # 获取所有迁移脚本文件
        migration_files = []
        for filename in os.listdir(MIGRATION_DIR):
            if filename.endswith(".py") and filename not in ["__init__.py", "migrate.py"]:
                migration_files.append(filename)
        
        # 按文件名排序确保顺序执行
        migration_files.sort()
        
        pending_migrations = [f for f in migration_files if f not in applied_migrations]
        
        if not pending_migrations:
            logger.info("没有需要执行的新迁移。")
            return

        logger.info(f"发现 {len(pending_migrations)} 个待执行迁移: {pending_migrations}")

        # 依次执行迁移
        for filename in pending_migrations:
            file_path = os.path.join(MIGRATION_DIR, filename)
            logger.info(f"正在执行迁移: {filename} ...")
            
            try:
                module = load_migration_module(file_path)
                
                if hasattr(module, 'upgrade'):
                    if asyncio.iscoroutinefunction(module.upgrade):
                        await module.upgrade(db)
                    else:
                        module.upgrade(db)
                    
                    await record_migration(db, filename)
                    logger.info(f"迁移成功: {filename}")
                else:
                    logger.warning(f"跳过迁移 {filename}: 未找到 upgrade 函数")
                    
            except Exception as e:
                logger.error(f"迁移失败 {filename}: {str(e)}")
                raise e

        logger.info("所有迁移执行完成！")
        
    except Exception as e:
        logger.error(f"迁移过程中发生错误: {str(e)}")
        raise e
    finally:
        client.close()

if __name__ == "__main__":
    # 添加项目根目录到 sys.path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
    sys.path.append(project_root)
    
    asyncio.run(run_migrations())
