# 暖洋洋启动脚本

Write-Host "🌟 启动暖洋洋服务..." -ForegroundColor Cyan

# 检查虚拟环境
if (-not (Test-Path "venv_nuanyangyang")) {
    Write-Host "❌ 虚拟环境不存在，正在创建..." -ForegroundColor Yellow
    python -m venv venv_nuanyangyang
}

# 激活虚拟环境
Write-Host "📦 激活虚拟环境..." -ForegroundColor Green
& "venv_nuanyangyang\Scripts\Activate.ps1"

# 检查Docker服务
Write-Host "🐳 检查Docker服务..." -ForegroundColor Green
$dockerRunning = docker ps 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker未运行，请先启动Docker Desktop" -ForegroundColor Red
    exit 1
}

# 启动Docker Compose服务
Write-Host "🚀 启动数据库服务（Qdrant, PostgreSQL, Redis）..." -ForegroundColor Green
docker-compose up -d

# 等待服务启动
Write-Host "⏳ 等待服务启动（10秒）..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# 初始化数据库
Write-Host "🗄️  初始化数据库..." -ForegroundColor Green
python -c "from database import init_db; init_db()"

# 启动应用
Write-Host "✨ 启动暖洋洋应用..." -ForegroundColor Cyan
Write-Host "📱 访问地址: http://localhost:8000" -ForegroundColor Green
Write-Host ""
python app.py
