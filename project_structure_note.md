# 项目结构说明

## 当前项目结构

```
导师社工小程序/
├── backend/              # 后端项目（FastAPI）
│   ├── app/             # 应用代码
│   ├── main.py          # 入口文件
│   ├── requirements.txt # Python依赖
│   └── ...
└── frontend/            # 前端项目（微信小程序）- 需要创建
    ├── pages/           # 页面
    ├── app.json         # 小程序配置
    ├── app.js           # 小程序逻辑
    └── ...
```

## 如何运行

### 1. 运行后端服务器

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 2. 运行小程序（需要先创建前端项目）

1. 在项目根目录创建 `frontend` 文件夹
2. 使用微信开发者工具打开 `frontend` 文件夹
3. 配置小程序的 `app.json` 文件

## 错误说明

**错误**: `app.json: 在项目根目录未找到 app.json`

**原因**: 
- 你在微信开发者工具中打开了 `backend` 文件夹
- `backend` 是 Python 后端项目，不是小程序项目
- 小程序需要 `app.json` 文件，但后端项目不需要

**解决方案**:
1. 如果要开发后端：在终端运行 `uvicorn main:app --reload`
2. 如果要开发小程序：需要创建独立的前端项目文件夹

## 当前 backend 项目功能

✅ 已实现的后端接口：
- 用户登录认证
- 用户资料管理
- 用户收藏功能
- 导师列表查询
- 导师详情查询
- 导师高级搜索
- 导师CRUD（管理员）
- 导师信息导出（管理员）

## 测试后端接口

```bash
# 运行各个测试脚本
python test_user_api.py
python test_favorite_api.py
python test_tutor_crud_api.py
python test_tutor_search_api.py
python test_tutor_detail_api.py
python test_tutor_export_api.py
```

## 下一步

如果你需要创建小程序前端项目，请告诉我，我可以帮你：
1. 创建小程序项目结构
2. 创建 app.json 配置文件
3. 创建页面和组件
4. 配置API调用
