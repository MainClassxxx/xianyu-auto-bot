import request from '@/api'

/**
 * 用户登录
 */
export function login(formData) {
  return request({
    url: '/api/auth/login',
    method: 'post',
    data: formData
  })
}

/**
 * 用户注册
 */
export function register(data) {
  return request({
    url: '/api/auth/register',
    method: 'post',
    data
  })
}

/**
 * 获取当前用户信息
 */
export function getCurrentUser() {
  return request({
    url: '/api/auth/me',
    method: 'get'
  })
}

/**
 * 获取图形验证码
 */
export function getCaptcha() {
  return request({
    url: '/api/auth/captcha',
    method: 'post'
  })
}

/**
 * 发送邮箱验证码
 */
export function sendEmailCode(data) {
  return request({
    url: '/api/auth/send-email-code',
    method: 'post',
    data
  })
}
