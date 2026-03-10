<template>
  <div class="items-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>商品管理</span>
          <el-input v-model="searchKeyword" placeholder="搜索商品" style="width: 200px;" clearable />
        </div>
      </template>

      <el-table :data="items" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="title" label="商品标题" />
        <el-table-column prop="price" label="价格" width="100">
          <template #default="{ row }">¥{{ row.price }}</template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="editPrice(row)">改价</el-button>
            <el-button type="warning" size="small" @click="toggleItem(row)">下架</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const searchKeyword = ref('')

const items = ref([
  { id: 1, title: 'AI 绘画提示词教程', price: 29.9, status: 'onsale' },
  { id: 2, title: 'Python 入门教程', price: 49.9, status: 'onsale' },
  { id: 3, title: '电影票代下单', price: 35.0, status: 'sold' }
])

const getStatusType = (status) => {
  const types = { 'onsale': 'success', 'sold': 'info', 'out': 'danger' }
  return types[status] || 'info'
}

const getStatusText = (status) => {
  const texts = { 'onsale': '在售', 'sold': '已售', 'out': '下架' }
  return texts[status] || status
}

const editPrice = (item) => {
  ElMessage.info(`修改商品 ${item.title} 价格`)
}

const toggleItem = (item) => {
  ElMessage.info(`切换商品 ${item.title} 状态`)
}
</script>

<style scoped>
.items-page { padding: 20px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>
