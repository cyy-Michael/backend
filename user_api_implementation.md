# 用户信息查询/修改接口实现文档

## 📋 实现概述

本次开发实现了用户信息的查询和修改接口，支持获取和更新用户的昵称、头像、院校、专业、年级等个人信息。

## 🎯 实现的功能

### 1. 用户信息查询接口
- **接口路径**: `GET /api/v1/user/profile`
- **功能**: 获取当前登录用户的完整个人信息
- **认证**: 需要JWT token
- **返回数据**: 用户ID、昵称、头像、院校、专业、年级、VIP状态等

### 2. 用户信息更新接口
- **接口路径**: `PUT /api/v1/user/profile` 和 `PATCH /api/v1/user/profile`
- **功能**: 更新当前登录用户的个人信息
- **认证**: 需要JWT token
- **支持字段**: nickname, avatar, school, major, grade
- **特点**: 支持部分更新，只需传入需要修改的字段

## 📁 新增/修改的文件

### 1. 数据模型层 (Schema)

#### `app/schemas/user_schema.py` (新建)
定义了用户信息相关的数据校验模型：
- `UserProfileResponse`: 用户信息响应模型
- `UserProfileUpdate`: 用户信息更新请求模型
- `UserProfileUpdateResponse`: 用户信息更新响应模型

包含完整的数据验证规则：
- 昵称长度验证（1-50字符）
- 头像URL格式验证（必须是HTTP/HTTPS）
- 文本字段自动去除首尾空格
- 字段长度限制

#### `app/schemas/__init__.py` (新建)
导出所有schema模型，方便其他模块导入使用。

### 2. API路由层

#### `app/api/v1/user/profile.py` (新建)
实现了用户信息管理的三个接口：
- `get_user_profile`: 获取用户信息
- `update_user_profile`: 更新用户信息（PUT方法）
- `patch_user_profile`: 部分更新用户信息（PATCH方法）

特点：
- 完整的错误处理和日志记录
- 详细的中文注释
- 支持部分字段更新
- 自动记录更新时间
- 返回更新的字段列表

#### `app/api/v1/__init__.py` (修改)
注册了新的用户信息路由：
```python
from app.api.v1.user.profile import router as user_profile_router
v1_router.include_router(user_profile_router, tags=["user"])
```

### 3. 认证模块优化

#### `app/api/v1/auth/login.py` (修改)
优化了数据库查询方式：
- 将同步的数据库查询改为异步查询
- 使用 `find_one` 和 `insert_one` 等异步方法
- 提高了性能和并发处理能力

### 4. 文档和测试

#### `app/api/v1/user/README.md` (新建)
详细的接口使用文档，包含：
- 接口说明和参数详解
- 请求/响应示例
- 数据验证规则
- 多种语言的使用示例（Python、JavaScript、微信小程序）
- 错误码说明
- 数据库集合结构
- 测试建议

#### `test_user_api.py` (新建)
完整的接口测试脚本，包含11个测试场景：
1. 登录获取token
2. 获取用户信息
3. 更新单个字段（昵称）
4. 更新多个字段
5. 使用PATCH方法更新
6. 验证更新结果
7. 测试无token访问（预期失败）
8. 测试无效token（预期失败）
9. 测试数据验证 - 昵称过长（预期失败）
10. 测试数据验证 - 无效URL（预期失败）
11. 测试空更新

## 🔧 技术实现细节

### 1. 数据验证
使用Pydantic进行严格的数据验证：
- 字段类型验证
- 长度限制验证
- URL格式验证
- 自定义验证器（validator）

### 2. 异步数据库操作
使用MongoDB的异步操作：
```python
from app.db.mongo import find_one, update_one

# 查询用户
user = await find_one("users", {"id": user_id})

# 更新用户
success = await update_one("users", {"id": user_id}, update_data)
```

### 3. JWT认证
通过依赖注入获取当前用户：
```python
async def get_user_profile(
    current_user: User = Depends(get_current_user)
):
    # current_user 已经通过JWT验证
    pass
```

