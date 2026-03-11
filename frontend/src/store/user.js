import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as authApi from '@/api/auth'

export const useUserStore = defineStore('user', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('token') || null)
  const loading = ref(false)

  const isLoggedIn = computed(() => !!token.value)
  const username = computed(() => user.value?.username || '')
  const role = computed(() => user.value?.role || '')

  async function login(formData) {
    loading.value = true
    try {
      const response = await authApi.login(formData)
      
      // 确保 response 中有 access_token
      if (response && response.access_token) {
        token.value = response.access_token
        user.value = response.user_info
        
        // 存储到 localStorage
        localStorage.setItem('token', response.access_token)
        localStorage.setItem('user', JSON.stringify(response.user_info))
        
        console.log('登录成功，token 已存储:', response.access_token.substring(0, 20) + '...')
        
        return response
      } else {
        throw new Error('登录响应格式错误')
      }
    } catch (error) {
      console.error('登录失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  async function register(userData) {
    loading.value = true
    try {
      const response = await authApi.register(userData)
      token.value = response.access_token
      user.value = response.user_info
      
      localStorage.setItem('token', response.access_token)
      localStorage.setItem('user', JSON.stringify(response.user_info))
      
      return response
    } catch (error) {
      throw error
    } finally {
      loading.value = false
    }
  }

  async function fetchUserInfo() {
    if (!token.value) return
    
    try {
      user.value = await authApi.getCurrentUser()
      localStorage.setItem('user', JSON.stringify(user.value))
    } catch (error) {
      // Token 可能已过期，清除本地存储
      logout()
      throw error
    }
  }

  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  // 初始化时从本地存储恢复用户信息
  function init() {
    const savedToken = localStorage.getItem('token')
    const savedUser = localStorage.getItem('user')
    
    if (savedToken && savedUser) {
      try {
        token.value = savedToken
        user.value = JSON.parse(savedUser)
        console.log('从本地存储恢复登录状态')
      } catch (e) {
        localStorage.removeItem('token')
        localStorage.removeItem('user')
      }
    }
  }

  init()

  return {
    user,
    token,
    loading,
    isLoggedIn,
    username,
    role,
    login,
    register,
    fetchUserInfo,
    logout
  }
})
