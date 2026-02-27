"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
from app.db.mongo import get_db

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """创建初始数据库结构和索引"""
    db = get_db()
    
    # 为teachers集合创建email唯一索引
    db.teachers.create_index("email", unique=True)
    
    # 为teachers集合创建其他常用索引
    db.teachers.create_index("basicInfo.name")
    db.teachers.create_index("academy.academyId")
    db.teachers.create_index("createTime")
    
    print("数据库初始化完成：已创建teachers集合索引")


def downgrade() -> None:
    """删除创建的索引"""
    db = get_db()
    
    # 删除创建的索引
    db.teachers.drop_index("email_1")
    db.teachers.drop_index("basicInfo.name_1")
    db.teachers.drop_index("academy.academyId_1")
    db.teachers.drop_index("createTime_1")
    
    print("数据库回滚完成：已删除teachers集合索引")