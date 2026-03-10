<template>
  <div class="accounts-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>闲鱼账号列表</span>
          <el-button type="primary" @click="showAddDialog = true">
            <el-icon><Plus /></el-icon>
            添加账号
          </el-button>
        </div>
      </template>

      <el-table :data="accountStore.accounts" v-loading="accountStore.loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="账号备注" width="150" />
        <el-table-column prop="device_id" label="设备 ID" width="150" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'danger'">
              {{ row.status === 'active' ? '正常' : '异常' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="添加时间" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleRefresh(row)">刷新</el-button>
            <el-button type="danger" size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 添加账号对话框 -->
    <el-dialog v-model="showAddDialog" title="添加闲鱼账号" width="500px">
      <el-form :model="newAccount" label-width="80px">
        <el-form-item label="账号备注">
          <el-input v-model="newAccount.name" placeholder="例如：主账号" />
        </el-form-item>
        <el-form-item label="Cookie" required>
          <el-input
            v-model="newAccount.cookie"
            type="textarea"
            :rows="5"
            placeholder="从浏览器 F12 Network 中复制 Cookie"
          />
        </el-form-item>
        <el-form-item label="设备 ID">
          <el-input v-model="newAccount.device_id" placeholder="可选，默认自动生成" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleAdd">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAccountStore } from '@/store/account'

const accountStore = useAccountStore()
const showAddDialog = ref(false)
const submitting = ref(false)

const newAccount = ref({
  name: '',
  cookie: '',
  device_id: ''
})

onMounted(() => {
  accountStore.fetchAccounts()
})

const handleAdd = async () => {
  if (!newAccount.value.cookie) {
    ElMessage.warning('请填写 Cookie')
    return
  }
  
  submitting.value = true
  try {
    await accountStore.addAccount(newAccount.value)
    ElMessage.success('账号添加成功')
    showAddDialog.value = false
    newAccount.value = { name: '', cookie: '', device_id: '' }
  } catch (error) {
    ElMessage.error('添加失败：' + error.message)
  } finally {
    submitting.value = false
  }
}

const handleRefresh = async (account) => {
  try {
    await accountStore.refreshAccount(account.id)
    ElMessage.success('刷新成功')
  } catch (error) {
    ElMessage.error('刷新失败：' + error.message)
  }
}

const handleDelete = (account) => {
  ElMessageBox.confirm(
    `确定要删除账号"${account.name}"吗？`,
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await accountStore.deleteAccount(account.id)
      ElMessage.success('删除成功')
    } catch (error) {
      ElMessage.error('删除失败：' + error.message)
    }
  })
}
</script>

<style scoped>
.accounts-page {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
