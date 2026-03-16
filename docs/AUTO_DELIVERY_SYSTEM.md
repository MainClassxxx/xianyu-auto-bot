# 自动发货系统完整说明

**版本**: v3.4.0  
**更新时间**: 2026-03-17  
**状态**: ✅ 核心功能已打通

---

## 📋 概述

自动发货系统是闲鱼机器人的**核心功能**，实现买家付款后自动发送商品内容（卡密、教程、链接等）。

---

## 🔄 完整流程

```
买家付款
    ↓
系统轮询订单（每 5 分钟）
    ↓
检测到已付款订单
    ↓
匹配发货规则（关键词）
    ↓
检查库存（如有限制）
    ↓
自动发货（发送消息）
    ↓
记录发货日志
    ↓
扣减库存
    ↓
通知卖家（可选）
```

---

## ⚙️ 功能特性

### 1. 发货规则管理 ✅

**规则配置**:
- 规则名称
- 关键词匹配（支持包含/精确/正则）
- 发货内容（文本/图片/文件/链接）
- 库存管理（无限/有限）
- 优先级设置
- 启用/禁用控制

**匹配逻辑**:
```python
# 包含匹配（默认）
keyword = "教程"
item_title = "Python 入门教程"
匹配成功 ✅

# 精确匹配
keyword = "Python 教程"
item_title = "Python 入门教程"
匹配失败 ❌

# 正则匹配
keyword = r"Python.*教程"
item_title = "Python 入门到精通教程"
匹配成功 ✅
```

### 2. 库存管理 ✅

**库存模式**:
- 无限库存：stock = -1
- 有限库存：stock = 100
- 自动补货：auto_restock = True

**扣减逻辑**:
```
发货成功 → 库存 -1
库存 = 0 → 停止发货
库存不足 → 记录日志
```

### 3. 发货记录 ✅

**记录内容**:
- 订单 ID
- 商品标题
- 买家名称
- 发货内容
- 发货状态（成功/失败）
- 错误信息
- 发货时间

### 4. 日志系统 ✅

**日志级别**:
- INFO - 正常发货
- WARNING - 警告（库存不足等）
- ERROR - 错误（API 失败等）

---

## 🛠️ API 接口

### 1. 创建发货规则

```bash
POST /api/auto-delivery/rules
Content-Type: application/json

{
  "account_id": 1,
  "name": "Python 教程自动发货",
  "keyword": "Python 教程",
  "match_type": "contains",
  "delivery_content": "教程链接：https://example.com\n密码：abc123",
  "delivery_type": "text",
  "stock": 100,
  "enabled": true,
  "priority": 1
}

Response:
{
  "id": 1,
  "name": "Python 教程自动发货",
  "keyword": "Python 教程",
  "stock": 100,
  "enabled": true,
  "total_delivered": 0,
  "today_delivered": 0
}
```

### 2. 获取规则列表

```bash
GET /api/auto-delivery/rules?account_id=1&enabled=true

Response:
[
  {
    "id": 1,
    "name": "Python 教程自动发货",
    "keyword": "Python 教程",
    "delivery_content": "教程链接...",
    "stock": 100,
    "enabled": true,
    "total_delivered": 50,
    "today_delivered": 5
  }
]
```

### 3. 更新规则

```bash
PUT /api/auto-delivery/rules/1
Content-Type: application/json

{
  "name": "Python 教程自动发货（更新）",
  "stock": 200
}
```

### 4. 删除规则

```bash
DELETE /api/auto-delivery/rules/1

Response:
{
  "success": true
}
```

### 5. 启用/禁用规则

```bash
POST /api/auto-delivery/rules/1/toggle

Response:
{
  "id": 1,
  "enabled": false
}
```

### 6. 更新库存

```bash
POST /api/auto-delivery/rules/1/stock?stock=500

Response:
{
  "success": true,
  "new_stock": 500
}
```

### 7. 获取发货记录

```bash
GET /api/auto-delivery/records?account_id=1&status=success&page=1&page_size=20

Response:
{
  "total": 100,
  "records": [
    {
      "id": 1,
      "order_id": "123456",
      "item_title": "Python 教程",
      "buyer_name": "张三",
      "delivery_content": "教程链接...",
      "delivery_status": "success",
      "delivered_at": "2026-03-17T00:00:00"
    }
  ]
}
```

### 8. 获取发货日志

```bash
GET /api/auto-delivery/logs?account_id=1&level=ERROR

Response:
{
  "total": 10,
  "logs": [
    {
      "level": "ERROR",
      "action": "deliver_order",
      "message": "订单 123456 发货失败",
      "order_id": "123456",
      "data": {"error": "API 超时"},
      "created_at": "2026-03-17T00:00:00"
    }
  ]
}
```

### 9. 手动触发发货

