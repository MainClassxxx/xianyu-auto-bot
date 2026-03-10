# 🎯 闲鱼自动售货机器人 - 完整实现计划

**日期**: 2026-03-10  
**版本**: v3.0.0  
**状态**: 核心功能已实现，继续完善中

---

## ✅ 已完成的核心功能

### 1. 数据库集成 ✅
- **文件**: `app/db.py`
- **功能**:
  - SQLAlchemy ORM 配置
  - SQLite 数据库
  - 会话管理
  - 自动建表

### 2. 真实闲鱼 API 客户端 ✅
- **文件**: `app/services/xianyu_api.py`
- **功能**:
  - 基于 Cookie 的 HTTP 请求
  - 账号连接测试
  - 消息收发
  - 订单管理（获取、详情、发货）
  - 商品管理（列表、改价、上下架）
  - 多账号管理

### 3. 自动发货服务 ✅
- **文件**: `app/services/auto_delivery_service.py`
- **功能**:
  - 自动检查待发货订单
  - 规则匹配（关键词）
  - 库存管理
  - 自动发货执行
  - 发货日志记录

---

## 📋 待完成的功能

### 第一阶段：API 路由与数据库集成（优先级：🔴 高）

#### 1. 账号管理 API
```python
# 需要更新 app/api/accounts.py
- GET /api/accounts - 从数据库获取账号列表
- POST /api/accounts - 添加账号到数据库
- DELETE /api/accounts/{id} - 删除账号
- POST /api/accounts/{id}/refresh - 测试账号连接
```

#### 2. 商品管理 API
```python
# 需要更新 app/api/items.py
- GET /api/items - 从闲鱼获取商品列表
- POST /api/items/{id}/price - 调用闲鱼 API 改价
- POST /api/items/{id}/toggle - 调用闲鱼 API 上下架
```

#### 3. 订单管理 API
```python
# 需要更新 app/api/orders.py
- GET /api/orders - 从闲鱼获取订单列表
- POST /api/orders/{id}/deliver - 调用闲鱼 API 发货
```

#### 4. 自动回复 API
```python
# 需要更新 app/api/auto_reply.py
- 实现规则 CRUD
- 实现自动回复逻辑
```

#### 5. 自动发货 API
```python
# 需要更新 app/api/auto_delivery.py
- GET /api/auto-delivery/rules - 从数据库获取规则
- POST /api/auto-delivery/rules - 创建规则
- 集成自动发货服务
```

### 第二阶段：定时任务（优先级：🟡 中）

#### 1. 订单检查任务
```python
# 每 5 分钟检查一次待发货订单
async def check_orders_job():
    for account in accounts:
        client = xianyu_manager.get_client(account.id)
        await delivery_service.check_and_deliver(account.id, client)
```

#### 2. 自动改价任务
```python
# 每 30 分钟检查一次价格
async def auto_price_job():
    # 根据竞争价格自动调整
```

### 第三阶段：前端真实数据（优先级：🔴 高）

#### 1. 更新前端 Store
```javascript
// 已经实现，需要测试
- store/account.js - 连接真实 API
- store/stats.js - 连接真实 API
```

#### 2. 更新前端页面
```javascript
// 已经实现，需要测试
- Accounts.vue - 真实数据
- Dashboard.vue - 真实数据
- Orders.vue - 真实数据
```

---

## 🔧 实现步骤

### Step 1: 更新 main.py 集成数据库
```python
from app.db import init_db, get_db

@app.on_event("startup")
async def startup_event():
    init_db()  # 初始化数据库
```

### Step 2: 更新 API 路由使用真实数据
```python
from app.db import get_db
from app.services.xianyu_api import xianyu_manager

@app.get("/api/accounts")
async def get_accounts(db: Session = Depends(get_db)):
    accounts = db.query(Account).all()
    return accounts
```

### Step 3: 添加闲鱼 Cookie 测试连接
```python
@app.post("/api/accounts")
async def add_account(account_data: AccountCreate, db: Session = Depends(get_db)):
    # 1. 保存到数据库
    # 2. 创建闲鱼客户端
    # 3. 测试连接
    # 4. 返回结果
```

### Step 4: 实现自动发货定时任务
```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()
scheduler.add_job(check_orders_job, 'interval', minutes=5)
scheduler.start()
```

---

## 📊 实现进度

| 模块 | 进度 | 状态 |
|------|------|------|
| 数据库集成 | 100% | ✅ 完成 |
| 闲鱼 API 客户端 | 100% | ✅ 完成 |
| 自动发货服务 | 100% | ✅ 完成 |
| API 路由更新 | 0% | ⏳ 待实现 |
| 定时任务 | 0% | ⏳ 待实现 |
| 前端真实数据 | 0% | ⏳ 待实现 |
| 测试和调试 | 0% | ⏳ 待实现 |

**总体进度**: ~40%

---

## 🎯 下一步行动

**立即执行**:
1. 更新 main.py 集成数据库
2. 更新账号管理 API
3. 测试闲鱼 Cookie 连接
4. 更新前端连接真实 API

**本周完成**:
5. 实现所有 API 路由
6. 实现定时任务
7. 前端完全打通
8. 完整测试

---

## 📝 使用说明（完成后）

### 1. 配置闲鱼 Cookie
```bash
# 访问闲鱼网页版
https://goofish.com/

# F12 → Network → 复制 Cookie
# 在管理界面添加账号
```

### 2. 配置自动发货规则
```bash
# 管理界面 → 自动发货
# 添加规则：
# - 规则名称：教程自动发货
# - 关键词：教程
# - 发货内容：链接：https://example.com/download
# - 库存：-1（无限）
```

### 3. 启动服务
```bash
# 后端
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8080

# 前端
cd frontend && npm run dev
```

### 4. 访问管理界面
```
http://localhost:3000
```

---

## ⚠️ 注意事项

1. **Cookie 有效期**: 闲鱼 Cookie 会过期，需要定期更新
2. **网络稳定性**: 确保服务器网络稳定
3. **合规使用**: 遵守闲鱼平台规则
4. **账号安全**: 不要频繁操作，避免封号

---

**Created by**: 易拉罐 🥫  
**Date**: 2026-03-10  
**Version**: v3.0.0  
**Status**: In Progress
