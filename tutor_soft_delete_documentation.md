# 导师软删除功能文档

## 📋 概述

本文档说明导师信息的软删除功能，包括软删除、批量修改、恢复删除等高级管理功能。

## 🔄 软删除 vs 硬删除

### 软删除（Soft Delete）
- **定义**: 在数据库中标记数据为已删除状态，但不实际删除数据
- **优点**: 
  - 可以恢复误删除的数据
  - 保留数据历史记录
  - 便于审计和追踪
- **实现**: 添加 `is_deleted`、`deleted_at`、`deleted_by` 字段

### 硬删除（Hard Delete）
- **定义**: 从数据库中物理删除数据
- **缺点**: 
  - 数据无法恢复
  - 失去历史记录
  - 可能影响数据完整性

## 📌 新增接口

### 1. 软删除导师（单个）

**接口地址**: `DELETE /api/v1/tutor/admin/delete/{tutor_id}`

**功能**: 软删除指定导师，标记为已删除状态

**请求头**:
```
Authorization: Bearer {admin_token}
```

**路径参数**:
- `tutor_id`: 导师ID

**响应示例**:
```json
{
  "code": 200,
  "message": "导师信息删除成功",
  "data": {
    "success": true,
    "tutor_id": "tutor_123",
    "message": "已删除导师 张三（软删除）"
  }
}
```

**数据库变化**:
```javascript
// 删除前
{
  "id": "tutor_123",
  "name": "张三",
  "is_deleted": false  // 或不存在此字段
}

// 删除后
{
  "id": "tutor_123",
  "name": "张三",
  "is_deleted": true,
  "deleted_at": ISODate("2024-03-01T12:00:00Z"),
  "deleted_by": "admin_user_001",
  "updated_at": ISODate("2024-03-01T12:00:00Z")
}
```

---

### 2. 批量软删除导师

**接口地址**: `POST /api/v1/tutor/admin/batch-delete`

**功能**: 批量软删除多个导师

**请求体**:
```json
{
  "tutor_ids": ["tutor_123", "tutor_456", "tutor_789"]
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "批量删除完成：成功2个，失败1个",
  "data": {
    "success_count": 2,
    "failed_count": 1,
    "total_count": 3,
    "failed_ids": ["tutor_789"]
  }
}
```

**失败原因**:
- 导师不存在
- 导师已被删除
- 数据库操作失败

---

### 3. 批量修改导师

**接口地址**: `POST /api/v1/tutor/admin/batch-update`

**功能**: 批量修改多个导师的相同字段

**请求体**:
```json
{
  "tutor_ids": ["tutor_123", "tutor_456"],
  "update_fields": {
    "title": "副教授",
    "tags": ["数据科学", "人工智能"]
  }
}
```

**支持的更新字段**:
- `title`: 职称
- `research_direction`: 研究方向
- `email`: 邮箱
- `phone`: 电话
- `tags`: 标签列表

**响应示例**:
```json
{
  "code": 200,
  "message": "批量修改完成：成功2个，失败0个",
  "data": {
    "success_count": 2,
    "failed_count": 0,
    "total_count": 2,
    "failed_ids": [],
    "updated_fields": ["title", "tags", "updated_at", "updated_by"]
  }
}
```

**限制**:
- 最多100个导师ID
- 只能修改指定的字段
- 不能修改已删除的导师

---

### 4. 恢复已删除的导师

**接口地址**: `POST /api/v1/tutor/admin/restore/{tutor_id}`

**功能**: 恢复软删除的导师信息

**请求头**:
```
Authorization: Bearer {admin_token}
```

**路径参数**:
- `tutor_id`: 导师ID

**响应示例**:
```json
{
  "code": 200,
  "message": "导师信息恢复成功",
  "data": {
    "success": true,
    "tutor_id": "tutor_123",
    "message": "已恢复导师 张三"
  }
}
```

**数据库变化**:
```javascript
// 恢复前
{
  "id": "tutor_123",
  "name": "张三",
  "is_deleted": true,
  "deleted_at": ISODate("2024-03-01T12:00:00Z"),
  "deleted_by": "admin_user_001"
}

// 恢复后
{
  "id": "tutor_123",
  "name": "张三",
  "is_deleted": false,
  "deleted_at": null,
  "deleted_by": null,
  "restored_at": ISODate("2024-03-01T13:00:00Z"),
  "restored_by": "admin_user_002",
  "updated_at": ISODate("2024-03-01T13:00:00Z")
}
```

---

## 🔍 查询接口变化

### 导师列表接口

**变化**: 自动过滤已删除的导师

**查询条件**:
```javascript
{
  "$or": [
    {"is_deleted": {"$exists": false}},  // 没有is_deleted字段
    {"is_deleted": false}  // 或者is_deleted为False
  ]
}
```

### 导师详情接口

**变化**: 查询已删除的导师返回404

**查询条件**:
```javascript
{
  "id": tutor_id,
  "$or": [
    {"is_deleted": {"$exists": false}},
    {"is_deleted": false}
  ]
}
```

---

## 🗄️ 数据库字段说明

### tutors 集合新增字段

| 字段 | 类型 | 说明 |
|------|------|------|
| is_deleted | boolean | 是否已删除，默认false |
| deleted_at | datetime | 删除时间 |
| deleted_by | string | 删除者用户ID |
| restored_at | datetime | 恢复时间（如果有恢复操作） |
| restored_by | string | 恢复者用户ID（如果有恢复操作） |

### 索引建议

