# 闲鱼自动售货机器人 (XianYu Auto Bot) v2.0

🤖 **参考 FishAutoPro 完整功能实现的闲鱼自动化管理工具**

![GitHub stars](https://img.shields.io/github/stars/MainClassxxx/xianyu-auto-bot)
![GitHub forks](https://img.shields.io/github/forks/MainClassxxx/xianyu-auto-bot)
![GitHub license](https://img.shields.io/github/license/MainClassxxx/xianyu-auto-bot)
![Python](https://img.shields.io/badge/python-3.11-blue)
![Docker](https://img.shields.io/badge/docker-latest-blue)

---

## ✨ 核心功能

### 📦 账号管理
- ✅ 多账号支持
- ✅ Cookie 管理
- ✅ 账号状态监控
- ✅ 账号隔离

### 🛍️ 商品管理
- ✅ 商品列表
- ✅ 商品上下架
- ✅ 价格修改
- ✅ 自动改价规则

### 📋 订单管理
- ✅ 订单列表
- ✅ 状态同步
- ✅ 自动发货
- ✅ 发货记录

### 💬 对话消息
- ✅ 实时消息
- ✅ 自动回复
- ✅ 图片发送
- ✅ 会话管理

### 🤖 自动化功能
- ✅ 自动回复（关键词/AI）
- ✅ 自动发货（多规格/库存）
- ✅ 自动评价
- ✅ 自动免拼

### 📊 数据统计
- ✅ 订单统计
- ✅ 收入统计
- ✅ 消息统计
- ✅ 数据导出

### 🔔 通知系统
- ✅ 飞书通知
- ✅ Telegram 通知
- ✅ 企业微信
- ✅ 钉钉通知
- ✅ Bark 推送
- ✅ Email 通知

### 🐳 部署支持
- ✅ Docker 部署
- ✅ Docker Compose
- ✅ 一键启动
- ✅ 数据持久化

---

## 🚀 快速开始

### Docker 部署（推荐）

```bash
# 1. 克隆项目
git clone https://github.com/MainClassxxx/xianyu-auto-bot.git
cd xianyu-auto-bot

# 2. 配置环境变量
cp .env.example .env
nano .env  # 编辑配置

# 3. 一键启动
docker-compose up -d

# 4. 查看日志
docker-compose logs -f

# 5. 访问管理界面
# http://localhost:8080/docs
```

### 本地部署

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境
cp .env.example .env

# 3. 启动服务
python app/main.py
```

---

## 📖 API 文档

启动服务后访问：

- **Swagger UI**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc
- **OpenAPI JSON**: http://localhost:8080/openapi.json

### 主要 API 端点

| 端点 | 说明 |
|------|------|
| `/api/accounts` | 账号管理 |
| `/api/items` | 商品管理 |
| `/api/orders` | 订单管理 |
| `/api/conversations` | 对话消息 |
| `/api/auto-reply` | 自动回复 |
| `/api/auto-delivery` | 自动发货 |
| `/api/notifications` | 通知管理 |
| `/api/stats` | 数据统计 |

---

## 🔧 配置说明

### 环境变量 (.env)

```bash
# 闲鱼配置
XIANFU_COOKIE=your_cookie_here
XIANFU_DEVICE_ID=device_001

# 数据库
DATABASE_URL=sqlite:///data/xianyu_bot.db

# 通知配置
FEISHU_WEBHOOK=
TELEGRAM_BOT_TOKEN=
WECHAT_WORK_WEBHOOK=
DINGTALK_WEBHOOK=

# AI 配置
OPENAI_API_KEY=
OPENAI_MODEL=gpt-3.5-turbo

# 服务配置
SERVER_HOST=0.0.0.0
SERVER_PORT=8080
DEBUG=false
```

---

## 📁 项目结构

```
xianyu-auto-bot/
├── app/
│   ├── main.py                    # FastAPI 入口
│   ├── api/                       # API 路由
│   │   ├── accounts.py            # 账号管理
│   │   ├── items.py               # 商品管理
│   │   ├── orders.py              # 订单管理
│   │   ├── conversations.py       # 对话消息
│   │   ├── auto_reply.py          # 自动回复
│   │   ├── auto_delivery.py       # 自动发货
│   │   ├── notifications.py       # 通知管理
│   │   └── stats.py               # 数据统计
│   ├── models/                    # 数据模型
│   ├── services/                  # 业务服务
│   └── utils/                     # 工具函数
├── .github/
│   ├── workflows/                 # GitHub Actions
│   └── dependabot.yml             # 依赖自动更新
├── docker/
├── docs/
├── scripts/
├── data/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🔄 自动维护

### GitHub Actions

- ✅ CI/CD 流水线
- ✅ 自动测试
- ✅ Docker 镜像构建
- ✅ 自动发布

### Dependabot

- ✅ 每周自动更新 Python 依赖
- ✅ 每周自动更新 Docker 镜像
- ✅ 每周自动更新 GitHub Actions

### 自动合并

- ✅ Dependabot PR 自动合并（minor 版本）
- ✅ 代码检查通过后自动合并

---

## 📊 开发进度

参考 [PROJECT.md](PROJECT.md) 查看完整开发计划。

### 已完成
- [x] 项目初始化
- [x] 基础架构
- [x] API 路由设计
- [x] 数据模型设计
- [x] GitHub Actions 配置
- [x] Docker 部署支持

### 进行中
- [ ] 闲鱼 API 客户端实现
- [ ] 数据库集成
- [ ] 自动回复逻辑
- [ ] 自动发货逻辑

### 计划中
- [ ] 前端管理界面
- [ ] AI 知识库
- [ ] 可视化流程编辑
- [ ] 移动端适配

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

- **GitHub**: https://github.com/MainClassxxx/xianyu-auto-bot
- **Issues**: https://github.com/MainClassxxx/xianyu-auto-bot/issues

---

## 🙏 致谢

- 参考项目：[FishAutoPro](https://xueandyue.github.io/FishAutoPro/)
- 灵感来源：闲鱼自动化管理需求

---

**Made with ❤️ by 易拉罐 for 啤酒瓶**

**Last Updated**: 2024-03-10
