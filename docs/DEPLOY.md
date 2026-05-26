# 部署指南

本文档详细介绍如何在生产环境部署识界AI项目。

## 目录

- [环境要求](#环境要求)
- [宝塔面板部署](#宝塔面板部署)
- [Docker部署](#docker部署)
- [Nginx配置](#nginx配置)
- [SSL证书配置](#ssl证书配置)
- [常见问题](#常见问题)

## 环境要求

### 服务器配置
- **操作系统**: CentOS 7+/Ubuntu 18.04+
- **内存**: 2GB+
- **磁盘**: 20GB+
- **Python**: 3.9+
- **Nginx**: 1.18+

### 域名和证书
- 已备案域名（国内服务器）
- SSL证书（推荐Let's Encrypt免费证书）

## 宝塔面板部署

### 1. 安装宝塔面板

```bash
# CentOS
yum install -y wget && wget -O install.sh http://download.bt.cn/install/install_6.0.sh && sh install.sh

# Ubuntu
wget -O install.sh http://download.bt.cn/install/install-ubuntu_6.0.sh && sudo bash install.sh
```

### 2. 安装必要软件

在宝塔面板中安装：
- Python项目管理器 2.0
- Nginx 1.22+
- SQLite（或MySQL/PostgreSQL）

### 3. 上传代码

```bash
# 方式1: Git克隆
cd /www/wwwroot
git clone https://github.com/jingshaoyi/shijie-ai.git

# 方式2: 直接上传压缩包并解压
```

### 4. 配置Python项目

1. 打开宝塔面板 → Python项目管理器
2. 添加项目：
   - 项目路径: `/www/wwwroot/shijie-ai/backend`
   - Python版本: 3.9+
   - 框架: FastAPI
   - 启动方式: Gunicorn
   - 启动文件: `app/main.py`
   - 端口: 9090

3. 安装依赖：
```bash
cd /www/wwwroot/shijie-ai/backend
pip install -r requirements.txt
```

### 5. 配置环境变量

创建 `.env` 文件：

```bash
cd /www/wwwroot/shijie-ai/backend
cp .env.example .env
nano .env
```

编辑内容：
```env
# 应用配置
APP_NAME=识界AI
DEBUG=false
HOST=0.0.0.0
PORT=9090

# 安全密钥（必须修改！）
SECRET_KEY=your-super-secret-key-here

# 数据库（SQLite默认，生产建议PostgreSQL）
DATABASE_URL=sqlite:///data/shijie_ai.db

# AI模型API密钥（至少配置一个）
DASHSCOPE_API_KEY=your-dashscope-api-key
OPENAI_API_KEY=your-openai-api-key
DEEPSEEK_API_KEY=your-deepseek-api-key

# 微信小程序配置
WECHAT_APPID=your-wechat-appid
WECHAT_SECRET=your-wechat-secret

# 文件上传配置
UPLOAD_DIR=uploads
MAX_IMAGE_SIZE=5242880
```

### 6. 初始化数据库

```bash
cd /www/wwwroot/shijie-ai/backend
python -c "from app.database import engine; from app.models import Base; Base.metadata.create_all(bind=engine)"

# 初始化提示词模板
python -c "
from app.database import SessionLocal
from app.services.prompt_service import PromptService
db = SessionLocal()
service = PromptService(db)
service.initialize_default_templates()
db.close()
"
```

### 7. 配置Nginx反向代理

在宝塔面板 → 网站 → 添加站点：
- 域名: `your-domain.com`
- 根目录: `/www/wwwroot/shijie-ai`
- PHP版本: 纯静态

然后配置反向代理：

```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL证书配置
    ssl_certificate /path/to/your/cert.pem;
    ssl_certificate_key /path/to/your/key.pem;

    # 静态文件
    location /uploads/ {
        alias /www/wwwroot/shijie-ai/backend/uploads/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # API代理
    location /api/ {
        proxy_pass http://127.0.0.1:9090/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket支持（如果需要）
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # 前端静态资源（可选，如果使用CDN）
    location / {
        root /www/wwwroot/shijie-ai/frontend/dist/build/h5;
        try_files $uri $uri/ /index.html;
    }
}
```

### 8. 启动服务

在Python项目管理器中启动项目，或命令行：

```bash
cd /www/wwwroot/shijie-ai/backend
gunicorn -c gunicorn.conf.py app.main:app
```

### 9. 配置定时任务

宝塔面板 → 计划任务 → 添加任务：

```bash
# 每天凌晨2点更新提示词模板
/www/server/pyporject_evn/shijieai/bin/python3 /www/wwwroot/shijie-ai/backend/scripts/update_prompts.py
```

## Docker部署

### 1. 构建镜像

```bash
cd /www/wwwroot/shijie-ai
docker-compose build
```

### 2. 启动服务

```bash
docker-compose up -d
```

### 3. 查看日志

```bash
docker-compose logs -f
```

## Nginx配置

### 完整配置示例

```nginx
upstream backend {
    server 127.0.0.1:9090;
    keepalive 32;
}

server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers off;

    # Gzip
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml application/json application/javascript application/rss+xml application/atom+xml image/svg+xml;

    # 上传文件大小限制
    client_max_body_size 10M;

    # 静态文件
    location /uploads/ {
        alias /www/wwwroot/shijie-ai/backend/uploads/;
        expires 30d;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    # API
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # 健康检查
    location /health {
        proxy_pass http://backend/health;
        access_log off;
    }
}
```

## SSL证书配置

### 使用Let's Encrypt

```bash
# 安装Certbot
yum install certbot python3-certbot-nginx

# 申请证书
certbot --nginx -d your-domain.com

# 自动续期
certbot renew --dry-run
```

## 常见问题

### 1. 数据库连接失败

检查数据库文件权限：
```bash
chmod 755 /www/wwwroot/shijie-ai/backend/data
chmod 644 /www/wwwroot/shijie-ai/backend/data/*.db
```

### 2. 上传文件失败

检查上传目录权限：
```bash
chmod 755 /www/wwwroot/shijie-ai/backend/uploads
chown -R www:www /www/wwwroot/shijie-ai/backend/uploads
```

### 3. 提示词模板未初始化

手动执行初始化：
```bash
cd /www/wwwroot/shijie-ai/backend
curl -X POST http://localhost:9090/api/prompts/initialize
```

### 4. 内存不足

添加Swap分区：
```bash
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo '/swapfile none swap sw 0 0' >> /etc/fstab
```

### 5. 服务无法启动

查看日志排查：
```bash
cd /www/wwwroot/shijie-ai/backend
tail -f logs/error.log
```

## 安全建议

1. **修改默认密钥**：务必修改 `SECRET_KEY`
2. **限制API访问**：配置防火墙，仅开放必要端口
3. **定期备份**：定时备份数据库和上传文件
4. **更新依赖**：定期更新Python依赖包
5. **监控告警**：配置服务器监控和告警

## 维护命令

```bash
# 重启服务
cd /www/wwwroot/shijie-ai/backend
pkill -f gunicorn
gunicorn -c gunicorn.conf.py app.main:app

# 查看日志
tail -f logs/app.log

# 数据库备份
cp data/shijie_ai.db backups/shijie_ai_$(date +%Y%m%d).db

# 清理缓存
python -c "
from app.database import SessionLocal
from app.services.prompt_service import PromptService
db = SessionLocal()
service = PromptService(db)
service.clear_expired_cache()
db.close()
"
```

---

如有其他问题，请提交 [GitHub Issue](https://github.com/jingshaoyi/shijie-ai/issues)。
