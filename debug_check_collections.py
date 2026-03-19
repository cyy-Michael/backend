import asyncio
from app.db.mongo import get_db

async def main():
    db = get_db()
    
    # 查看所有集合
    collections = await db.list_collection_names()
    print("数据库中的所有集合:")
    for coll in collections:
        print(f"  - {coll}")
    
    # 查看 papers 集合的结构
    if "papers" in collections:
        print("\n=== papers 集合 ===")
        paper = await db.papers.find_one({})
        if paper:
            print("样例文档:")
            for key, value in paper.items():
                print(f"  {key}: {value}")
        count = await db.papers.count_documents({})
        print(f"总计: {count} 条")
    
    # 查看 projects 集合的结构
    if "projects" in collections:
        print("\n=== projects 集合 ===")
        project = await db.projects.find_one({})
        if project:
            print("样例文档:")
            for key, value in project.items():
                print(f"  {key}: {value}")
        count = await db.projects.count_documents({})
        print(f"总计: {count} 条")
    
    # 查看 coops 集合的结构（如果有）
    if "coops" in collections:
        print("\n=== coops 集合 ===")
        coop = await db.coops.find_one({})
        if coop:
            print("样例文档:")
            for key, value in coop.items():
                print(f"  {key}: {value}")
        count = await db.coops.count_documents({})
        print(f"总计: {count} 条")
    
    # 查看 tutors 集合中的合作关系字段
    print("\n=== tutors 集合中的 coops 字段 ===")
    tutor = await db.tutors.find_one({"coops": {"$exists": True}})
    if tutor:
        print(f"导师: {tutor.get('name')}")
        print(f"coops: {tutor.get('coops', [])}")
    else:
        print("没有带 coops 字段的导师文档")

if __name__ == "__main__":
    asyncio.run(main())
