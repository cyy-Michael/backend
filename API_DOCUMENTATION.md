导师资料查询小程序后端API文档
1. 概述
本文档定义了小程序前端与后端服务器之间的数据交互接口及字段规范。后端主要负责用户认证、数据存储（爬虫数据+用户数据）、业务逻辑处理（收藏、预约、匹配）。

2. 技术栈
后端框架: FastAPI (Python)
数据库: MongoDB
认证方式: JWT (JSON Web Token)
API版本: v1
3. 接口规范
3.1 基础URL
所有API接口的基础URL为：/api/v1

3.2 响应格式
统一的JSON响应结构：

{
  "success": true,
  "message": "操作成功",
  "data": { ... },
  "error": null,
  "meta": null
}
错误响应格式：

{
  "success": false,
  "message": "操作失败",
  "data": null,
  "error": {
    "code": "ERROR_CODE",
    "details": { ... }
  },
  "meta": null
}
3.3 认证方式
使用Bearer Token认证，在请求头中添加：

Authorization: Bearer <token>
4. 核心模块
4.1 用户模块 (User)
功能: 微信登录、用户信息维护、会员状态管理。

A. 登录 (Login)
接口: POST /api/v1/auth/login
输入: code (微信登录凭证)
输出:
token (JWT, 用于后续鉴权)
userInfo (包含 nickname, avatar, vipStatus, vipExpireDate)
B. 获取用户信息 (Get User Info)
接口: GET /api/v1/user/profile
输出: userInfo 对象。
C. 更新用户信息 (Update User Info)
接口: PUT /api/v1/user/profile
输入: nickname, avatar, school, major, grade (年级)
D. 获取VIP状态 (Get VIP Status)
接口: GET /api/v1/user/vip-status
输出: VIP状态信息。
4.2 导师模块 (Tutor)
功能: 导师列表查询、详情展示、筛选。

A. 导师列表 (List Tutors)
接口: GET /api/v1/tutor/list
参数:
page: 页码 (默认1)
pageSize: 每页数量 (默认10)
keyword: 搜索关键词 (姓名/研究方向)
school: 学校筛选 (可选)
department: 学院筛选 (可选)
city: 城市筛选 (可选)
输出:
list: 导师简略信息列表 [{ id, name, title, school, department, tags, avatar }]
total: 总记录数
page: 当前页码
pageSize: 每页数量
B. 导师详情 (Get Tutor Detail)
接口: GET /api/v1/tutor/detail/:id
参数: id (导师ID)
输出:
tutor: 包含爬虫抓取的所有详细字段 (bio, papers, projects, coops, students, risks, socials 等)。
isCollected: Boolean (当前用户是否收藏)
C. 搜索建议 (Search Suggestions)
接口: GET /api/v1/tutor/search/suggestions
参数:
keyword: 搜索关键词
field: 搜索字段 (all, name, school, department)
输出: 搜索建议列表。
4.3 业务交互模块 (Interaction)
A. 收藏/取消收藏 (Toggle Favorite)
接口: POST /api/v1/user/favorite
输入:
type: "tutor" | "project"
targetId: 目标ID
输出: status (collected/uncollected)
B. 获取收藏列表 (Get Favorites)
接口: GET /api/v1/user/favorites
参数:
type: "tutor" | "project"
page: 页码
pageSize: 每页数量
输出: 收藏对象的列表。
C. 检查收藏状态 (Check Favorite)
接口: GET /api/v1/user/favorite/check
参数:
type: "tutor" | "project"
targetId: 目标ID
输出: isCollected (是否已收藏)
D. 预约咨询 (Book Consultation - 仅VIP)
接口: POST /api/v1/service/book
输入: tutorId, date, message
输出: bookingId, status (pending)
E. 获取预约列表 (Get Bookings)
接口: GET /api/v1/service/bookings
参数: status (可选)
输出: 预约列表。
F. 取消预约 (Cancel Booking)
接口: POST /api/v1/service/booking/:id/cancel
参数: id (预约ID)
输出: 取消结果。
4.4 智能匹配模块 (Research Match)
功能: 根据用户输入的学科方向和关键词，推荐匹配度高的导师。

A. 提交匹配请求 (Submit Match)
接口: POST /api/v1/match/submit
输入:
discipline: 学科方向 (String)
keywords: 研究兴趣关键词 (String, 逗号分隔)
preferences: 偏好设置 { crossSchool: Boolean, highOutput: Boolean, youngScholar: Boolean }
输出:
matchId: 匹配任务ID
results: 匹配导师列表 [{ tutorId, matchScore, matchReason, ...tutorInfo }]
B. 获取匹配历史 (Get Match History)
接口: GET /api/v1/match/history
参数: page, pageSize
输出: 匹配历史列表。
C. 获取匹配历史详情 (Get Match History Detail)
接口: GET /api/v1/match/history/:id
参数: id (历史记录ID)
输出: 匹配历史详情。
4.5 合作机会模块 (Cooperation Opportunities)
功能: 展示跨校合作项目、产学研机会。

