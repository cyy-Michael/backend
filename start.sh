#!/bin/bash

# 启动脚本 - 用于启动后端服务

echo "=== 导师资料查询小程序后端服务启动脚本 ==="
echo ""

# 检查Python版本
echo "检查Python版本..."
python3 --version

# 检查pip是否安装
if ! command -v pip3 &> /dev/null; then
    echo "错误: pip3 未安装，请先安装Python和pip"
    exit 1
fi

# 检查docker是否安装
if ! command -v docker &> /dev/null; then
    echo "警告: Docker未安装，无法启动MongoDB容器"
    echo "请手动安装MongoDB或安装Docker后重新运行"
    exit 1
fi

# 检查docker-compose是否安装
if ! command -v docker-compose &> /dev/null; then
    echo "警告: docker-compose未安装，无法启动MongoDB容器"
    echo "请手动安装MongoDB或安装docker-compose后重新运行"
    exit 1
fi

echo ""
echo "=== 启动MongoDB数据库 ==="
# 启动MongoDB容器
echo "启动MongoDB和Mongo-Express..."
docker-compose up -d

if [ $? -ne 0 ]; then
    echo "错误: MongoDB容器启动失败"
    exit 1
fi

echo "MongoDB启动成功！"
echo "MongoDB地址: mongodb://localhost:27017"
echo "MongoDB Compass连接字符串: mongodb://admin:password@localhost:27017/"
echo ""

echo "=== 安装Python依赖 ==="
# 安装依赖
echo "安装Python依赖包..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "错误: 依赖安装失败"
    exit 1
fi

echo "依赖安装成功！"
echo ""

echo "=== 初始化数据库 ==="
# 初始化数据库
echo "初始化数据库和示例数据..."
python3 app/db/init_data.py

if [ $? -ne 0 ]; then
    echo "错误: 数据库初始化失败"
    echo "请检查MongoDB是否正常运行"
    exit 1
fi

echo "数据库初始化成功！"
echo ""

echo "=== 启动FastAPI服务 ==="
echo "启动FastAPI后端服务..."
echo ""
echo "服务将在 http://localhost:8000 启动"
echo "API文档地址: http://localhost:8000/docs"
echo "按 Ctrl+C 停止服务"
echo ""

# 启动FastAPI服务
uvicorn main:app --host 0.0.0.0 --port 8000 --reload