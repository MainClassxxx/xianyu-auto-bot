<template>
  <div class="dashboard">
    <!-- 统计卡片 -->
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon primary">
              <el-icon :size="30"><User /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.accounts?.active || 0 }}</div>
              <div class="stat-label">在线账号</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon success">
              <el-icon :size="30"><ShoppingCart /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.items?.onsale || 0 }}</div>
              <div class="stat-label">在售商品</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon warning">
              <el-icon :size="30"><List /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.overview?.pending_orders || 0 }}</div>
              <div class="stat-label">待发货订单</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon danger">
              <el-icon :size="30"><Money /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.overview?.formatted_revenue || '¥0.00' }}</div>
              <div class="stat-label">今日收入</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>📈 订单趋势</span>
              <el-radio-group v-model="orderPeriod" size="small" @change="loadOrderStats">
                <el-radio-button label="7">近 7 天</el-radio-button>
                <el-radio-button label="30">近 30 天</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div ref="orderChartRef" class="chart-container"></div>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>💰 收入统计</span>
              <el-radio-group v-model="revenuePeriod" size="small" @change="loadRevenueStats">
                <el-radio-button label="7">近 7 天</el-radio-button>
                <el-radio-button label="30">近 30 天</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div ref="revenueChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 最近订单 -->
    <el-card style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>📦 最近订单</span>
          <el-button type="primary" link @click="$router.push('/orders')">查看全部</el-button>
        </div>
      </template>

      <el-table :data="recentOrders" v-loading="loading" style="width: 100%">
        <el-table-column prop="order_id" label="订单号" width="180" />
        <el-table-column prop="buyer_name" label="买家" width="120" />
        <el-table-column prop="item_title" label="商品" />
        <el-table-column prop="price" label="金额" width="100">
          <template #default="{ row }">
            <span class="price">¥{{ row.price }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="时间" width="180" />
      </el-table>
    </el-card>

    <!-- 账号状态 -->
    <el-card style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>👥 账号状态</span>
          <el-button type="primary" link @click="$router.push('/accounts')">管理账号</el-button>
        </div>
      </template>

      <el-row :gutter="20">
        <el-col :span="8">
          <div class="account-stat">
            <div class="account-stat-value">{{ stats.accounts?.total || 0 }}</div>
            <div class="account-stat-label">总账号数</div>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="account-stat">
            <div class="account-stat-value success">{{ stats.accounts?.active || 0 }}</div>
            <div class="account-stat-label">正常</div>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="account-stat">
            <div class="account-stat-value danger">{{ stats.accounts?.inactive || 0 }}</div>
            <div class="account-stat-label">异常</div>
          </div>
        </el-col>
      </el-row>
    </el-card>
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
    stats.accounts = await statsApi.getAccountStats()
    stats.items = await statsApi.getItemStats()
  } catch (error) {
    console.error('加载统计数据失败:', error)
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
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'category',
      data: ['待付款', '已付款', '待发货', '已发货', '已完成', '已退款']
    },
    yAxis: { type: 'value' },
    series: [{
      name: '订单数',
      type: 'bar',
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
          { offset: 0, color: '#83bff6' },
          { offset: 1, color: '#188df0' }
        ])
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
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'category',
      data: daily.map(d => d.date)
    },
    yAxis: { type: 'value' },
    series: [{
      name: '收入',
      type: 'line',
      data: daily.map(d => d.revenue),
      smooth: true,
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(103, 194, 58, 0.5)' },
          { offset: 1, color: 'rgba(103, 194, 58, 0.1)' }
        ])
      },
      itemStyle: { color: '#67C23A' }
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
  
  // 窗口大小变化时重新渲染图表
  window.addEventListener('resize', () => {
    orderChart?.resize()
    revenueChart?.resize()
  })
})
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.stat-card {
  border-radius: 12px;
  transition: transform 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 15px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.stat-icon.primary { background: linear-gradient(135deg, #409EFF 0%, #337ecc 100%); }
.stat-icon.success { background: linear-gradient(135deg, #67C23A 0%, #529b2e 100%); }
.stat-icon.warning { background: linear-gradient(135deg, #E6A23C 0%, #b88230 100%); }
.stat-icon.danger { background: linear-gradient(135deg, #F56C6C 0%, #c45656 100%); }

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-container {
  height: 300px;
  width: 100%;
}

.price {
  color: #F56C6C;
  font-weight: 600;
}

.account-stat {
  text-align: center;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.account-stat-value {
  font-size: 36px;
  font-weight: bold;
  color: #303133;
}

.account-stat-value.success {
  color: #67C23A;
}

.account-stat-value.danger {
  color: #F56C6C;
}

.account-stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 8px;
}
</style>
