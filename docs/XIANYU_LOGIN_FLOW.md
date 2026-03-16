# 闲鱼扫码登录流程说明

## 📋 概述

闲鱼机器人平台支持通过扫码方式登录闲鱼账号，自动获取 Cookie 并保存到系统中，无需手动提取。

---

## 🔄 完整流程

```
用户点击"闲鱼扫码登录"
        ↓
后端创建浏览器会话
        ↓
生成登录二维码
        ↓
用户用闲鱼 APP 扫码
        ↓
前端轮询检查登录状态（每 2 秒）
        ↓
检测到登录成功
        ↓
自动获取所有 Cookie
        ↓
保存到账号管理
        ↓
登录完成
```

---

## 🛠️ 技术实现

### 后端实现

#### 1. OAuth 服务 (`app/services/xianyu_oauth.py`)

**核心功能**:
- 使用 Playwright 启动浏览器
- 创建独立的登录会话
- 访问淘宝/闲鱼登录页
- 检测登录状态
- 获取并保存 Cookie

**关键方法**:

```python
# 创建登录会话
async def create_login_session(session_id: str, headless: bool = False) -> str:
    """创建登录会话，返回登录 URL"""
    # 启动浏览器
    # 访问登录页
    # 保存会话
    return login_url

# 检查登录状态
async def check_login_status(session_id: str) -> Dict[str, Any]:
    """检查登录状态"""
    # 检测页面元素
    # 检查 Cookie
    # 获取用户信息
    # 返回登录结果
    return {
        "status": "logged_in",  # waiting/logged_in/error
        "cookie": "xxx",
        "user_info": {...}
    }
```

**Cookie 获取逻辑**:
```python
# 获取所有 Cookie
cookies = await page.context.cookies()

# 过滤闲鱼/淘宝相关域名
xianyu_cookies = [
    c for c in cookies 
    if any(domain in c.get('domain', '') 
           for domain in [".goofish.com", ".xianyu.com", ".taobao.com", ".alibaba.com"])
]

# 转换为字符串
cookie_str = "; ".join([f"{c['name']}={c['value']}" for c in xianyu_cookies])
```

**登录状态检测**:
1. 检查 URL 是否还在登录页
2. 检查是否包含登录 Cookie（`_tb_token_`, `cookie2`, `sgcookie`）
3. 检查页面用户元素（头像、用户名等）
4. 检查页面内容（"退出登录"、"个人中心"等）

#### 2. API 接口 (`app/api/auth.py`)

**创建二维码**:
```python
POST /api/auth/xianyu/qr

Response:
{
    "session_id": "xxx",
    "qr_code": "data:image/png;base64,...",
    "login_url": "https://login.taobao.com/",
    "message": "请使用闲鱼 APP 扫描二维码登录"
}
```

**检查状态**:
```python
GET /api/auth/xianyu/{session_id}/status

Response:
{
    "status": "logged_in",  # waiting/logged_in/error
    "cookie": "xxx",
    "user_info": {
        "nick": "用户名",
        "avatar": "...",
        "userId": "..."
    },
    "message": "登录成功"
}
```

**取消会话**:
```python
DELETE /api/auth/xianyu/{session_id}
```

### 前端实现

#### 1. 登录页面 (`frontend/src/views/Login.vue`)

**扫码登录流程**:

```javascript
// 1. 生成二维码
const showQrLogin = async () => {
  const result = await authApi.createXianyuQrLogin()
  qrSessionId.value = result.session_id
  qrCodeUrl.value = result.qr_code
  
  // 开始轮询
  startQrStatusCheck()
}

// 2. 轮询检查状态
const startQrStatusCheck = () => {
  qrCheckTimer = setInterval(async () => {
    const result = await authApi.getXianyuQrStatus(qrSessionId.value)
    
    if (result.status === 'logged_in') {
      // 登录成功
      await saveXianyuCookie(result.cookie, result.user_info)
    }
  }, 2000)
}

// 3. 保存 Cookie
const saveXianyuCookie = async (cookie, userInfo) => {
  await accountApi.addAccount({
    name: userInfo.nick || '闲鱼账号',
    cookie: cookie,
    device_id: `device_${Date.now()}`
  })
}
```

#### 2. API 调用 (`frontend/src/api/auth.js`)

```javascript
// 创建二维码
export function createXianyuQrLogin(headless = false) {
  return api.post('/auth/xianyu/qr', { headless })
}

// 检查状态
export function getXianyuQrStatus(sessionId) {
  return api.get(`/auth/xianyu/${sessionId}/status`)
}

// 取消会话
export function cancelXianyuQrSession(sessionId) {
  return api.delete(`/auth/xianyu/${sessionId}`)
}
```

---

## 🧪 测试方法

### 方法 1: 使用测试脚本

```bash
cd /Users/macxiaoli/.openclaw/workspace/xianyu-auto-bot
python3 scripts/test_login.py
```

