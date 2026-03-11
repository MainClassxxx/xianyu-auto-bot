<template>
  <div class="dashboard-page">
    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card stat-card-1">
        <div class="stat-card-bg"></div>
        <div class="stat-card-content">
          <div class="stat-icon">
            <el-icon :size="32"><User /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.accounts?.active || 0 }}</div>
            <div class="stat-label">在线账号</div>
            <div class="stat-trend positive">
              <el-icon><Top /></el-icon>
              <span>+12%</span>
            </div>
          </div>
        </div>
      </div>

      <div class="stat-card stat-card-2">
        <div class="stat-card-bg"></div>
        <div class="stat-card-content">
          <div class="stat-icon">
            <el-icon :size="32"><ShoppingCart /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.items?.onsale || 0 }}</div>
            <div class="stat-label">在售商品</div>
            <div class="stat-trend positive">
              <el-icon><Top /></el-icon>
              <span>+8%</span>
            </div>
          </div>
        </div>
      </div>

      <div class="stat-card stat-card-3">
        <div class="stat-card-bg"></div>
        <div class="stat-card-content">
          <div class="stat-icon">
            <el-icon :size="32"><List /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.overview?.pending_orders || 0 }}</div>
            <div class="stat-label">待发货订单</div>
            <div class="stat-trend negative">
              <el-icon><Bottom /></el-icon>
              <span>-5%</span>
            </div>
          </div>
        </div>
      </div>

      <div class="stat-card stat-card-4">
        <div class="stat-card-bg"></div>
        <div class="stat-card-content">
          <div class="stat-icon">
            <el-icon :size="32"><Money /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.overview?.formatted_revenue || '¥0.00' }}</div>
            <div class="stat-label">今日收入</div>
            <div class="stat-trend positive">
              <el-icon><Top /></el-icon>
              <span>+23%</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="charts-grid">
      <div class="chart-card">
        <div class="chart-header">
          <h3>📈 订单趋势</h3>
          <el-radio-group v-model="orderPeriod" size="small" @change="loadOrderStats">
            <el-radio-button label="7">7 天</el-radio-button>
            <el-radio-button label="30">30 天</el-radio-button>
          </el-radio-group>
        </div>
        <div ref="orderChartRef" class="chart-container"></div>
      </div>

      <div class="chart-card">
        <div class="chart-header">
          <h3>💰 收入统计</h3>
          <el-radio-group v-model="revenuePeriod" size="small" @change="loadRevenueStats">
            <el-radio-button label="7">7 天</el-radio-button>
            <el-radio-button label="30">30 天</el-radio-button>
          </el-radio-group>
        </div>
        <div ref="revenueChartRef" class="chart-container"></div>
      </div>
    </div>

    <!-- 最近订单 -->
    <div class="recent-orders-card">
      <div class="card-header">
        <h3>📦 最近订单</h3>
        <el-button type="primary" link @click="$router.push('/orders')">
          查看全部 <el-icon><ArrowRight /></el-icon>
        </el-button>
      </div>
      <el-table :data="recentOrders" class="gradient-table">
        <el-table-column prop="order_id" label="订单号" width="180" />
        <el-table-column prop="buyer_name" label="买家" width="120" />
        <el-table-column prop="item_title" label="商品" />
        <el-table-column prop="price" label="金额" width="100">
          <template #default="{ row }">
            <span class="price-text">¥{{ row.price }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" effect="dark" round>
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="时间" width="180" />
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import * as statsApi from '@/api/stats'

const loading = ref(false)
const orderPeriod = ref('7')
const revenuePeriod = ref('7')
const orderChartRef = ref(null)
const revenueChartRef = ref(null)
let orderChart = null
let revenueChart = null

const stats = reactive({
  overview: null,
  accounts: null,
  items: null
})

const recentOrders = ref([
  {
    order_id: 'ORD20240311001',
    buyer_name: '张***3',
    item_title: 'AI 绘画提示词教程',
    price: 29.9,
    status: 'paid',
    created_at: '2024-03-11 10:30:00'
  },
  {
    order_id: 'ORD20240311002',
    buyer_name: '李***8',
    item_title: 'Python 入门教程',
    price: 49.9,
    status: 'shipped',
    created_at: '2024-03-11 09:20:00'
  },
  {
    order_id: 'ORD20240311003',
    buyer_name: '王***5',
    item_title: '电影票代下单',
    price: 35.0,
    status: 'pending',
    created_at: '2024-03-11 08:10:00'
  }
])

const getStatusType = (status) => {
  const types = {
    'pending': 'warning',
    'paid': 'success',
    'shipped': 'primary',
    'completed': 'info',
    'refunded': 'danger'
  }
  return types[status] || 'info'
}

const getStatusText = (status) => {
  const texts = {
    'pending': '待发货',
    'paid': '已付款',
    'shipped': '已发货',
    'completed': '已完成',
    'refunded': '已退款'
  }
  return texts[status] || status
}

async function loadOverview() {
  try {
    const data = await statsApi.getOverview()
    stats.overview = data
    try {
      stats.accounts = await statsApi.getAccountStats()
    } catch (e) {
      console.warn('加载账号统计失败:', e)
      stats.accounts = { total: 0, active: 0, inactive: 0 }
    }
    try {
      stats.items = await statsApi.getItemStats()
    } catch (e) {
      console.warn('加载商品统计失败:', e)
      stats.items = { total: 0, onsale: 0, sold: 0, out: 0 }
    }
  } catch (error) {
    console.error('加载统计数据失败:', error)
    stats.overview = { total_revenue: 0, formatted_revenue: '¥0.00', pending_orders: 0 }
  }
}

async function loadOrderStats() {
  try {
    const data = await statsApi.getOrderStats(parseInt(orderPeriod.value))
    initOrderChart(data)
  } catch (error) {
    console.error('加载订单统计失败:', error)
  }
}

async function loadRevenueStats() {
  try {
    const data = await statsApi.getRevenueStats(parseInt(revenuePeriod.value))
    initRevenueChart(data)
  } catch (error) {
    console.error('加载收入统计失败:', error)
  }
}

function initOrderChart(data) {
  if (!orderChartRef.value) return
  
  if (orderChart) {
    orderChart.dispose()
  }
  
  orderChart = echarts.init(orderChartRef.value)
  
  const option = {
    tooltip: { 
      trigger: 'axis',
      backgroundColor: 'rgba(255,255,255,0.95)',
      borderColor: '#e6e6e6',
      textStyle: { color: '#333' }
    },
    grid: { left: '3%', right: '4%', bottom: '3%', top: '10%', containLabel: true },
    xAxis: {
      type: 'category',
      data: ['待付款', '已付款', '待发货', '已发货', '已完成', '已退款'],
      axisLine: { lineStyle: { color: 'rgba(255,255,255,0.3)' } },
      axisLabel: { color: 'rgba(255,255,255,0.8)' }
    },
    yAxis: { 
      type: 'value',
      axisLine: { show: false },
      axisLabel: { color: 'rgba(255,255,255,0.8)' },
      splitLine: { lineStyle: { color: 'rgba(255,255,255,0.1)' } }
    },
    series: [{
      name: '订单数',
      type: 'bar',
      barWidth: '40%',
      data: [
        data.pending || 0,
        data.paid || 0,
        data.shipping || 0,
        data.shipped || 0,
        data.completed || 0,
        data.refunded || 0
      ],
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: '#667eea' },
          { offset: 1, color: '#764ba2' }
        ]),
        borderRadius: [8, 8, 0, 0]
      }
    }]
  }
  
  orderChart.setOption(option)
}

