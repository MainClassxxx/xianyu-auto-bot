<template>
  <div class="auto-delivery-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>自动发货规则</span>
          <el-button type="primary" @click="showAddDialog = true">
            <el-icon><Plus /></el-icon> 添加规则
          </el-button>
        </div>
      </template>

      <el-table :data="rules" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="规则名称" width="150" />
        <el-table-column prop="keyword" label="关键词" />
        <el-table-column prop="delivery_content" label="发货内容" show-overflow-tooltip />
        <el-table-column prop="stock" label="库存" width="100">
          <template #default="{ row }">{{ row.stock === -1 ? '∞' : row.stock }}</template>
        </el-table-column>
        <el-table-column prop="enabled" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.enabled ? 'success' : 'info'">{{ row.enabled ? '启用' : '禁用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="toggleRule(row)">{{ row.enabled ? '禁用' : '启用' }}</el-button>
            <el-button type="danger" size="small" @click="deleteRule(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="showAddDialog" title="添加自动发货规则" width="600px">
      <el-form :model="newRule" label-width="100px">
        <el-form-item label="规则名称">
          <el-input v-model="newRule.name" placeholder="例如：教程自动发货" />
        </el-form-item>
        <el-form-item label="关键词">
          <el-input v-model="newRule.keyword" placeholder="匹配商品的关键词" />
        </el-form-item>
        <el-form-item label="发货内容">
          <el-input v-model="newRule.delivery_content" type="textarea" :rows="4" placeholder="发货内容" />
        </el-form-item>
        <el-form-item label="库存">
          <el-input-number v-model="newRule.stock" :min="-1" :disabled="newRule.stock === -1" />
          <span style="margin-left: 10px; color: #909399;">-1 表示无限库存</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="addRule">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const showAddDialog = ref(false)

const rules = ref([
  { id: 1, name: '教程自动发货', keyword: '教程', delivery_content: '链接：https://example.com', stock: -1, enabled: true }
])

const newRule = ref({ name: '', keyword: '', delivery_content: '', stock: -1 })

const addRule = () => {
  rules.value.push({ id: rules.value.length + 1, ...newRule.value, enabled: true })
  ElMessage.success('规则添加成功')
  showAddDialog.value = false
  newRule.value = { name: '', keyword: '', delivery_content: '', stock: -1 }
}

const toggleRule = (rule) => { rule.enabled = !rule.enabled }
const deleteRule = (rule) => {
  rules.value = rules.value.filter(r => r.id !== rule.id)
  ElMessage.success('删除成功')
}
</script>

<style scoped>
.auto-delivery-page { padding: 20px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>