```javascript
// 为is_deleted字段创建索引，提高查询性能
db.tutors.createIndex({ "is_deleted": 1 })

// 复合索引：用于过滤已删除数据的查询
db.tutors.createIndex({ "is_deleted": 1, "created_at": -1 })
```

---

## 📝 使用示例

### Python

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"
headers = {"Authorization": f"Bearer {admin_token}"}

# 1. 软删除导师
delete_response = requests.delete(
    f"{BASE_URL}/tutor/admin/delete/tutor_123",
    headers=headers
)
print(delete_response.json())

# 2. 批量修改导师
batch_update_response = requests.post(
    f"{BASE_URL}/tutor/admin/batch-update",
    headers=headers,
    json={
        "tutor_ids": ["tutor_123", "tutor_456"],
        "update_fields": {
            "title": "副教授",
            "tags": ["AI", "机器学习"]
        }
    }
)
print(batch_update_response.json())

# 3. 批量软删除
batch_delete_response = requests.post(
    f"{BASE_URL}/tutor/admin/batch-delete",
    headers=headers,
    json={"tutor_ids": ["tutor_123", "tutor_456"]}
)
print(batch_delete_response.json())

# 4. 恢复已删除的导师
restore_response = requests.post(
    f"{BASE_URL}/tutor/admin/restore/tutor_123",
    headers=headers
)
print(restore_response.json())
```

### JavaScript

```javascript
const BASE_URL = "http://localhost:8000/api/v1";
const headers = { "Authorization": `Bearer ${adminToken}` };

// 软删除
await fetch(`${BASE_URL}/tutor/admin/delete/tutor_123`, {
  method: "DELETE",
  headers
});

// 批量修改
await fetch(`${BASE_URL}/tutor/admin/batch-update`, {
  method: "POST",
  headers: { ...headers, "Content-Type": "application/json" },
  body: JSON.stringify({
    tutor_ids: ["tutor_123", "tutor_456"],
    update_fields: { title: "副教授" }
  })
});

// 恢复删除
await fetch(`${BASE_URL}/tutor/admin/restore/tutor_123`, {
  method: "POST",
  headers
});
```

---

## ⚠️ 注意事项

### 1. 软删除的数据处理

**查询接口**:
- 所有公开查询接口（列表、详情）都会过滤已删除数据
- 用户无法看到已删除的导师

**管理接口**:
- 管理员可以通过恢复接口恢复已删除的数据
- 已删除的数据不能再次删除（会返回错误）

### 2. 批量操作限制

**批量修改**:
- 最多100个导师ID
- 只能修改指定的字段
- 不能修改已删除的导师

**批量删除**:
- 最多100个导师ID
- 已删除的导师会被跳过
- 返回成功和失败的统计

### 3. 数据一致性

**关联数据**:
- 软删除不会删除论文和项目数据
- 论文和项目仍然保留在数据库中
- 收藏记录不受影响

**恢复数据**:
- 恢复导师后，所有关联数据自动可用
- 不需要单独恢复论文和项目

### 4. 审计追踪

**记录信息**:
- 删除者ID（deleted_by）
- 删除时间（deleted_at）
- 恢复者ID（restored_by）
- 恢复时间（restored_at）

---

## 🔄 迁移指南

### 从硬删除迁移到软删除

如果你的系统之前使用硬删除，需要进行以下迁移：

1. **添加字段**:
```javascript
// 为所有现有导师添加is_deleted字段
db.tutors.updateMany(
  { is_deleted: { $exists: false } },
  { $set: { is_deleted: false } }
)
```

2. **创建索引**:
```javascript
db.tutors.createIndex({ "is_deleted": 1 })
```

3. **更新查询**:
   - 所有查询都需要添加 `is_deleted: false` 条件
   - 或使用 `$or` 条件兼容旧数据

---

## 📊 错误码说明

| 错误码 | HTTP状态码 | 说明 |
|--------|-----------|------|
| ALREADY_DELETED | 400 | 导师已被删除 |
| NOT_DELETED | 400 | 导师未被删除，无需恢复 |
| INVALID_REQUEST | 400 | 请求参数无效 |
| TOO_MANY_IDS | 400 | 导师ID数量超过限制 |
| NO_VALID_FIELDS | 400 | 没有有效的更新字段 |
| TUTOR_NOT_FOUND | 404 | 导师不存在 |
| RESTORE_FAILED | 500 | 恢复导师失败 |

---

## 🧪 测试建议

### 软删除测试
1. 删除导师
2. 验证查询接口无法查到
3. 恢复导师
4. 验证查询接口可以查到
5. 再次删除
6. 尝试重复删除（应该失败）

### 批量操作测试
1. 批量修改多个导师
2. 验证修改成功
3. 批量删除多个导师
4. 验证删除成功
5. 测试包含不存在ID的批量操作

### 边界测试
1. 批量操作100个导师（上限）
2. 批量操作超过100个（应该失败）
3. 恢复未删除的导师（应该失败）
4. 删除已删除的导师（应该失败）

---

## 🎯 最佳实践

### 1. 定期清理
建议定期清理长时间未恢复的软删除数据：
```javascript
// 删除90天前软删除的数据（硬删除）
db.tutors.deleteMany({
  is_deleted: true,
  deleted_at: { $lt: new Date(Date.now() - 90 * 24 * 60 * 60 * 1000) }
})
```

### 2. 权限控制
- 软删除：所有管理员
- 恢复删除：高级管理员
- 硬删除：超级管理员

### 3. 日志记录
- 记录所有删除和恢复操作
- 包含操作者、时间、原因
- 便于审计和追踪

---

**文档版本**: v2.0.0  
**最后更新**: 2024-03-01  
**维护者**: Backend Team