A. 项目列表 (List Projects)
接口: GET /api/v1/project/list
参数:
type: ai/bigdata/iot/all
page: 页码
pageSize: 每页数量
输出: 项目列表 [{ id, title, tags, desc, members: [{ name, school }] }]
B. 项目详情 (Get Project Detail)
接口: GET /api/v1/project/detail/:id
参数: id (项目ID)
输出: 项目详细信息。
C. 申请加入 (Apply Project)
接口: POST /api/v1/project/apply
输入: projectId, reason, resume (简历链接)
输出: applicationId, status
D. 获取申请列表 (Get Applications)
接口: GET /api/v1/project/applications
参数: status (可选)
输出: 申请列表。
5. 数据库设计
5.1 用户表 (users)
id: 用户ID
openid: 微信openid
unionid: 微信unionid
nickname: 昵称
avatar: 头像URL
school: 学校
major: 专业
grade: 年级
vip_status: VIP状态
vip_expire_date: VIP过期时间
created_at: 创建时间
updated_at: 更新时间
5.2 导师表 (tutors)
id: 导师ID
name: 姓名
title: 职称
school_id: 学校ID
school_name: 学校名称
department_id: 院系ID
department_name: 院系名称
bio: 个人简介
email: 邮箱
phone: 电话
avatar_url: 头像URL
personal_page_url: 个人主页
research_direction: 研究方向
tags: 标签列表
city: 城市
crawled_at: 爬取时间
created_at: 创建时间
updated_at: 更新时间
5.3 导师详情表 (tutor_details)
tutor_id: 导师ID
bio: 详细简介
achievements_summary: 成果总结
papers: 论文列表 (JSON)
projects: 项目列表 (JSON)
coops: 合作经历 (JSON)
students: 学生信息 (JSON)
risks: 风险提示 (JSON)
socials: 社交账号 (JSON)
5.4 收藏表 (favorites)
id: 收藏ID
user_id: 用户ID
target_type: 目标类型 (tutor/project)
target_id: 目标ID
created_at: 创建时间
5.5 预约表 (bookings)
id: 预约ID
user_id: 用户ID
tutor_id: 导师ID
date: 预约时间
message: 留言
status: 状态 (pending/confirmed/cancelled/completed)
created_at: 创建时间
updated_at: 更新时间
6. 错误码定义
| 错误码 | 描述 | HTTP状态码 | |--------|------|------------| | WECHAT_AUTH_FAILED | 微信授权失败 | 400 | | USER_NOT_FOUND | 用户不存在 | 404 | | TUTOR_NOT_FOUND | 导师不存在 | 404 | | PROJECT_NOT_FOUND | 项目不存在 | 404 | | VIP_REQUIRED | 需要VIP权限 | 403 | | VIP_EXPIRED | VIP已过期 | 403 | | TIME_CONFLICT | 时间冲突 | 400 | | DUPLICATE_BOOKING | 重复预约 | 400 | | ALREADY_APPLIED | 已申请过该项目 | 400 | | INVALID_TYPE | 无效的类型 | 400 | | INVALID_KEYWORDS | 无效的关键词 | 400 | | BOOKING_NOT_FOUND | 预约记录不存在 | 404 | | CANNOT_CANCEL | 无法取消 | 400 | | HISTORY_NOT_FOUND | 历史记录不存在 | 404 |

7. 部署说明
7.1 环境变量
需要配置以下环境变量：

MONGODB_URI: MongoDB连接字符串
DATABASE_NAME: 数据库名称
JWT_SECRET_KEY: JWT密钥
JWT_ALGORITHM: JWT算法
JWT_ACCESS_TOKEN_EXPIRE_MINUTES: JWT过期时间（分钟）
APP_NAME: 应用名称
APP_VERSION: 应用版本
DEBUG: 是否开启调试模式
7.2 启动命令
# 安装依赖
pip install -r requirements.txt

# 初始化数据库
python app/db/init_data.py

# 启动服务
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
8. 开发说明
8.1 项目结构
backend/
├── app/
│   ├── api/                  # API路由
│   │   ├── v1/               # v1版本API
│   │   │   ├── auth/         # 认证相关
│   │   │   ├── user/         # 用户相关
│   │   │   ├── tutor/        # 导师相关
│   │   │   ├── interaction/  # 交互相关
│   │   │   ├── match/        # 匹配相关
│   │   │   └── project/      # 项目相关
│   ├── core/                 # 核心配置
│   │   ├── config/           # 配置文件
│   ├── db/                   # 数据库相关
│   │   ├── mongo.py          # MongoDB连接
│   │   └── init_data.py      # 数据初始化
│   ├── models/               # 数据模型
│   ├── schemas/              # 数据校验
│   └── utils/                # 工具函数
├── main.py                   # 应用入口
├── requirements.txt          # 依赖列表
├── .env.example              # 环境变量示例
└── alembic.ini               # 数据库迁移配置
8.2 代码规范
使用Pydantic V2进行数据验证
使用MongoDB进行数据存储
使用JWT进行用户认证
统一的错误处理和日志记录
RESTful API设计规范
9. 安全注意事项
数据安全: 敏感数据加密存储，如用户密码（虽然本项目使用微信登录）
认证安全: JWT令牌设置合理的过期时间
输入验证: 所有用户输入必须经过严格验证
权限控制: VIP功能需要权限检查
CORS配置: 合理配置CORS策略
日志记录: 记录关键操作日志，便于审计