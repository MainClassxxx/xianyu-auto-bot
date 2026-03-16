# 用户等级系统说明文档

## 📋 概述

闲鱼机器人平台现已支持完整的用户等级系统，包含三种会员等级和管理员权限管理。

---

## 👥 用户等级

### 1️⃣ 普通用户 (normal)

**获取方式**: VIP 过期后自动降级

**权限**:
- ✅ 基础 API 调用
- ❌ 自动发货
- ❌ 自动回复
- ❌ 多账号管理
- ❌ 数据导出

**限制**:
- 最多绑定账号数：**1 个**
- 每日 API 调用限制：**100 次**

---

### 2️⃣ VIP 用户 (vip) ⭐

**获取方式**: 
- 新用户注册赠送 **1 天** VIP
- 管理员手动升级
- 付费购买（待实现）

**权限**:
- ✅ 基础 API 调用
- ✅ 高级 API 调用
- ✅ 自动发货
- ✅ 自动回复
- ✅ 多账号管理（最多 5 个）
- ✅ 数据导出

**限制**:
- 最多绑定账号数：**5 个**
- 每日 API 调用限制：**1000 次**

---

### 3️⃣ SVIP 用户 (svip) 👑

**获取方式**: 
- 管理员手动升级
- 付费购买（待实现）

**权限**:
- ✅ 所有 VIP 权限
- ✅ Webhook 回调
- ✅ AI 智能回复
- ✅ 无限账号绑定
- ✅ 无限 API 调用

**限制**:
- 最多绑定账号数：**无限制**
- 每日 API 调用限制：**无限制**

---

## 🔐 管理员权限

### 管理员 (admin)

**权限**:
- 👥 用户管理（查看、升级、封禁）
- 📊 查看系统统计
- 📝 查看操作日志
- 🔧 账号管理

### 超级管理员 (super_admin)

**权限**:
- 所有管理员权限
- ⚙️ 系统设置
- 📋 查看管理员操作日志

---

## 📊 权限对照表

| 功能/等级 | 普通用户 | VIP 用户 | SVIP 用户 |
|-----------|---------|---------|----------|
| 基础 API | ✅ | ✅ | ✅ |
| 高级 API | ❌ | ✅ | ✅ |
| 自动发货 | ❌ | ✅ | ✅ |
| 自动回复 | ❌ | ✅ | ✅ |
| 多账号管理 | ❌ | ✅ (5 个) | ✅ (无限) |
| 数据导出 | ❌ | ✅ | ✅ |
| Webhook | ❌ | ❌ | ✅ |
| AI 回复 | ❌ | ❌ | ✅ |
| 每日 API 限制 | 100 | 1000 | 无限 |

---

## 🎁 新用户福利

**注册即送 VIP 权益！**

- 🎉 新用户注册自动获得 **VIP 会员**
- ⏰ 有效期：**1 天**
- 🚀 可体验所有 VIP 功能

**试用期结束后**:
- 自动降级为普通用户
- 已绑定的账号保留（超出 1 个需手动解绑）
- 可重新付费升级或等待管理员赠送

---

## 🔧 API 使用示例

### 1. 用户注册（自动获得 1 天 VIP）

```bash
POST /api/auth/register
{
  "username": "newuser",
  "email": "user@example.com",
  "password": "password123",
  "captcha": "abcd",
  "captcha_id": "xxx",
  "email_code": "123456"
}

# 响应包含会员信息
{
  "access_token": "xxx",
  "user_info": {
    "username": "newuser",
    "membership_level": "vip",
    "membership_expire_at": "2026-03-18T00:00:00",
    "trial_message": "🎉 新用户赠送 1 天 VIP 权益，快去体验高级功能吧！"
  }
}
```

### 2. 查看当前用户信息（含会员等级）

```bash
GET /api/auth/me
Authorization: Bearer <token>

# 响应
{
  "username": "newuser",
  "membership_level": "vip",
  "membership_expire_at": "2026-03-18T00:00:00",
  "features": {
    "level": "vip",
    "level_name": "VIP 用户",
    "is_valid": true,
    "permissions": ["api.basic", "api.advanced", ...],
    "features": {
      "auto_delivery": true,
      "auto_reply": true,
      ...
    },
    "limits": {
      "max_accounts": 5,
      "daily_api_limit": 1000
    },
    "usage": {
      "today_api_calls": 10,
      "total_api_calls": 50
    }
  }
}
```

### 3. 管理员升级用户会员

```bash
POST /api/admin/users/upgrade
Authorization: Bearer <admin_token>
{
  "user_id": 123,
  "level": "svip",
  "days": 30
}
```

### 4. 管理员查看用户列表

```bash
GET /api/admin/users?page=1&page_size=20&membership_level=vip
Authorization: Bearer <admin_token>
```

### 5. 管理员封禁用户

```bash
POST /api/admin/users/ban
Authorization: Bearer <admin_token>
{
  "user_id": 123,
  "reason": "违反用户协议"
}
```

---

## 📝 数据库变更

### users 表新增字段

```sql
ALTER TABLE users ADD COLUMN membership_level VARCHAR(20) DEFAULT 'normal';
ALTER TABLE users ADD COLUMN membership_expire_at DATETIME;
ALTER TABLE users ADD COLUMN total_api_calls INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN today_api_calls INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN last_api_call_at DATETIME;
ALTER TABLE users ADD COLUMN permissions JSON;
ALTER TABLE users ADD COLUMN last_login_at DATETIME;
ALTER TABLE users ADD COLUMN phone VARCHAR(20) DEFAULT '';
```

### 新增表

```sql
-- API 调用日志表
CREATE TABLE api_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    endpoint VARCHAR(200),
    method VARCHAR(10),
    status_code INTEGER,
    ip_address VARCHAR(50),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 管理员操作日志表
CREATE TABLE admin_operation_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    admin_id INTEGER,
    admin_username VARCHAR(50),
    operation VARCHAR(100),
    target_user_id INTEGER,
    target_username VARCHAR(50),
    details JSON,
    ip_address VARCHAR(50),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🔒 权限检查

系统会在以下场景进行权限检查：

1. **API 调用**: 检查每日调用次数限制
2. **账号绑定**: 检查账号数量限制
3. **功能使用**: 检查功能权限（自动发货、自动回复等）
4. **会员有效期**: 登录时检查会员是否过期

---

## 📊 管理员后台

管理员可以通过以下 API 管理系统：

- `GET /api/admin/users` - 用户列表
- `GET /api/admin/users/{id}` - 用户详情
- `POST /api/admin/users/upgrade` - 升级会员
- `POST /api/admin/users/ban` - 封禁用户
- `POST /api/admin/users/unban/{id}` - 解封用户
- `GET /api/admin/stats` - 系统统计
- `GET /api/admin/logs` - 操作日志

---

## 🛠️ 实现文件

```
app/
├── api/
│   ├── admin.py              # 管理员 API
│   └── auth.py               # 认证 API（已更新）
├── models/
│   └── user.py               # 用户模型（已扩展）
├── services/
│   └── membership_service.py # 会员服务（新增）
└── scripts/
    └── migrate_membership.py # 数据库迁移脚本
```

---

## 📅 更新日志

**2026-03-17**
- ✅ 实现完整的用户等级系统
- ✅ 新用户注册赠送 1 天 VIP
- ✅ 添加管理员权限管理
- ✅ 实现 API 调用限制
- ✅ 添加会员有效期管理

---

**开发**: 易拉罐 🥫  
**版本**: v3.1.0
