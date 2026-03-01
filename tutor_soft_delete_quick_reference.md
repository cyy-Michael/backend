# 导师软删除功能快速参考

## 🚀 快速开始

### 1. 软删除导师
```bash
DELETE /api/v1/tutor/admin/delete/{tutor_id}
Authorization: Bearer {admin_token}
```

### 2. 批量修改导师
```bash
POST /api/v1/tutor/admin/batch-update
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "tutor_ids": ["id1", "id2"],
  "update_fields": {
    "title": "副教授",
    "tags": ["AI", "ML"]
  }
}
```

### 3. 批量软删除
```bash
POST /api/v1/tutor/admin/batch-delete
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "tutor_ids": ["id1", "id2", "id3"]
}
```

### 4. 恢复删除
```bash
POST /api/v1/tutor/admin/restore/{tutor_id}
Authorization: Bearer {admin_token}
```

---

## 📋 接口对比

| 功能 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 软删除 | DELETE | `/admin/delete/{id}` | 标记删除，可恢复 |
| 批量修改 | POST | `/admin/batch-update` | 修改多个导师相同字段 |
| 批量删除 | POST | `/admin/batch-delete` | 批量软删除 |
| 恢复删除 | POST | `/admin/restore/{id}` | 恢复已删除导师 |

---

## 🔑 关键字段

```javascript
{
  "is_deleted": false,      // 是否已删除
  "deleted_at": null,       // 删除时间
  "deleted_by": null,       // 删除者ID
  "restored_at": null,      // 恢复时间
  "restored_by": null       // 恢复者ID
}
```

---

## ⚡ 测试命令

```bash
# 运行测试
cd backend
python test_tutor_crud_api.py

# 测试覆盖：
# ✅ 软删除单个导师
# ✅ 恢复已删除导师
# ✅ 批量修改导师
# ✅ 批量软删除导师
# ✅ 查询接口过滤已删除数据
```

---

## 📊 数据库查询

```javascript
// 查询所有未删除的导师
db.tutors.find({
  $or: [
    { is_deleted: { $exists: false } },
    { is_deleted: false }
  ]
})

// 查询所有已删除的导师
db.tutors.find({ is_deleted: true })

// 恢复导师（手动）
db.tutors.updateOne(
  { id: "tutor_123" },
  {
    $set: {
      is_deleted: false,
      deleted_at: null,
      deleted_by: null,
      restored_at: new Date(),
      updated_at: new Date()
    }
  }
)
```

---

## ⚠️ 重要提示

1. **软删除不是物理删除**：数据仍在数据库中
2. **查询自动过滤**：列表和详情接口会过滤已删除数据
3. **可恢复**：使用恢复接口可以还原已删除数据
4. **批量限制**：最多100个导师ID
5. **权限要求**：所有接口都需要管理员权限

---

## 🐛 常见问题

**Q: 软删除后能否再次删除？**  
A: 不能，会返回 `ALREADY_DELETED` 错误

**Q: 恢复后数据是否完整？**  
A: 是的，论文、项目等关联数据都会自动可用

**Q: 批量操作失败如何处理？**  
A: 返回成功和失败的统计，以及失败的ID列表

**Q: 如何永久删除数据？**  
A: 需要超级管理员权限，直接操作数据库

---

**快速参考版本**: v1.0.0  
**对应完整文档**: TUTOR_SOFT_DELETE_DOCUMENTATION.md
