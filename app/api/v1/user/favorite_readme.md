# 收藏功能接口文档

## 概述

本模块提供用户收藏导师的完整功能，包括收藏/取消收藏、查询收藏列表、查询收藏状态等。

## 接口列表

### 1. 收藏/取消收藏导师（Toggle）

**接口地址**: `POST /api/v1/user/favorite/toggle`

**接口描述**: 切换导师的收藏状态，如果已收藏则取消收藏，如果未收藏则添加收藏

**请求头**:
```
Authorization: Bearer {token}
Content-Type: application/json
```

**请求体**:
```json
{
  "tutor_id": "tutor_123456789"
}
```

**字段说明**:
- `tutor_id` (必填): 导师ID，不能为空

**成功响应**:

收藏成功：
```json
{
  "code": 200,
  "message": "收藏成功",
  "data": {
    "action": "collected",
    "tutor_id": "tutor_123456789",
    "message": "已收藏该导师"
  }
}
```

取消收藏成功：
```json
{
  "code": 200,
  "message": "取消收藏成功",
  "data": {
    "action": "uncollected",
    "tutor_id": "tutor_123456789",
    "message": "已取消收藏该导师"
  }
}
```

**错误响应**:
- `401 Unauthorized`: 未登录或token无效
- `404 Not Found`: 导师不存在
- `422 Unprocessable Entity`: 导师ID格式错误
- `500 Internal Server Error`: 服务器内部错误

---

### 2. 获取收藏的导师列表

**接口地址**: `GET /api/v1/user/favorites`

**接口描述**: 获取当前用户收藏的所有导师，支持分页

**请求头**:
```
Authorization: Bearer {token}
```

**查询参数**:
| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| page | int | 否 | 1 | 页码，从1开始 |
| page_size | int | 否 | 10 | 每页数量，范围1-100 |

**响应示例**:
```json
{
  "code": 200,
  "message": "获取收藏列表成功",
  "data": {
    "list": [
      {
        "id": "tutor_123456789",
        "name": "张三",
        "title": "教授",
        "school": "清华大学",
        "department": "计算机科学与技术系",
        "avatar": "https://example.com/avatar.jpg",
        "research_direction": "人工智能、机器学习",
        "tags": ["AI", "深度学习", "计算机视觉"],
        "collected_at": "2024-03-01T12:00:00"
      }
    ],
    "total": 15,
    "page": 1,
    "page_size": 10
  }
}
```

**字段说明**:
- `list`: 收藏的导师列表
  - `id`: 导师ID
  - `name`: 导师姓名
  - `title`: 职称
  - `school`: 所在学校
  - `department`: 所在院系
  - `avatar`: 头像URL
  - `research_direction`: 研究方向
  - `tags`: 标签列表
  - `collected_at`: 收藏时间
- `total`: 总收藏数量
- `page`: 当前页码
- `page_size`: 每页数量

**错误响应**:
- `401 Unauthorized`: 未登录或token无效
- `500 Internal Server Error`: 服务器内部错误

---

### 3. 查询导师收藏状态

**接口地址**: `GET /api/v1/user/favorite/status/{tutor_id}`

**接口描述**: 查询指定导师是否已被当前用户收藏

**请求头**:
```
Authorization: Bearer {token}
```

**路径参数**:
- `tutor_id`: 导师ID

**响应示例**:
```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "is_collected": true,
    "tutor_id": "tutor_123456789"
  }
}
```

**字段说明**:
- `is_collected`: 是否已收藏（true/false）
- `tutor_id`: 导师ID

**错误响应**:
- `401 Unauthorized`: 未登录或token无效
- `500 Internal Server Error`: 服务器内部错误

---

### 4. 批量查询导师收藏状态

**接口地址**: `POST /api/v1/user/favorite/batch-status`

**接口描述**: 批量查询多个导师是否已被当前用户收藏

**请求头**:
```
Authorization: Bearer {token}
Content-Type: application/json
```

**请求体**:
```json
{
  "tutor_ids": ["tutor_123", "tutor_456", "tutor_789"]
}
```

