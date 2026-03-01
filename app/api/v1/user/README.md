# 用户信息管理接口文档

## 概述

本模块提供用户信息的查询和修改功能，包括用户昵称、头像、院校、专业、年级等个人信息的管理。

## 接口列表

### 1. 获取用户信息

**接口地址**: `GET /api/v1/user/profile`

**接口描述**: 获取当前登录用户的个人信息

**请求头**:
```
Authorization: Bearer {token}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "nickname": "张三",
    "avatar": "https://example.com/avatar.jpg",
    "school": "清华大学",
    "major": "计算机科学与技术",
    "grade": "2024级",
    "vip_status": true,
    "vip_expire_date": "2024-12-31T23:59:59",
    "created_at": "2024-01-01T00:00:00"
  }
}
```

**错误响应**:
- `401 Unauthorized`: 未登录或token无效
- `404 Not Found`: 用户信息不存在
- `500 Internal Server Error`: 服务器内部错误

---

### 2. 更新用户信息 (PUT)

**接口地址**: `PUT /api/v1/user/profile`

**接口描述**: 更新当前登录用户的个人信息，支持部分字段更新

**请求头**:
```
Authorization: Bearer {token}
Content-Type: application/json
```

**请求体**:
```json
{
  "nickname": "李四",
  "avatar": "https://example.com/new-avatar.jpg",
  "school": "北京大学",
  "major": "软件工程",
  "grade": "2023级"
}
```

**字段说明**:
- `nickname` (可选): 用户昵称，1-50个字符
- `avatar` (可选): 用户头像URL，必须是有效的HTTP/HTTPS地址
- `school` (可选): 所在院校，最多100个字符
- `major` (可选): 专业，最多100个字符
- `grade` (可选): 年级，最多20个字符

**注意**: 所有字段都是可选的，只需要传入需要更新的字段即可

**响应示例**:
```json
{
  "code": 200,
  "message": "用户信息更新成功",
  "data": {
    "success": true,
    "updated_fields": ["nickname", "school"],
    "user": {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "nickname": "李四",
      "avatar": "https://example.com/new-avatar.jpg",
      "school": "北京大学",
      "major": "软件工程",
      "grade": "2023级",
      "vip_status": true,
      "vip_expire_date": "2024-12-31T23:59:59",
      "created_at": "2024-01-01T00:00:00"
    }
  }
}
```

**错误响应**:
- `400 Bad Request`: 请求参数验证失败
- `401 Unauthorized`: 未登录或token无效
- `500 Internal Server Error`: 更新失败或服务器内部错误

---

### 3. 部分更新用户信息 (PATCH)

**接口地址**: `PATCH /api/v1/user/profile`

**接口描述**: 部分更新当前登录用户的个人信息（功能与PUT相同，提供RESTful API完整支持）

**请求和响应**: 与PUT方法完全相同

---

## 数据验证规则

### 昵称 (nickname)
- 长度: 1-50个字符
- 不能为空字符串
- 自动去除首尾空格

### 头像 (avatar)
- 必须是有效的HTTP或HTTPS URL
- 最大长度: 500个字符

### 院校 (school)
- 最大长度: 100个字符
- 自动去除首尾空格

### 专业 (major)
- 最大长度: 100个字符
- 自动去除首尾空格

### 年级 (grade)
- 最大长度: 20个字符

---

## 使用示例

### Python (requests)

```python
import requests

# 基础URL
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

# 获取用户信息
profile_response = requests.get(
    f"{BASE_URL}/user/profile",
    headers=headers
)
print(profile_response.json())

# 更新用户信息
update_response = requests.put(
    f"{BASE_URL}/user/profile",
    headers=headers,
    json={
        "nickname": "新昵称",
        "school": "新学校"
    }
)
print(update_response.json())
```

### JavaScript (fetch)

