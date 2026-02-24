from app.db.mongo import get_db
from bson.objectid import ObjectId

# 获取数据库实例和teachers集合
db = get_db()
teacher_collection = db["teachers"]

# 根据邮箱查询导师
def get_teacher_by_email(email: str):
    return teacher_collection.find_one({"email": email})

# 获取所有导师列表
def get_all_teachers():
    teachers = list(teacher_collection.find())
    # 将ObjectId转换为字符串，方便前端处理
    for teacher in teachers:
        if "_id" in teacher:
            teacher["_id"] = str(teacher["_id"])
    return teachers

# 新增导师
def create_teacher(teacher_data: dict):
    result = teacher_collection.insert_one(teacher_data)
    return {"id": str(result.inserted_id), "email": teacher_data["email"]}

# 更新导师信息
def update_teacher(email: str, update_data: dict):
    # 只更新传入的字段（$set）
    result = teacher_collection.update_one(
        {"email": email},
        {"$set": update_data}
    )
    return result.modified_count > 0

# 删除导师
def delete_teacher(email: str):
    result = teacher_collection.delete_one({"email": email})
    return result.deleted_count > 0