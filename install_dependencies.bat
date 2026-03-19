@echo off
chcp 65001 >nul
echo ========================================
echo 安装后端依赖（使用国内镜像源）
echo ========================================
echo.

cd /d "%~dp0"

echo [1/3] 升级 pip、setuptools 和 wheel...
python -m pip install --upgrade pip setuptools wheel -i https://pypi.tuna.tsinghua.edu.cn/simple
if errorlevel 1 (
    echo ✗ 升级失败，尝试使用默认源...
    python -m pip install --upgrade pip setuptools wheel
)

echo.
echo [2/3] 先安装预编译的 pydantic-core（避免编译卡住）...
pip install pydantic-core -i https://pypi.tuna.tsinghua.edu.cn/simple
if errorlevel 1 (
    echo ⚠ 使用默认源重试...
    pip install pydantic-core
)

echo.
echo [3/3] 安装所有依赖...
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
if errorlevel 1 (
    echo ⚠ 使用默认源重试...
    pip install -r requirements.txt
)

echo.
echo ========================================
echo 安装完成！
echo ========================================
echo.
echo 现在可以启动后端服务了：
echo   python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
echo.
pause
