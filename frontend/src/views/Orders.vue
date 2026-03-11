<template>
  <div class="orders-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>📋 订单管理</span>
          <div style="display: flex; gap: 10px;">
            <el-select v-model="selectedAccount" placeholder="选择账号" style="width: 150px;" @change="loadOrders">
              <el-option v-for="acc in accounts" :key="acc.id" :label="acc.name" :value="acc.id" />
            </el-select>
            <el-select v-model="statusFilter" placeholder="状态筛选" style="width: 120px;" clearable @change="loadOrders">
              <el-option label="待付款" value="pending" />
              <el-option label="已付款" value="paid" />
              <el-option label="待发货" value="paid" />
              <el-option label="已发货" value="shipped" />
              <el-option label="已完成" value="completed" />
            </el-select>
            <el-button type="primary" @click="loadOrders">刷新</el-button>
          </div>
        </div>
      </template>

      <el-table :data="orders" v-loading="loading" style="width: 100%">
        <el-table-column prop="order_id" label="订单号" width="180" />
        <el-table-column prop="buyer_name" label="买家" width="120" />
        <el-table-column prop="item_title" label="商品" min-width="200" show-overflow-tooltip />
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
        <el-table-column prop="created_at" label="下单时间" width="180" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'paid'"
              type="success"
              size="small"
              @click="showDelivery(row)"
            >
              发货
            </el-button>
            <el-button type="primary" size="small" @click="viewOrder(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination" v-if="total > pageSize">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next"
          :total="total"
          @change="loadOrders"
        />
      </div>
    </el-card>

    <!-- 发货对话框 -->
    <el-dialog v-model="deliveryDialogVisible" title="订单发货" width="500px">
      <el-form :model="deliveryForm" label-width="80px">
        <el-form-item label="订单号">
          <div>{{ currentOrder.order_id }}</div>
        </el-form-item>
        <el-form-item label="商品">
          <div>{{ currentOrder.item_title }}</div>
        </el-form-item>
        <el-form-item label="买家">
          <div>{{ currentOrder.buyer_name }}</div>
        </el-form-item>
        <el-form-item label="发货内容" required>
          <el-input
            v-model="deliveryForm.content"
            type="textarea"
            :rows="6"
            placeholder="输入发货内容，如：百度网盘链接：https://pan.baidu.com/s/xxx 提取码：xxxx"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="deliveryDialogVisible = false">取消</el-button>
        <el-button type="success" :loading="deliverySubmitting" @click="submitDelivery">确认发货</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import { useAccountStore } from '@/store/account'

const accountStore = useAccountStore()
const loading = ref(false)
const selectedAccount = ref(null)
const statusFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const accounts = computed(() => accountStore.accounts)
const orders = ref([])

const deliveryDialogVisible = ref(false)
const deliverySubmitting = ref(false)
const currentOrder = ref({})
const deliveryForm = reactive({
  content: ''
})

onMounted(() => {
  accountStore.fetchAccounts()
})

async function loadOrders() {
  if (!selectedAccount.value) {
    orders.value = []
    return
  }

  loading.value = true
  try {
    const response = await axios.get('http://localhost:8080/api/orders', {
      params: {
        account_id: selectedAccount.value,
        status: statusFilter.value || undefined,
        page: currentPage.value,
        page_size: pageSize.value
      }
    })
    orders.value = response.data || []
    total.value = orders.value.length
  } catch (error) {
    ElMessage.error('加载订单失败：' + error.message)
    orders.value = []
  } finally {
    loading.value = false
  }
}

function getStatusType(status) {
  const types = {
    'pending': 'warning',
    'paid': 'success',
    'shipped': 'primary',
    'completed': 'info',
    'refunded': 'danger'
  }
  return types[status] || 'info'
}

function getStatusText(status) {
  const texts = {
    'pending': '待付款',
    'paid': '待发货',
    'shipped': '已发货',
    'completed': '已完成',
    'refunded': '已退款'
  }
  return texts[status] || status
}

function showDelivery(order) {
  currentOrder.value = { ...order }
  deliveryForm.content = ''
  deliveryDialogVisible.value = true
}

async function submitDelivery() {
  if (!deliveryForm.content.trim()) {
    ElMessage.warning('请填写发货内容')
    return
  }

  deliverySubmitting.value = true
  try {
    await axios.post(
      `http://localhost:8080/api/orders/${currentOrder.value.order_id}/deliver`,
      { content: deliveryForm.content },
      { params: { account_id: selectedAccount.value } }
    )
    ElMessage.success('发货成功')
    deliveryDialogVisible.value = false
    loadOrders()
  } catch (error) {
    ElMessage.error('发货失败：' + error.message)
  } finally {
    deliverySubmitting.value = false
  }
}

function viewOrder(order) {
  ElMessage.info('查看订单详情：' + order.order_id)
}
</script>

<style scoped>
.orders-page {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}

.price {
  color: #F56C6C;
  font-weight: 600;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
