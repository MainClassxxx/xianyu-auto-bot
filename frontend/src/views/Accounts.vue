<template>
  <div class="accounts-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>闲鱼账号列表</span>
          <div style="display: flex; gap: 10px;">
            <el-button type="success" @click="openXianyuLogin">
              <el-icon><FishFish /></el-icon>
              闲鱼登录
            </el-button>
            <el-button type="primary" @click="showAddDialog = true">
              <el-icon><Plus /></el-icon>
              手动添加
            </el-button>
          </div>
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

    <!-- 闲鱼扫码登录对话框 -->
    <el-dialog
      v-model="showXianyuLogin"
      title="闲鱼扫码登录"
      width="450px"
      :close-on-click-modal="false"
    >
      <div class="xianyu-login-container">
        <div v-loading="loginStatus === 'waiting'" element-loading-text="等待扫码中...">
          <!-- 显示二维码 -->
          <div v-if="qrCodeUrl" class="qr-code-container">
            <img :src="qrCodeUrl" alt="登录二维码" class="qr-code-image" />
            <p class="qr-hint">请使用闲鱼 APP 扫描二维码</p>
          </div>
          
          <!-- 登录状态 -->
          <div class="login-status-section">
            <div v-if="loginStatus === 'waiting'" class="status-waiting">
              <el-icon class="is-loading" :size="40"><Loading /></el-icon>
              <p>等待扫码登录...</p>
            </div>
            
            <div v-if="loginStatus === 'success'" class="status-success">
              <el-icon :size="40" color="#67C23A"><SuccessFilled /></el-icon>
              <p>登录成功！</p>
              <p class="user-info">👤 {{ userInfo.nick }}</p>
            </div>
            
            <div v-if="loginStatus === 'error'" class="status-error">
              <el-icon :size="40" color="#F56C6C"><CircleClose /></el-icon>
              <p>登录失败：{{ errorMessage }}</p>
            </div>
          </div>
        </div>
        
        <div class="login-actions">
          <el-button @click="cancelXianyuLogin" :disabled="loginStatus === 'success'">取消</el-button>
        </div>
      </div>
    </el-dialog>


  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAccountStore } from '@/store/account'
import axios from 'axios'

const accountStore = useAccountStore()
const showAddDialog = ref(false)
const submitting = ref(false)

// 闲鱼登录相关
const showXianyuLogin = ref(false)
const loginSessionId = ref('')
const loginStatus = ref('waiting') // waiting, success, error
const userInfo = ref({ nick: '' })
const errorMessage = ref('')
const qrCodeUrl = ref('')
let checkInterval = null

const newAccount = ref({
  name: '',
  cookie: '',
  device_id: ''
})

onMounted(() => {
  accountStore.fetchAccounts()
})

// 打开闲鱼登录（扫码登录）
const openXianyuLogin = async () => {
  try {
    const response = await axios.post('http://localhost:8080/api/auth/xianyu/qr', { headless: false })
    loginSessionId.value = response.data.session_id
    const qrCode = response.data.qr_code
    
    // 显示二维码而不是打开新窗口
    showXianyuLogin.value = true
    loginStatus.value = 'waiting'
    qrCodeUrl.value = qrCode
    
    // 定时检查登录状态
    checkInterval = setInterval(checkLoginStatus, 2000)
    
    ElMessage.info('请使用闲鱼 APP 扫描二维码登录')
  } catch (error) {
    console.error('闲鱼登录失败:', error)
    ElMessage.error('生成二维码失败：' + error.message)
  }
}

// 检查登录状态
const checkLoginStatus = async () => {
  if (!loginSessionId.value) return
  
  try {
    const response = await axios.get(`http://localhost:8080/api/auth/xianyu/${loginSessionId.value}/status`)
    const result = response.data
    
    if (result.status === 'logged_in') {
      // 验证 Cookie 是否有效
      if (!result.cookie || result.cookie.length < 10) {
        console.error('Cookie 无效:', result.cookie)
        loginStatus.value = 'error'
        errorMessage.value = '登录成功但未获取到有效 Cookie，请重试'
        clearInterval(checkInterval)
        return
      }
      
      // 登录成功
      clearInterval(checkInterval)
      loginStatus.value = 'success'
      userInfo.value = result.user_info || { nick: 'Unknown' }
      
      console.log('✅ 登录成功，准备保存账号')
      console.log('Cookie 长度:', result.cookie?.length)
      console.log('用户信息:', result.user_info)
      
      // 自动添加账号
      await addAccountFromLogin(result.cookie, result.user_info)
      
      // 2 秒后关闭对话框
      setTimeout(() => {
        showXianyuLogin.value = false
        cancelXianyuLogin()
      }, 2000)
    } else if (result.status === 'error') {
      // 登录出错
      clearInterval(checkInterval)
      loginStatus.value = 'error'
      errorMessage.value = result.message || '未知错误'
    }
  } catch (error) {
    console.error('检查登录状态失败:', error)
  }
}

const addAccountFromLogin = async (cookie, user_info) => {
  try {
    // 再次验证 Cookie
    if (!cookie || cookie.trim().length < 10) {
      throw new Error('Cookie 为空或过短')
    }
    
    await accountStore.addAccount({
      name: user_info?.nick || '闲鱼账号',
      cookie: cookie,
      device_id: `device_${Date.now()}`
    })
    ElMessage.success('✅ 账号添加成功！')
  } catch (error) {
    console.error('添加账号失败:', error)
    ElMessage.error('添加账号失败：' + error.message)
  }
}

// 取消登录
const cancelXianyuLogin = () => {
  if (checkInterval) {
    clearInterval(checkInterval)
    checkInterval = null
  }
  if (loginSessionId.value) {
    axios.delete(`http://localhost:8080/api/auth/xianyu/${loginSessionId.value}`).catch(() => {})
    loginSessionId.value = ''
  }
  loginStatus.value = 'waiting'
  userInfo.value = { nick: '' }
  errorMessage.value = ''
  qrCodeUrl.value = ''
}

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

.xianyu-login-container {
  padding: 20px;
}

.qr-code-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
  margin-bottom: 20px;
}

.qr-code-image {
  width: 280px;
  height: 280px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.qr-hint {
  font-size: 14px;
  color: #606266;
  margin: 0;
}

.login-status-section {
  text-align: center;
  padding: 20px 0;
}

.status-waiting,
.status-success,
.status-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.status-waiting p,
.status-success p,
.status-error p {
  font-size: 15px;
  color: #606266;
}

.user-info {
  font-size: 16px;
  font-weight: bold;
  color: #67C23A;
  margin-top: 5px;
}

.login-actions {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-top: 20px;
}
</style>