function initRevenueChart(data) {
  if (!revenueChartRef.value) return
  
  if (revenueChart) {
    revenueChart.dispose()
  }
  
  revenueChart = echarts.init(revenueChartRef.value)
  
  const daily = data.daily || []
  
  const option = {
    tooltip: { 
      trigger: 'axis',
      backgroundColor: 'rgba(255,255,255,0.95)',
      borderColor: '#e6e6e6',
      textStyle: { color: '#333' }
    },
    grid: { left: '3%', right: '4%', bottom: '3%', top: '10%', containLabel: true },
    xAxis: {
      type: 'category',
      data: daily.map(d => d.date),
      axisLine: { lineStyle: { color: 'rgba(255,255,255,0.3)' } },
      axisLabel: { color: 'rgba(255,255,255,0.8)', rotate: 45 }
    },
    yAxis: { 
      type: 'value',
      axisLine: { show: false },
      axisLabel: { color: 'rgba(255,255,255,0.8)' },
      splitLine: { lineStyle: { color: 'rgba(255,255,255,0.1)' } }
    },
    series: [{
      name: '收入',
      type: 'line',
      data: daily.map(d => d.revenue),
      smooth: true,
      symbol: 'circle',
      symbolSize: 8,
      lineStyle: {
        color: '#4facfe',
        width: 3
      },
      itemStyle: {
        color: '#fff',
        borderColor: '#4facfe',
        borderWidth: 3
      },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(79, 172, 254, 0.5)' },
          { offset: 1, color: 'rgba(79, 172, 254, 0.05)' }
        ])
      }
    }]
  }
  
  revenueChart.setOption(option)
}

