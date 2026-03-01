# 收藏功能接口实现文档

## 📋 实现概述

本次开发实现了用户收藏导师的完整功能，包括收藏/取消收藏、查询收藏列表、查询收藏状态等核心功能。

## 🎯 实现的功能

### 1. 收藏/取消收藏导师接口
- **接口路径**: `POST /api/v1/user/favorite/toggle`
- **功能**: 切换导师的收藏状态（已收藏→取消收藏，未收藏→收藏）
- **认证**: 需要JWT token
- **特点**: 幂等操作，自动判断当前状态并执行相反操作

### 2. 查询收藏列表接口
- **接口路径**: `GET /api/v1/user/favorites`
- **功能**: 获取当前用户收藏的所有导师
- **认证**: 需要JWT token
- **特点**: 支持分页，按收藏时间倒序排列

### 3. 查询收藏状态接口
- **接口路径**: `GET /api/v1/user/favorite/status/{tutor_id}`
- **功能**: 查询指定导师是否已被收藏
- **认证**: 需要JWT token
- **用途**: 导师详情页显示收藏状态

### 4. 批量查询收藏状态接口
- **接口路径**: `POST /api/v1/user/favorite/batch-status`
- **功能**: 批量查询多个导师的收藏状态
- **认证**: 需要JWT token
- **特点**: 支持最多100个导师ID，自动去重
- **用途**: 导师列表页批量查询收藏状态

### 5. 取消收藏接口（DELETE方法）
- **接口路径**: `DELETE /api/v1/user/favorite/{tutor_id}`
- **功能**: 使用RESTful DELETE方法取消收藏
- **认证**: 需要JWT token
- **特点**: 提供标准的RESTful API支持

## 📁 新增/修改的文件

### 1. 数据模型层 (Schema)

#### `app/schemas/favorite_schema.py` (新建)
定义了收藏相关的数据校验模型：
- `FavoriteToggleRequest`: 收藏/取消收藏请求模型
- `FavoriteToggleResponse`: 收藏/取消收藏响应模型
- `FavoriteTutorBrief`: 收藏的导师简略信息模型
- `FavoriteListResponse`: 收藏列表响应模型
- `FavoriteStatusResponse`: 收藏状态响应模型
- `BatchFavoriteStatusRequest`: 批量查询请求模型
- `BatchFavoriteStatusResponse`: 批量查询响应模型

包含完整的数据验证规则：
- 导师ID非空验证
- 导师ID列表数量限制（1-100个）
- 自动去重和去除空格

#### `app/schemas/__init__.py` (修改)
添加了收藏相关schema的导出。

### 2. API路由层

#### `app/api/v1/user/favorite.py` (新建)
实现了收藏管理的5个接口：
- `toggle_favorite`: 收藏/取消收藏导师
- `get_favorite_list`: 获取收藏列表
- `get_favorite_status`: 查询收藏状态
- `get_batch_favorite_status`: 批量查询收藏状态
- `delete_favorite`: 取消收藏（DELETE方法）

特点：
- 完整的错误处理和日志记录
- 详细的中文注释
- 支持分页查询
- 批量查询优化
- 导师存在性验证
- 自动记录收藏时间

#### `app/api/v1/__init__.py` (修改)
注册了新的收藏路由：
```python
from app.api.v1.user.favorite import router as user_favorite_router
v1_router.include_router(user_favorite_router, tags=["user", "favorite"])
```

### 3. 文档和测试

#### `app/api/v1/user/FAVORITE_README.md` (新建)
详细的收藏接口使用文档，包含：
- 接口说明和参数详解
- 请求/响应示例
- 数据验证规则
- 多种语言的使用示例（Python、JavaScript、微信小程序）
- 错误码说明
- 数据库集合结构和索引建议
- 业务逻辑说明
- 性能优化建议
- 前端集成建议
- 测试建议
- 未来扩展方向

#### `test_favorite_api.py` (新建)
完整的收藏接口测试脚本，包含15个测试场景：
1. 登录获取token
2. 查询初始收藏列表
3. 查询导师收藏状态
4. 收藏导师
5. 再次查询收藏状态（验证收藏成功）
6. 查询收藏列表
7. 批量查询收藏状态
8. 取消收藏（Toggle方式）
9. 验证取消收藏后的状态
10. 测试DELETE方法取消收藏
11. 测试无token访问（预期失败）
12. 测试收藏不存在的导师（预期失败）
13. 测试空导师ID（预期失败）
14. 测试分页功能
15. 测试DELETE未收藏的导师（预期失败）

## 🔧 技术实现细节

### 1. 数据验证
使用Pydantic进行严格的数据验证：
- 导师ID非空验证
- 导师ID列表长度限制（1-100）
- 自动去重
- 自定义验证器（validator）

### 2. 异步数据库操作
使用MongoDB的异步操作：
```python
from app.db.mongo import find_one, insert_one, delete_one, get_collection

# 查询收藏记录
favorite = await find_one("favorites", {"user_id": user_id, "target_id": tutor_id})

# 创建收藏记录
await insert_one("favorites", favorite_data)

# 删除收藏记录
await delete_one("favorites", {"id": favorite_id})

# 批量查询
favorites_collection = get_collection("favorites")
favorites = await favorites_collection.find(query).to_list(length=100)
```

### 3. JWT认证
通过依赖注入获取当前用户：
```python
async def toggle_favorite(
    current_user: User = Depends(get_current_user)
):
    # current_user 已经通过JWT验证
    pass
```

### 4. 错误处理
完整的错误处理机制：
- 导师不存在验证（404）
- 导师未收藏验证（404，DELETE方法）
- 数据库操作异常处理
- 详细的错误日志记录

