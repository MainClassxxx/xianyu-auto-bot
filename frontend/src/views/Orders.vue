<template>
  <div class="orders-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>订单管理</span>
          <el-radio-group v-model="statusFilter" size="small">
            <el-radio-button label="">全部</el-radio-button>
            <el-radio-button label="pending">待发货</el-radio-button>
            <el-radio-button label="paid">已付款</el-radio-button>
            <el-radio-button label="shipped">已发货</el-radio-button>
          </el-radio-group>
        </div>
      </template>

      <el-table :data="orders" style="width: 100%">
        <el-table-column prop="order_id" label="订单号" width="180" />
        <el-table-column prop="buyer_name" label="买家" width="120" />
        <el-table-column prop="item_title" label="商品" />
        <el-table-column prop="price" label="金额" width="100">¥{{ row.price }}</el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.status === 'paid'" type="primary" size="small" @click="deliver(row)">发货</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const statusFilter = ref('')

const orders = ref([
  { order_id: 'ORD20240310001', buyer_name: '张***3', item_title: 'AI 教程', price: 29.9, status: 'paid' },
  { order_id: 'ORD20240310002', buyer_name: '李***8', item_title: 'Python 教程', price: 49.9, status: 'pending' }
])

const getStatusType = (status) => {
  const types = { 'pending': 'warning', 'paid': 'success', 'shipped': 'primary', 'completed': 'info' }
  return types[status] || 'info'
}

const getStatusText = (status) => {
  const texts = { 'pending': '待发货', 'paid': '已付款', 'shipped': '已发货', 'completed': '已完成' }
  return texts[status] || status
}

const deliver = (order) => {
  ElMessage.success(`订单 ${order.order_id} 发货成功`)
}
</script>

<style scoped>
.orders-page { padding: 20px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>
