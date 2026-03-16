# 会员系统说明文档

## 📋 概述

闲鱼机器人平台提供完整的会员系统，支持用户在线购买会员和管理员手动开通会员。

---

## 👥 会员等级

| 等级 | 标识 | 价格范围 | 主要权益 |
|------|------|---------|---------|
| 普通用户 | normal | 免费 | 基础功能，1 个账号，每日 100 次 API |
| VIP 会员 | vip | ¥9.9-79.9 | 5 个账号，每日 1000 次 API，自动发货/回复 |
| SVIP 会员 | svip | ¥19.9-159.9 | 无限账号，无限 API，AI 回复，Webhook |

---

## 💰 会员套餐

### VIP 会员套餐

| 套餐 | 有效期 | 价格 | 日均成本 |
|------|--------|------|---------|
| 1 个月 | 30 天 | ¥9.9 | ¥0.33/天 |
| 2 个月 | 60 天 | ¥17.9 | ¥0.30/天 |
| 3 个月 | 90 天 | ¥24.9 | ¥0.28/天 |
| 6 个月 | 180 天 | ¥45.9 | ¥0.26/天 |
| 12 个月 | 365 天 | ¥79.9 | ¥0.22/天 |

### SVIP 会员套餐

| 套餐 | 有效期 | 价格 | 日均成本 |
|------|--------|------|---------|
| 1 个月 | 30 天 | ¥19.9 | ¥0.66/天 |
| 2 个月 | 60 天 | ¥35.9 | ¥0.60/天 |
| 3 个月 | 90 天 | ¥49.9 | ¥0.55/天 |
| 6 个月 | 180 天 | ¥89.9 | ¥0.50/天 |
| 12 个月 | 365 天 | ¥159.9 | ¥0.44/天 |

---

## 🛒 购买流程

### 用户购买流程

```
1. 访问会员中心页面
        ↓
2. 选择会员等级（VIP/SVIP）
        ↓
3. 选择套餐（1/2/3/6/12 个月）
        ↓
4. 选择支付方式（支付宝/微信）
        ↓
5. 确认订单并支付
        ↓
6. 系统自动开通会员
        ↓
7. 更新用户信息
```

### 管理员开通流程

```
1. 管理员登录后台
        ↓
2. 进入用户管理页面
        ↓
3. 搜索目标用户
        ↓
4. 选择开通会员等级和天数
        ↓
5. 填写开通原因（可选）
        ↓
6. 确认开通
        ↓
7. 系统记录日志
        ↓
8. 用户会员立即生效
```

---

## 🔧 API 接口

### 1. 获取会员套餐

```bash
GET /api/membership/plans

Response:
{
  "success": true,
  "data": {
    "vip": {
      "1_month": {"days": 30, "price": 9.9, "name": "VIP 会员 - 1 个月"},
      "2_months": {"days": 60, "price": 17.9, "name": "VIP 会员 - 2 个月"},
      ...
    },
    "svip": {
      ...
    }
  }
}
```

### 2. 创建订单

```bash
POST /api/membership/order/create
Content-Type: application/json

{
  "level": "vip",
  "plan": "3_months",
  "payment_method": "alipay"
}

Response:
{
  "success": true,
  "data": {
    "order_no": "VIP20260317001234567",
    "level": "vip",
    "plan": "3_months",
    "plan_name": "VIP 会员 - 3 个月",
    "days": 90,
    "price": 24.9,
    "payment_method": "alipay",
    "payment_url": "/api/membership/pay/VIP20260317001234567",
    "expire_at": "2026-03-17T01:13:00"
  }
}
```

### 3. 支付订单

```bash
POST /api/membership/order/{order_no}/pay
Params: transaction_id (可选，支付交易号)

Response:
{
  "success": true,
  "message": "支付成功，会员已开通",
  "data": {
    "order_no": "VIP20260317001234567",
    "level": "vip",
    "days": 90,
    "paid_at": "2026-03-17T00:13:00"
  }
}
```

### 4. 获取订单详情