### 4. 错误处理
完整的错误处理机制：
- HTTP异常处理
- 业务逻辑异常处理
- 数据库操作异常处理
- 详细的错误日志记录

### 5. 日志记录
每个操作都有详细的日志：
```python
api_logger.info(
    f"用户信息更新成功: {current_user.id}\n"
    f"Updated fields: {', '.join(updated_fields)}\n"
    f"Request ID: {request.state.request_id}"
)
```

## 📊 数据库集合结构

### users 集合
```javascript
{
  "_id": ObjectId("..."),
  "id": "uuid",                    // 用户唯一标识
  "openid": "wx_xxx",              // 微信openid
  "unionid": "union_xxx",          // 微信unionid（可选）
  "nickname": "张三",               // 昵称
  "avatar": "https://...",         // 头像URL
  "school": "清华大学",             // 院校
  "major": "计算机科学与技术",      // 专业
  "grade": "2024级",                // 年级
  "vip_status": false,             // VIP状态
  "vip_expire_date": ISODate(),    // VIP到期时间
  "created_at": ISODate(),         // 创建时间
  "updated_at": ISODate()          // 更新时间
}
```

## 🔐 安全性考虑

1. **JWT认证**: 所有接口都需要有效的JWT token
2. **用户隔离**: 用户只能查询和修改自己的信息
3. **数据验证**: 严格的输入数据验证，防止注入攻击
4. **错误信息**: 不暴露敏感的系统信息
5. **日志记录**: 记录所有操作，便于审计

## 🚀 如何使用

### 1. 启动服务
```bash
cd backend
python main.py
```

### 2. 运行测试
```bash
python test_user_api.py
```

### 3. 查看API文档
访问: http://localhost:8000/docs

### 4. 接口调用示例

#### 获取用户信息
```bash
curl -X GET "http://localhost:8000/api/v1/user/profile" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 更新用户信息
```bash
curl -X PUT "http://localhost:8000/api/v1/user/profile" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nickname": "新昵称",
    "school": "清华大学",
    "major": "计算机科学与技术"
  }'
```

## 📝 接口响应格式

### 成功响应
```json
{
  "code": 200,
  "message": "success",
  "data": {
    // 具体数据
  }
}
```

### 错误响应
```json
{
  "code": 400,
  "message": "错误信息",
  "error": {
    "type": "错误类型",
    "details": {}
  }
}
```

## ✅ 测试清单

- [x] 用户信息查询功能
- [x] 用户信息更新功能（PUT）
- [x] 用户信息部分更新功能（PATCH）
- [x] JWT认证验证
- [x] 数据验证（昵称长度、URL格式等）
- [x] 错误处理（401、404、422、500等）
- [x] 日志记录
- [x] 异步数据库操作
- [x] 接口文档编写
- [x] 测试脚本编写

## 🔍 代码质量

- ✅ 所有代码都有详细的中文注释
- ✅ 遵循PEP 8代码规范
- ✅ 使用类型提示（Type Hints）
- ✅ 完整的错误处理
- ✅ 详细的日志记录
- ✅ 无Linter错误

## 📌 注意事项

1. **MongoDB连接**: 确保MongoDB连接字符串正确配置
   ```python
   MONGO_URI = "mongodb+srv://0227_wx201383_db_user:hdkkdbdikwksbffkfjdwl645s87jwksadasfsafasf@cluster0.roe7na.mongodb.net/"
   ```

2. **数据库名称**: 默认使用 `teacher_query` 数据库

3. **JWT配置**: 确保在配置文件中正确设置JWT密钥和过期时间

4. **CORS配置**: 如果前端需要跨域访问，确保CORS中间件配置正确

## 🎉 总结

本次实现完成了用户信息管理的核心功能，包括：
- ✅ 完整的用户信息查询接口
- ✅ 灵活的用户信息更新接口（支持部分更新）
- ✅ 严格的数据验证和错误处理
- ✅ 完善的文档和测试
- ✅ 优化的异步数据库操作
- ✅ 详细的中文注释

所有代码已经过测试，可以直接投入使用。如有问题，请参考 `app/api/v1/user/README.md` 文档或运行 `test_user_api.py` 进行测试。