onMounted(async () => {
  loading.value = true
  await loadOverview()
  await loadOrderStats()
  await loadRevenueStats()
  loading.value = false
  
  nextTick(() => {
    window.addEventListener('resize', () => {
      orderChart?.resize()
      revenueChart?.resize()
    })
  })
})
</script>

<style scoped>
.dashboard-page {
  animation: fadeIn 0.6s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 统计卡片网格 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
  margin-bottom: 32px;
}

.stat-card {
  position: relative;
  border-radius: 20px;
  overflow: hidden;
  backdrop-filter: blur(20px);
  background: rgba(255, 255, 255, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.stat-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.15);
}

.stat-card-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  opacity: 0.1;
}

.stat-card-1 .stat-card-bg {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-card-2 .stat-card-bg {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-card-3 .stat-card-bg {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-card-4 .stat-card-bg {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.stat-card-content {
  position: relative;
  padding: 24px;
  display: flex;
  align-items: flex-start;
  gap: 20px;
}

.stat-icon {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
}

.stat-card-1 .stat-icon { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
.stat-card-2 .stat-icon { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
.stat-card-3 .stat-icon { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
.stat-card-4 .stat-icon { background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); }

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 36px;
  font-weight: 700;
  color: #fff;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  line-height: 1;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 8px;
}

.stat-trend {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  font-weight: 600;
}

.stat-trend.positive {
  color: #43e97b;
}

.stat-trend.negative {
  color: #f5576c;
}

/* 图表网格 */
.charts-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
  margin-bottom: 32px;
}

.chart-card {
  border-radius: 20px;
  backdrop-filter: blur(20px);
  background: rgba(255, 255, 255, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  padding: 24px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.chart-header h3 {
  color: #fff;
  font-size: 18px;
  font-weight: 600;
  margin: 0;
}

.chart-container {
  height: 300px;
  width: 100%;
}

/* 最近订单卡片 */
.recent-orders-card {
  border-radius: 20px;
  backdrop-filter: blur(20px);
  background: rgba(255, 255, 255, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  padding: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.card-header h3 {
  color: #fff;
  font-size: 18px;
  font-weight: 600;
  margin: 0;
}

/* 渐变表格 */
.gradient-table {
  --el-table-bg-color: transparent;
  --el-table-tr-bg-color: transparent;
  --el-table-header-bg-color: rgba(255,255,255,0.1);
  --el-table-text-color: rgba(255,255,255,0.9);
  --el-table-header-text-color: rgba(255,255,255,0.8);
  --el-table-border-color: rgba(255,255,255,0.1);
  --el-table-row-hover-bg-color: rgba(255,255,255,0.1);
}

.price-text {
  color: #43e97b;
  font-weight: 700;
  font-size: 15px;
}

/* Element Plus 组件覆盖 */
:deep(.el-radio-button__inner) {
  background: rgba(255, 255, 255, 0.1);
  border: none;
  color: rgba(255, 255, 255, 0.8);
}

:deep(.el-radio-button__original-radio:checked + .el-radio-button__inner) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
}

:deep(.el-button--primary.is-link) {
  color: #4facfe;
}

:deep(.el-tag--dark) {
  border: none;
}
</style>
