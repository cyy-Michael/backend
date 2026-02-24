#!/usr/bin/env python3
"""
数据库迁移管理脚本
用于执行数据库迁移操作
"""

import os
import sys
import subprocess
from app.core.config.database import get_database_settings

def run_alembic_command(command: str) -> None:
    """执行Alembic命令"""
    try:
        print(f"执行命令: alembic {command}")
        result = subprocess.run(
            ["alembic", command],
            check=True,
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        print(result.stdout)
        if result.stderr:
            print(f"警告: {result.stderr}")
        print("命令执行成功")
    except subprocess.CalledProcessError as e:
        print(f"命令执行失败: {e}")
        print(f"错误输出: {e.stderr}")
        sys.exit(1)

def create_migration(message: str) -> None:
    """创建新的迁移"""
    run_alembic_command(f"revision --autogenerate -m \"{message}\"")

def upgrade() -> None:
    """升级到最新版本"""
    run_alembic_command("upgrade head")

def downgrade(revision: str = "base") -> None:
    """回滚到指定版本"""
    run_alembic_command(f"downgrade {revision}")

def show_history() -> None:
    """显示迁移历史"""
    run_alembic_command("history --verbose")

def show_current() -> None:
    """显示当前版本"""
    run_alembic_command("current")

def main() -> None:
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python migrate.py [command] [options]")
        print("\n命令:")
        print("  create <message>    创建新的迁移")
        print("  upgrade             升级到最新版本")
        print("  downgrade [revision] 回滚到指定版本 (默认: base)")
        print("  history             显示迁移历史")
        print("  current             显示当前版本")
        sys.exit(1)

    command = sys.argv[1]
    
    if command == "create" and len(sys.argv) >= 3:
        create_migration(sys.argv[2])
    elif command == "upgrade":
        upgrade()
    elif command == "downgrade":
        revision = sys.argv[2] if len(sys.argv) >= 3 else "base"
        downgrade(revision)
    elif command == "history":
        show_history()
    elif command == "current":
        show_current()
    else:
        print(f"未知命令: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()