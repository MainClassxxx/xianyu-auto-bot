import api from './index'

/**
 * 用户登录（使用 form-data 格式）
 */
export function login(formData) {
  return api.post('/auth/login', formData, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    }
  })
}

/**
 * 用户注册
 */
export function register(data) {
  return api.post('/auth/register', data, {
    headers: {
      'Content-Type': 'application/json'
    }
  })
}

/**
 * 获取当前用户信息
 */
export function getCurrentUser() {
  return api.get('/auth/me')
}

/**
 * 获取图形验证码
 */
export function getCaptcha() {
  return api.post('/auth/captcha')
}

/**
 * 发送邮箱验证码
 */
export function sendEmailCode(data) {
  return api.post('/auth/send-email-code', data, {
    headers: {
      'Content-Type': 'application/json'
    }
  })
}

/**
 * 创建闲鱼二维码登录会话
 */
export function createXianyuQrLogin(headless = false) {
  return api.post('/auth/xianyu/qr', { headless })
}

/**
 * 检查闲鱼二维码登录状态
 */
export function getXianyuQrStatus(sessionId) {
  return api.get(`/auth/xianyu/${sessionId}/status`)
}

/**
 * 取消闲鱼登录会话
 */
export function cancelXianyuQrSession(sessionId) {
  return api.delete(`/auth/xianyu/${sessionId}`)
}

/**
 * 测试闲鱼 Cookie 是否有效
 */
export function testXianyuCookie(cookie) {
  return api.post('/auth/xianyu/test-cookie', null, {
    params: { cookie }
  })
}
