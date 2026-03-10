<template>
  <div class="auto-reply-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>自动回复规则</span>
          <el-button type="primary" @click="showAddDialog = true">
            <el-icon><Plus /></el-icon> 添加规则
          </el-button>
        </div>
      </template>

      <el-table :data="rules" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="规则名称" width="150" />
        <el-table-column prop="keyword" label="关键词" width="200" />
        <el-table-column prop="match_type" label="匹配方式" width="100">
          <template #default="{ row }">
            <el-tag size="small">{{ row.match_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="reply_content" label="回复内容" />
        <el-table-column prop="enabled" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.enabled ? 'success' : 'info'">{{ row.enabled ? '启用' : '禁用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="toggleRule(row)">
              {{ row.enabled ? '禁用' : '启用' }}
            </el-button>
            <el-button type="danger" size="small" @click="deleteRule(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="showAddDialog" title="添加自动回复规则" width="600px">
      <el-form :model="newRule" label-width="100px">
        <el-form-item label="规则名称">
          <el-input v-model="newRule.name" placeholder="例如：欢迎语" />
        </el-form-item>
        <el-form-item label="关键词">
          <el-input v-model="newRule.keyword" placeholder="匹配关键词" />
        </el-form-item>
        <el-form-item label="匹配方式">
          <el-select v-model="newRule.match_type">
            <el-option label="包含关键词" value="contains" />
            <el-option label="精确匹配" value="exact" />
            <el-option label="正则匹配" value="regex" />
            <el-option label="AI 回复" value="ai" />
          </el-select>
        </el-form-item>
        <el-form-item label="回复内容">
          <el-input v-model="newRule.reply_content" type="textarea" :rows="4" placeholder="回复内容" />
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
  { id: 1, name: '欢迎语', keyword: '你好', match_type: 'contains', reply_content: '您好，欢迎光临！', enabled: true },
  { id: 2, name: '发货说明', keyword: '发货', match_type: 'contains', reply_content: '虚拟商品自动发货，付款后秒发！', enabled: true }
])

const newRule = ref({ name: '', keyword: '', match_type: 'contains', reply_content: '' })

const addRule = () => {
  rules.value.push({ id: rules.value.length + 1, ...newRule.value, enabled: true })
  ElMessage.success('规则添加成功')
  showAddDialog.value = false
  newRule.value = { name: '', keyword: '', match_type: 'contains', reply_content: '' }
}

const toggleRule = (rule) => {
  rule.enabled = !rule.enabled
  ElMessage.success(rule.enabled ? '规则已启用' : '规则已禁用')
}

const deleteRule = (rule) => {
  rules.value = rules.value.filter(r => r.id !== rule.id)
  ElMessage.success('删除成功')
}
</script>

<style scoped>
.auto-reply-page { padding: 20px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>
