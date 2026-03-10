import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as statsApi from '@/api/stats'

export const useStatsStore = defineStore('stats', () => {
  const overview = ref({
    total_items: 0,
    total_orders: 0,
    total_revenue: 0,
    pending_orders: 0
  })

  const loading = ref(false)

  const formattedRevenue = computed(() => {
    return `¥${overview.value.total_revenue.toFixed(2)}`
  })

  async function fetchOverview() {
    loading.value = true
    try {
      const data = await statsApi.getOverview()
      overview.value = data
    } catch (error) {
      console.error('获取统计数据失败:', error)
    } finally {
      loading.value = false
    }
  }

  return {
    overview,
    loading,
    formattedRevenue,
    fetchOverview
  }
})
