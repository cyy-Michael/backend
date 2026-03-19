import asyncio

from app.db.mongo import get_db


async def main():
    db = get_db()
    coll = db.tutors
    kw = "张子威"
    print("DEBUG search keyword =", kw)
    total_all = await coll.count_documents({})
    total_name = await coll.count_documents({"name": {"$regex": kw}})
    total_name_i = await coll.count_documents({"name": {"$regex": kw, "$options": "i"}})
    # 按后端当前逻辑（注意字段名 research_direction 在实际文档中是 direction）
    query_backend = {
        "$or": [
            {"is_deleted": {"$exists": False}},
            {"is_deleted": False},
        ],
        "$and": [
            {
                "$or": [
                    {"name": {"$regex": kw, "$options": "i"}},
                    {"research_direction": {"$regex": kw, "$options": "i"}},
                ]
            }
        ],
    }
    total_backend = await coll.count_documents(query_backend)

    print("TOTAL_ALL       =", total_all)
    print("TOTAL_NAME      =", total_name)
    print("TOTAL_NAME_i    =", total_name_i)
    print("TOTAL_BACKEND_Q =", total_backend)


if __name__ == "__main__":
    asyncio.run(main())

