# 闲鱼自动售货机器人 - 使用文档

## 📖 快速开始指南

### 1. 环境准备

**系统要求：**
- Python 3.11+
- Docker 20.10+ (可选，用于容器化部署)
- 闲鱼账号

**获取闲鱼 Cookie：**
1. 浏览器访问 https://goofish.com
2. 登录你的闲鱼账号
3. 按 F12 打开开发者工具
4. 切换到 Network 标签
5. 刷新页面，找到任意请求
6. 复制 Request Headers 中的 Cookie 值

### 2. Docker 部署（推荐）

```bash
# 1. 克隆项目
git clone https://github.com/YOUR_USERNAME/xianyu-auto-bot.git
cd xianyu-auto-bot

# 2. 配置环境变量
cp .env.example .env
nano .env  # 编辑配置文件

# 3. 启动服务
docker-compose up -d

# 4. 查看日志
docker-compose logs -f

# 5. 访问管理界面
# 浏览器打开 http://localhost:8080/docs
```

### 3. 本地部署

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 安装 Playwright (用于自动买票)
playwright install

# 3. 配置环境
cp .env.example .env
# 编辑 .env 文件

# 4. 启动服务
python app/main.py

# 5. 访问 API 文档
# 浏览器打开 http://localhost:8080/docs
```

---

## 🔧 功能配置

### 自动发货配置

在 `.env` 文件中配置：

```bash
AUTO_DELIVERY_ENABLED=true
```

**添加发货规则：**

1. 访问 `http://localhost:8080/docs`
2. 找到 `POST /api/delivery/rules`
3. 填写规则信息：
   ```json
   {
     "name": "虚拟商品自动发货",
     "keyword": "教程",
     "delivery_content": "这是您的教程链接：https://example.com/download",
     "enabled": true
   }
   ```

### 电影票检测配置

**启用截图检测：**

```bash
SCREENSHOT_DETECTION_ENABLED=true
```

**配置 OCR（可选，使用百度 OCR）：**

```bash
BAIDU_OCR_API_KEY=your_api_key
BAIDU_OCR_SECRET_KEY=your_secret_key
```

**使用示例：**

```bash
# 上传图片检测
curl -X POST "http://localhost:8080/api/ticket/detect" \
  -H "Content-Type: application/json" \
  -d '{"image_url": "https://example.com/ticket.jpg"}'
```

### 自动改价配置

**启用自动改价：**

```bash
AUTO_PRICE_UPDATE_ENABLED=true
```

**添加改价规则：**

```json
{
  "item_id": "item_123",
  "min_price": 10.0,
  "max_price": 100.0,
  "adjust_percent": -5.0
}
```

### 自动买票配置

**启用自动买票：**

```bash
AUTO_BUY_TICKET_ENABLED=true
```

**使用示例：**

```bash
curl -X POST "http://localhost:8080/api/ticket/buy" \
  -H "Content-Type: application/json" \
  -d '{
    "movie_name": "流浪地球 2",
    "cinema_name": "万达影城",
    "show_time": "2024-03-10 19:30",
    "seat_info": "8 排 9 座"
  }'
```

---

## 📊 API 使用指南

### 查看 API 文档

启动服务后访问：`http://localhost:8080/docs`

这是 FastAPI 自动生成的交互式 API 文档，可以在线测试所有接口。

### 常用 API

#### 1. 健康检查
```bash
GET http://localhost:8080/health
```

#### 2. 获取系统状态
```bash
GET http://localhost:8080/api/status
```

#### 3. 获取发货规则
```bash
GET http://localhost:8080/api/delivery/rules
```

#### 4. 创建发货规则
```bash
POST http://localhost:8080/api/delivery/rules
Content-Type: application/json

{
  "name": "规则名称",
  "keyword": "关键词",
  "delivery_content": "发货内容",
  "enabled": true
}
```

#### 5. 检测电影票
```bash
POST http://localhost:8080/api/ticket/detect?image_url=图片 URL
```

---

## 🔔 通知配置

### 飞书通知

1. 在飞书群聊中添加机器人
2. 获取 Webhook URL
3. 在 `.env` 中配置：
   ```bash
   FEISHU_WEBHOOK=https://open.feishu.cn/open-apis/bot/v2/hook/xxx
   ```

### Telegram 通知

1. 联系 @BotFather 创建机器人
2. 获取 Bot Token
3. 在 `.env` 中配置：
   ```bash
   TELEGRAM_BOT_TOKEN=your_bot_token
   ```

---

## 🛠️ 故障排查

### 服务无法启动

**检查日志：**
```bash
docker-compose logs xianyu-bot
```

**常见问题：**
1. 端口被占用：修改 `.env` 中的 `SERVER_PORT`
2. 数据库权限：确保 `data/` 目录可写
3. 依赖缺失：运行 `pip install -r requirements.txt`

### 闲鱼连接失败

1. 检查 Cookie 是否过期（重新获取）
2. 检查网络连接
3. 查看日志中的详细错误信息

### 电影票检测不准确

1. 确保截图清晰
2. 调整截图角度（正面拍摄）
3. 考虑使用付费 OCR 服务（百度/腾讯）

---

## 📝 更新日志

### v1.0.0 (2024-03-10)
- ✨ 初始版本发布
- 📦 自动发货功能
- 🎬 电影票截图检测
- 💰 自动改价
- 🎫 自动买票
- 🐳 Docker 部署支持

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

---

## 📄 许可证

MIT License

---

## 👥 联系方式

- **作者**: 易拉罐
- **项目发起**: 啤酒瓶
- **GitHub**: https://github.com/YOUR_USERNAME/xianyu-auto-bot

**Made with ❤️**
