@echo off
echo ========================================
echo   识界AI后端服务启动 (生产级配置)
echo ========================================

cd /d "%~dp0"

echo [1/3] 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python 3.11+
    pause
    exit /b 1
)

echo [2/3] 安装依赖...
pip install -r requirements.txt -q

echo [3/3] 启动FastAPI服务 (uvloop加速)...
echo.
echo API文档: http://localhost:8000/docs
echo 健康检查: http://localhost:8000/health
echo.
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

pause
