# 导师CRUD接口文档（管理员）

## 📋 概述

本模块提供导师信息的完整管理功能，包括新增、更新、删除等操作。所有接口都需要管理员权限。

## 🔐 权限说明

### 管理员验证方式

系统支持三种管理员验证方式（优先级从高到低）：

1. **用户ID白名单**（推荐）
   - 在 `app/utils/admin.py` 中的 `ADMIN_USER_IDS` 列表中配置
   - 示例：`["admin_user_001", "admin_user_002"]`

2. **数据库is_admin字段**
   - 在users集合中设置 `is_admin: true`
   - 适合动态管理管理员权限

3. **邮箱白名单**（备用）
   - 在 `app/utils/admin.py` 中的 `ADMIN_EMAILS` 列表中配置
   - 示例：`["admin@example.com"]`

### 如何添加管理员

**方法1：修改代码**（开发环境）
```python
# 在 app/utils/admin.py 中
ADMIN_USER_IDS = [
    "admin_user_001",
    "your_user_id_here"  # 添加你的用户ID
]
```

**方法2：数据库设置**（生产环境推荐）
```javascript
// 在MongoDB中执行
db.users.updateOne(
  { id: "your_user_id" },
  { $set: { is_admin: true } }
)
```

## 📌 接口列表

| 接口 | 方法 | 路径 | 功能 | 权限 |
|------|------|------|------|------|
| 新增导师 | POST | `/api/v1/tutor/admin/create` | 创建导师信息 | 管理员 |
| 更新导师 | PUT | `/api/v1/tutor/admin/update/{tutor_id}` | 更新导师信息 | 管理员 |
| 删除导师 | DELETE | `/api/v1/tutor/admin/delete/{tutor_id}` | 删除导师信息 | 管理员 |
| 批量删除 | POST | `/api/v1/tutor/admin/batch-delete` | 批量删除导师 | 管理员 |

---

## 1. 新增导师信息

### 接口信息
- **接口地址**: `POST /api/v1/tutor/admin/create`
- **接口描述**: 管理员新增导师信息，包括基本信息、论文、项目等
- **权限要求**: 管理员

### 请求头
```
Authorization: Bearer {admin_token}
Content-Type: application/json
```

### 请求体
```json
{
  "name": "张三",
  "school": "清华大学",
  "department": "计算机科学与技术系",
  "title": "教授、博士生导师",
  "research_direction": "人工智能、机器学习、计算机视觉",
  "email": "zhangsan@example.edu.cn",
  "phone": "010-12345678",
  "avatar_url": "https://example.com/avatar.jpg",
  "personal_page_url": "https://example.com/~zhangsan",
  "bio": "张三教授，博士生导师，主要研究方向为人工智能...",
  "papers": [
    {
      "title": "基于深度学习的图像识别研究",
      "authors": ["张三", "李四"],
      "journal": "计算机学报",
      "year": 2024,
      "doi": "10.1234/example.2024.001",
      "abstract": "本文研究了..."
    }
  ],
  "projects": [
    {
      "title": "国家自然科学基金项目",
      "funding": "国家自然科学基金委员会",
      "start_date": "2024-01-01",
      "end_date": "2026-12-31",
      "description": "研究人工智能在医疗领域的应用"
    }
  ],
  "tags": ["AI", "深度学习", "计算机视觉"]
}
```

### 字段说明

#### 基本信息（必填）
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | ✅ | 导师姓名，1-50字符 |
| school | string | ✅ | 所在院校，1-100字符 |
| department | string | ✅ | 所在院系/专业，1-100字符 |

#### 基本信息（可选）
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| title | string | ❌ | 职称，最多50字符 |
| research_direction | string | ❌ | 研究方向，最多500字符 |
| email | string | ❌ | 邮箱，必须是有效的邮箱格式 |
| phone | string | ❌ | 联系电话，最多20字符 |
| avatar_url | string | ❌ | 头像URL，必须是HTTP/HTTPS地址 |
| personal_page_url | string | ❌ | 个人主页URL |
| bio | string | ❌ | 个人简介，最多2000字符 |
| tags | array | ❌ | 标签列表，最多20个 |

