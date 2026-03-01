# 🚀 快速启动指南

## 📋 前置要求

- Python 3.8+
- MongoDB Atlas账号（已配置）
- pip包管理器

## 🔧 安装步骤

### 1. 安装依赖
```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置环境变量（可选）
MongoDB连接已经在代码中配置好，如需修改可创建 `.env` 文件：
```bash
# .env 文件内容
MONGO_URI=mongodb+srv://0227_wx201383_db_user:hdkkdbdikwksbffkfjdwl645s87jwksadasfsafasf@cluster0.roe7na.mongodb.net/
DB_NAME=teacher_query
```

### 3. 启动服务
```bash
python main.py
```

服务将在 `http://localhost:8000` 启动

## 📚 访问API文档

启动服务后，访问以下地址查看自动生成的API文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🧪 测试用户信息接口

### 方法1: 使用测试脚本
```bash
python test_user_api.py
```

### 方法2: 使用curl命令

#### 1. 登录获取token
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"code": "test_wx_code"}'
```

#### 2. 获取用户信息
```bash
curl -X GET "http://localhost:8000/api/v1/user/profile" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 3. 更新用户信息
```bash
curl -X PUT "http://localhost:8000/api/v1/user/profile" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nickname": "张三",
    "school": "清华大学",
    "major": "计算机科学与技术",
    "grade": "2024级"
  }'
```

### 方法3: 使用Postman或其他API测试工具

1. 导入接口到Postman
2. 先调用登录接口获取token
3. 在后续请求的Header中添加: `Authorization: Bearer {token}`
4. 测试各个接口

## 📖 接口列表

### 认证相关
- `POST /api/v1/auth/login` - 微信登录
- `POST /api/v1/auth/logout` - 用户登出
- `GET /api/v1/auth/refresh` - 刷新token

### 用户信息相关（新增）
- `GET /api/v1/user/profile` - 获取用户信息
- `PUT /api/v1/user/profile` - 更新用户信息
- `PATCH /api/v1/user/profile` - 部分更新用户信息

### 其他接口
- `GET /health` - 健康检查
- 更多接口请查看API文档

## 🗂️ 项目结构

```
backend/
├── app/
│   ├── api/                    # API路由
│   │   ├── v1/
│   │   │   ├── auth/          # 认证接口
│   │   │   │   └── login.py
│   │   │   ├── user/          # 用户接口（新增）
│   │   │   │   ├── profile.py # 用户信息接口
│   │   │   │   └── README.md  # 用户接口文档
│   │   │   ├── tutor/         # 导师接口
│   │   │   ├── interaction/   # 交互接口
│   │   │   ├── match/         # 匹配接口
│   │   │   └── project/       # 项目接口
│   ├── core/                  # 核心配置
│   │   └── config/
│   │       └── database.py    # 数据库配置
│   ├── db/                    # 数据库相关
│   │   └── mongo.py           # MongoDB连接
│   ├── models/                # 数据模型
│   │   └── user.py
│   ├── schemas/               # 数据校验（新增）
│   │   ├── __init__.py
│   │   ├── user_schema.py     # 用户信息校验
│   │   └── teacher_schema.py
│   └── utils/                 # 工具函数
├── main.py                    # 应用入口
├── requirements.txt           # 依赖列表
├── test_user_api.py          # 测试脚本（新增）
├── USER_API_IMPLEMENTATION.md # 实现文档（新增）
└── QUICK_START.md            # 快速启动指南（本文件）
```

## 💡 常见问题

### 1. MongoDB连接失败
**问题**: 无法连接到MongoDB
**解决**: 
- 检查网络连接
- 确认MongoDB Atlas白名单设置
- 验证连接字符串是否正确

### 2. 端口被占用
**问题**: 8000端口已被占用
**解决**: 
- 修改 `main.py` 中的端口配置
- 或者关闭占用8000端口的程序

### 3. 依赖安装失败
**问题**: pip install失败
**解决**: 
- 使用国内镜像源: `pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple`
- 升级pip: `pip install --upgrade pip`

### 4. JWT token无效
**问题**: 401 Unauthorized错误
**解决**: 
- 重新登录获取新token
- 检查token是否正确复制（包含完整的Bearer前缀）
- 确认token未过期

## 📞 技术支持

如遇到问题，请查看：
1. `USER_API_IMPLEMENTATION.md` - 详细实现文档
2. `app/api/v1/user/README.md` - 用户接口详细文档
3. API文档: http://localhost:8000/docs

## ✅ 验证安装

运行以下命令验证服务是否正常：
```bash
curl http://localhost:8000/health
```

预期响应：
```json
{
  "code": 200,
  "message": "导师资料查询小程序后端 服务运行正常",
  "data": {
    "version": "1.0.0",
    "environment": "development",
    "timestamp": "2024-03-01 12:00:00"
  }
}
```

## 🎉 开始使用

现在你可以开始使用用户信息管理接口了！

1. 启动服务: `python main.py`
2. 运行测试: `python test_user_api.py`
3. 查看文档: http://localhost:8000/docs
4. 开始开发你的小程序前端！

祝开发顺利！🚀
