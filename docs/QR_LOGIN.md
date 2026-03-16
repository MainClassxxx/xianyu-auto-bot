# 闲鱼扫码登录功能

## 功能说明

实现了闲鱼账号的**二维码扫码自动登录**，无需手动复制 Cookie！

## 使用流程

### 1. 访问登录页面
打开前端界面：http://localhost:3000

### 2. 点击扫码登录
在登录页面点击 **"闲鱼扫码登录"** 按钮

### 3. 生成二维码
系统会自动生成闲鱼登录二维码

### 4. 扫码登录
使用 **闲鱼 APP** 扫描二维码并确认登录

### 5. 自动保存
登录成功后，系统会自动：
- 获取 Cookie
- 提取用户信息
- 保存到账号管理列表

## 技术实现

### 后端
- **Playwright**：自动化浏览器控制
- **二维码生成**：qrcode 库生成登录二维码
- **会话管理**：UUID 标识每个登录会话
- **状态轮询**：前端每 2 秒检查登录状态

### 前端
- **二维码显示**：Base64 图片展示
- **状态监控**：实时显示等待/成功/失败状态
- **自动保存**：登录成功后自动调用账号管理 API

## API 接口

### 创建二维码登录会话
```
POST /api/auth/xianyu/qr
Body: { "headless": false }
Response: {
  "session_id": "uuid",
  "qr_code": "data:image/png;base64,...",
  "login_url": "https://goofish.com/",
  "message": "请使用闲鱼 APP 扫描二维码登录"
}
```

### 检查登录状态
```
GET /api/auth/xianyu/{session_id}/status
Response: {
  "status": "waiting|logged_in|error",
  "cookie": "xxx",  // 登录成功后返回
  "user_info": { "nick": "用户名" }
}
```

### 取消登录会话
```
DELETE /api/auth/xianyu/{session_id}
```

### 测试 Cookie 有效性
```
POST /api/auth/xianyu/test-cookie?cookie=xxx
```

## 注意事项

1. **浏览器依赖**：首次使用需要安装 Playwright 浏览器
   ```bash
   playwright install chromium
   ```

2. **扫码时效**：二维码有效期约 5 分钟，超时需重新生成

3. **账号安全**：
   - Cookie 加密存储在本地数据库
   - 不会上传到第三方服务器
   - 建议定期更新 Cookie

4. **登录失败处理**：
   - 检查网络连接
   - 确认闲鱼 APP 已登录
   - 重新生成二维码

## 故障排查

### 二维码无法显示
- 检查后端服务是否运行
- 查看后端日志：`data/backend.log`
- 确认 qrcode 库已安装

### 扫码后无响应
- 检查浏览器是否正常打开
- 查看 Playwright 是否正常工作
- 确认闲鱼网站可访问

### Cookie 保存失败
- 检查账号管理 API 是否正常
- 确认数据库连接正常
- 查看前端控制台错误信息

## 开发者调试

### 启用浏览器界面
```json
{ "headless": false }  // 显示浏览器窗口，便于调试
```

### 查看浏览器日志
```python
# 在 xianyu_oauth.py 中添加
page.on("console", lambda msg: print(f"Browser: {msg.text}"))
```

### 手动测试 Cookie
```bash
curl -X POST "http://localhost:8080/api/auth/xianyu/test-cookie?cookie=your_cookie_here"
```
