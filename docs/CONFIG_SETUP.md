# ⚙️ 飞书配置说明

## 📋 配置飞书 Webhook

### 1. 创建飞书机器人

1. 打开飞书，进入任意群聊
2. 点击右上角设置 → 群机器人
3. 添加机器人 → 自定义机器人
4. 填写机器人名称：`闲鱼机器人进度助手`
5. 复制 Webhook 地址

### 2. 配置 Webhook

编辑配置文件 `app/config.py`（需要创建）：

```python
# 飞书 Webhook
FEISHU_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_WEBHOOK_HERE"
```

或者直接在代码中修改：

```python
# app/services/hourly_report.py
FEISHU_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/你的实际_WEBHOOK"
```

### 3. 测试发送

启动服务后，系统会每小时自动发送进度报告。

**手动测试**:
```bash
curl -X POST "http://localhost:8080/api/admin/send-report" \
  -H "Content-Type: application/json" \
  -d '{"test": true}'
```

---

## 🔐 超级管理员配置

创建配置文件 `config.json`：

```json
{
  "auth": {
    "superAdmin": {
      "username": "admin",
      "password": "admin123"
    }
  },
  "database": {
    "url": "sqlite:///./data/xianyu_bot.db"
  },
  "jwt": {
    "secret_key": "your-secret-key-change-in-production",
    "expire_minutes": 10080
  }
}
```

**⚠️ 重要**:
- 首次启动后请修改默认密码！
- 生产环境请修改 secret_key！

---

## 📊 进度汇报格式

**每小时整点发送**，包含：

- 📈 当前进度百分比
- ✅ 已完成任务数
- 🎯 当前任务
- 📅 项目日期信息
- 🔗 项目链接

**示例**:
```
🚀 闲鱼机器人开发进度 - Day 1

当前进度：5.4% (5/93)
███████░░░░░░░░░░░░░ 5%

当前任务：开发登录注册前端页面

─────────────────────
📅 开始日期：2026-03-10
🎯 目标日期：2026-03-17
⏰ 汇报时间：2026-03-10 18:00:00

[查看项目]
```

---

## 🎨 前端风格配置

**简约浅色系 + 可爱卡通**

编辑 `frontend/src/assets/styles/variables.css`：

```css
:root {
  /* 主色调 - 浅粉色 */
  --primary-color: #FFB6C1;
  --primary-light: #FFC0CB;
  --primary-dark: #FF69B4;
  
  /* 辅助色 - 浅蓝色 */
  --secondary-color: #87CEEB;
  --secondary-light: #B0E0F6;
  --secondary-dark: #4682B4;
  
  /* 成功 - 浅绿色 */
  --success-color: #98FB98;
  
  /* 警告 - 浅橙色 */
  --warning-color: #FFE4B5;
  
  /* 危险 - 粉红色 */
  --danger-color: #FFC0CB;
  
  /* 背景 */
  --background-color: #F5F7FA;
  --card-background: #FFFFFF;
  
  /* 文字 */
  --text-primary: #606266;
  --text-secondary: #909399;
  --text-placeholder: #C0C4CC;
  
  /* 边框 */
  --border-color: #E6E6E6;
  
  /* 圆角 */
  --border-radius-small: 8px;
  --border-radius-base: 12px;
  --border-radius-large: 16px;
  
  /* 阴影 */
  --box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  --box-shadow-light: 0 1px 4px 0 rgba(0, 0, 0, 0.05);
  
  /* 动画 */
  --transition-base: all 0.3s ease;
  --transition-fast: all 0.2s ease;
  --transition-slow: all 0.5s ease;
}
```

---

## 📝 下一步

1. **配置飞书 Webhook**
2. **创建 config.json**
3. **重启服务**
4. **测试飞书消息**

---

**Created**: 2026-03-10  
**By**: 易拉罐 🥫
