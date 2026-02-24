# 导师资料查询小程序后端项目结构说明

## 项目整体结构

```
backend/                    # 后端根模块(Python技术栈，核心业务/AI逻辑)
├── alembic/                # 数据库迁移配置和脚本
│   ├── env.py              # Alembic环境配置，连接MongoDB数据库
│   ├── script.py.mako      # 迁移脚本模板
│   └── versions/           # 迁移脚本存储目录
│       └── 001_initial_migration.py  # 初始迁移脚本，创建索引
├── app/                    # 后端核心代码
│   ├── api/                # API接口层（对接小程序前端）
│   │   ├── api.py          # API路由汇总，统一管理所有版本接口
│   │   └── v1/             # API版本化接口目录
│   │       └── teachers.py # 导师信息CRUD接口，提供增删改查功能
│   ├── core/               # 全局配置（数据库、日志、安全）
│   │   ├── __init__.py     # 核心模块初始化
│   │   └── config/         # 配置管理模块
│   │       ├── __init__.py # 配置模块初始化
│   │       ├── app.py      # 应用配置，管理环境、服务、API等设置
│   │       ├── database.py # 数据库配置，统一管理连接参数
│   │       ├── logging.py  # 日志配置，支持复杂的日志系统
│   │       └── security.py # 安全配置，管理JWT、CORS、密码策略
│   ├── crud/               # 数据库增删改查
│   │   └── teacher_crud.py # 导师信息数据库操作，封装MongoDB交互
│   ├── db/                 # 数据库连接/迁移
│   │   └── mongo.py        # MongoDB数据库连接配置和实例管理
│   ├── models/             # ORM数据模型
│   │   └── teacher.py      # 导师信息数据模型，定义数据结构
│   ├── schemas/            # 数据校验/序列化
│   │   └── teacher_schema.py # 导师信息请求参数校验，确保数据完整性
│   ├── services/           # 业务逻辑（AI推荐、LLM交互）
│   └── utils/              # 后端通用工具
│       ├── __init__.py     # 工具模块初始化
│       ├── logger.py       # 日志工具，支持文件轮转、多级别日志
│       ├── response.py     # 统一响应格式工具，标准化API输出
│       └── security.py     # 安全工具，JWT、密码加密、数据验证
├── main.py                 # 后端启动入口（FastAPI）
├── migrate.py              # 数据库迁移管理脚本
├── requirements.txt        # 后端依赖清单
├── .env                    # 后端环境变量
├── .env.example            # 后端环境变量示例
└── README_MIGRATION.md     # 数据库迁移管理指南
```

## 详细文件说明

### 根目录文件

```
backend/
├── alembic.ini             # Alembic主配置文件，管理迁移参数
├── main.py                 # 后端服务主入口，FastAPI应用配置和启动
├── migrate.py              # 数据库迁移管理脚本，提供命令行工具
├── requirements.txt        # Python依赖包列表，管理项目依赖
├── .env                    # 环境变量配置，包含敏感信息
├── .env.example            # 环境变量示例，用于开发参考
└── README_MIGRATION.md     # 数据库迁移使用文档和最佳实践
```

### alembic目录

```
alembic/
├── env.py                  # Alembic环境配置，处理MongoDB连接和迁移上下文
├── script.py.mako          # 迁移脚本模板，定义生成格式
└── versions/
    └── 001_initial_migration.py  # 初始数据库结构迁移，创建teachers集合索引
```

### app/api目录

```
app/api/
├── api.py                  # API路由汇总，统一挂载所有版本接口
└── v1/
    └── teachers.py         # 导师信息接口，包含5个RESTful API端点
```

### app/core目录

```
app/core/
├── __init__.py             # 核心模块导出
└── config/
    ├── __init__.py         # 配置模块导出
    ├── app.py              # 应用基础配置，环境管理
    ├── database.py         # 数据库连接配置
    ├── logging.py          # 日志系统配置
    └── security.py         # 安全相关配置
```

### app/crud目录

```
app/crud/
└── teacher_crud.py         # 导师信息CRUD操作，封装数据库访问逻辑
```

### app/db目录

```
app/db/
└── mongo.py                # MongoDB数据库连接管理，提供数据库实例
```

### app/models目录

```
app/models/
└── teacher.py              # 导师信息数据模型，定义完整数据结构
```

### app/schemas目录

```
app/schemas/
└── teacher_schema.py       # API请求参数校验模型，确保数据合法性
```

### app/utils目录

```
app/utils/
├── __init__.py             # 工具模块导出
├── logger.py               # 日志工具类，提供统一的日志记录方式
├── response.py             # 响应格式化工具，统一API返回格式
└── security.py             # 安全工具，包含认证、加密、验证功能
```

## 模块功能说明

### 1. 核心业务模块

**app/api/v1/teachers.py** - 导师信息接口层
- 提供5个RESTful API端点：查询单个、查询列表、新增、更新、删除
- 支持分页查询、字段过滤、输入验证
- 统一的错误处理和响应格式

**app/crud/teacher_crud.py** - 数据访问层
- 封装MongoDB数据库操作
- 提供增删改查的原子操作
- 处理ObjectId转换和数据格式化

**app/models/teacher.py** - 数据模型层
- 定义导师信息完整数据结构
- 使用Pydantic V2进行数据验证
- 支持嵌套模型和复杂数据类型

### 2. 配置管理模块

**app/core/config/** - 统一配置管理
- 应用配置：环境、服务端口、API前缀
- 数据库配置：连接字符串、数据库名称
- 日志配置：级别、格式、文件路径
- 安全配置：JWT、CORS、密码策略

### 3. 工具支持模块

**app/utils/response.py** - 响应格式化
- 标准化API响应结构
- 支持成功、错误、分页等响应类型
- 统一的错误码和消息格式

**app/utils/logger.py** - 日志系统
- 支持文件和控制台输出
- 自动日志轮转
- 多级别日志管理

**app/utils/security.py** - 安全工具
- JWT令牌生成和验证
- 密码加密和验证
- 输入验证和XSS防护

### 4. 数据库迁移模块

**alembic/** - 数据库版本管理
- 支持MongoDB索引创建和管理
- 版本化的数据库变更
- 可回滚的迁移操作

**migrate.py** - 迁移管理工具
- 命令行界面管理迁移
- 支持创建、升级、回滚操作
- 迁移历史查看

## 技术栈说明

- **FastAPI**: 高性能异步Web框架
- **MongoDB**: 文档型数据库
- **Pydantic V2**: 数据验证和序列化
- **Alembic**: 数据库迁移管理
- **JWT**: 用户认证和授权
- **Python 3.9+**: 编程语言

## 开发和部署

### 开发环境
```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务（开发模式）
python main.py

# 执行数据库迁移
python migrate.py upgrade
```

### 生产环境
```bash
# 安装依赖
pip install -r requirements.txt

# 设置环境变量
export APP_ENVIRONMENT=production

# 启动服务
uvicorn main:app --host 0.0.0.0 --port 8000
```

## API接口文档

启动服务后，可通过以下地址访问自动生成的API文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 安全和性能

- **安全特性**: JWT认证、密码加密、输入验证、CORS保护
- **性能优化**: 连接池、请求缓存、异步处理
- **监控日志**: 详细的请求日志、数据库操作日志、错误日志
- **错误处理**: 统一的异常处理和错误响应