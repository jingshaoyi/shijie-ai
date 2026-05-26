#!/bin/bash
# ========================================
# 识界AI后端服务启动 - Gunicorn方式 (生产环境推荐)
# ========================================
# Gunicorn是WSGI HTTP服务器，性能更好，适合生产环境
# 特点：多进程、自动重启、负载均衡

cd "$(dirname "$0")"

echo "[1/3] 检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未找到Python3，请先安装Python 3.11+"
    exit 1
fi

echo "[2/3] 安装依赖..."
pip3 install -r requirements.txt -q
pip3 install gunicorn -q

echo "[3/3] 初始化数据库..."
python3 -m app.init_db

echo "启动Gunicorn服务..."
echo "API文档: http://localhost:9090/docs"
echo ""

# 启动配置说明：
# -w 4: 4个工作进程 (建议: 2 * CPU核心数 + 1)
# -k uvicorn.workers.UvicornWorker: 使用Uvicorn worker处理异步请求
# -b 0.0.0.0:9090: 绑定所有IP，端口9090
# --access-logfile -: 访问日志输出到stdout
# --error-logfile -: 错误日志输出到stdout
# --reload: 开发模式自动重载(生产环境请去掉)

gunicorn app.main:app \
    -w 4 \
    -k uvicorn.workers.UvicornWorker \
    -b 0.0.0.0:9090 \
    --access-logfile - \
    --error-logfile - \
    --reload
