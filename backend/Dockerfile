FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

# 安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir uvloop==0.20.0 && \
    pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建数据目录
RUN mkdir -p /app/data

# 暴露端口
EXPOSE 9090

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "9090"]
