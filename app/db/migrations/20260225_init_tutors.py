"""
初始化导师数据集合索引
"""
from pymongo import IndexModel, ASCENDING, DESCENDING

async def upgrade(db):
    """
    执行迁移操作：创建索引
    """
    # 1. 导师集合索引
    tutors_collection = db["tutors"]
    
    # 创建复合索引：按名字和研究方向搜索
    await tutors_collection.create_indexes([
        IndexModel([("name", ASCENDING)], name="idx_name"),
        IndexModel([("research_areas", ASCENDING)], name="idx_research_areas"),
        IndexModel([("school", ASCENDING), ("department", ASCENDING)], name="idx_school_dept")
    ])
    
    # 2. 用户集合索引
    users_collection = db["users"]
    await users_collection.create_indexes([
        IndexModel([("openid", ASCENDING)], unique=True, name="idx_openid_unique"),
        IndexModel([("email", ASCENDING)], unique=True, sparse=True, name="idx_email_unique")
    ])

    print("初始化索引完成")

async def downgrade(db):
    """
    回滚操作（可选）
    """
    # 删除索引
    await db["tutors"].drop_index("idx_name")
    await db["tutors"].drop_index("idx_research_areas")
    await db["tutors"].drop_index("idx_school_dept")
    
    await db["users"].drop_index("idx_openid_unique")
    await db["users"].drop_index("idx_email_unique")
