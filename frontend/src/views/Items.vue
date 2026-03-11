<template>
  <div class="items-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>📦 商品管理</span>
          <div style="display: flex; gap: 10px;">
            <el-select v-model="selectedAccount" placeholder="选择账号" style="width: 150px;" @change="loadItems">
              <el-option v-for="acc in accounts" :key="acc.id" :label="acc.name" :value="acc.id" />
            </el-select>
            <el-input v-model="searchKeyword" placeholder="搜索商品" style="width: 200px;" clearable @input="filterItems" />
          </div>
        </div>
      </template>

      <el-table :data="filteredItems" v-loading="loading" style="width: 100%">
        <el-table-column prop="item_id" label="商品 ID" width="120" />
        <el-table-column prop="title" label="商品标题" min-width="250" show-overflow-tooltip />
        <el-table-column prop="price" label="价格" width="100">
          <template #default="{ row }">
            <span class="price">¥{{ row.price }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="original_price" label="原价" width="100">
          <template #default="{ row }">
            <span v-if="row.original_price" class="original-price">¥{{ row.original_price }}</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="showPriceEdit(row)">改价</el-button>
            <el-button :type="row.status === 'onsale' ? 'warning' : 'success'" size="small" @click="toggleItem(row)">
              {{ row.status === 'onsale' ? '下架' : '上架' }}
            </el-button>
            <el-button type="info" size="small" @click="viewItem(row)">详情</el-button>
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
          @change="loadItems"
        />
      </div>
    </el-card>

    <!-- 改价对话框 -->
    <el-dialog v-model="priceDialogVisible" title="修改价格" width="400px">
      <el-form :model="priceForm" label-width="80px">
        <el-form-item label="商品">
          <div>{{ currentItem.title }}</div>
        </el-form-item>
        <el-form-item label="当前价">
          <span class="current-price">¥{{ currentItem.price }}</span>
        </el-form-item>
        <el-form-item label="新价格" required>
          <el-input-number v-model="priceForm.price" :min="0" :precision="2" :step="0.1" style="width: 100%;" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="priceDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="priceSubmitting" @click="submitPrice">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'
import { useAccountStore } from '@/store/account'

const accountStore = useAccountStore()
const loading = ref(false)
const searchKeyword = ref('')
const selectedAccount = ref(null)
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const accounts = computed(() => accountStore.accounts)
const items = ref([])

const filteredItems = computed(() => {
  if (!searchKeyword.value) return items.value
  return items.value.filter(item =>
    item.title?.toLowerCase().includes(searchKeyword.value.toLowerCase())
  )
})

const priceDialogVisible = ref(false)
const priceSubmitting = ref(false)
const currentItem = ref({})
const priceForm = reactive({
  price: 0
})

onMounted(() => {
  accountStore.fetchAccounts()
})

async function loadItems() {
  if (!selectedAccount.value) {
    items.value = []
    return
  }

  loading.value = true
  try {
    const response = await axios.get('http://localhost:8080/api/items', {
      params: {
        account_id: selectedAccount.value,
        page: currentPage.value,
        page_size: pageSize.value
      }
    })
    items.value = response.data || []
    total.value = items.value.length
  } catch (error) {
    ElMessage.error('加载商品失败：' + error.message)
    items.value = []
  } finally {
    loading.value = false
  }
}

function filterItems() {
  // 前端过滤
}

function getStatusType(status) {
  const types = { 'onsale': 'success', 'sold': 'info', 'out': 'danger' }
  return types[status] || 'info'
}

function getStatusText(status) {
  const texts = { 'onsale': '在售', 'sold': '已售', 'out': '下架' }
  return texts[status] || status
}

function showPriceEdit(item) {
  currentItem.value = { ...item }
  priceForm.price = item.price
  priceDialogVisible.value = true
}

async function submitPrice() {
  if (!selectedAccount.value || priceForm.price <= 0) {
    ElMessage.warning('请输入有效价格')
    return
  }

  priceSubmitting.value = true
  try {
    await axios.post(
      `http://localhost:8080/api/items/${currentItem.value.item_id}/price`,
      { price: priceForm.price },
      { params: { account_id: selectedAccount.value } }
    )
    ElMessage.success('改价成功')
    priceDialogVisible.value = false
    loadItems()
  } catch (error) {
    ElMessage.error('改价失败：' + error.message)
  } finally {
    priceSubmitting.value = false
  }
}

async function toggleItem(item) {
  const action = item.status === 'onsale' ? 'offshelf' : 'onshelf'
  const actionText = item.status === 'onsale' ? '下架' : '上架'

  try {
    await ElMessageBox.confirm(
      `确定要${actionText}商品"${item.title}"吗？`,
      '提示',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
    )

    await axios.post(
      `http://localhost:8080/api/items/${item.item_id}/toggle`,
      { action },
      { params: { account_id: selectedAccount.value } }
    )

    ElMessage.success(`${actionText}成功`)
    loadItems()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(`${actionText}失败：` + error.message)
    }
  }
}

function viewItem(item) {
  ElMessage.info('查看商品详情：' + item.title)
}
</script>

<style scoped>
.items-page {
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

.original-price {
  color: #909399;
  text-decoration: line-through;
  font-size: 13px;
}

.current-price {
  font-size: 18px;
  color: #F56C6C;
  font-weight: bold;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