**字段说明**:
- `tutor_ids` (必填): 导师ID列表，最少1个，最多100个，自动去重

**响应示例**:
```json
{
  "code": 200,
  "message": "批量查询成功",
  "data": {
    "favorites": {
      "tutor_123": true,
      "tutor_456": false,
      "tutor_789": true
    }
  }
}
```

**字段说明**:
- `favorites`: 收藏状态字典
  - key: 导师ID
  - value: 是否已收藏（true/false）

**错误响应**:
- `401 Unauthorized`: 未登录或token无效
- `422 Unprocessable Entity`: 导师ID列表格式错误
- `500 Internal Server Error`: 服务器内部错误

---

### 5. 取消收藏导师（DELETE方法）

**接口地址**: `DELETE /api/v1/user/favorite/{tutor_id}`

**接口描述**: 使用DELETE方法取消收藏指定的导师

**请求头**:
```
Authorization: Bearer {token}
```

**路径参数**:
- `tutor_id`: 导师ID

**响应示例**:
```json
{
  "code": 200,
  "message": "取消收藏成功",
  "data": {
    "tutor_id": "tutor_123456789",
    "action": "deleted"
  }
}
```

**错误响应**:
- `401 Unauthorized`: 未登录或token无效
- `404 Not Found`: 该导师未收藏
- `500 Internal Server Error`: 服务器内部错误

---

## 数据验证规则

### 导师ID (tutor_id)
- 不能为空
- 自动去除首尾空格
- 必须是有效的导师ID（数据库中存在）

### 导师ID列表 (tutor_ids)
- 至少包含1个导师ID
- 最多包含100个导师ID
- 自动去重

---

## 使用示例

### Python (requests)

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# 登录获取token
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={"code": "wx_login_code"}
)
token = login_response.json()["data"]["token"]

# 设置请求头
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# 1. 收藏导师
collect_response = requests.post(
    f"{BASE_URL}/user/favorite/toggle",
    headers=headers,
    json={"tutor_id": "tutor_123"}
)
print(collect_response.json())

# 2. 查询收藏列表
favorites_response = requests.get(
    f"{BASE_URL}/user/favorites",
    headers=headers,
    params={"page": 1, "page_size": 10}
)
print(favorites_response.json())

# 3. 查询收藏状态
status_response = requests.get(
    f"{BASE_URL}/user/favorite/status/tutor_123",
    headers=headers
)
print(status_response.json())

# 4. 批量查询收藏状态
batch_response = requests.post(
    f"{BASE_URL}/user/favorite/batch-status",
    headers=headers,
    json={"tutor_ids": ["tutor_123", "tutor_456", "tutor_789"]}
)
print(batch_response.json())

# 5. 取消收藏（Toggle方式）
uncollect_response = requests.post(
    f"{BASE_URL}/user/favorite/toggle",
    headers=headers,
    json={"tutor_id": "tutor_123"}
)
print(uncollect_response.json())

# 6. 取消收藏（DELETE方式）
delete_response = requests.delete(
    f"{BASE_URL}/user/favorite/tutor_123",
    headers=headers
)
print(delete_response.json())
```

### JavaScript (fetch)

```javascript
const BASE_URL = "http://localhost:8000/api/v1";

// 登录获取token
const loginResponse = await fetch(`${BASE_URL}/auth/login`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ code: "wx_login_code" })
});
const { data: { token } } = await loginResponse.json();

// 设置请求头
const headers = {
  "Authorization": `Bearer ${token}`,
  "Content-Type": "application/json"
};

// 1. 收藏导师
const collectResponse = await fetch(`${BASE_URL}/user/favorite/toggle`, {
  method: "POST",
  headers,
  body: JSON.stringify({ tutor_id: "tutor_123" })
});
console.log(await collectResponse.json());

// 2. 查询收藏列表
const favoritesResponse = await fetch(
  `${BASE_URL}/user/favorites?page=1&page_size=10`,
  { headers }
);
console.log(await favoritesResponse.json());

// 3. 查询收藏状态
const statusResponse = await fetch(
  `${BASE_URL}/user/favorite/status/tutor_123`,
  { headers }
);
console.log(await statusResponse.json());