### 5. 日志记录
每个操作都有详细的日志：
```python
api_logger.info(
    f"收藏成功: User {current_user.id} -> Tutor {tutor_id} ({tutor['name']})\n"
    f"Request ID: {request.state.request_id}"
)
```

### 6. 性能优化
- **批量查询**: 使用`$in`操作符一次性查询多个导师的收藏状态
- **分页加载**: 收藏列表支持分页，避免一次加载过多数据
- **索引优化**: 建议创建复合索引提高查询性能

## 📊 数据库集合结构

### favorites 集合
```javascript
{
  "_id": ObjectId("..."),
  "id": "fav_uuid",              // 收藏记录唯一标识
  "user_id": "user_123",         // 用户ID
  "target_type": "tutor",        // 目标类型（tutor/project）
  "target_id": "tutor_123",      // 目标ID（导师ID）
  "created_at": ISODate()        // 收藏时间
}
```

### 推荐索引
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

## 🔐 安全性考虑

1. **JWT认证**: 所有接口都需要有效的JWT token
2. **用户隔离**: 用户只能查询和操作自己的收藏
3. **导师验证**: 收藏时验证导师是否存在
4. **数据验证**: 严格的输入数据验证，防止注入攻击
5. **错误信息**: 不暴露敏感的系统信息
6. **日志记录**: 记录所有操作，便于审计
7. **防重复收藏**: 数据库层面通过唯一索引防止重复收藏

## 🚀 如何使用

### 1. 启动服务
```bash
cd backend
python main.py
```

### 2. 运行测试
```bash
python test_favorite_api.py
```

### 3. 查看API文档
访问: http://localhost:8000/docs

### 4. 接口调用示例

#### 收藏导师
```bash
curl -X POST "http://localhost:8000/api/v1/user/favorite/toggle" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"tutor_id": "tutor_123"}'
```

#### 查询收藏列表
```bash
curl -X GET "http://localhost:8000/api/v1/user/favorites?page=1&page_size=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 查询收藏状态
```bash
curl -X GET "http://localhost:8000/api/v1/user/favorite/status/tutor_123" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 批量查询收藏状态
```bash
curl -X POST "http://localhost:8000/api/v1/user/favorite/batch-status" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"tutor_ids": ["tutor_123", "tutor_456", "tutor_789"]}'
```

#### 取消收藏
```bash
curl -X DELETE "http://localhost:8000/api/v1/user/favorite/tutor_123" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 📝 接口响应格式

### 成功响应
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    // 具体数据
  }
}
```

### 错误响应
```json
{
  "code": 404,
  "message": "导师不存在",
  "error": {
    "code": "TUTOR_NOT_FOUND",
    "details": {
      "tutor_id": "tutor_123"
    }
  }
}
```

## ✅ 测试清单

- [x] 收藏导师功能
- [x] 取消收藏功能（Toggle方式）
- [x] 取消收藏功能（DELETE方式）
- [x] 查询收藏列表功能
- [x] 查询收藏状态功能
- [x] 批量查询收藏状态功能
- [x] 分页功能
- [x] JWT认证验证
- [x] 导师存在性验证
- [x] 数据验证（空ID、不存在的导师）
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

3. **集合名称**: 
   - `favorites` - 收藏记录
   - `tutors` - 导师信息

4. **测试数据**: 运行测试前需要确保数据库中有测试导师数据

5. **索引创建**: 建议创建推荐的数据库索引以提高性能

## 🎯 业务逻辑

### 收藏/取消收藏流程
1. 验证用户身份（JWT token）
2. 验证导师是否存在
3. 查询当前收藏状态
4. 如果已收藏：删除收藏记录
5. 如果未收藏：创建收藏记录
6. 返回操作结果和新状态

### 查询收藏列表流程
1. 验证用户身份（JWT token）
2. 查询用户的收藏记录（分页、按时间倒序）
3. 根据收藏记录查询导师详细信息
4. 组合数据并返回

### 批量查询优化
使用MongoDB的`$in`操作符一次性查询多个导师的收藏状态，避免N+1查询问题。

## 📈 性能优化

1. **数据库索引**: 创建合适的复合索引
2. **批量查询**: 列表页使用批量查询接口
3. **分页加载**: 避免一次加载过多数据
4. **异步操作**: 所有数据库操作都是异步的
5. **缓存策略**: 未来可以考虑使用Redis缓存

## 🔄 与其他模块的集成

### 导师详情页集成
导师详情接口（`/api/v1/tutor/detail/{tutor_id}`）已经集成了收藏状态查询：
```python
# 检查是否已收藏
if current_user:
    favorite = db.favorites.find_one({
        "user_id": current_user.id,
        "target_type": "tutor",
        "target_id": tutor_id
    })
    detail_data["is_collected"] = favorite is not None
```

### 用户信息模块
收藏功能与用户信息模块共享同一个路由前缀 `/api/v1/user`，保持API设计的一致性。

## 🎉 总结

本次实现完成了收藏功能的核心模块，包括：
- ✅ 5个完整的收藏接口
- ✅ 7个数据校验模型
- ✅ 完善的错误处理和日志记录
- ✅ 详细的接口文档
- ✅ 完整的测试脚本（15个测试场景）
- ✅ 性能优化和安全考虑
- ✅ 详细的中文注释

所有功能已经过测试，代码质量良好，可以直接投入使用！

## 📚 相关文档

- **接口详细文档**: `app/api/v1/user/FAVORITE_README.md`
- **测试脚本**: `test_favorite_api.py`
- **数据模型**: `app/schemas/favorite_schema.py`
- **API实现**: `app/api/v1/user/favorite.py`

---

**开发时间**: 2024-03-01  
**开发者**: AI Assistant  
**版本**: v1.0.0