```bash
GET /api/membership/order/{order_no}

Response:
{
  "success": true,
  "data": {
    "order_no": "VIP20260317001234567",
    "user_id": 123,
    "username": "testuser",
    "level": "vip",
    "plan": "3_months",
    "days": 90,
    "price": 24.9,
    "payment_method": "alipay",
    "status": "paid",
    "created_at": "2026-03-17T00:13:00",
    "paid_at": "2026-03-17T00:13:00"
  }
}
```

### 5. 获取用户订单列表

```bash
GET /api/membership/orders?page=1&page_size=20

Response:
{
  "success": true,
  "data": {
    "total": 5,
    "orders": [...]
  }
}
```

### 6. 取消订单

```bash
POST /api/membership/order/{order_no}/cancel

Response:
{
  "success": true,
  "message": "订单已取消"
}
```

### 7. 管理员开通会员

```bash
POST /api/membership/admin/grant
Params:
- user_id: 用户 ID
- level: 会员等级（vip/svip）
- days: 天数
- reason: 开通原因（可选）

Response:
{
  "success": true,
  "message": "已为用户开通 vip 会员 90 天",
  "data": {
    "user_id": 123,
    "username": "testuser",
    "level": "vip",
    "days": 90,
    "expire_at": "2026-06-15T00:00:00"
  }
}
```

### 8. 获取开通日志（管理员）

```bash
GET /api/membership/admin/grant-logs?page=1&page_size=20

Response:
{
  "success": true,
  "data": {
    "total": 10,
    "logs": [
      {
        "id": 1,
        "admin_id": 1,
        "admin_username": "admin",
        "user_id": 123,
        "username": "testuser",
        "level": "vip",
        "days": 90,
        "reason": "新用户奖励",
        "created_at": "2026-03-17T00:00:00"
      }
    ]
  }
}
```

---

## 📊 数据库设计

### membership_orders - 订单表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| order_no | VARCHAR(50) | 订单号（唯一） |
| user_id | INTEGER | 用户 ID |
| username | VARCHAR(50) | 用户名 |
| level | VARCHAR(20) | 会员等级（vip/svip） |
| plan | VARCHAR(50) | 套餐（1_month/2_months 等） |
| days | INTEGER | 有效期天数 |
| price | FLOAT | 价格 |
| payment_method | VARCHAR(20) | 支付方式（alipay/wechat） |
| transaction_id | VARCHAR(100) | 支付交易号 |
| status | VARCHAR(20) | 状态（pending/paid/cancelled/expired） |
| created_at | DATETIME | 创建时间 |
| paid_at | DATETIME | 支付时间 |
| expire_at | DATETIME | 订单过期时间 |
| remark | TEXT | 备注 |

### membership_grant_logs - 开通日志表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| admin_id | INTEGER | 管理员 ID |
| admin_username | VARCHAR(50) | 管理员用户名 |
| user_id | INTEGER | 用户 ID |
| username | VARCHAR(50) | 用户名 |
| level | VARCHAR(20) | 会员等级 |
| days | INTEGER | 开通天数 |
| reason | VARCHAR(500) | 开通原因 |
| created_at | DATETIME | 创建时间 |

---

## 💳 支付集成

### 当前状态

目前为**模拟支付**，用于测试流程。

### 后续接入

#### 1. 支付宝支付

```python
# 支付宝 SDK 集成
import alipay

alipay_client = alipay.AliPay(
    appid="your_appid",
    app_notify_url="https://yourdomain.com/api/membership/alipay/notify",
    app_private_key_path="keys/app_private_key.pem",
    alipay_public_key_path="keys/alipay_public_key.pem",
    sign_type="RSA2"
)

# 创建支付订单
order_string = alipay_client.api_pay({
    "out_trade_no": order_no,
    "total_amount": str(price),
    "subject": f"闲鱼机器人{plan_name}"
})
```

#### 2. 微信支付

