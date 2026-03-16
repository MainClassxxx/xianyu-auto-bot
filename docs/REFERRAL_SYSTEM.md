# 推广返利系统说明

## 📋 概述

闲鱼机器人平台的推广返利系统支持**双重返利**：
1. 邀请人购买会员 → 返利 30%
2. 邀请人充值余额 → 返利 30%

---

## 💰 返利规则

### 返利比例

| 场景 | 返利比例 | 说明 |
|------|---------|------|
| 会员购买 | 30% | 被邀请人购买任意会员套餐 |
| 余额充值 | 30% | 被邀请人充值任意金额 |

### 返利计算

**公式**: `返利金额 = 订单金额 × 30%`

**示例**:
- 被邀请人购买 VIP 会员（¥99）→ 返利 ¥29.7
- 被邀请人购买 SVIP 会员（¥159.9）→ 返利 ¥47.97
- 被邀请人充值¥100 → 返利 ¥30
- 被邀请人充值¥500 → 返利 ¥150

---

## 🔄 完整流程

### 推广流程

```
1. 用户 A 进入推广中心
        ↓
2. 获取专属推广链接
   https://yourdomain.com/register?ref=A1B2C3D4
        ↓
3. 分享给好友（微信/QQ/微博）
        ↓
4. 好友 B 点击链接注册
        ↓
5. 系统自动建立推广关系
        ↓
6. 好友 B 购买会员或充值
        ↓
7. 用户 A 获得 30% 返利
        ↓
8. 返利自动入账到余额
        ↓
9. 用户 A 可用余额继续购买或提现
```

### 返利场景

#### 场景 1: 会员购买返利

```
用户 B 通过推广链接注册
        ↓
用户 B 购买 VIP 会员 3 个月（¥24.9）
        ↓
系统计算返利：¥24.9 × 30% = ¥7.47
        ↓
用户 A 余额 +¥7.47
        ↓
记录交易：推广会员购买返利
```

#### 场景 2: 充值返利

```
用户 B 通过推广链接注册
        ↓
用户 B 充值¥100（实际到账¥115，含赠送）
        ↓
系统计算返利：¥100 × 30% = ¥30
        ↓
用户 A 余额 +¥30
        ↓
记录交易：推广充值返利
```

---

## 📊 数据统计

### 推广数据统计

**推广链接统计**:
- 总点击数
- 总注册数
- 总购买数（会员 + 充值）
- 总收益（累计返利）

**推广记录**:
- 被邀请人列表
- 每笔订单返利详情
- 返利状态（待生效/已生效）

### 余额统计

**余额信息**:
- 可用余额
- 冻结余额
- 总充值金额
- 总消费金额
- 总返利金额

**交易记录**:
- 充值入账
- 返利入账
- 消费支出
- 提现支出

---

## 🛠️ API 接口

### 1. 获取推广链接

```bash
GET /api/referral/link

Response:
{
  "id": 1,
  "referral_code": "A1B2C3D4",
  "referral_url": "https://yourdomain.com/register?ref=A1B2C3D4",
  "total_clicks": 100,
  "total_registrations": 20,
  "total_purchases": 10,
  "total_earnings": 500.0,
  "is_active": true
}
```

### 2. 获取推广统计

```bash
GET /api/referral/stats

Response:
{
  "total_registrations": 20,
  "total_purchases": 10,
  "total_earnings": 500.0,
  "recent_records": [
    {
      "id": 1,
      "referrer_username": "用户 A",
      "referred_username": "用户 B",
      "order_no": "VIP20260317001",
      "order_amount": 99.0,
      "commission_amount": 29.7,
      "status": "active",
      "purchased_at": "2026-03-17T00:00:00"
    }
  ]
}
```

### 3. 获取用户余额

```bash
GET /api/referral/balance

Response:
{
  "user_id": 1,
  "username": "用户 A",
  "balance": 500.0,
  "frozen_balance": 0.0,
  "total_recharge": 1000.0,
  "total_consumption": 500.0,
  "total_commission": 500.0
}
```

### 4. 获取余额交易记录

```bash
GET /api/referral/balance/transactions?page=1&page_size=20

Response:
{
  "total": 50,
  "transactions": [
    {
      "id": 1,
      "transaction_type": "commission",
      "amount": 30.0,
      "balance_before": 470.0,
      "balance_after": 500.0,
      "related_order_no": "VIP20260317001",
      "description": "推广会员购买返利 - 订单 VIP20260317001",
      "remark": "返利比例：30%",
      "created_at": "2026-03-17T00:00:00"
    },
    {
      "id": 2,
      "transaction_type": "commission",
      "amount": 150.0,
      "balance_before": 320.0,
      "balance_after": 470.0,
      "related_order_no": "RC20260317001",
      "description": "推广充值返利 - 订单 RC20260317001",
      "remark": "返利比例：30%",
      "created_at": "2026-03-17T00:00:00"
    }
  ]
}
```

### 5. 追踪推广注册

```bash
POST /api/referral/register/track?referral_code=A1B2C3D4

Response:
{
  "success": true,
  "message": "推广注册已记录",
  "referrer": "用户 A"
}
```

---

## 💡 使用示例

### 前端调用示例