#### 论文信息（可选）
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| papers | array | ❌ | 论文列表 |
| papers[].title | string | ✅ | 论文标题，1-500字符 |
| papers[].authors | array | ✅ | 作者列表，至少1个 |
| papers[].journal | string | ❌ | 期刊名称，最多200字符 |
| papers[].year | integer | ✅ | 发表年份，1900-2100 |
| papers[].doi | string | ❌ | DOI，最多100字符 |
| papers[].abstract | string | ❌ | 摘要，最多2000字符 |

#### 项目信息（可选）
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| projects | array | ❌ | 项目列表 |
| projects[].title | string | ✅ | 项目名称，1-500字符 |
| projects[].funding | string | ❌ | 资助来源，最多200字符 |
| projects[].start_date | string | ❌ | 开始日期，格式：YYYY-MM-DD |
| projects[].end_date | string | ❌ | 结束日期，格式：YYYY-MM-DD |
| projects[].description | string | ❌ | 项目描述，最多2000字符 |

### 成功响应
```json
{
  "code": 200,
  "message": "导师信息创建成功",
  "data": {
    "id": "tutor_a1b2c3d4e5f6",
    "name": "张三",
    "school": "清华大学",
    "department": "计算机科学与技术系",
    "title": "教授、博士生导师",
    "research_direction": "人工智能、机器学习、计算机视觉",
    "email": "zhangsan@example.edu.cn",
    "phone": "010-12345678",
    "avatar_url": "https://example.com/avatar.jpg",
    "personal_page_url": "https://example.com/~zhangsan",
    "bio": "张三教授，博士生导师...",
    "papers": [...],
    "projects": [...],
    "tags": ["AI", "深度学习", "计算机视觉"],
    "created_at": "2024-03-01T12:00:00",
    "updated_at": "2024-03-01T12:00:00"
  }
}
```

### 错误响应
- `401 Unauthorized`: 未登录或token无效
- `403 Forbidden`: 权限不足，非管理员用户
- `422 Unprocessable Entity`: 数据验证失败
- `500 Internal Server Error`: 服务器内部错误

---

## 2. 更新导师信息

### 接口信息
- **接口地址**: `PUT /api/v1/tutor/admin/update/{tutor_id}`
- **接口描述**: 管理员更新导师信息，支持部分字段更新
- **权限要求**: 管理员

### 请求头
```
Authorization: Bearer {admin_token}
Content-Type: application/json
```

### 路径参数
- `tutor_id`: 导师ID

### 请求体
```json
{
  "title": "教授、博士生导师、长江学者",
  "research_direction": "人工智能、深度学习、自然语言处理",
  "email": "zhangsan_new@example.edu.cn",
  "tags": ["AI", "NLP", "深度学习"]
}
```

**注意**：
- 所有字段都是可选的，只需传入需要更新的字段
- `papers` 和 `projects` 如果传入，会完全替换原有数据
- 不传入的字段保持原值不变

### 成功响应
```json
{
  "code": 200,
  "message": "导师信息更新成功",
  "data": {
    "updated_fields": ["title", "research_direction", "email", "tags"],
    "tutor": {
      "id": "tutor_a1b2c3d4e5f6",
      "name": "张三",
      ...
    }
  }
}
```

### 错误响应
- `401 Unauthorized`: 未登录或token无效
- `403 Forbidden`: 权限不足
- `404 Not Found`: 导师不存在
- `422 Unprocessable Entity`: 数据验证失败
- `500 Internal Server Error`: 服务器内部错误

---

## 3. 删除导师信息

### 接口信息
- **接口地址**: `DELETE /api/v1/tutor/admin/delete/{tutor_id}`
- **接口描述**: 管理员删除指定的导师信息及其相关数据
- **权限要求**: 管理员

### 请求头
```
Authorization: Bearer {admin_token}
```

### 路径参数
- `tutor_id`: 导师ID

### 成功响应
```json
{
  "code": 200,
  "message": "导师信息删除成功",
  "data": {
    "success": true,
    "tutor_id": "tutor_a1b2c3d4e5f6",
    "message": "已删除导师 张三 及其相关数据"
  }
}
```

**删除范围**：
- 导师基本信息
- 导师的所有论文
- 导师的所有项目
- 用户对该导师的所有收藏记录

