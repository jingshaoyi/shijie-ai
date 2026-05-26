#!/bin/bash
echo "========================================"
echo "  识界AI后端服务启动"
echo "========================================"

cd "$(dirname "$0")"

echo "[1/3] 检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未找到Python3，请先安装Python 3.11+"
    exit 1
fi

echo "[2/3] 安装依赖..."
pip3 install -r requirements.txt -q

echo "[3/3] 初始化数据库..."
python3 -m app.init_db

echo "启动FastAPI服务..."
echo "API文档: http://localhost:9090/docs"
echo ""
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 9090 --reload