```javascript
const BASE_URL = "http://localhost:8000/api/v1";

// 登录获取token
const loginResponse = await fetch(`${BASE_URL}/auth/login`, {
  method: "POST",
  headers: {
    "Content-Type": "application/json"
  },
  body: JSON.stringify({ code: "wx_login_code" })
});
const { data: { token } } = await loginResponse.json();

// 设置请求头
const headers = {
  "Authorization": `Bearer ${token}`,
  "Content-Type": "application/json"
};

// 获取用户信息
const profileResponse = await fetch(`${BASE_URL}/user/profile`, {
  headers
});
const profile = await profileResponse.json();
console.log(profile);

// 更新用户信息
const updateResponse = await fetch(`${BASE_URL}/user/profile`, {
  method: "PUT",
  headers,
  body: JSON.stringify({
    nickname: "新昵称",
    school: "新学校"
  })
});
const updateResult = await updateResponse.json();
console.log(updateResult);
```

### 微信小程序

```javascript
// 登录获取token
wx.request({
  url: 'http://localhost:8000/api/v1/auth/login',
  method: 'POST',
  data: {
    code: wx.getStorageSync('code')
  },
  success: (res) => {
    const token = res.data.data.token;
    wx.setStorageSync('token', token);
    
    // 获取用户信息
    wx.request({
      url: 'http://localhost:8000/api/v1/user/profile',
      method: 'GET',
      header: {
        'Authorization': `Bearer ${token}`
      },
      success: (res) => {
        console.log('用户信息:', res.data);
      }
    });
    
    // 更新用户信息
    wx.request({
      url: 'http://localhost:8000/api/v1/user/profile',
      method: 'PUT',
      header: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      data: {
        nickname: '新昵称',
        school: '新学校'
      },
      success: (res) => {
        console.log('更新结果:', res.data);
      }
    });
  }
});
```

---

## 错误码说明

| 错误码 | HTTP状态码 | 说明 |
|--------|-----------|------|
| USER_NOT_FOUND | 404 | 用户信息不存在 |
| UPDATE_FAILED | 500 | 用户信息更新失败 |
| authentication_error | 401 | 认证失败，token无效 |

---

## 注意事项

1. **认证要求**: 所有接口都需要在请求头中携带有效的JWT token
2. **部分更新**: 更新接口支持部分字段更新，只需传入需要修改的字段
3. **数据验证**: 所有输入数据都会进行严格的验证，不符合规则的数据会返回400错误
4. **自动去空格**: 文本字段会自动去除首尾空格
5. **更新时间**: 每次更新操作都会自动更新`updated_at`字段
6. **日志记录**: 所有操作都会记录详细的日志，便于问题排查

---

## 数据库集合结构

### users 集合

```javascript
{
  "_id": ObjectId("..."),
  "id": "123e4567-e89b-12d3-a456-426614174000",  // 用户唯一标识
  "openid": "wx_xxxxxxxxxxxxxxxx",               // 微信openid
  "unionid": "union_xxxxxxxxxxxxxxxx",           // 微信unionid（可选）
  "nickname": "张三",                             // 昵称
  "avatar": "https://example.com/avatar.jpg",    // 头像URL
  "school": "清华大学",                           // 院校
  "major": "计算机科学与技术",                    // 专业
  "grade": "2024级",                              // 年级
  "vip_status": false,                           // VIP状态
  "vip_expire_date": ISODate("2024-12-31T23:59:59Z"), // VIP到期时间
  "created_at": ISODate("2024-01-01T00:00:00Z"), // 创建时间
  "updated_at": ISODate("2024-01-01T00:00:00Z")  // 更新时间
}
```

---

## 测试建议

1. **正常流程测试**:
   - 登录获取token
   - 获取用户信息
   - 更新单个字段
   - 更新多个字段
   - 再次获取验证更新结果

2. **异常情况测试**:
   - 不带token访问
   - 使用无效token
   - 传入过长的字符串
   - 传入无效的URL格式
   - 传入空字符串

3. **边界值测试**:
   - 昵称长度边界（1字符、50字符、51字符）
   - 特殊字符处理
   - 空值和null值处理
