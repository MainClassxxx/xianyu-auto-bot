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
  }).then(response => response.data)
}

/**
 * 用户注册
 */
export function register(data) {
  return axios({
    url: 'http://localhost:8080/api/auth/register',
    method: 'post',
    data: data,
    headers: {
      'Content-Type': 'application/json'
    }
  }).then(response => response.data)
}

/**
 * 获取当前用户信息
 */
export function getCurrentUser() {
  return axios({
    url: 'http://localhost:8080/api/auth/me',
    method: 'get',
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    }
  }).then(response => response.data)
}

/**
 * 获取图形验证码
 */
export function getCaptcha() {
  return axios({
    url: 'http://localhost:8080/api/auth/captcha',
    method: 'post'
  }).then(response => response.data)
}

/**
 * 发送邮箱验证码
 */
export function sendEmailCode(data) {
  return axios({
    url: 'http://localhost:8080/api/auth/send-email-code',
    method: 'post',
    data: data,
    headers: {
      'Content-Type': 'application/json'
    }
  }).then(response => response.data)
}
