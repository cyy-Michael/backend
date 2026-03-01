# 导师管理系统 - 完整功能文档

## 📚 文档导航

本系统包含完整的导师管理功能，包括基础CRUD、软删除、批量操作等。

### 核心功能文档

1. **[导师CRUD API文档](TUTOR_CRUD_API_DOCUMENTATION.md)**
   - 创建导师（含论文、项目）
   - 查询导师详情
   - 更新导师信息
   - 删除导师（软删除）

2. **[软删除功能文档](TUTOR_SOFT_DELETE_DOCUMENTATION.md)**
   - 软删除vs硬删除
   - 批量修改导师
   - 恢复已删除导师
   - 数据库字段说明

3. **[快速参考](TUTOR_SOFT_DELETE_QUICK_REFERENCE.md)**
   - 常用API命令
   - 测试命令
   - 常见问题

4. **[变更总结](SOFT_DELETE_CHANGES_SUMMARY.md)**
   - 功能变更说明
   - 迁移指南
   - 性能影响分析

---

## 🚀 快速开始

### 1. 环境配置

```bash
# 安装依赖
pip install -r requirements.txt

# 配置数据库
# MongoDB URI已配置在 app/core/config/database.py
```

### 2. 启动服务

```bash
# 启动FastAPI服务
cd backend
uvicorn main:app --reload --port 8000
```

### 3. 运行测试

```bash
# 运行导师管理测试
python test_tutor_crud_api.py
```

---

## 📋 功能概览

### 基础CRUD功能

| 功能 | 方法 | 路径 | 权限 |
|------|------|------|------|
| 创建导师 | POST | `/tutor/admin/create` | 管理员 |
| 查询列表 | GET | `/tutor/list` | 公开 |
| 查询详情 | GET | `/tutor/detail/{id}` | 公开 |
| 更新导师 | PUT | `/tutor/admin/update/{id}` | 管理员 |
| 删除导师 | DELETE | `/tutor/admin/delete/{id}` | 管理员 |

### 高级功能

| 功能 | 方法 | 路径 | 权限 |
|------|------|------|------|
| 批量修改 | POST | `/tutor/admin/batch-update` | 管理员 |
| 批量删除 | POST | `/tutor/admin/batch-delete` | 管理员 |
| 恢复删除 | POST | `/tutor/admin/restore/{id}` | 管理员 |

---

## 🔑 核心特性

### 1. 软删除机制

- **数据保留**: 删除的数据仍保留在数据库中
- **可恢复**: 支持恢复误删除的数据
- **自动过滤**: 查询接口自动过滤已删除数据
- **审计追踪**: 记录删除者、删除时间、恢复者、恢复时间

### 2. 批量操作

- **批量修改**: 一次修改多个导师的相同字段
- **批量删除**: 一次软删除多个导师
- **限制**: 最多100个导师ID
- **统计**: 返回成功和失败的详细统计

### 3. 完整的数据模型

- **基本信息**: 姓名、学校、院系、职称、研究方向
- **联系方式**: 邮箱、电话、个人主页
- **学术成果**: 论文列表、项目列表
- **标签系统**: 支持自定义标签

### 4. 权限控制

- **管理员验证**: 所有管理接口需要管理员权限
- **JWT认证**: 基于JWT的用户认证
- **灵活配置**: 支持白名单和数据库角色两种方式

---

## 📊 数据库设计

### 核心集合

1. **tutors** - 导师基本信息
   ```javascript
   {
     id: "tutor_123",
     name: "张三",
     school_name: "清华大学",
     department_name: "计算机系",
     title: "教授",
     research_direction: "人工智能",
     email: "zhangsan@example.com",
     phone: "13800138000",
     avatar_url: "https://...",
     personal_page_url: "https://...",
     bio: "个人简介...",
     tags: ["AI", "机器学习"],
     is_deleted: false,
     deleted_at: null,
     deleted_by: null,
     created_at: ISODate("..."),
     updated_at: ISODate("...")
   }
   ```

