# 导师资料查询小程序后端文件说明

## 项目结构说明

```
backend/                    # 后端根模块(Python技术栈，核心业务/AI逻辑)
├── alembic/                # 数据库迁移配置和脚本
│   ├── env.py              # Alembic环境配置，连接MongoDB数据库
│   ├── script.py.mako      # 迁移脚本模板，定义生成格式
│   └── versions/           # 迁移脚本存储目录
│       └── 001_initial_migration.py  # 初始迁移脚本，创建teachers集合索引
├── alembic.ini             # Alembic主配置文件，管理迁移参数和日志
├── app/                    # 后端核心代码
│   ├── api/                # API接口层（对接小程序前端）
│   │   ├── api.py          # API路由汇总，统一管理所有版本接口
│   │   └── v1/             # API版本化接口目录
│   │       └── teachers.py # 导师信息CRUD接口，提供增删改查功能
│   ├── core/               # 全局配置（数据库、日志、安全）
│   │   ├── __init__.py     # 核心模块初始化，统一导出配置
│   │   └── config/         # 配置管理模块
│   │       ├── __init__.py # 配置模块初始化，统一导出
│   │       ├── app.py      # 应用配置，管理环境、服务、API等设置
│   │       ├── database.py # 数据库配置，统一管理连接参数
│   │       ├── logging.py  # 日志配置，支持复杂的日志系统设置
│   │       └── security.py # 安全配置，管理JWT、CORS、密码策略等
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
│       ├── __init__.py     # 工具模块初始化，统一导出工具函数
│       ├── logger.py       # 日志工具，支持文件轮转、多级别日志
│       ├── response.py     # 统一响应格式工具，标准化API输出
│       └── security.py     # 安全工具，JWT、密码加密、数据验证
├── main.py                 # 后端启动入口（FastAPI），应用配置和服务启动
├── migrate.py              # 数据库迁移管理脚本，提供命令行工具
├── requirements.txt        # 后端依赖清单，管理Python包依赖
├── .env                    # 后端环境变量，包含敏感配置信息
├── .env.example            # 后端环境变量示例，开发参考模板
├── PROJECT_STRUCTURE.md    # 项目结构详细说明文档
└── README_MIGRATION.md     # 数据库迁移管理指南和最佳实践
```

## 核心文件功能说明

### API接口层

| 文件名 | 功能说明 | 主要职责 |
|--------|----------|----------|
| `app/api/api.py` | API路由汇总 | 统一挂载所有版本的API接口，管理路由前缀 |
| `app/api/v1/teachers.py` | 导师信息接口 | 提供5个RESTful API端点，支持增删改查操作 |

### 配置管理层

| 文件名 | 功能说明 | 主要职责 |
|--------|----------|----------|
| `app/core/config/app.py` | 应用配置 | 管理应用基础信息、环境设置、服务配置 |
| `app/core/config/database.py` | 数据库配置 | 管理数据库连接参数、迁移设置 |
| `app/core/config/logging.py` | 日志配置 | 管理日志级别、格式、文件路径、轮转设置 |
| `app/core/config/security.py` | 安全配置 | 管理JWT、CORS、密码策略、敏感数据处理 |

### 数据访问层

| 文件名 | 功能说明 | 主要职责 |
|--------|----------|----------|
| `app/db/mongo.py` | MongoDB连接 | 管理数据库连接实例，提供数据库访问接口 |
| `app/crud/teacher_crud.py` | 导师CRUD操作 | 封装MongoDB的增删改查操作，提供业务接口 |
| `app/models/teacher.py` | 导师数据模型 | 定义导师信息的数据结构和验证规则 |
| `app/schemas/teacher_schema.py` | 请求参数校验 | 定义API请求和响应的数据结构 |

### 工具支持层

| 文件名 | 功能说明 | 主要职责 |
|--------|----------|----------|
| `app/utils/response.py` | 响应格式化 | 提供统一的API响应格式，支持成功、错误、分页响应 |
| `app/utils/logger.py` | 日志工具 | 提供自定义日志类，支持多级别、多文件日志 |
| `app/utils/security.py` | 安全工具 | 提供JWT生成验证、密码加密、数据验证等功能 |

### 数据库迁移层

| 文件名 | 功能说明 | 主要职责 |
|--------|----------|----------|
| `alembic.ini` | Alembic配置 | 管理迁移工具的全局配置参数 |
| `alembic/env.py` | 迁移环境配置 | 连接MongoDB，提供迁移上下文 |
| `alembic/versions/001_initial_migration.py` | 初始迁移脚本 | 创建teachers集合和索引 |
| `migrate.py` | 迁移管理工具 | 提供命令行界面管理数据库迁移 |

### 应用入口层

| 文件名 | 功能说明 | 主要职责 |
|--------|----------|----------|
| `main.py` | 应用主入口 | FastAPI应用配置、中间件设置、路由挂载、服务启动 |
| `requirements.txt` | 依赖管理 | 列出项目所需的所有Python包及其版本 |
| `.env` | 环境变量 | 存储敏感配置信息，如数据库密码、JWT密钥 |

## 技术特性说明

### 1. 模块化设计
- 采用清晰的分层架构，各模块职责明确
- 支持功能扩展和代码复用
- 便于团队协作开发

### 2. 配置管理
- 使用Pydantic V2进行配置验证
- 支持环境变量覆盖默认配置
- 单例模式确保配置一致性

### 3. 安全特性
- JWT令牌认证机制
- 密码bcrypt加密存储
- 输入验证和XSS防护
- CORS跨域保护
- 敏感数据屏蔽

### 4. 日志系统
- 多级别日志支持（DEBUG/INFO/WARNING/ERROR/CRITICAL）
- 文件和控制台双输出
- 日志自动轮转
- 请求日志和数据库操作日志分离

### 5. API设计
- RESTful API设计规范
- 版本化API管理
- 统一响应格式
- 完善的错误处理
- 自动生成API文档

### 6. 数据库管理
- MongoDB文档数据库
- Alembic版本化迁移
- 索引优化
- 连接池管理

## 开发和部署说明

### 开发环境启动
```bash
# 安装依赖
pip install -r requirements.txt

# 执行数据库迁移
python migrate.py upgrade

# 启动开发服务器
python main.py
```

### 生产环境部署
```bash
# 设置生产环境变量
export APP_ENVIRONMENT=production
export LOG_LEVEL=INFO

# 使用Gunicorn/Uvicorn部署
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

### API文档访问
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI: http://localhost:8000/api/openapi.json

## 文件组织原则

1. **职责单一原则**：每个文件只负责一个功能模块
2. **高内聚低耦合**：相关功能集中在同一模块，模块间依赖最小化
3. **可扩展性**：支持新功能和新模块的添加
4. **可维护性**：代码结构清晰，易于理解和修改
5. **安全性**：敏感信息通过环境变量管理，避免硬编码