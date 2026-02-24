# 数据库迁移管理指南

## 概述

本项目使用 Alembic 进行数据库迁移管理，支持 MongoDB 数据库的结构变更和版本控制。

## 安装依赖

```bash
# 安装迁移相关依赖
pip install -r requirements.txt
```

## 迁移配置说明

### 配置文件

- `alembic.ini` - Alembic 主配置文件
- `alembic/env.py` - 环境配置，连接 MongoDB 数据库
- `alembic/script.py.mako` - 迁移脚本模板
- `alembic/versions/` - 迁移脚本存储目录

### 环境变量

确保 `.env` 文件中包含以下配置：

```env
MONGO_URI=mongodb://teacher_dev:123456@192.168.1.100:27017/teacher_query
DB_NAME=teacher_query
```

## 使用方法

### 1. 执行迁移管理脚本

项目根目录下的 `migrate.py` 提供了简化的迁移管理命令：

```bash
# 显示帮助信息
python migrate.py

# 创建新的迁移
python migrate.py create "添加新的索引和集合"

# 升级到最新版本
python migrate.py upgrade

# 回滚到指定版本
python migrate.py downgrade 001

# 回滚到初始状态
python migrate.py downgrade base

# 查看迁移历史
python migrate.py history

# 查看当前版本
python migrate.py current
```

### 2. 直接使用 Alembic 命令

也可以直接使用 Alembic 原生命令：

```bash
# 创建新的迁移
alembic revision --autogenerate -m "添加新的索引和集合"

# 升级到最新版本
alembic upgrade head

# 回滚到上一个版本
alembic downgrade -1

# 查看迁移历史
alembic history --verbose
```

## 迁移脚本示例

迁移脚本位于 `alembic/versions/` 目录下，示例：

```python
"""添加用户集合和索引

Revision ID: 002
Revises: 001
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
from app.db.mongo import get_db

revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None

def upgrade() -> None:
    """升级操作"""
    db = get_db()
    
    # 创建用户集合
    if 'users' not in db.list_collection_names():
        db.create_collection('users')
    
    # 创建索引
    db.users.create_index("username", unique=True)
    db.users.create_index("email", unique=True)
    
    print("已创建users集合和索引")

def downgrade() -> None:
    """回滚操作"""
    db = get_db()
    
    # 删除索引
    if 'users' in db.list_collection_names():
        db.users.drop_index("username_1")
        db.users.drop_index("email_1")
    
    print("已删除users集合索引")
```

## 最佳实践

1. **版本管理**：每次数据库结构变更都应该创建对应的迁移脚本
2. **团队协作**：迁移脚本应该纳入版本控制系统，团队成员共同维护
3. **测试环境**：在生产环境执行迁移前，先在测试环境验证
4. **备份数据**：执行迁移前确保数据库数据已备份
5. **回滚计划**：每个迁移脚本都应该提供对应的回滚操作
6. **文档说明**：迁移脚本应该包含清晰的注释和说明

## 注意事项

1. MongoDB 是文档数据库，Alembic 主要用于 SQL 数据库，这里我们做了适配
2. 迁移主要用于管理索引、集合创建等操作，文档结构变更需要在应用代码中处理
3. 执行迁移时确保 MongoDB 服务可用
4. 生产环境迁移建议在低峰期进行

## 故障排除

### 常见问题

1. **连接失败**：检查 MONGO_URI 配置是否正确
2. **权限不足**：确保数据库用户有足够的权限执行操作
3. **索引冲突**：检查是否有重复的索引创建操作
4. **版本冲突**：多个开发者同时创建迁移可能导致版本冲突

### 解决方案

1. **连接问题**：验证 MongoDB 服务状态和网络连接
2. **权限问题**：为数据库用户授予正确的权限
3. **索引问题**：先删除冲突的索引，再重新创建
4. **版本冲突**：使用 `alembic merge` 命令合并冲突的版本

## 自动迁移集成

可以在应用启动时自动执行迁移：

```python
# 在 main.py 中添加
from app.core.config.database import get_database_settings

settings = get_database_settings()
if settings.ENABLE_AUTO_MIGRATION:
    import subprocess
    subprocess.run(["python", "migrate.py", "upgrade"], check=True)
```

## 相关文件

- `app/core/config/database.py` - 数据库配置管理
- `migrate.py` - 迁移管理脚本
- `alembic.ini` - Alembic 配置文件