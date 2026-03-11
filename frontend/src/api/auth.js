import axios from 'axios'

/**
 * 用户登录（使用 form-data 格式）
 */
export function login(formData) {
  return axios({
    url: 'http://localhost:8080/api/auth/login',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    }
  })
}

/**
 * 用户注册
 */
export function register(data) {
  return request({
    url: '/auth/register',
    method: 'post',
    data
  })
}

/**
 * 获取当前用户信息
 */
export function getCurrentUser() {
  return request({
    url: '/auth/me',
    method: 'get'
  })
}

/**
 * 获取图形验证码
 */
export function getCaptcha() {
  return request({
    url: '/auth/captcha',
    method: 'post'
  })
}

/**
 * 发送邮箱验证码
 */
export function sendEmailCode(data) {
  return request({
    url: '/auth/send-email-code',
    method: 'post',
    data
  })
}
