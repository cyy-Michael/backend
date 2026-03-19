import asyncio
from app.db.mongo import get_db
import json

async def test_network():
    db = get_db()
    
    # 测试导师 ID 格式
    tutor_id = "tutor_Ziwei_Zhang"
    
    # 1. 查找包含该导师的 coops 记录
    coops = await db.coops.find({"members.id": tutor_id}).to_list(length=10)
    
    print(f"导师 {tutor_id} 的合作记录数: {len(coops)}")
    
    if coops:
        for i, coop in enumerate(coops[:3]):
            print(f"\n合作 {i+1}:")
            print(f"  ID: {coop.get('id')}")
            print(f"  标题: {coop.get('title_cn') or coop.get('title', 'N/A')}")
            print(f"  类型: {coop.get('type_cn') or coop.get('type', 'N/A')}")
            
            members = coop.get('members', [])
            print(f"  成员数量: {len(members)}")
            print(f"  成员详情:")
            for m in members:
                print(f"    - ID: {m.get('id')}, 姓名: {m.get('name')}, 学校: {m.get('school')}")
    else:
        print("没有找到合作记录")
    
    # 2. 查看是否有包含多个成员的合作记录
    print("\n\n查找包含多个成员的合作记录:")
    multi_member_coops = await db.coops.find({
        "$and": [
            {"members.0": {"$exists": True}},
            {"members.1": {"$exists": True}}
        ]
    }).to_list(length=5)
    
    print(f"找到 {len(multi_member_coops)} 条多成员合作记录")
    
    for i, coop in enumerate(multi_member_coops[:3]):
        print(f"\n多成员合作 {i+1}:")
        print(f"  ID: {coop.get('id')}")
        members = coop.get('members', [])
        print(f"  成员数量: {len(members)}")
        for m in members:
            print(f"    - {m.get('id')}: {m.get('name')} ({m.get('school')})")
    
    # 3. 如果没有多成员记录，看看如何从现有数据生成合作关系
    if not multi_member_coops:
        print("\n\n数据库中没有多成员合作记录。")
        print("现有数据结构建议：")
        print("  - 基于相同领域/标签生成虚拟合作关系")
        print("  - 或者从其他数据源导入合作信息")
        
        # 查看所有导师的标签，找相似的
        print("\n\n查看导师标签，寻找可能的合作关系:")
        tutors = await db.tutors.find({}).to_list(length=20)
        for tutor in tutors[:5]:
            print(f"  {tutor.get('id')}: {tutor.get('name')}")
            print(f"    方向: {tutor.get('direction', 'N/A')}")
            print(f"    标签: {tutor.get('tags', [])}")
            print()

if __name__ == "__main__":
    asyncio.run(test_network())