// 4. 批量查询收藏状态
const batchResponse = await fetch(`${BASE_URL}/user/favorite/batch-status`, {
  method: "POST",
  headers,
  body: JSON.stringify({
    tutor_ids: ["tutor_123", "tutor_456", "tutor_789"]
  })
});
console.log(await batchResponse.json());

// 5. 取消收藏（DELETE方式）
const deleteResponse = await fetch(`${BASE_URL}/user/favorite/tutor_123`, {
  method: "DELETE",
  headers
});
console.log(await deleteResponse.json());
```

### 微信小程序

```javascript
// 获取token（假设已存储在本地）
const token = wx.getStorageSync('token');

// 1. 收藏/取消收藏导师
wx.request({
  url: 'http://localhost:8000/api/v1/user/favorite/toggle',
  method: 'POST',
  header: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  data: {
    tutor_id: 'tutor_123'
  },
  success: (res) => {
    console.log('收藏操作:', res.data);
    if (res.data.data.action === 'collected') {
      wx.showToast({ title: '收藏成功', icon: 'success' });
    } else {
      wx.showToast({ title: '取消收藏成功', icon: 'success' });
    }
  }
});

// 2. 查询收藏列表
wx.request({
  url: 'http://localhost:8000/api/v1/user/favorites',
  method: 'GET',
  header: {
    'Authorization': `Bearer ${token}`
  },
  data: {
    page: 1,
    page_size: 10
  },
  success: (res) => {
    console.log('收藏列表:', res.data);
    const favorites = res.data.data.list;
    // 更新页面数据
    this.setData({ favorites });
  }
});

// 3. 查询收藏状态
wx.request({
  url: `http://localhost:8000/api/v1/user/favorite/status/tutor_123`,
  method: 'GET',
  header: {
    'Authorization': `Bearer ${token}`
  },
  success: (res) => {
    console.log('收藏状态:', res.data);
    const isCollected = res.data.data.is_collected;
    // 更新收藏按钮状态
    this.setData({ isCollected });
  }
});

// 4. 批量查询收藏状态（用于列表页）
wx.request({
  url: 'http://localhost:8000/api/v1/user/favorite/batch-status',
  method: 'POST',
  header: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  data: {
    tutor_ids: ['tutor_123', 'tutor_456', 'tutor_789']
  },
  success: (res) => {
    console.log('批量收藏状态:', res.data);
    const favorites = res.data.data.favorites;
    // 更新列表中每个导师的收藏状态
    const tutorList = this.data.tutorList.map(tutor => ({
      ...tutor,
      isCollected: favorites[tutor.id] || false
    }));
    this.setData({ tutorList });
  }
});
```

---

## 错误码说明

| 错误码 | HTTP状态码 | 说明 |
|--------|-----------|------|
| TUTOR_NOT_FOUND | 404 | 导师不存在 |
| NOT_COLLECTED | 404 | 该导师未收藏（DELETE方法） |
| COLLECT_FAILED | 500 | 收藏失败 |
| UNCOLLECT_FAILED | 500 | 取消收藏失败 |
| DELETE_FAILED | 500 | 删除收藏失败 |
| authentication_error | 401 | 认证失败，token无效 |

---

## 数据库集合结构

### favorites 集合

```javascript
{
  "_id": ObjectId("..."),
  "id": "fav_123e4567-e89b-12d3-a456-426614174000",  // 收藏记录唯一标识
  "user_id": "user_123456789",                       // 用户ID
  "target_type": "tutor",                            // 目标类型（tutor/project）
  "target_id": "tutor_123456789",                    // 目标ID（导师ID）
  "created_at": ISODate("2024-03-01T12:00:00Z")     // 收藏时间
}
```

**索引建议**:
```javascript
// 复合索引：用于快速查询用户的收藏
db.favorites.createIndex({ "user_id": 1, "target_type": 1, "created_at": -1 })

// 复合唯一索引：防止重复收藏
db.favorites.createIndex(
  { "user_id": 1, "target_type": 1, "target_id": 1 },
  { unique: true }
)