```javascript
// 1. 获取推广链接
const link = await referralApi.getReferralLink()
console.log('我的推广链接:', link.referral_url)
console.log('推广码:', link.referral_code)

// 2. 获取推广统计
const stats = await referralApi.getReferralStats()
console.log('总注册:', stats.total_registrations)
console.log('总购买:', stats.total_purchases)
console.log('总收益:', stats.total_earnings)

// 3. 获取余额
const balance = await referralApi.getBalance()
console.log('可用余额:', balance.balance)
console.log('总返利:', balance.total_commission)

// 4. 获取交易记录
const transactions = await referralApi.getBalanceTransactions({
  page: 1,
  page_size: 20
})
console.log('交易记录:', transactions.data.transactions)
```

### 推广注册流程

```javascript
// 注册页面
const urlParams = new URLSearchParams(window.location.search)
const referralCode = urlParams.get('ref')

// 用户注册成功后
if (referralCode) {
  await referralApi.trackReferralRegistration(referralCode)
  console.log('推广关系已建立')
}
```

---

## 🔍 交易类型说明

### commission - 返利

**来源**:
- 会员购买返利
- 充值返利

**描述格式**:
- `推广会员购买返利 - 订单 {订单号}`
- `推广充值返利 - 订单 {订单号}`

### recharge - 充值

**来源**:
- 用户主动充值

**描述格式**:
- `充值 ¥{金额} + 赠送 ¥{bonus}`

### consumption - 消费

**来源**:
- 使用余额购买会员
- 其他消费

**描述格式**:
- `购买{会员等级}会员-{套餐}`

---

## 📋 数据库设计

### referral_links - 推广链接表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| user_id | INTEGER | 用户 ID |
| referral_code | VARCHAR(20) | 推广码（唯一） |
| referral_url | VARCHAR(500) | 推广链接 |
| total_clicks | INTEGER | 点击数 |
| total_registrations | INTEGER | 注册数 |
| total_purchases | INTEGER | 购买数（会员 + 充值） |
| total_earnings | FLOAT | 总收益 |

### referral_records - 推广记录表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| referrer_id | INTEGER | 推广人 ID |
| referred_user_id | INTEGER | 被推广人 ID |
| order_no | VARCHAR(50) | 订单号 |
| order_amount | FLOAT | 订单金额 |
| commission_amount | FLOAT | 返利金额 |
| status | VARCHAR(20) | pending/active |

### user_balances - 用户余额表

| 字段 | 类型 | 说明 |
|------|------|------|
| user_id | INTEGER | 用户 ID |
| balance | FLOAT | 可用余额 |
| total_recharge | FLOAT | 总充值 |
| total_consumption | FLOAT | 总消费 |
| total_commission | FLOAT | 总返利 |

### balance_transactions - 交易记录表

| 字段 | 类型 | 说明 |
|------|------|------|
| transaction_type | VARCHAR(20) | recharge/commission/consumption |
| amount | FLOAT | 金额 |
| balance_before | FLOAT | 交易前余额 |
| balance_after | FLOAT | 交易后余额 |
| description | VARCHAR(500) | 描述 |

---

## 🎯 收益示例

### 场景：推广 10 个用户

假设每个用户：
- 购买 VIP 会员：¥99
- 充值：¥100

**收益计算**:

| 用户 | 购买会员返利 | 充值返利 | 总返利 |
|------|------------|---------|--------|
| 用户 1 | ¥29.7 | ¥30 | ¥59.7 |
| 用户 2 | ¥29.7 | ¥30 | ¥59.7 |
| ... | ... | ... | ... |
| 用户 10 | ¥29.7 | ¥30 | ¥59.7 |
| **总计** | **¥297** | **¥300** | **¥597** |

**推广 100 个用户**:
- 总收益：¥5,970

---

## 🔒 安全机制

### 防作弊

1. **唯一推广码**: 每个用户只能有一个推广链接
2. **禁止自推**: 不能通过自己的链接注册
3. **订单验证**: 只有真实支付后才返利
4. **状态追踪**: 待生效 → 已生效

### 数据一致性

1. **事务处理**: 订单和返利在同一事务中
2. **幂等性**: 同一订单只返利一次
3. **余额校验**: 消费前检查余额充足

---

## 📁 相关文件

- `app/models/referral.py` - 推广返利模型
- `app/services/referral_service.py` - 推广返利服务
- `app/api/referral.py` - 推广返利 API
- `app/api/membership.py` - 会员购买 API（支持返利）
- `frontend/src/api/referral.js` - 前端 API

---

## 🚀 后续优化

### 短期（1-2 周）

- [ ] 推广中心前端页面
- [ ] 余额中心前端页面
- [ ] 实时收益通知
- [ ] 推广排行榜

### 中期（1 个月）

- [ ] 多级分销（可选）
- [ ] 推广素材库
- [ ] 自动提现功能
- [ ] 推广数据分析

### 长期（3 个月）

- [ ] 推广活动系统
- [ ] 邀请任务奖励
- [ ] 团队管理功能
- [ ] 推广效果分析

---

**版本**: v3.3.0  
**最后更新**: 2026-03-17  
**开发**: 易拉罐 🥫
