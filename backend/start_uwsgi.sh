#!/bin/bash
# ========================================
# 识界AI后端服务启动 - uWSGI方式
# ========================================
# uWSGI是高性能WSGI服务器，功能丰富
# 特点：支持多种协议、高度可配置、性能优秀

cd "$(dirname "$0")"

echo "[1/3] 检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未找到Python3，请先安装Python 3.11+"
    exit 1
fi

echo "[2/3] 安装依赖..."
pip3 install -r requirements.txt -q
pip3 install uwsgi -q

echo "[3/3] 初始化数据库..."
python3 -m app.init_db

echo "启动uWSGI服务..."
echo "API文档: http://localhost:9090/docs"
echo ""

# 启动配置说明：
# --http 0.0.0.0:9090: HTTP模式，监听所有IP，端口9090
# --wsgi-file app/main.py: 入口文件
# --callable app: FastAPI应用实例
# --processes 4: 4个工作进程
# --threads 2: 每个进程2个线程
# --master: 启用主进程管理
# --die-on-term: 收到SIGTERM时优雅退出
# --reload: 开发模式自动重载(生产环境请去掉)

uwsgi --http 0.0.0.0:9090 \
    --module app.main:app \
    --processes 4 \
    --threads 2 \
    --master \
    --die-on-term \
    --reload
