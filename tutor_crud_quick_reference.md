# 🎓 导师CRUD接口快速参考

## 📌 接口速查表

| 接口 | 方法 | 路径 | 功能 | 权限 |
|------|------|------|------|------|
| 新增导师 | POST | `/api/v1/tutor/admin/create` | 创建导师信息 | 管理员 |
| 更新导师 | PUT | `/api/v1/tutor/admin/update/{tutor_id}` | 更新导师信息 | 管理员 |
| 删除导师 | DELETE | `/api/v1/tutor/admin/delete/{tutor_id}` | 删除导师信息 | 管理员 |
| 批量删除 | POST | `/api/v1/tutor/admin/batch-delete` | 批量删除导师 | 管理员 |

## 🔐 添加管理员

### 方法1：修改代码（开发环境）
```python
# 编辑 app/utils/admin.py
ADMIN_USER_IDS = [
    "admin_user_001",
    "your_user_id_here"  # 添加你的用户ID
]
```

### 方法2：数据库设置（生产环境）
```javascript
// 在MongoDB中执行
db.users.updateOne(
  { id: "your_user_id" },
  { $set: { is_admin: true } }
)
```

## 🚀 快速开始

### 1. 创建导师
```bash
curl -X POST "http://localhost:8000/api/v1/tutor/admin/create" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "张三",
    "school": "清华大学",
    "department": "计算机系",
    "title": "教授",
    "research_direction": "人工智能",
    "email": "zhangsan@example.edu.cn",
    "papers": [
      {
        "title": "深度学习研究",
        "authors": ["张三", "李四"],
        "year": 2024
      }
    ]
  }'
```

### 2. 更新导师
```bash
curl -X PUT "http://localhost:8000/api/v1/tutor/admin/update/tutor_123" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "教授、博士生导师",
    "email": "zhangsan_new@example.edu.cn"
  }'
```

### 3. 删除导师
```bash
curl -X DELETE "http://localhost:8000/api/v1/tutor/admin/delete/tutor_123" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

### 4. 批量删除
```bash
curl -X POST "http://localhost:8000/api/v1/tutor/admin/batch-delete" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tutor_ids": ["tutor_123", "tutor_456"]
  }'
```

## 📝 最小请求示例

### 创建导师（最少字段）
```json
{
  "name": "张三",
  "school": "清华大学",
  "department": "计算机系"
}
```

### 更新导师（任意字段）
```json
{
  "title": "教授"
}
```

## ⚠️ 常见错误

| 错误码 | 状态码 | 说明 | 解决方法 |
|--------|--------|------|----------|
| FORBIDDEN | 403 | 权限不足 | 使用管理员账号登录 |
| TUTOR_NOT_FOUND | 404 | 导师不存在 | 检查导师ID是否正确 |
| authentication_error | 401 | token无效 | 重新登录获取token |
| - | 422 | 数据验证失败 | 检查请求参数格式 |

## 🧪 测试

```bash
# 运行测试脚本
python test_tutor_crud_api.py
```

## 📖 详细文档

- **完整接口文档**: `TUTOR_CRUD_API_DOCUMENTATION.md`
- **测试脚本**: `test_tutor_crud_api.py`

---

**提示**: 所有接口都需要管理员权限！
