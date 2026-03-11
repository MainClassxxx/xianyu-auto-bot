<template>
  <div class="login-page">
    <!-- 动态背景 -->
    <div class="animated-bg">
      <div class="gradient-orb orb-1"></div>
      <div class="gradient-orb orb-2"></div>
      <div class="gradient-orb orb-3"></div>
      <div class="gradient-orb orb-4"></div>
    </div>

    <!-- 粒子效果 -->
    <div class="particles">
      <div v-for="i in 20" :key="i" class="particle" :style="getParticleStyle(i)"></div>
    </div>

    <!-- 登录卡片 -->
    <div class="login-container">
      <div class="login-card glass-effect">
        <!-- 装饰元素 -->
        <div class="card-decoration">
          <div class="decoration-circle decoration-1"></div>
          <div class="decoration-circle decoration-2"></div>
          <div class="decoration-circle decoration-3"></div>
        </div>

        <!-- Logo 区域 -->
        <div class="logo-section">
          <div class="logo-wrapper">
            <div class="logo-emoji">🥫</div>
            <h1 class="logo-title">闲鱼自动售货机器人</h1>
            <p class="logo-subtitle">智能 · 高效 · 自动</p>
          </div>
        </div>

        <!-- 登录表单 -->
        <el-form
          ref="loginFormRef"
          :model="loginForm"
          :rules="rules"
          class="login-form"
          size="large"
        >
          <el-form-item prop="username">
            <div class="input-wrapper">
              <el-icon class="input-icon"><User /></el-icon>
              <el-input
                v-model="loginForm.username"
                placeholder="用户名"
                class="custom-input"
                clearable
              />
            </div>
          </el-form-item>

          <el-form-item prop="password">
            <div class="input-wrapper">
              <el-icon class="input-icon"><Lock /></el-icon>
              <el-input
                v-model="loginForm.password"
                type="password"
                placeholder="密码"
                class="custom-input"
                show-password
                @keyup.enter="handleLogin"
              />
            </div>
          </el-form-item>

          <el-form-item>
            <div class="form-options">
              <el-checkbox v-model="loginForm.remember" class="custom-checkbox">
                <span>记住我</span>
              </el-checkbox>
              <el-link type="primary" class="forgot-link">忘记密码？</el-link>
            </div>
          </el-form-item>

          <el-form-item>
            <el-button
              type="primary"
              class="login-btn"
              :loading="loading"
              @click="handleLogin"
            >
              <span v-if="!loading">登 录</span>
              <span v-else>登录中...</span>
              <div class="btn-shine"></div>
            </el-button>
          </el-form-item>

          <div class="divider">
            <span>或</span>
          </div>

          <div class="register-section">
            <span>还没有账号？</span>
            <el-link type="primary" class="register-link" @click="goToRegister">
              立即注册 <el-icon><ArrowRight /></el-icon>
            </el-link>
          </div>
        </el-form>

        <!-- 底部链接 -->
        <div class="card-footer">
          <el-link class="footer-link" @click="showDisclaimer">
            <el-icon><Document /></el-icon>
            用户协议与免责声明
          </el-link>
        </div>
      </div>

      <!-- 右侧装饰卡片 -->
      <div class="info-card glass-effect">
        <div class="info-content">
          <h2>欢迎回来</h2>
          <p>管理您的闲鱼店铺，从未如此简单</p>
          
          <div class="features">
            <div class="feature-item">
              <div class="feature-icon">📊</div>
              <div class="feature-text">
                <h4>数据统计</h4>
                <span>实时掌握经营情况</span>
              </div>
            </div>
            <div class="feature-item">
              <div class="feature-icon">🤖</div>
              <div class="feature-text">
                <h4>自动发货</h4>
                <span>24 小时自动处理订单</span>
              </div>
            </div>
            <div class="feature-item">
              <div class="feature-icon">💬</div>
              <div class="feature-text">
                <h4>智能回复</h4>
                <span>自动回复买家咨询</span>
              </div>
            </div>
            <div class="feature-item">
              <div class="feature-icon">📱</div>
              <div class="feature-text">
                <h4>消息通知</h4>
                <span>重要消息实时推送</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 免责声明对话框 -->
    <el-dialog
      v-model="disclaimerVisible"
      title="用户协议与免责声明"
      class="disclaimer-dialog"
      width="600px"
      :close-on-click-modal="false"
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
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/store/user'

const router = useRouter()
const route = useRoute()
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

// 生成粒子样式
const getParticleStyle = (index) => {
  const size = Math.random() * 20 + 10
  const left = Math.random() * 100
  const delay = Math.random() * 20
  const duration = Math.random() * 10 + 10
  return {
    width: `${size}px`,
    height: `${size}px`,
    left: `${left}%`,
    animationDelay: `${delay}s`,
    animationDuration: `${duration}s`
  }
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

      const response = await userStore.login(formData)
      
      console.log('登录成功:', response)
      
      ElMessage.success('登录成功！欢迎回来')
      
      // 延迟一下确保 token 存储完成
      setTimeout(() => {
        // 检查是否有 redirect 参数
        const redirect = route.query.redirect
        if (redirect) {
          router.push(redirect)
        } else {
          router.push('/dashboard')
        }
      }, 300)
      
    } catch (error) {
      console.error('登录失败:', error)
      const errorMsg = error.response?.data?.detail || '登录失败，请检查用户名和密码'
      ElMessage.error(errorMsg)
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
  ElMessage.success('感谢同意，请登录')
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  position: relative;
  overflow: hidden;
}

/* 动态背景 */
.animated-bg {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: -2;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.gradient-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.5;
  animation: float 20s infinite ease-in-out;
}

