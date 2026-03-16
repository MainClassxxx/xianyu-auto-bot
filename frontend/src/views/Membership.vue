<template>
  <div class="membership-page">
    <div class="page-header">
      <h1>会员中心</h1>
      <p>升级会员，解锁更多高级功能</p>
    </div>

    <!-- 当前会员状态 -->
    <el-card class="current-membership-card" shadow="hover">
      <div class="membership-status">
        <div class="status-icon" :class="userStore.membershipLevel">
          <el-icon v-if="userStore.membershipLevel === 'svip'"><Star /></el-icon>
          <el-icon v-else-if="userStore.membershipLevel === 'vip'"><CreditCard /></el-icon>
          <el-icon v-else><User /></el-icon>
        </div>
        <div class="status-info">
          <div class="level-text">
            <span class="level-label">当前等级</span>
            <el-tag :type="userStore.membershipLevel === 'svip' ? 'warning' : userStore.membershipLevel === 'vip' ? 'success' : 'info'" size="large">
              {{ membershipLevelName }}
            </el-tag>
          </div>
          <div class="expire-text" v-if="userStore.membershipExpireAt">
            有效期至：{{ formatDate(userStore.membershipExpireAt) }}
          </div>
          <div class="expire-text" v-else>
            永久有效
          </div>
        </div>
      </div>
    </el-card>

    <!-- 会员套餐选择 -->
    <div class="plans-section">
      <h2 class="section-title">选择会员套餐</h2>
      
      <el-tabs v-model="activeLevel" class="level-tabs">
        <el-tab-pane label="VIP 会员" name="vip"></el-tab-pane>
        <el-tab-pane label="SVIP 会员" name="svip"></el-tab-pane>
      </el-tabs>

      <div class="plans-grid">
        <div 
          v-for="(plan, planKey) in plans[activeLevel]" 
          :key="planKey"
          class="plan-card"
          :class="{ active: selectedPlan === planKey }"
          @click="selectedPlan = planKey"
        >
          <div class="plan-header">
            <h3 class="plan-name">{{ plan.name }}</h3>
            <div class="plan-days">{{ plan.days }}天</div>
          </div>
          <div class="plan-price">
            <span class="price-symbol">¥</span>
            <span class="price-value">{{ plan.price }}</span>
          </div>
          <div class="plan-features">
            <div v-for="feature in getFeatures(activeLevel)" :key="feature" class="feature-item">
              <el-icon class="feature-icon"><CircleCheck /></el-icon>
              <span>{{ feature }}</span>
            </div>
          </div>
          <el-button 
            type="primary" 
            class="select-btn"
            :class="{ selected: selectedPlan === planKey }"
            @click.stop="selectPlan(planKey)"
          >
            {{ selectedPlan === planKey ? '已选择' : '选择套餐' }}
          </el-button>
        </div>
      </div>
    </div>

    <!-- 支付方式 -->
    <div class="payment-section" v-if="selectedPlan">
      <h2 class="section-title">选择支付方式</h2>
      <div class="payment-methods">
        <div 
          class="payment-method"
          :class="{ active: paymentMethod === 'alipay' }"
          @click="paymentMethod = 'alipay'"
        >
          <el-icon class="payment-icon"><Alipay /></el-icon>
          <span>支付宝</span>
        </div>
        <div 
          class="payment-method"
          :class="{ active: paymentMethod === 'wechat' }"
          @click="paymentMethod = 'wechat'"
        >
          <el-icon class="payment-icon"><Wechat /></el-icon>
          <span>微信支付</span>
        </div>
      </div>
    </div>

    <!-- 订单确认 -->
    <el-dialog
      v-model="orderDialogVisible"
      title="确认订单"
      width="500px"
      :close-on-click-modal="false"
    >
      <div class="order-confirm">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="会员等级">{{ selectedPlanInfo.name }}</el-descriptions-item>
          <el-descriptions-item label="有效期">{{ selectedPlanInfo.days }}天</el-descriptions-item>
          <el-descriptions-item label="订单金额">¥{{ selectedPlanInfo.price }}</el-descriptions-item>
          <el-descriptions-item label="支付方式">
            {{ paymentMethod === 'alipay' ? '支付宝' : '微信支付' }}
          </el-descriptions-item>
        </el-descriptions>
        
        <el-alert
          type="info"
          class="payment-hint"
          show-icon
          :closable="false"
        >
          <p>💡 提示：当前为测试环境，支付将模拟完成</p>
          <p>后续将接入真实的支付宝/微信支付</p>
        </el-alert>
      </div>
      
      <template #footer>
        <el-button @click="orderDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="paying" @click="confirmPay">
          {{ paying ? '支付中...' : '确认支付' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/store/user'
import * as membershipApi from '@/api/membership'

const userStore = useUserStore()

const activeLevel = ref('vip')
const selectedPlan = ref('')
const paymentMethod = ref('alipay')
const orderDialogVisible = ref(false)
const paying = ref(false)

const plans = ref({})

// 加载会员套餐
onMounted(async () => {
  try {
    const result = await membershipApi.getMembershipPlans()
    plans.value = result.plans
  } catch (error) {
    console.error('加载套餐失败:', error)
    ElMessage.error('加载套餐失败')
  }
})

const membershipLevelName = computed(() => {
  const levelMap = {
    'normal': '普通用户',
    'vip': 'VIP 会员',
    'svip': 'SVIP 会员'
  }
  return levelMap[userStore.membershipLevel] || '普通用户'
})

const selectedPlanInfo = computed(() => {
  if (!selectedPlan.value || !plans.value[activeLevel.value]) return null
  return plans.value[activeLevel.value][selectedPlan.value]
})

const getFeatures = (level) => {
  const features = {
    'vip': [
      '支持 5 个闲鱼账号',
      '每日 1000 次 API 调用',
      '自动发货功能',
      '自动回复功能',
      '数据导出功能'
    ],
    'svip': [
      '无限账号数量',
      '无限 API 调用',
      '所有 VIP 功能',
      'AI 智能回复',
      'Webhook 回调',
      '优先技术支持'
    ]
  }
  return features[level] || []
}

const formatDate = (dateStr) => {
  if (!dateStr) return '永久'
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN')
}

const selectPlan = (planKey) => {
  selectedPlan.value = planKey
  orderDialogVisible.value = true
}

const confirmPay = async () => {
  if (!selectedPlan.value) return
  
  paying.value = true
  
  try {
    // 1. 创建订单
    const orderResult = await membershipApi.createOrder({
      level: activeLevel.value,
      plan: selectedPlan.value,
      payment_method: paymentMethod.value
    })
    
    console.log('订单创建成功:', orderResult)
    
    // 2. 模拟支付（后续接入真实支付）
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    // 3. 确认支付
    const payResult = await membershipApi.payOrder(orderResult.data.order_no)
    
    console.log('支付成功:', payResult)
    
    ElMessage.success('支付成功，会员已开通！')
    orderDialogVisible.value = false
    
    // 4. 刷新用户信息
    await userStore.fetchUserInfo()
    
  } catch (error) {
    console.error('支付失败:', error)
    ElMessage.error(error.response?.data?.detail || '支付失败，请重试')
  } finally {
    paying.value = false
  }
}
</script>

<style scoped>
.membership-page {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 30px;
}

.page-header h1 {
  font-size: 28px;
  font-weight: 700;
  color: #333;
  margin: 0 0 8px 0;
}

.page-header p {
  color: #666;
  margin: 0;
}

/* 当前会员状态 */
.current-membership-card {
  margin-bottom: 30px;
}

.membership-status {
  display: flex;
  align-items: center;
  gap: 20px;
}

.status-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 40px;
  color: #fff;
}

.status-icon.svip {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.status-icon.vip {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.status-icon.normal {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.status-info {
  flex: 1;
}

.level-text {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.level-label {
  color: #666;
  font-size: 14px;
}

.expire-text {
  color: #999;
  font-size: 14px;
}

/* 套餐选择 */
.plans-section {
  margin-bottom: 30px;
}

.section-title {
  font-size: 20px;
  font-weight: 600;
  color: #333;
  margin: 0 0 20px 0;
}

.level-tabs {
  margin-bottom: 20px;
}

.plans-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.plan-card {
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  padding: 24px;
  cursor: pointer;
  transition: all 0.3s;
  position: relative;
  background: #fff;
}

.plan-card:hover {
  border-color: #409EFF;
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(64, 158, 255, 0.15);
}

.plan-card.active {
  border-color: #409EFF;
  background: #f0f9ff;
}

.plan-header {
  margin-bottom: 16px;
}

.plan-name {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 0 0 8px 0;
}

.plan-days {
  font-size: 14px;
  color: #666;
}

.plan-price {
  margin-bottom: 20px;
}

.price-symbol {
  font-size: 20px;
  color: #f56c6c;
  margin-right: 4px;
}

.price-value {
  font-size: 36px;
  font-weight: 700;
  color: #f56c6c;
}

.plan-features {
  margin-bottom: 20px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  font-size: 14px;
  color: #666;
}

.feature-icon {
  color: #67c23a;
  font-size: 16px;
}

.select-btn {
  width: 100%;
}

.select-btn.selected {
  background: #67c23a;
  border-color: #67c23a;
}

/* 支付方式 */
.payment-section {
  margin-bottom: 30px;
}

.payment-methods {
  display: flex;
  gap: 20px;
}

.payment-method {
  flex: 1;
  max-width: 200px;
  padding: 20px;
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  transition: all 0.3s;
}

.payment-method:hover {
  border-color: #409EFF;
}

.payment-method.active {
  border-color: #409EFF;
  background: #f0f9ff;
}

.payment-icon {
  font-size: 48px;
}

.payment-method:nth-child(1) .payment-icon {
  color: #1677FF;
}

.payment-method:nth-child(2) .payment-icon {
  color: #07C160;
}

/* 订单确认 */
.order-confirm {
  padding: 10px 0;
}

.payment-hint {
  margin-top: 20px;
}

.payment-hint p {
  margin: 4px 0;
  font-size: 14px;
}
</style>