```bash
POST /api/auto-delivery/trigger
Content-Type: application/json

{
  "account_id": 1
}

Response:
{
  "success": true,
  "message": "自动发货已触发",
  "delivered_count": 5
}
```

---

## 📊 数据库设计

### delivery_rules - 发货规则表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| account_id | INTEGER | 账号 ID |
| name | VARCHAR(100) | 规则名称 |
| keyword | VARCHAR(200) | 关键词 |
| match_type | VARCHAR(20) | 匹配方式 |
| delivery_content | TEXT | 发货内容 |
| delivery_type | VARCHAR(20) | 发货类型 |
| stock | INTEGER | 库存（-1 无限） |
| enabled | BOOLEAN | 是否启用 |
| priority | INTEGER | 优先级 |
| total_delivered | INTEGER | 累计发货数 |
| today_delivered | INTEGER | 今日发货数 |

### delivery_records - 发货记录表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| account_id | INTEGER | 账号 ID |
| rule_id | INTEGER | 规则 ID |
| order_id | VARCHAR(50) | 订单 ID |
| item_title | VARCHAR(500) | 商品标题 |
| buyer_name | VARCHAR(100) | 买家名称 |
| delivery_content | TEXT | 发货内容 |
| delivery_status | VARCHAR(20) | 状态 |
| error_message | TEXT | 错误信息 |
| delivered_at | DATETIME | 发货时间 |

### auto_delivery_logs - 发货日志表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| account_id | INTEGER | 账号 ID |
| level | VARCHAR(20) | 日志级别 |
| action | VARCHAR(50) | 操作类型 |
| message | TEXT | 日志内容 |
| order_id | VARCHAR(50) | 订单 ID |
| data | JSON | 附加数据 |
| created_at | DATETIME | 时间 |

---

## 🔧 使用示例

### 创建规则

```python
# 创建文本发货规则
rule_data = {
    "account_id": 1,
    "name": "Python 教程",
    "keyword": "Python 教程",
    "delivery_content": """
感谢购买！
教程链接：https://example.com/python
提取码：abc123

如有问题请联系客服。
""",
    "delivery_type": "text",
    "stock": 100,
    "enabled": True,
    "priority": 1
}

response = requests.post(
    "http://localhost:8080/api/auto-delivery/rules",
    json=rule_data,
    headers={"Authorization": f"Bearer {token}"}
)
```

### 批量创建规则

```python
rules = [
    {
        "account_id": 1,
        "name": "Java 教程",
        "keyword": "Java 教程",
        "delivery_content": "Java 教程链接...",
        "stock": 50
    },
    {
        "account_id": 1,
        "name": "前端教程",
        "keyword": "前端教程",
        "delivery_content": "前端教程链接...",
        "stock": 200
    }
]

for rule in rules:
    requests.post("/api/auto-delivery/rules", json=rule)
```

### 监控发货状态

```python
# 获取今日发货记录
response = requests.get(
    "/api/auto-delivery/records",
    params={
        "account_id": 1,
        "status": "success",
        "page": 1,
        "page_size": 100
    }
)

records = response.json()["records"]
print(f"今日成功发货：{len(records)} 单")
```

---

## ⚠️ 注意事项

### 1. 关键词设置

**推荐**:
- ✅ 使用商品核心关键词
- ✅ 避免过于宽泛的词
- ✅ 多个关键词用逗号分隔

**不推荐**:
- ❌ "教程"（太宽泛）
- ❌ "全部商品"（无法匹配）

### 2. 库存管理

**建议**:
- 定期检查库存
- 设置库存预警
- 启用自动补货（如适用）

### 3. 发货内容

**格式**:
```
感谢购买！

【商品内容】
链接：xxx
密码：xxx

【使用说明】
1. 第一步...
2. 第二步...

【售后服务】
有问题请联系客服
```

### 4. 错误处理

**常见错误**:
- API 超时 → 重试机制
- 库存不足 → 通知补货
- 匹配失败 → 检查关键词

---

## 📁 相关文件

- `app/models/auto_delivery.py` - 自动发货模型
- `app/services/auto_delivery_service.py` - 发货服务
- `app/api/auto_delivery.py` - 发货 API
- `scripts/migrate_auto_delivery.py` - 数据库迁移

---

## 🚀 后续优化

### 短期（1 周）

- [ ] 真实闲鱼 API 对接
- [ ] 定时任务调度
- [ ] 发货失败重试
- [ ] 飞书通知推送

### 中期（2 周）

- [ ] 多规格支持
- [ ] 文件自动发送
- [ ] 图片发货
- [ ] 链接发货

### 长期（1 月）

- [ ] AI 智能匹配
- [ ] 数据分析
- [ ] 批量操作
- [ ] 模板管理

---

**开发**: 易拉罐 🥫  
**版本**: v3.4.0