### 错误响应
- `401 Unauthorized`: 未登录或token无效
- `403 Forbidden`: 权限不足
- `404 Not Found`: 导师不存在
- `500 Internal Server Error`: 服务器内部错误

---

## 4. 批量删除导师

### 接口信息
- **接口地址**: `POST /api/v1/tutor/admin/batch-delete`
- **接口描述**: 管理员批量删除多个导师信息
- **权限要求**: 管理员

### 请求头
```
Authorization: Bearer {admin_token}
Content-Type: application/json
```

### 请求体
```json
{
  "tutor_ids": ["tutor_123", "tutor_456", "tutor_789"]
}
```

**限制**：
- 最少1个导师ID
- 最多100个导师ID
- 自动去重

### 成功响应
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

### 错误响应
- `401 Unauthorized`: 未登录或token无效
- `403 Forbidden`: 权限不足
- `422 Unprocessable Entity`: 导师ID列表格式错误
- `500 Internal Server Error`: 服务器内部错误

---

## 🗄️ 数据库集合结构

### tutors 集合
```javascript
{
  "_id": ObjectId("..."),
  "id": "tutor_a1b2c3d4e5f6",              // 导师唯一标识
  "name": "张三",                           // 导师姓名
  "school_name": "清华大学",                // 所在院校
  "department_name": "计算机科学与技术系",   // 所在院系
  "title": "教授、博士生导师",              // 职称
  "research_direction": "人工智能...",      // 研究方向
  "email": "zhangsan@example.edu.cn",      // 邮箱
  "phone": "010-12345678",                 // 电话
  "avatar_url": "https://...",             // 头像URL
  "personal_page_url": "https://...",      // 个人主页
  "bio": "张三教授...",                     // 个人简介
  "tags": ["AI", "深度学习"],              // 标签
  "created_at": ISODate("..."),            // 创建时间
  "updated_at": ISODate("..."),            // 更新时间
  "created_by": "admin_user_001",          // 创建者ID
  "updated_by": "admin_user_001"           // 更新者ID
}
```

### papers 集合
```javascript
{
  "_id": ObjectId("..."),
  "id": "paper_x1y2z3",                    // 论文唯一标识
  "tutor_id": "tutor_a1b2c3d4e5f6",        // 导师ID
  "title": "基于深度学习...",              // 论文标题
  "authors": ["张三", "李四"],             // 作者列表
  "journal": "计算机学报",                 // 期刊
  "year": 2024,                            // 年份
  "doi": "10.1234/...",                    // DOI
  "abstract": "本文研究了...",             // 摘要
  "created_at": ISODate("...")             // 创建时间
}
```

### projects 集合
```javascript
{
  "_id": ObjectId("..."),
  "id": "project_p1q2r3",                  // 项目唯一标识
  "tutor_id": "tutor_a1b2c3d4e5f6",        // 导师ID
  "title": "国家自然科学基金项目",         // 项目名称
  "funding": "国家自然科学基金委员会",     // 资助来源
  "start_date": "2024-01-01",              // 开始日期
  "end_date": "2026-12-31",                // 结束日期
  "description": "研究人工智能...",        // 项目描述
  "created_at": ISODate("...")             // 创建时间
}
```

---

## 📝 使用示例

### Python (requests)

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# 1. 管理员登录
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={"code": "admin_wx_code"}
)
admin_token = login_response.json()["data"]["token"]

# 设置请求头
headers = {
    "Authorization": f"Bearer {admin_token}",
    "Content-Type": "application/json"
}

# 2. 创建导师
tutor_data = {
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
}

create_response = requests.post(
    f"{BASE_URL}/tutor/admin/create",
    headers=headers,
    json=tutor_data
)
tutor_id = create_response.json()["data"]["id"]
print(f"创建导师成功: {tutor_id}")

# 3. 更新导师
update_data = {
    "title": "教授、博士生导师",
    "email": "zhangsan_new@example.edu.cn"
}

update_response = requests.put(
    f"{BASE_URL}/tutor/admin/update/{tutor_id}",
    headers=headers,
    json=update_data
)
print("更新导师成功")

# 4. 删除导师
delete_response = requests.delete(
    f"{BASE_URL}/tutor/admin/delete/{tutor_id}",
    headers=headers
)
print("删除导师成功")