.orb-1 {
  width: 600px;
  height: 600px;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  top: -200px;
  right: -200px;
  animation-delay: 0s;
}

.orb-2 {
  width: 500px;
  height: 500px;
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  bottom: -150px;
  left: -150px;
  animation-delay: -7s;
}

.orb-3 {
  width: 400px;
  height: 400px;
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
  top: 50%;
  left: 50%;
  animation-delay: -14s;
}

.orb-4 {
  width: 350px;
  height: 350px;
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
  top: 20%;
  right: 20%;
  animation-delay: -10s;
}

@keyframes float {
  0%, 100% { transform: translate(0, 0) scale(1); }
  25% { transform: translate(50px, -50px) scale(1.1); }
  50% { transform: translate(-50px, 50px) scale(0.9); }
  75% { transform: translate(50px, 50px) scale(1.05); }
}

/* 粒子效果 */
.particles {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: -1;
  pointer-events: none;
}

.particle {
  position: absolute;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  animation: rise 20s infinite ease-in;
  bottom: -50px;
}

@keyframes rise {
  0% {
    transform: translateY(0) rotate(0deg);
    opacity: 0;
  }
  10% {
    opacity: 1;
  }
  90% {
    opacity: 1;
  }
  100% {
    transform: translateY(-100vh) rotate(720deg);
    opacity: 0;
  }
}

/* 登录容器 */
.login-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 40px;
  max-width: 1100px;
  width: 100%;
  animation: slideIn 0.8s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(40px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 登录卡片 */
.login-card {
  position: relative;
  padding: 50px 40px;
  border-radius: 24px;
  backdrop-filter: blur(20px);
  background: rgba(255, 255, 255, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
  overflow: hidden;
}

.card-decoration {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  overflow: hidden;
}

.decoration-circle {
  position: absolute;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
}

.decoration-1 {
  width: 300px;
  height: 300px;
  top: -150px;
  right: -150px;
}

.decoration-2 {
  width: 200px;
  height: 200px;
  bottom: -100px;
  left: -100px;
}

.decoration-3 {
  width: 150px;
  height: 150px;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

/* Logo 区域 */
.logo-section {
  text-align: center;
  margin-bottom: 40px;
}

.logo-wrapper {
  display: inline-block;
}

.logo-emoji {
  font-size: 80px;
  display: block;
  margin-bottom: 16px;
  animation: bounce 2s infinite;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-15px); }
}

.logo-title {
  font-size: 28px;
  font-weight: 700;
  color: #fff;
  margin: 0 0 8px 0;
  text-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
}

.logo-subtitle {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
  margin: 0;
}

/* 登录表单 */
.login-form {
  position: relative;
  z-index: 1;
}

.input-wrapper {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 24px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s;
  width: 100%;
  box-sizing: border-box;
}

.input-wrapper:focus-within {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.4);
  box-shadow: 0 0 0 4px rgba(255, 255, 255, 0.1);
}

.input-icon {
  color: rgba(255, 255, 255, 0.6);
  font-size: 20px;
  flex-shrink: 0;
}

.custom-input {
  flex: 1;
}

.custom-input :deep(.el-input__wrapper) {
  background: transparent;
  box-shadow: none;
  padding: 0;
}

.custom-input :deep(.el-input__inner) {
  color: #fff;
  font-size: 15px;
  padding: 0;
}

.custom-input :deep(.el-input__inner::placeholder) {
  color: rgba(255, 255, 255, 0.5);
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.custom-checkbox :deep(.el-checkbox__label) {
  color: rgba(255, 255, 255, 0.8);
}

.forgot-link {
  color: rgba(255, 255, 255, 0.8);
}

.login-btn {
  width: 100%;
  height: 50px;
  font-size: 16px;
  font-weight: 600;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 12px;
  position: relative;
  overflow: hidden;
  transition: all 0.3s;
}

.login-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
}

.btn-shine {
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
  animation: shine 3s infinite;
}

@keyframes shine {
  0% { left: -100%; }
  20%, 100% { left: 100%; }
}

.divider {
  display: flex;
  align-items: center;
  margin: 30px 0;
}

.divider::before,
.divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: rgba(255, 255, 255, 0.2);
}

.divider span {
  padding: 0 16px;
  color: rgba(255, 255, 255, 0.5);
  font-size: 14px;
}

.register-section {
  text-align: center;
  color: rgba(255, 255, 255, 0.8);
}

.register-link {
  color: #fff;
  font-weight: 600;
  margin-left: 8px;
}

.card-footer {
  margin-top: 30px;
  text-align: center;
}

.footer-link {
  color: rgba(255, 255, 255, 0.6);
  font-size: 13px;
}

/* 信息卡片 */
.info-card {
  padding: 50px 40px;
  border-radius: 24px;
  backdrop-filter: blur(20px);
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.info-content h2 {
  font-size: 32px;
  font-weight: 700;
  color: #fff;
  margin: 0 0 12px 0;
  text-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
}

.info-content > p {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.8);
  margin: 0 0 40px 0;
}

.features {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.08);
  transition: all 0.3s;
}

.feature-item:hover {
  background: rgba(255, 255, 255, 0.12);
  transform: translateX(8px);
}

.feature-icon {
  font-size: 36px;
  flex-shrink: 0;
}

.feature-text h4 {
  font-size: 16px;
  font-weight: 600;
  color: #fff;
  margin: 0 0 4px 0;
}

.feature-text span {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
}

/* 免责声明对话框 */
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

.agree-checkbox {
  margin-top: 20px;
  display: block;
}

/* 响应式设计 */
@media (max-width: 900px) {
  .login-container {
    grid-template-columns: 1fr;
    max-width: 500px;
  }

  .info-card {
    display: none;
  }
}
</style>
