import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as accountApi from '@/api/account'

export const useAccountStore = defineStore('account', () => {
  const accounts = ref([])
  const loading = ref(false)

  const activeCount = computed(() => {
    return accounts.value.filter(a => a.status === 'active').length
  })

  async function fetchAccounts() {
    loading.value = true
    try {
      const data = await accountApi.getAccounts()
      accounts.value = data
    } catch (error) {
      console.error('获取账号列表失败:', error)
    } finally {
      loading.value = false
    }
  }

  async function addAccount(data) {
    await accountApi.addAccount(data)
    await fetchAccounts()
  }

  async function deleteAccount(id) {
    await accountApi.deleteAccount(id)
    await fetchAccounts()
  }

  async function refreshAccount(id) {
    await accountApi.refreshAccount(id)
    await fetchAccounts()
  }

  return {
    accounts,
    loading,
    activeCount,
    fetchAccounts,
    addAccount,
    deleteAccount,
    refreshAccount
  }
})