// 单字段索引：用于查询特定导师的收藏情况
db.favorites.createIndex({ "target_id": 1 })
```

---

## 业务逻辑说明

### 收藏/取消收藏流程

1. **验证用户身份**: 通过JWT token验证用户登录状态
2. **验证导师存在**: 查询tutors集合确认导师存在
3. **检查收藏状态**: 查询favorites集合检查是否已收藏
4. **执行操作**:
   - 如果已收藏：删除收藏记录，返回"uncollected"
   - 如果未收藏：创建收藏记录，返回"collected"
5. **记录日志**: 记录操作日志便于追踪

### 查询收藏列表流程

1. **验证用户身份**: 通过JWT token验证用户登录状态
2. **查询收藏记录**: 从favorites集合查询用户的收藏（按时间倒序）
3. **获取导师信息**: 根据收藏记录中的target_id查询导师详细信息
4. **构建响应**: 组合收藏记录和导师信息，返回完整列表
5. **支持分页**: 通过page和page_size参数实现分页

### 批量查询优化

批量查询接口使用`$in`操作符一次性查询多个导师的收藏状态，避免多次数据库查询，提高性能。

---

## 性能优化建议

1. **数据库索引**: 为favorites集合创建合适的索引
2. **批量查询**: 列表页使用批量查询接口而不是单个查询
3. **缓存策略**: 可以考虑使用Redis缓存用户的收藏列表
4. **分页加载**: 收藏列表使用分页，避免一次加载过多数据

---

## 注意事项

1. **认证要求**: 所有接口都需要在请求头中携带有效的JWT token
2. **幂等性**: Toggle接口是幂等的，多次调用会在收藏和取消收藏之间切换
3. **导师验证**: 收藏时会验证导师是否存在，不存在会返回404错误
4. **重复收藏**: 数据库层面通过唯一索引防止重复收藏
5. **软删除**: 当前实现是物理删除，如需要可以改为软删除（添加deleted_at字段）
6. **收藏统计**: 可以在导师表中添加collected_count字段记录收藏数量

---

## 前端集成建议

### 1. 导师详情页

```javascript
// 页面加载时查询收藏状态
onLoad(options) {
  const tutorId = options.tutorId;
  this.loadTutorDetail(tutorId);
  this.loadFavoriteStatus(tutorId);
}

// 收藏按钮点击
onFavoriteClick() {
  // 调用toggle接口
  // 根据返回的action更新按钮状态
}
```

### 2. 导师列表页

```javascript
// 页面加载时批量查询收藏状态
onLoad() {
  this.loadTutorList().then(tutors => {
    const tutorIds = tutors.map(t => t.id);
    this.loadBatchFavoriteStatus(tutorIds);
  });
}
```

### 3. 收藏列表页

```javascript
// 支持下拉刷新和上拉加载
onPullDownRefresh() {
  this.loadFavorites(1);
}

onReachBottom() {
  this.loadFavorites(this.data.page + 1);
}
```

---

## 测试建议

1. **正常流程测试**:
   - 收藏导师
   - 查询收藏列表
   - 查询收藏状态
   - 取消收藏

2. **异常情况测试**:
   - 不带token访问
   - 使用无效token
   - 收藏不存在的导师
   - 空导师ID
   - 重复收藏

3. **性能测试**:
   - 批量查询大量导师
   - 分页加载测试
   - 并发收藏测试

4. **边界值测试**:
   - 批量查询100个导师（上限）
   - 批量查询超过100个导师（应该失败）
   - 分页参数边界值

---

## 未来扩展

1. **收藏分组**: 支持用户创建收藏夹，对收藏进行分类
2. **收藏备注**: 允许用户为收藏添加备注
3. **收藏导出**: 支持导出收藏列表为PDF或Excel
4. **收藏分享**: 支持分享收藏列表给其他用户
5. **收藏提醒**: 当收藏的导师有新动态时推送通知
6. **收藏统计**: 统计用户的收藏偏好，推荐相似导师

---

**文档版本**: v1.0.0  
**最后更新**: 2024-03-01  
**维护者**: Backend Team