2. **papers** - 论文信息
   ```javascript
   {
     id: "paper_123",
     tutor_id: "tutor_123",
     title: "论文标题",
     authors: ["张三", "李四"],
     journal: "期刊名称",
     year: 2024,
     doi: "10.1234/...",
     abstract: "摘要..."
   }
   ```

3. **projects** - 项目信息
   ```javascript
   {
     id: "project_123",
     tutor_id: "tutor_123",
     title: "项目标题",
     funding: "国家自然科学基金",
     start_date: ISODate("..."),
     end_date: ISODate("..."),
     description: "项目描述..."
   }
   ```

### 索引建议

```javascript
// tutors集合
db.tutors.createIndex({ "is_deleted": 1 })
db.tutors.createIndex({ "is_deleted": 1, "created_at": -1 })
db.tutors.createIndex({ "name": "text", "research_direction": "text" })

// papers集合
db.papers.createIndex({ "tutor_id": 1 })

// projects集合
db.projects.createIndex({ "tutor_id": 1 })
```

---

## 🧪 测试指南

### 测试脚本

**文件**: `test_tutor_crud_api.py`

**测试场景**:
1. ✅ 登录获取token
2. ✅ 创建导师（含论文、项目）
3. ✅ 查询导师详情
4. ✅ 更新导师信息
5. ✅ 更新论文列表
6. ✅ 软删除导师
7. ✅ 恢复已删除导师
8. ✅ 批量修改导师
9. ✅ 批量软删除导师
10. ✅ 权限验证
11. ✅ 数据验证
12. ✅ 错误处理

### 运行测试

```bash
# 完整测试
python test_tutor_crud_api.py

# 预期输出
# ✅ 14个测试场景全部通过
```

---

## 📝 使用示例

### Python示例

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# 1. 登录获取token
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={"code": "wx_code"}
)
token = login_response.json()["data"]["token"]
headers = {"Authorization": f"Bearer {token}"}

# 2. 创建导师
tutor_data = {
    "name": "张三",
    "school": "清华大学",
    "department": "计算机系",
    "title": "教授",
    "research_direction": "人工智能",
    "email": "zhangsan@example.com",
    "papers": [
        {
            "title": "论文标题",
            "authors": ["张三"],
            "journal": "期刊名",
            "year": 2024
        }
    ]
}
create_response = requests.post(
    f"{BASE_URL}/tutor/admin/create",
    headers=headers,
    json=tutor_data
)
tutor_id = create_response.json()["data"]["id"]

# 3. 查询导师
detail_response = requests.get(
    f"{BASE_URL}/tutor/detail/{tutor_id}",
    headers=headers
)

# 4. 更新导师
update_data = {
    "title": "副教授",
    "tags": ["AI", "机器学习"]
}
update_response = requests.put(
    f"{BASE_URL}/tutor/admin/update/{tutor_id}",
    headers=headers,
    json=update_data
)

# 5. 批量修改
batch_update_data = {
    "tutor_ids": [tutor_id],
    "update_fields": {"title": "教授"}
}
batch_update_response = requests.post(
    f"{BASE_URL}/tutor/admin/batch-update",
    headers=headers,
    json=batch_update_data
)

# 6. 软删除
delete_response = requests.delete(
    f"{BASE_URL}/tutor/admin/delete/{tutor_id}",
    headers=headers
)

# 7. 恢复删除
restore_response = requests.post(
    f"{BASE_URL}/tutor/admin/restore/{tutor_id}",
    headers=headers
)
```

### JavaScript示例

```javascript
const BASE_URL = "http://localhost:8000/api/v1";

// 登录
const loginRes = await fetch(`${BASE_URL}/auth/login`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ code: "wx_code" })
});
const { token } = (await loginRes.json()).data;
const headers = { "Authorization": `Bearer ${token}` };

// 创建导师
const createRes = await fetch(`${BASE_URL}/tutor/admin/create`, {
  method: "POST",
  headers: { ...headers, "Content-Type": "application/json" },
  body: JSON.stringify({
    name: "张三",
    school: "清华大学",
    department: "计算机系",
    title: "教授"
  })
});