**测试流程**:
1. 自动启动浏览器
2. 打开登录页面
3. 手动扫码登录
4. 自动检测并打印 Cookie
5. 关闭浏览器

### 方法 2: 前端界面测试

1. 启动前端服务：`npm run dev`
2. 访问登录页面
3. 点击"闲鱼扫码登录"
4. 使用闲鱼 APP 扫码
5. 等待自动保存

### 方法 3: API 直接测试

```bash
# 1. 创建会话
curl -X POST http://localhost:8080/api/auth/xianyu/qr \
  -H "Content-Type: application/json" \
  -d '{"headless": false}'

# 2. 检查状态
curl http://localhost:8080/api/auth/xianyu/{session_id}/status

# 3. 取消会话
curl -X DELETE http://localhost:8080/api/auth/xianyu/{session_id}
```

---

## 📊 Cookie 说明

### 关键 Cookie

登录成功后会获取以下关键 Cookie：

| Cookie 名称 | 作用 | 必需 |
|------------|------|------|
| `_tb_token_` | 淘宝 Token | ✅ |
| `cookie2` | 用户标识 | ✅ |
| `sgcookie` | 安全 Cookie | ✅ |
| `l` | 登录状态 | ✅ |
| `isg` | 安全验证 | ✅ |
| `tfstk` | Token | ⭕ |

### Cookie 格式

保存的 Cookie 格式为字符串：
```
_tb_token_=xxx; cookie2=xxx; sgcookie=xxx; l=xxx; ...
```

### Cookie 验证

保存后可以通过以下方式验证：

```python
from app.services.xianyu_client import XianyuClient

client = XianyuClient(cookie="...")
info = await client.get_account_info()

if info:
    print("✅ Cookie 有效")
else:
    print("❌ Cookie 无效")
```

---

## 🔒 安全性

### Cookie 保护

1. **加密存储**: Cookie 在数据库中加密存储
2. **权限控制**: 只有账号所有者可查看
3. **定期刷新**: 支持 Cookie 刷新机制
4. **会话隔离**: 每个登录会话独立

### 会话管理

- 会话超时：30 分钟无操作自动关闭
- 最大会话数：每个用户最多 5 个活跃会话
- 会话清理：定期清理过期会话

---

## 🐛 常见问题

### 1. 二维码生成失败

**原因**: 
- Playwright 未安装
- 浏览器启动失败

**解决**:
```bash
# 安装 Playwright
playwright install chromium

# 检查依赖
python3 -m playwright install-deps
```

### 2. 扫码后一直显示"等待扫码"

**原因**:
- 网络问题
- Cookie 检测逻辑问题

**解决**:
- 检查后端日志
- 查看浏览器控制台
- 确认扫码的是正确的二维码

### 3. Cookie 为空

**原因**:
- 登录未完成就检测
- Cookie 域名过滤错误

**解决**:
- 增加检测延迟
- 检查域名配置

### 4. 保存账号失败

**原因**:
- 账号 API 问题
- 数据库连接问题

**解决**:
- 检查账号管理 API
- 查看数据库状态

---

## 📝 日志示例

### 成功登录日志

```
🔑 创建闲鱼登录会话：session_123
✅ 浏览器已初始化
✅ 创建登录会话：session_123, URL: https://login.taobao.com/
📍 当前 URL: https://goofish.com/
✅ 检测到登录 Cookie: ['_tb_token_', 'cookie2', 'sgcookie']
✅ 获取到 15 个 Cookie，闲鱼相关 8 个
📝 Cookie 名称：_tb_token_, cookie2, sgcookie, l, isg...
📝 Cookie 长度：1234 字符
✅ 登录成功！用户：张三
```

### 失败日志

```
🔑 创建闲鱼登录会话：session_456
❌ 创建二维码登录失败：浏览器启动失败
Traceback (most recent call last):
  ...
```

---

## 🚀 优化建议

### 性能优化

1. **浏览器复用**: 复用浏览器实例，减少启动时间
2. **会话缓存**: 缓存登录会话，避免重复创建
3. **延迟检测**: 根据登录进度动态调整检测频率

### 用户体验

1. **进度提示**: 显示更详细的登录进度
2. **错误提示**: 提供明确的错误原因和解决方案
3. **自动重试**: 失败时自动重试

### 安全性

1. **Cookie 加密**: 数据库加密存储
2. **访问控制**: 严格的权限验证
3. **审计日志**: 记录所有登录操作

---

## 🔗 相关文件

- `app/services/xianyu_oauth.py` - OAuth 服务
- `app/api/auth.py` - 认证 API
- `frontend/src/views/Login.vue` - 登录页面
- `frontend/src/api/auth.js` - 前端 API
- `scripts/test_login.py` - 测试脚本

---

**版本**: v3.1.0  
**最后更新**: 2026-03-17  
**开发**: 易拉罐 🥫