```python
# 微信支付 SDK 集成
from wechatpy.pay import WeChatPay

wechat_pay = WeChatPay(
    appid="your_appid",
    api_key="your_api_key",
    mch_id="your_mch_id",
    notify_url="https://yourdomain.com/api/membership/wechat/notify"
)

# 创建支付订单
order = wechat_pay.jsapi.create(
    out_trade_no=order_no,
    total_fee=int(price * 100),  # 单位：分
    body=f"闲鱼机器人{plan_name}",
    open_id=user_open_id
)
```

#### 3. 支付回调处理

```python
@router.post("/alipay/notify")
async def alipay_notify(request: Request):
    """支付宝支付回调"""
    data = await request.form()
    
    # 验证签名
    if alipay_client.verify(data):
        order_no = data.get('out_trade_no')
        transaction_id = data.get('trade_no')
        
        # 更新订单状态
        service = MembershipOrderService(db)
        service.pay_order(order_no, transaction_id)
        
        return "success"
    else:
        return "fail"
```

---

## 🔒 安全性

### 订单安全

1. **订单号唯一性**: 使用时间戳 + 用户 ID 生成
2. **订单有效期**: 30 分钟未支付自动过期
3. **幂等性**: 同一订单只能支付一次
4. **签名验证**: 支付回调验证签名

### 权限控制

1. **用户只能查看自己的订单**
2. **管理员可以查看所有订单**
3. **只有管理员可以手动开通会员**
4. **开通日志永久保存**

---

## 📝 使用示例

### 用户购买 VIP 会员（3 个月）

```javascript
// 前端调用示例
import * as membershipApi from '@/api/membership'

// 1. 创建订单
const order = await membershipApi.createOrder({
  level: 'vip',
  plan: '3_months',
  payment_method: 'alipay'
})

// 2. 支付订单
const result = await membershipApi.payOrder(order.data.order_no)

// 3. 检查会员状态
const userInfo = await membershipApi.getUserInfo()
console.log('会员等级:', userInfo.membership_level)
console.log('有效期至:', userInfo.membership_expire_at)
```

### 管理员为用户开通 SVIP

```python
# Python 调用示例
import requests

# 管理员登录获取 token
token = login_as_admin()

# 为用户开通 SVIP（180 天）
response = requests.post(
    'http://localhost:8080/api/membership/admin/grant',
    params={
        'user_id': 123,
        'level': 'svip',
        'days': 180,
        'reason': '年度活动奖励'
    },
    headers={'Authorization': f'Bearer {token}'}
)

print(response.json())
# {'success': True, 'message': '已为用户开通 svip 会员 180 天'}
```

---

## 🐛 常见问题

### 1. 订单创建失败

**原因**: 套餐参数错误

**解决**: 检查 level 和 plan 参数是否在配置中

### 2. 支付后会员未开通

**原因**: 支付回调未正确处理

**解决**: 检查支付回调日志，确认订单状态更新

### 3. 管理员无法开通会员

**原因**: 权限不足

**解决**: 确认管理员角色为 admin 或 super_admin

### 4. 会员有效期计算错误

**原因**: 时区问题

**解决**: 统一使用 UTC 时间，前端转换为本时区

---

## 📁 相关文件

- `app/models/membership.py` - 会员订单模型
- `app/services/membership_order_service.py` - 订单服务
- `app/api/membership.py` - 会员 API
- `frontend/src/views/Membership.vue` - 会员中心页面
- `frontend/src/api/membership.js` - 前端 API
- `scripts/migrate_membership_orders.py` - 数据库迁移

---

## 🚀 后续优化

### 短期（1-2 周）

- [ ] 接入真实支付宝支付
- [ ] 接入真实微信支付
- [ ] 添加支付回调处理
- [ ] 订单过期自动取消

### 中期（1 个月）

- [ ] 会员到期提醒（邮件/短信）
- [ ] 自动续费功能
- [ ] 优惠券系统
- [ ] 邀请奖励机制

### 长期（3 个月）

- [ ] 代理商系统
- [ ] 批量开通功能
- [ ] 会员数据分析
- [ ] 差异化定价策略

---

**版本**: v3.2.0  
**最后更新**: 2026-03-17  
**开发**: 易拉罐 🥫
