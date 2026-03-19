import asyncio
from app.db.mongo import get_db

async def test_network():
    db = get_db()
    
    # 测试导师 ID 格式
    tutor_id = "tutor_Ziwei_Zhang"  # 张子威
    
    # 1. 查找包含该导师的 coops 记录
    coops = await db.coops.find({"members.id": tutor_id}).to_list(length=10)
    
    print(f"导师 {tutor_id} 的合作记录数: {len(coops)}")
    
    if coops:
        for i, coop in enumerate(coops[:3]):  # 只显示前3条
            print(f"\n合作 {i+1}:")
            print(f"  标题: {coop.get('title_cn', coop.get('title', 'N/A'))}")
            print(f"  类型: {coop.get('type_cn', coop.get('type', 'N/A'))}")
            print(f"  成员: {[m.get('name') for m in coop.get('members', [])]}")
    else:
        print("没有找到合作记录")
        
        # 查看有哪些导师有合作记录
        print("\n查看 coops 集合中的样例数据:")
        sample = await db.coops.find_one({})
        if sample:
            print(f"样例 coop ID: {sample.get('id')}")
            print(f"样例成员: {sample.get('members', [])}")
            
            # 获取所有唯一的导师ID
            all_coops = await db.coops.find({}).to_list(length=20)
            tutor_ids = set()
            for coop in all_coops:
                for member in coop.get('members', []):
                    tutor_ids.add(member.get('id'))
            print(f"\n有合作记录的导师ID列表:")
            for tid in list(tutor_ids)[:10]:
                print(f"  - {tid}")

if __name__ == "__main__":
    asyncio.run(test_network())