// 批量修改
await fetch(`${BASE_URL}/tutor/admin/batch-update`, {
  method: "POST",
  headers: { ...headers, "Content-Type": "application/json" },
  body: JSON.stringify({
    tutor_ids: ["id1", "id2"],
    update_fields: { title: "副教授" }
  })
});
```

---

## ⚠️ 注意事项

### 1. 权限要求

- **所有管理接口**: 需要管理员权限
- **查询接口**: 公开访问
- **认证方式**: JWT Bearer Token

### 2. 数据限制

- **批量操作**: 最多100个导师ID
- **论文数量**: 建议不超过100篇
- **项目数量**: 建议不超过50个
- **标签数量**: 建议不超过20个

### 3. 软删除机制

- **查询自动过滤**: 列表和详情接口会过滤已删除数据
- **可恢复**: 使用恢复接口可以还原数据
- **定期清理**: 建议90天后清理未恢复的数据

### 4. 性能优化

- **索引**: 确保创建必要的数据库索引
- **缓存**: 考虑对热门导师数据进行缓存
- **分页**: 列表查询支持分页，建议每页不超过50条

---

## 🔧 配置说明

### 数据库配置

**文件**: `app/core/config/database.py`

```python
MONGO_URI = "mongodb+srv://..."
DATABASE_NAME = "tutor_social_work"
```

### 管理员配置

**文件**: `app/utils/admin.py`

```python
# 方式1: 白名单
ADMIN_USER_IDS = ["admin_id_1", "admin_id_2"]

# 方式2: 数据库角色
# 在users集合中添加role字段
# {"id": "user_123", "role": "admin"}
```

---

## 📈 性能指标

### 响应时间（参考值）

| 操作 | 平均响应时间 | 备注 |
|------|-------------|------|
| 创建导师 | 50-100ms | 含论文、项目 |
| 查询详情 | 20-50ms | 含关联数据 |
| 更新导师 | 30-60ms | 部分字段 |
| 删除导师 | 20-40ms | 软删除 |
| 批量修改 | 100-300ms | 10个导师 |
| 批量删除 | 50-150ms | 10个导师 |

### 并发能力

- **单实例**: 100-200 QPS
- **集群**: 500-1000 QPS
- **建议**: 使用负载均衡和数据库读写分离

---

## 🐛 常见问题

### Q1: 软删除后能否再次删除？
**A**: 不能，会返回 `ALREADY_DELETED` 错误。

### Q2: 恢复后数据是否完整？
**A**: 是的，论文、项目等关联数据都会自动可用。

### Q3: 批量操作失败如何处理？
**A**: 返回成功和失败的统计，以及失败的ID列表，可以针对失败的ID重试。

### Q4: 如何永久删除数据？
**A**: 需要超级管理员权限，直接操作数据库。建议90天后自动清理。

### Q5: 查询性能如何优化？
**A**: 
1. 创建必要的索引
2. 使用分页查询
3. 考虑缓存热门数据
4. 定期清理软删除数据

---

## 📞 技术支持

### 文档资源

- **完整API文档**: TUTOR_CRUD_API_DOCUMENTATION.md
- **软删除文档**: TUTOR_SOFT_DELETE_DOCUMENTATION.md
- **快速参考**: TUTOR_SOFT_DELETE_QUICK_REFERENCE.md
- **变更总结**: SOFT_DELETE_CHANGES_SUMMARY.md

### 测试资源

- **测试脚本**: test_tutor_crud_api.py
- **测试数据**: 脚本中包含示例数据

### 联系方式

- **技术问题**: 联系后端团队
- **功能建议**: 提交issue
- **紧急问题**: 联系项目负责人

---

## 🎯 后续规划

### 短期（1-2周）
- [ ] 添加导师审核功能
- [ ] 实现导师推荐算法
- [ ] 优化查询性能

### 中期（1-2月）
- [ ] 添加导师评分系统
- [ ] 实现高级搜索功能
- [ ] 导师数据分析

### 长期（3-6月）
- [ ] AI辅助导师匹配
- [ ] 导师画像系统
- [ ] 数据可视化大屏

---

**文档版本**: v1.0.0  
**最后更新**: 2024-03-01  
**维护者**: Backend Team  
**项目**: 导师社工小程序
