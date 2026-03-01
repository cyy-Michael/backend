# 🔖 收藏功能快速参考

## 📌 接口速查表

| 接口 | 方法 | 路径 | 功能 |
|------|------|------|------|
| 收藏/取消收藏 | POST | `/api/v1/user/favorite/toggle` | 切换收藏状态 |
| 收藏列表 | GET | `/api/v1/user/favorites` | 获取收藏列表 |
| 收藏状态 | GET | `/api/v1/user/favorite/status/{tutor_id}` | 查询收藏状态 |
| 批量查询状态 | POST | `/api/v1/user/favorite/batch-status` | 批量查询收藏状态 |
| 取消收藏 | DELETE | `/api/v1/user/favorite/{tutor_id}` | 取消收藏 |

## 🚀 快速开始

### 1. 收藏导师
```bash
curl -X POST "http://localhost:8000/api/v1/user/favorite/toggle" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"tutor_id": "tutor_123"}'
```

### 2. 查询收藏列表
```bash
curl -X GET "http://localhost:8000/api/v1/user/favorites?page=1&page_size=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3. 查询收藏状态
```bash
curl -X GET "http://localhost:8000/api/v1/user/favorite/status/tutor_123" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 📱 微信小程序示例

```javascript
// 收藏/取消收藏
wx.request({
  url: 'http://localhost:8000/api/v1/user/favorite/toggle',
  method: 'POST',
  header: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  data: { tutor_id: 'tutor_123' },
  success: (res) => {
    if (res.data.data.action === 'collected') {
      wx.showToast({ title: '收藏成功', icon: 'success' });
    } else {
      wx.showToast({ title: '取消收藏成功', icon: 'success' });
    }
  }
});

// 查询收藏列表
wx.request({
  url: 'http://localhost:8000/api/v1/user/favorites',
  method: 'GET',
  header: { 'Authorization': `Bearer ${token}` },
  data: { page: 1, page_size: 10 },
  success: (res) => {
    this.setData({ favorites: res.data.data.list });
  }
});
```

## 🗄️ 数据库索引

```javascript
// 创建索引（在MongoDB中执行）
db.favorites.createIndex({ "user_id": 1, "target_type": 1, "created_at": -1 })
db.favorites.createIndex({ "user_id": 1, "target_type": 1, "target_id": 1 }, { unique: true })
db.favorites.createIndex({ "target_id": 1 })
```

## ⚠️ 常见错误

| 错误码 | 状态码 | 说明 | 解决方法 |
|--------|--------|------|----------|
| TUTOR_NOT_FOUND | 404 | 导师不存在 | 检查导师ID是否正确 |
| authentication_error | 401 | token无效 | 重新登录获取token |
| - | 422 | 数据验证失败 | 检查请求参数格式 |

## 🧪 测试

```bash
# 运行测试脚本
python test_favorite_api.py
```

## 📖 详细文档

- **完整接口文档**: `app/api/v1/user/FAVORITE_README.md`
- **实现文档**: `FAVORITE_API_IMPLEMENTATION.md`

---

**提示**: 所有接口都需要JWT token认证！