# 5. 批量删除
batch_delete_response = requests.post(
    f"{BASE_URL}/tutor/admin/batch-delete",
    headers=headers,
    json={"tutor_ids": ["tutor_1", "tutor_2", "tutor_3"]}
)
result = batch_delete_response.json()["data"]
print(f"批量删除: 成功{result['success_count']}个")
```

### JavaScript (fetch)

```javascript
const BASE_URL = "http://localhost:8000/api/v1";

// 管理员登录
const loginResponse = await fetch(`${BASE_URL}/auth/login`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ code: "admin_wx_code" })
});
const { data: { token: adminToken } } = await loginResponse.json();

// 设置请求头
const headers = {
  "Authorization": `Bearer ${adminToken}`,
  "Content-Type": "application/json"
};

// 创建导师
const createResponse = await fetch(`${BASE_URL}/tutor/admin/create`, {
  method: "POST",
  headers,
  body: JSON.stringify({
    name: "张三",
    school: "清华大学",
    department: "计算机系",
    title: "教授"
  })
});
const { data: { id: tutorId } } = await createResponse.json();
console.log(`创建导师成功: ${tutorId}`);

// 更新导师
await fetch(`${BASE_URL}/tutor/admin/update/${tutorId}`, {
  method: "PUT",
  headers,
  body: JSON.stringify({
    title: "教授、博士生导师"
  })
});

// 删除导师
await fetch(`${BASE_URL}/tutor/admin/delete/${tutorId}`, {
  method: "DELETE",
  headers
});
```

---

## ⚠️ 注意事项

### 1. 权限管理
- 所有接口都需要管理员权限
- 非管理员用户会收到403错误
- 建议在生产环境使用数据库的is_admin字段管理权限

### 2. 数据验证
- 所有必填字段必须提供
- 邮箱必须是有效格式
- URL必须是HTTP/HTTPS地址
- 电话号码只能包含数字、空格、短横线、括号

### 3. 数据关联
- 删除导师会级联删除其论文、项目和收藏记录
- 更新论文/项目列表会完全替换原有数据
- 建议在删除前做好数据备份

### 4. 性能考虑
- 批量删除最多支持100个导师
- 论文和项目列表建议不超过100条
- 标签列表最多20个

### 5. 日志记录
- 所有操作都会记录详细日志
- 包含操作者ID、操作时间、操作内容
- 便于审计和问题排查

---

## 🧪 测试建议

### 1. 功能测试
- 创建导师（含论文、项目）
- 更新导师基本信息
- 更新论文列表
- 删除单个导师
- 批量删除导师

### 2. 权限测试
- 非管理员访问（应返回403）
- 无token访问（应返回401）
- 无效token访问（应返回401）

### 3. 数据验证测试
- 缺少必填字段（应返回422）
- 无效的邮箱格式（应返回422）
- 无效的URL格式（应返回422）
- 超长字段（应返回422）

### 4. 边界测试
- 批量删除100个导师（上限）
- 批量删除超过100个（应返回422）
- 删除不存在的导师（应返回404）

---

## 📊 错误码说明

| 错误码 | HTTP状态码 | 说明 |
|--------|-----------|------|
| FORBIDDEN | 403 | 权限不足，非管理员用户 |
| TUTOR_NOT_FOUND | 404 | 导师不存在 |
| CREATE_FAILED | 500 | 创建导师失败 |
| UPDATE_FAILED | 500 | 更新导师失败 |
| DELETE_FAILED | 500 | 删除导师失败 |
| authentication_error | 401 | 认证失败，token无效 |

---

## 🚀 快速开始

### 1. 启动服务
```bash
cd backend
python main.py
```

### 2. 添加管理员
```python
# 方法1：修改代码
# 编辑 app/utils/admin.py
ADMIN_USER_IDS = ["your_user_id"]

# 方法2：数据库设置
# 在MongoDB中执行
db.users.updateOne(
  { id: "your_user_id" },
  { $set: { is_admin: true } }
)
```

### 3. 运行测试
```bash
python test_tutor_crud_api.py
```

### 4. 查看API文档
访问: http://localhost:8000/docs

---

**文档版本**: v1.0.0  
**最后更新**: 2024-03-01  
**维护者**: Backend Team
