# 安装后端依赖（使用国内镜像源）
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "安装后端依赖（使用国内镜像源）" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 切换到脚本所在目录
Set-Location $PSScriptRoot

# 镜像源配置
$MIRROR = "https://pypi.tuna.tsinghua.edu.cn/simple"

Write-Host "[1/3] 升级 pip、setuptools 和 wheel..." -ForegroundColor Yellow
python -m pip install --upgrade pip setuptools wheel -i $MIRROR
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠ 升级失败，尝试使用默认源..." -ForegroundColor Yellow
    python -m pip install --upgrade pip setuptools wheel
}

Write-Host ""
Write-Host "[2/3] 先安装预编译的 pydantic-core（避免编译卡住）..." -ForegroundColor Yellow
pip install pydantic-core -i $MIRROR
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠ 使用默认源重试..." -ForegroundColor Yellow
    pip install pydantic-core
}

Write-Host ""
Write-Host "[3/3] 安装所有依赖..." -ForegroundColor Yellow
pip install -r requirements.txt -i $MIRROR
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠ 使用默认源重试..." -ForegroundColor Yellow
    pip install -r requirements.txt
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "安装完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "现在可以启动后端服务了：" -ForegroundColor Cyan
Write-Host "  python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload" -ForegroundColor White
Write-Host ""
