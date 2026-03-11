<template>
  <div class="register-container">
    <div class="register-card">
      <div class="register-header">
        <div class="logo">🥫</div>
        <h1>注册账号</h1>
        <p class="subtitle">开启自动化管理之旅</p>
      </div>

      <el-form
        ref="registerFormRef"
        :model="registerForm"
        :rules="rules"
        class="register-form"
        size="large"
      >
        <el-form-item prop="username">
          <el-input
            v-model="registerForm.username"
            placeholder="用户名（3-20 位）"
            prefix-icon="User"
            clearable
          />
        </el-form-item>

        <el-form-item prop="email">
          <el-input
            v-model="registerForm.email"
            placeholder="邮箱地址"
            prefix-icon="Message"
            clearable
          />
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="registerForm.password"
            type="password"
            placeholder="密码（至少 6 位）"
            prefix-icon="Lock"
            show-password
          />
        </el-form-item>

        <el-form-item prop="confirmPassword">
          <el-input
            v-model="registerForm.confirmPassword"
            type="password"
            placeholder="确认密码"
            prefix-icon="Lock"
            show-password
          />
        </el-form-item>

        <el-form-item prop="captcha">
          <div class="captcha-row">
            <el-input
              v-model="registerForm.captcha"
              placeholder="验证码"
              prefix-icon="Picture"
              style="flex: 1"
            />
            <div class="captcha-image" @click="refreshCaptcha">
              <span>{{ captchaCode }}</span>
            </div>
          </div>
        </el-form-item>

        <el-form-item prop="emailCode">
          <div class="code-row">
            <el-input
              v-model="registerForm.emailCode"
              placeholder="邮箱验证码"
              prefix-icon="Message"
              style="flex: 1"
            />
            <el-button
              :disabled="countdown > 0"
              @click="sendEmailCode"
            >
              {{ countdown > 0 ? `${countdown}s 后重试` : '发送验证码' }}
            </el-button>
          </div>
        </el-form-item>

        <el-form-item>
          <el-checkbox v-model="registerForm.agreeTerms">
            我已阅读并同意
            <el-link type="primary" @click="showDisclaimer">《用户协议与免责声明》</el-link>
          </el-checkbox>
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            class="register-btn"
            :loading="loading"
            @click="handleRegister"
          >
            立即注册
          </el-button>
        </el-form-item>

        <div class="login-link">
          已有账号？
          <el-link type="primary" @click="goToLogin">立即登录</el-link>
        </div>
      </el-form>
    </div>

    <!-- 免责声明对话框 -->
    <el-dialog
      v-model="disclaimerVisible"
      title="用户协议与免责声明"
      width="600px"
    >
      <div class="disclaimer-content">
        <h3>⚠️ 重要提示</h3>
        <p>欢迎使用闲鱼自动售货机器人。在使用本软件前，请仔细阅读并同意以下条款：</p>

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
        </ul>
      </div>

      <template #footer>
        <el-button @click="disclaimerVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/store/user'

const router = useRouter()
const userStore = useUserStore()
const registerFormRef = ref(null)
const loading = ref(false)
const disclaimerVisible = ref(false)
const countdown = ref(0)
const captchaCode = ref('ABCD')
let countdownTimer = null

const registerForm = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  captcha: '',
  emailCode: '',
  agreeTerms: false
})

const validateConfirmPassword = (rule, value, callback) => {
  if (value !== registerForm.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3-20 个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少 6 位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ],
  captcha: [
    { required: true, message: '请输入验证码', trigger: 'blur' },
    { len: 4, message: '验证码为 4 位字符', trigger: 'blur' }
  ],
  emailCode: [
    { required: true, message: '请输入邮箱验证码', trigger: 'blur' },
    { len: 6, message: '邮箱验证码为 6 位数字', trigger: 'blur' }
  ]
}

const refreshCaptcha = () => {
  captchaCode.value = Array.from({ length: 4 }, () =>
    'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'[Math.floor(Math.random() * 32)]
  ).join('')
}

const sendEmailCode = async () => {
  if (!registerForm.email) {
    ElMessage.warning('请先输入邮箱地址')
    return
  }

  try {
    // TODO: 调用发送邮箱验证码 API
    await new Promise(resolve => setTimeout(resolve, 500))
    
    ElMessage.success('验证码已发送到邮箱（测试环境请查看控制台）')
    console.log('测试邮箱验证码：123456')
    
    countdown.value = 60
    countdownTimer = setInterval(() => {
      countdown.value--
      if (countdown.value <= 0) {
        clearInterval(countdownTimer)
      }
    }, 1000)
  } catch (error) {
    ElMessage.error('发送失败，请稍后重试')
  }
}

const handleRegister = async () => {
  if (!registerFormRef.value) return

  await registerFormRef.value.validate(async (valid) => {
    if (!valid) return

    if (!registerForm.agreeTerms) {
      ElMessage.warning('请先同意用户协议与免责声明')
      return
    }

    loading.value = true
    try {
      await userStore.register({
        username: registerForm.username,
        email: registerForm.email,
        password: registerForm.password,
        captcha: registerForm.captcha,
        emailCode: registerForm.emailCode
      })

      ElMessage.success('注册成功！')
      router.push('/dashboard')
    } catch (error) {
      ElMessage.error(error.response?.data?.detail || '注册失败，请稍后重试')
    } finally {
      loading.value = false
    }
  })
}

const goToLogin = () => {
  router.push('/login')
}

const showDisclaimer = () => {
  disclaimerVisible.value = true
}

onUnmounted(() => {
  if (countdownTimer) {
    clearInterval(countdownTimer)
  }
})
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.register-card {
  background: white;
  border-radius: 20px;
  padding: 40px;
  width: 100%;
  max-width: 450px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.register-header {
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

.register-header h1 {
  font-size: 24px;
  color: #333;
  margin-bottom: 8px;
}

.subtitle {
  color: #999;
  font-size: 14px;
}

.register-form {
  margin-top: 30px;
}

.captcha-row,
.code-row {
  display: flex;
  gap: 10px;
  width: 100%;
}

.captcha-image {
  width: 100px;
  height: 40px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
  font-size: 18px;
  letter-spacing: 3px;
  cursor: pointer;
  user-select: none;
}

.captcha-image:hover {
  opacity: 0.9;
}

.register-btn {
  width: 100%;
  height: 44px;
  font-size: 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
}

.register-btn:hover {
  opacity: 0.9;
}

.login-link {
  text-align: center;
  margin-top: 20px;
  color: #666;
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
</style>
