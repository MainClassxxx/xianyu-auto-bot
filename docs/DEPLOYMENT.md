# 闲鱼自动售货机器人 - 部署文档

## 🐳 Docker 部署

### 快速部署

```bash
# 1. 克隆项目
git clone https://github.com/YOUR_USERNAME/xianyu-auto-bot.git
cd xianyu-auto-bot

# 2. 配置环境
cp .env.example .env
# 编辑 .env，至少配置 XIANFU_COOKIE

# 3. 一键启动
docker-compose up -d

# 4. 查看状态
docker-compose ps

# 5. 查看日志
docker-compose logs -f xianyu-bot
```

### Docker 命令参考

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 查看日志
docker-compose logs -f

# 进入容器
docker-compose exec xianyu-bot bash

# 重建镜像
docker-compose build --no-cache

# 更新服务
docker-compose pull
docker-compose up -d
```

### 数据持久化

项目使用 volume 挂载以下目录：

- `./data` - 数据库和日志
- `./config` - 配置文件
- `./logs` - 日志文件

这些目录在宿主机上，容器删除后数据不会丢失。

---

## 🖥️ 本地部署

### macOS / Linux

```bash
# 1. 初始化项目
./scripts/init.sh

# 2. 配置环境
nano .env

# 3. 启动服务
./scripts/start.sh

# 或使用 Python 直接启动
python3 app/main.py
```

### Windows

```powershell
# 1. 安装依赖
pip install -r requirements.txt

# 2. 安装 Playwright
playwright install

# 3. 配置环境
copy .env.example .env
# 编辑 .env

# 4. 启动服务
python app/main.py
```

---

## 🔧 配置说明

### 必需配置

```bash
# 闲鱼 Cookie (必需)
XIANFU_COOKIE=your_cookie_here
```

### 可选配置

```bash
# 数据库
DATABASE_URL=sqlite:///data/xianyu_bot.db

# 通知
FEISHU_WEBHOOK=
TELEGRAM_BOT_TOKEN=

# AI
OPENAI_API_KEY=

# OCR
BAIDU_OCR_API_KEY=
BAIDU_OCR_SECRET_KEY=

# 功能开关
AUTO_DELIVERY_ENABLED=true
AUTO_PRICE_UPDATE_ENABLED=true
AUTO_BUY_TICKET_ENABLED=true
SCREENSHOT_DETECTION_ENABLED=true
```

---

## 📊 监控和维护

### 健康检查

```bash
# 检查服务状态
curl http://localhost:8080/health

# 查看系统状态
curl http://localhost:8080/api/status
```

### 日志管理

```bash
# Docker 部署查看日志
docker-compose logs -f

# 本地部署查看日志
tail -f data/bot.log

# 日志轮转
# 日志文件超过 10MB 自动轮转，保留 7 天
```

### 数据备份

```bash
# 备份数据库
cp data/xianyu_bot.db data/xianyu_bot.db.backup.$(date +%Y%m%d)

# 备份配置
tar -czf config.backup.$(date +%Y%m%d).tar.gz config/ .env
```

---

## 🔄 更新升级

### Docker 部署更新

```bash
# 1. 拉取最新代码
git pull

# 2. 重建镜像
docker-compose build

# 3. 重启服务
docker-compose up -d
```

### 本地部署更新

```bash
# 1. 拉取最新代码
git pull

# 2. 更新依赖
pip install -r requirements.txt --upgrade

# 3. 重启服务
# 先停止当前服务 (Ctrl+C)
# 然后重新启动
python app/main.py
```

---

## ⚠️ 注意事项

1. **Cookie 有效期**：闲鱼 Cookie 会过期，定期检查更新
2. **网络稳定性**：确保服务器网络稳定，避免断线
3. **资源占用**：建议至少 1GB 内存
4. **安全配置**：生产环境建议配置防火墙
5. **合规使用**：遵守闲鱼平台规则，避免违规操作

---

## 🆘 故障排查

### 常见问题

**1. 服务启动失败**
```bash
# 查看详细错误
docker-compose logs xianyu-bot

# 检查端口占用
lsof -i :8080
```

**2. 闲鱼连接失败**
- 检查 Cookie 是否过期
- 检查网络连接
- 查看日志中的详细错误

**3. 数据库错误**
```bash
# 检查权限
ls -la data/

# 重建数据库
rm data/xianyu_bot.db
python app/main.py
```

**4. OCR 识别失败**
- 确保截图清晰
- 检查 OCR API 配置
- 查看日志中的识别结果

---

## 📞 获取帮助

- **API 文档**: http://localhost:8080/docs
- **GitHub Issues**: 提交问题和建议
- **项目日志**: data/bot.log

---

**Last Updated**: 2024-03-10
