# 闲鱼自动售货机器人 (XianYu Auto Bot)

🤖 一个功能强大的闲鱼自动化管理工具，支持自动发货、电影票截图检测、自动改价、自动买票等功能。

## ✨ 功能特性

### 核心功能
- 📦 **自动发货** - 支持虚拟商品自动发货，多种发货规则配置
- 🎬 **电影票截图检测** - 自动识别电影票截图，提取观影信息
- 💰 **自动改价** - 根据规则自动修改商品报价
- 🎫 **自动买票** - 自动化电影票购买流程
- 💬 **自动回复** - 智能关键词匹配 + AI 回复
- 📊 **订单管理** - 完整的订单跟踪和管理
- 🔔 **多渠道通知** - 支持飞书、Telegram、企业微信等

### 技术特性
- 🐳 **Docker 部署** - 一键容器化部署
- 🔐 **多账号隔离** - 支持多闲鱼账号独立管理
- 📈 **数据统计** - 销售数据、订单统计分析
- 🔄 **自动重试** - 失败任务自动重试机制
- 🛡️ **安全合规** - 敏感操作二次确认

## 🚀 快速开始

### Docker 部署（推荐）

```bash
# 1. 克隆项目
git clone https://github.com/YOUR_USERNAME/xianyu-auto-bot.git
cd xianyu-auto-bot

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入闲鱼 Cookie 等配置

# 3. 启动服务
docker-compose up -d

# 4. 访问管理界面
# 浏览器打开 http://localhost:8080
```

### 本地部署

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境
cp .env.example .env
# 编辑 .env 文件

# 3. 启动服务
python app/main.py
```

## 📋 配置说明

### 环境变量 (.env)

```bash
# 闲鱼配置
XIANFU_COOKIE=your_cookie_here
XIANFU_DEVICE_ID=your_device_id

# 数据库配置
DATABASE_URL=sqlite:///data/xianyu_bot.db

# 通知配置
FEISHU_WEBHOOK=your_feishu_webhook
TELEGRAM_BOT_TOKEN=your_telegram_token

# AI 配置 (可选)
OPENAI_API_KEY=your_openai_key
OPENAI_MODEL=gpt-3.5-turbo

# 服务配置
SERVER_HOST=0.0.0.0
SERVER_PORT=8080
DEBUG=false
```

## 📁 项目结构

```
xianyu-auto-bot/
├── app/                      # 主应用目录
│   ├── main.py              # 入口文件
│   ├── api/                 # API 路由
│   ├── models/              # 数据模型
│   ├── services/            # 业务服务
│   └── utils/               # 工具函数
├── config/                   # 配置文件
├── data/                     # 数据目录
├── docker/                   # Docker 配置
├── docs/                     # 文档
├── scripts/                  # 脚本工具
├── docker-compose.yml        # Docker Compose 配置
├── Dockerfile               # Docker 镜像构建
├── requirements.txt         # Python 依赖
└── README.md                # 项目说明
```

## 🔧 功能模块

### 1. 自动发货
- 支持多种发货规则（关键词匹配、商品匹配、订单匹配）
- 库存管理，自动扣减
- 发货记录追踪

### 2. 电影票截图检测
- OCR 识别电影票信息
- 自动提取：影片名、时间、座位、票价
- 支持主流购票平台截图

### 3. 自动改价
- 根据时间、库存、竞争价格自动调整
- 支持改价规则配置
- 改价历史记录

### 4. 自动买票
- 自动化选座购票流程
- 支持多影院、多场次
- 购票失败自动重试

## ⚠️ 免责声明

本项目仅供学习交流使用，请勿用于商业目的。使用本项目产生的任何风险由使用者自行承担。

## 📄 许可证

MIT License

## 👥 交流反馈

- GitHub Issues: 提交问题和建议
- 微信群：扫描 README 底部二维码

---

**Made with ❤️ by 易拉罐 for 啤酒瓶**
