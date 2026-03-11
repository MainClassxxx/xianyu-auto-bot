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
    const savedUser = localStorage.getItem('user')
    if (savedUser && token.value) {
      try {
        user.value = JSON.parse(savedUser)
      } catch (e) {
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
