import asyncio

from app.db.mongo import get_db
from app.core.config.database import database_settings


async def main():
    print("DEBUG: MONGO_URI =", database_settings.MONGO_URI)
    print("DEBUG: DB_NAME   =", database_settings.DB_NAME)
    db = get_db()
    coll = db.tutors
    try:
        print("DEBUG: start tutor list query")
        total = await coll.count_documents({})
        print("DEBUG: total =", total)
        cursor = coll.find({}).sort("created_at", -1).skip(0).limit(10)
        docs = await cursor.to_list(length=10)
        print("DEBUG: docs_len =", len(docs))
        if docs:
            first = docs[0]
            print("DEBUG: first_keys =", list(first.keys()))
            print("DEBUG: first_sample =", {k: first.get(k) for k in list(first.keys())[:10]})
    except Exception as e:
        import traceback

        print("DEBUG: exception type:", type(e))
        print("DEBUG: exception:", repr(e))
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

