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

    <!-- 闲鱼登录对话框 -->
    <el-dialog
      v-model="showXianyuLogin"
      title="闲鱼账号登录"
      width="800px"
      :close-on-click-modal="false"
    >
      <div class="xianyu-login-container">
        <el-alert
          title="在打开的浏览器窗口中登录闲鱼账号"
          description="登录成功后，点击下方的'我已登录完成'按钮"
          type="info"
          :closable="false"
          show-icon
        />
        
        <div class="login-content">
          <div v-if="loginStatus === 'waiting'" class="login-waiting">
            <el-icon class="is-loading" :size="50"><Loading /></el-icon>
            <p>等待登录...</p>
            <el-button type="primary" @click="showCompleteDialog">
              <el-icon><Check /></el-icon>
              我已登录完成
            </el-button>
          </div>
          
          <div v-if="loginStatus === 'success'" class="login-success">
            <el-icon :size="50" color="#67C23A"><SuccessFilled /></el-icon>
            <p>登录成功！</p>
            <p class="user-info">{{ userInfo.nick }}</p>
          </div>
          
          <div v-if="loginStatus === 'error'" class="login-error">
            <el-icon :size="50" color="#F56C6C"><CircleClose /></el-icon>
            <p>登录失败：{{ errorMessage }}</p>
          </div>
        </div>
        
        <div class="login-actions">
          <el-button @click="cancelXianyuLogin">取消</el-button>
        </div>
      </div>
    </el-dialog>

    <!-- 手动完成登录对话框 -->
    <el-dialog
      v-model="showCompleteDlg"
      title="完成闲鱼登录"
      width="600px"
    >
      <el-form :model="completeForm" label-width="100px">
        <el-form-item label="账号备注">
          <el-input v-model="completeForm.nick" placeholder="例如：主账号" />
        </el-form-item>
        <el-form-item label="Cookie" required>
          <el-input
            v-model="completeForm.cookie"
            type="textarea"
            :rows="5"
            placeholder="按 F12 打开开发者工具 → Network → 复制 Cookie"
          />
          <el-link type="primary" style="margin-top: 8px;" @click="showCookieGuide = true">
            如何获取 Cookie？
          </el-link>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCompleteDlg = false">取消</el-button>
        <el-button type="primary" :loading="completing" @click="submitComplete">
          完成登录
        </el-button>
      </template>
    </el-dialog>

    <!-- Cookie 获取指引 -->
    <el-dialog
      v-model="showCookieGuide"
      title="如何获取 Cookie"
      width="700px"
    >
      <div class="cookie-guide">
        <h4>📝 步骤：</h4>
        <ol>
          <li>在刚才打开的窗口中登录闲鱼账号</li>
          <li>按 <kbd>F12</kbd> 打开开发者工具</li>
          <li>切换到 <kbd>Network</kbd> 标签</li>
          <li>刷新页面或点击任意商品</li>
          <li>在请求列表中找到任意请求</li>
          <li>在右侧 Headers 中找到 <kbd>Cookie</kbd> 字段</li>
          <li>复制整个 Cookie 值并粘贴到上方输入框</li>
        </ol>

        <el-alert
          title="💡 提示"
          description="Cookie 是敏感信息，请妥善保管，不要分享给他人"
          type="info"
          :closable="false"
          show-icon
          style="margin-top: 16px;"
        />
      </div>
      <template #footer>
        <el-button type="primary" @click="showCookieGuide = false">我知道了</el-button>
      </template>
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
let checkInterval = null

const newAccount = ref({
  name: '',
  cookie: '',
  device_id: ''
})

// 手动完成登录相关
const showCompleteDlg = ref(false)
const showCookieGuide = ref(false)
const completing = ref(false)
const completeForm = ref({
  nick: '',
  cookie: ''
})

onMounted(() => {
  accountStore.fetchAccounts()
})

// 打开闲鱼登录
const openXianyuLogin = async () => {
  try {
    const response = await axios.post('http://localhost:8080/api/auth/xianyu', { headless: false })
    loginSessionId.value = response.data.session_id
    const loginUrl = response.data.login_url
    
    // 打开新窗口
    window.open(loginUrl, '_blank')
    
    // 显示登录对话框
    showXianyuLogin.value = true
    loginStatus.value = 'waiting'
    
    // 定时检查登录状态
    checkInterval = setInterval(checkLoginStatus, 2000)
    
    ElMessage.info('请在新打开的窗口中登录闲鱼账号')
  } catch (error) {
    console.error('闲鱼登录失败:', error)
    ElMessage.error('闲鱼登录功能开发中，请使用手动添加 Cookie 方式')
  }
}

// 检查登录状态
const checkLoginStatus = async () => {
  if (!loginSessionId.value) return
  
  try {
    const response = await axios.get(`http://localhost:8080/api/auth/xianyu/${loginSessionId.value}`)
    const result = response.data
    
    if (result.status === 'logged_in') {
      // 登录成功
      clearInterval(checkInterval)
      loginStatus.value = 'success'
      userInfo.value = result.user_info || { nick: 'Unknown' }
      
      // 自动添加账号
      await addAccountFromLogin(result.cookie, result.user_info)
      
      // 2 秒后关闭对话框
      setTimeout(() => {
        showXianyuLogin.value = false
        cancelXianyuLogin()
      }, 2000)
    }
  } catch (error) {
    console.error('检查登录状态失败:', error)
  }
}

// 手动完成登录
const showCompleteDialog = () => {
  completeForm.value = { nick: '', cookie: '' }
  showCompleteDlg.value = true
}

const submitComplete = async () => {
  if (!completeForm.value.cookie) {
    ElMessage.warning('请填写 Cookie')
    return
  }

  completing.value = true
  try {
    // 调用后端 API 标记为已登录
    await axios.post(
      `http://localhost:8080/api/auth/xianyu/${loginSessionId.value}/complete`,
      null,
      {
        params: {
          cookie: completeForm.value.cookie,
          nick: completeForm.value.nick || '闲鱼用户'
        }
      }
    )

    // 添加账号
    await addAccountFromLogin(completeForm.value.cookie, {
      nick: completeForm.value.nick || '闲鱼用户'
    })

    showCompleteDlg.value = false
  } catch (error) {
    ElMessage.error('完成登录失败：' + error.message)
  } finally {
    completing.value = false
  }
}
const addAccountFromLogin = async (cookie, user_info) => {
  try {
    await accountStore.addAccount({
      name: user_info.nick || '闲鱼账号',
      cookie: cookie,
      device_id: `device_${Date.now()}`
    })
    ElMessage.success('账号添加成功！')
  } catch (error) {
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

.login-content {
  padding: 40px 0;
  text-align: center;
}

.login-waiting,
.login-success,
.login-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
}

.login-waiting p,
.login-success p,
.login-error p {
  font-size: 16px;
  color: #606266;
}

.user-info {
  font-size: 18px;
  font-weight: bold;
  color: #67C23A;
}

.login-actions {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-top: 20px;
}
</style>
