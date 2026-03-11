<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <div class="logo">🥫</div>
        <h1>闲鱼自动售货机器人</h1>
        <p class="subtitle">轻松管理，自动发货</p>
      </div>

      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="rules"
        class="login-form"
        size="large"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="用户名"
            prefix-icon="User"
            clearable
          />
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="密码"
            prefix-icon="Lock"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>

        <el-form-item>
          <div class="form-options">
            <el-checkbox v-model="loginForm.remember">记住我</el-checkbox>
            <el-link type="primary" :underline="false">忘记密码？</el-link>
          </div>
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            class="login-btn"
            :loading="loading"
            @click="handleLogin"
          >
            登录
          </el-button>
        </el-form-item>

        <div class="register-link">
          还没有账号？
          <el-link type="primary" @click="goToRegister">立即注册</el-link>
        </div>
      </el-form>

      <div class="footer">
        <el-link type="info" @click="showDisclaimer">
          <el-icon><Document /></el-icon>
          用户协议与免责声明
        </el-link>
      </div>
    </div>

    <!-- 免责声明对话框 -->
    <el-dialog
      v-model="disclaimerVisible"
      title="用户协议与免责声明"
      width="600px"
      :close-on-click-modal="false"
    >
      <div class="disclaimer-content">
        <h3>⚠️ 重要提示</h3>
        <p>
          欢迎使用闲鱼自动售货机器人。在使用本软件前，请仔细阅读并同意以下条款：
        </p>

        <h4>1. 合法使用</h4>
        <ul>
          <li>本软件仅供学习交流使用，请勿用于非法用途</li>
          <li>用户需遵守闲鱼平台规则及相关法律法规</li>
          <li>因违规使用导致的账号封禁等后果，用户自行承担</li>
        </ul>

        <h4>2. 数据安全</h4>
        <ul>
          <li>请妥善保管您的账号密码和 Cookie 信息</li>
          <li>本软件不会上传您的任何数据到第三方服务器</li>
          <li>所有数据均存储在本地</li>
        </ul>

        <h4>3. 使用风险</h4>
        <ul>
          <li>自动化操作可能存在一定风险，请谨慎使用</li>
          <li>建议设置合理的操作频率，避免被平台限制</li>
          <li>本软件不保证 100% 稳定运行</li>
        </ul>

        <h4>4. 免责声明</h4>
        <ul>
          <li>因使用本软件导致的任何直接或间接损失，开发者不承担责任</li>
          <li>本软件按"原样"提供，不提供任何明示或暗示的保证</li>
          <li>开发者保留随时修改或终止服务的权利</li>
        </ul>

        <el-checkbox v-model="agreeTerms" class="agree-checkbox">
          我已阅读并同意以上条款
        </el-checkbox>
      </div>

      <template #footer>
        <el-button @click="disclaimerVisible = false">取消</el-button>
        <el-button type="primary" :disabled="!agreeTerms" @click="confirmDisclaimer">
          同意并继续
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/store/user'

const router = useRouter()
const userStore = useUserStore()
const loginFormRef = ref(null)
const loading = ref(false)
const disclaimerVisible = ref(false)
const agreeTerms = ref(false)

const loginForm = reactive({
  username: '',
  password: '',
  remember: false
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3-20 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少 6 位', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  await loginFormRef.value.validate(async (valid) => {
    if (!valid) return

    loading.value = true
    try {
      const formData = new FormData()
      formData.append('username', loginForm.username)
      formData.append('password', loginForm.password)

      await userStore.login(formData)
      
      ElMessage.success('登录成功！')
      router.push('/dashboard')
    } catch (error) {
      ElMessage.error(error.response?.data?.detail || '登录失败，请检查用户名和密码')
    } finally {
      loading.value = false
    }
  })
}

const goToRegister = () => {
  router.push('/register')
}

const showDisclaimer = () => {
  disclaimerVisible.value = true
  agreeTerms.value = false
}

const confirmDisclaimer = () => {
  disclaimerVisible.value = false
  ElMessage.success('感谢同意，请登录或注册')
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-card {
  background: white;
  border-radius: 20px;
  padding: 40px;
  width: 100%;
  max-width: 420px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.logo {
  font-size: 64px;
  margin-bottom: 10px;
  animation: bounce 2s infinite;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.login-header h1 {
  font-size: 24px;
  color: #333;
  margin-bottom: 8px;
}

.subtitle {
  color: #999;
  font-size: 14px;
}

.login-form {
  margin-top: 30px;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.login-btn {
  width: 100%;
  height: 44px;
  font-size: 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
}

.login-btn:hover {
  opacity: 0.9;
}

.register-link {
  text-align: center;
  margin-top: 20px;
  color: #666;
}

.footer {
  margin-top: 30px;
  text-align: center;
}

.footer .el-link {
  color: #999;
  font-size: 13px;
}

.disclaimer-content {
  max-height: 400px;
  overflow-y: auto;
  padding: 10px;
}

.disclaimer-content h3 {
  color: #f56c6c;
  margin-bottom: 15px;
}

.disclaimer-content h4 {
  color: #333;
  margin: 15px 0 10px;
  font-size: 15px;
}

.disclaimer-content ul {
  padding-left: 20px;
  color: #666;
  font-size: 14px;
  line-height: 1.8;
}

.disclaimer-content li {
  margin-bottom: 5px;
}

.agree-checkbox {
  margin-top: 20px;
  display: block;
}
</style>
