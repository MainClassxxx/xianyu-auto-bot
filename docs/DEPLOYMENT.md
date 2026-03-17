# 闲鱼自动机器人 - 部署指南

**版本**: v3.0  
**最后更新**: 2026-03-17  
**适用环境**: Development / Testing / Production

---

## 📋 目录

1. [环境要求](#环境要求)
2. [开发环境部署](#开发环境部署)
3. [生产环境部署](#生产环境部署)
4. [Docker 部署](#docker-部署)
5. [Kubernetes 部署](#kubernetes-部署)
6. [配置说明](#配置说明)
7. [常见问题](#常见问题)

---

## 环境要求

### 硬件要求

| 环境 | CPU | 内存 | 磁盘 |
|------|-----|------|------|
| 开发 | 2 核 | 4GB | 10GB |
| 测试 | 4 核 | 8GB | 20GB |
| 生产 | 8 核 + | 16GB+ | 100GB+ |

### 软件要求

- **Python**: 3.11+
- **Node.js**: 18+ (前端)
- **数据库**: SQLite (开发) / PostgreSQL 14+ (生产)
- **Redis**: 6+ (可选，用于缓存和队列)
- **Docker**: 20+ (可选)
- **Docker Compose**: 2.0+ (可选)

---

## 开发环境部署

### 1. 克隆项目

```bash
git clone https://github.com/MainClassxxx/xianyu-auto-bot.git
cd xianyu-auto-bot
```

### 2. 创建虚拟环境

```bash
# Python 虚拟环境
python3.11 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 开发依赖
```

### 3. 前端依赖

```bash
cd frontend
npm install
cd ..
```

### 4. 配置环境变量

```bash
cp .env.example .env
nano .env  # 编辑配置
```

**最小配置**:
```ini
# 环境
ENVIRONMENT=development
DEBUG=true

# 数据库
DATABASE_URL=sqlite:///./data/xianyu_bot.db

# 服务
SERVER_HOST=0.0.0.0
SERVER_PORT=8080

# 闲鱼 Cookie (从浏览器获取)
XIANFU_COOKIE=your_cookie_here
```

### 5. 初始化数据库

```bash
python -c "from app.db import init_db; init_db()"
```

### 6. 启动服务

```bash
# 后端
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080

# 前端 (新终端)
cd frontend
npm run dev
```

### 7. 访问应用

- **后端 API**: http://localhost:8080
- **API 文档**: http://localhost:8080/docs
- **前端界面**: http://localhost:3000

---

## 生产环境部署

### 1. 系统准备

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装依赖
sudo apt install -y python3.11 python3.11-venv python3-pip nginx postgresql redis-server

# 创建用户
sudo useradd -m -s /bin/bash xianyu
sudo su - xianyu
```

### 2. 项目部署

```bash
# 克隆项目
git clone https://github.com/MainClassxxx/xianyu-auto-bot.git
cd xianyu-auto-bot

# 创建虚拟环境
python3.11 -m venv .venv
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 数据库配置

```bash
# 创建 PostgreSQL 数据库
sudo -u postgres psql
CREATE DATABASE xianyu_bot;
CREATE USER xianyu WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE xianyu_bot TO xianyu;
\q
```

**更新 .env**:
```ini
DATABASE_URL=postgresql://xianyu:your_password@localhost:5432/xianyu_bot
```

### 4. 配置 systemd 服务

```bash
sudo nano /etc/systemd/system/xianyu-bot.service
```

**服务内容**:
```ini
[Unit]
Description=Xianyu Auto Bot
After=network.target postgresql.service redis.service

[Service]
Type=notify
User=xianyu
Group=xianyu
WorkingDirectory=/home/xianyu/xianyu-auto-bot
Environment="PATH=/home/xianyu/xianyu-auto-bot/.venv/bin"
ExecStart=/home/xianyu/xianyu-auto-bot/.venv/bin/uvicorn app.main:app --workers 4 --host 0.0.0.0 --port 8080
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# 安全配置
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

**启动服务**:
```bash
sudo systemctl daemon-reload
sudo systemctl enable xianyu-bot
sudo systemctl start xianyu-bot
sudo systemctl status xianyu-bot
```

### 5. Nginx 配置

```bash
sudo nano /etc/nginx/sites-available/xianyu-bot
```

**Nginx 配置**:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 后端 API
    location /api {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_read_timeout 60s;
    }

    # 前端静态文件
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # 静态资源缓存
    location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

**启用配置**:
```bash
sudo ln -s /etc/nginx/sites-available/xianyu-bot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 6. SSL 证书 (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

---

## Docker 部署

### 1. 构建镜像

```bash
docker build -t xianyu-auto-bot:latest .
```

### 2. Docker Compose

**docker-compose.yml**:
```yaml
version: '3.8'

services:
  backend:
    image: xianyu-auto-bot:latest
    container_name: xianyu-backend
    restart: always
    environment:
      - DATABASE_URL=postgresql://xianyu:password@db:5432/xianyu_bot
      - REDIS_URL=redis://redis:6379
      - ENVIRONMENT=production
    volumes:
      - ./data:/app/data
      - ./.cookies:/app/.cookies
    depends_on:
      - db
      - redis
    networks:
      - xianyu-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: xianyu-frontend
    restart: always
    depends_on:
      - backend
    networks:
      - xianyu-network

  db:
    image: postgres:14-alpine
    container_name: xianyu-db
    restart: always
    environment:
      - POSTGRES_DB=xianyu_bot
      - POSTGRES_USER=xianyu
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - xianyu-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U xianyu"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:6-alpine
    container_name: xianyu-redis
    restart: always
    volumes:
      - redis-data:/data
    networks:
      - xianyu-network

  nginx:
    image: nginx:alpine
    container_name: xianyu-nginx
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - backend
      - frontend
    networks:
      - xianyu-network

volumes:
  postgres-data:
  redis-data:

networks:
  xianyu-network:
    driver: bridge
```

### 3. 启动服务

```bash
docker-compose up -d
docker-compose ps
docker-compose logs -f
```

---

## Kubernetes 部署

### 1. 创建命名空间

```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: xianyu-bot
```

### 2. 配置 ConfigMap

```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: xianyu-config
  namespace: xianyu-bot
data:
  ENVIRONMENT: "production"
  DEBUG: "false"
  LOG_LEVEL: "INFO"
```

### 3. 配置 Secret

```yaml
# secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: xianyu-secret
  namespace: xianyu-bot
type: Opaque
stringData:
  DATABASE_URL: "postgresql://user:pass@db:5432/xianyu_bot"
  JWT_SECRET_KEY: "your-secret-key"
  XIANFU_COOKIE: "your-cookie"
```

### 4. 部署应用

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: xianyu-backend
  namespace: xianyu-bot
spec:
  replicas: 3
  selector:
    matchLabels:
      app: xianyu-backend
  template:
    metadata:
      labels:
        app: xianyu-backend
    spec:
      containers:
      - name: backend
        image: xianyu-auto-bot:latest
        ports:
        - containerPort: 8080
        envFrom:
        - configMapRef:
            name: xianyu-config
        - secretRef:
            name: xianyu-secret
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
```

### 5. 部署

```bash
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f secret.yaml
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
```

---

## 配置说明

### 环境变量详解

| 变量 | 说明 | 默认值 | 必填 |
|------|------|--------|------|
| `ENVIRONMENT` | 运行环境 | development | 是 |
| `DEBUG` | 调试模式 | false | 否 |
| `DATABASE_URL` | 数据库 URL | sqlite:///./data/xianyu_bot.db | 是 |
| `SERVER_HOST` | 服务地址 | 0.0.0.0 | 否 |
| `SERVER_PORT` | 服务端口 | 8080 | 否 |
| `XIANFU_COOKIE` | 闲鱼 Cookie | - | 是 |
| `JWT_SECRET_KEY` | JWT 密钥 | - | 是 |
| `FEISHU_WEBHOOK` | 飞书 Webhook | - | 否 |

### Cookie 获取方法

1. 浏览器打开闲鱼网页版
2. F12 打开开发者工具
3. Network 标签页
4. 复制请求中的 Cookie

---

## 常见问题

### Q1: 数据库连接失败

**解决**:
```bash
# 检查数据库服务
sudo systemctl status postgresql

# 检查连接字符串
echo $DATABASE_URL

# 测试连接
psql $DATABASE_URL
```

### Q2: Cookie 过期

**解决**:
1. 重新登录闲鱼网页版
2. 复制新的 Cookie
3. 更新 .env 文件
4. 重启服务

### Q3: 端口被占用

**解决**:
```bash
# 查看端口占用
lsof -i :8080

# 修改端口
export SERVER_PORT=8081
```

### Q4: 内存不足

**解决**:
```bash
# 限制工作进程数
WORKERS=2

# 添加 Swap
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

## 监控与维护

### 日志查看

```bash
# systemd 日志
journalctl -u xianyu-bot -f

# Docker 日志
docker-compose logs -f backend

# 应用日志
tail -f data/bot.log
```

### 备份数据

```bash
# SQLite 备份
cp data/xianyu_bot.db data/xianyu_bot.db.backup

# PostgreSQL 备份
pg_dump $DATABASE_URL > backup.sql

# 定时备份 (cron)
0 2 * * * /path/to/backup.sh
```

### 健康检查

```bash
# API 健康检查
curl http://localhost:8080/health

# 数据库连接
python -c "from app.db import SessionLocal; SessionLocal().execute('SELECT 1')"

# Cookie 有效性
python -c "from app.services.xianyu_api import xianyu_manager; print(xianyu_manager.test_all_connections())"
```

---

**🥫 部署完成后，访问 API 文档开始使用！**
