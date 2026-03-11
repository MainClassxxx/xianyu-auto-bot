<template>
  <div class="layout-container">
    <!-- 动态背景 -->
    <div class="animated-bg">
      <div class="gradient-orb orb-1"></div>
      <div class="gradient-orb orb-2"></div>
      <div class="gradient-orb orb-3"></div>
    </div>

    <!-- 侧边栏 -->
    <aside class="sidebar glass-effect">
      <div class="sidebar-header">
        <div class="logo-wrapper">
          <div class="logo-emoji">🥫</div>
          <div class="logo-text">
            <h1>闲鱼机器人</h1>
            <span class="logo-subtitle">智能售货系统</span>
          </div>
        </div>
      </div>

      <nav class="sidebar-nav">
        <router-link
          v-for="item in menuItems"
          :key="item.path"
          :to="item.path"
          class="nav-item"
          active-class="active"
        >
          <div class="nav-icon">
            <el-icon :size="22"><component :is="item.icon" /></el-icon>
          </div>
          <span class="nav-text">{{ item.title }}</span>
          <div class="nav-indicator"></div>
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <div class="user-profile">
          <el-avatar :size="40" class="user-avatar">
            <el-icon><User /></el-icon>
          </el-avatar>
          <div class="user-info">
            <div class="user-name">管理员</div>
            <div class="user-role">超级管理员</div>
          </div>
        </div>
      </div>
    </aside>

    <!-- 主内容区 -->
    <main class="main-content">
      <!-- 顶部导航栏 -->
      <header class="top-header glass-effect">
        <div class="header-left">
          <h2 class="page-title">{{ currentPageTitle }}</h2>
        </div>
        <div class="header-right">
          <div class="header-actions">
            <el-badge :value="3" :hidden="false" class="notification-btn">
              <el-button circle>
                <el-icon><Bell /></el-icon>
              </el-button>
            </el-badge>
            
            <el-dropdown @command="handleCommand">
              <div class="user-menu">
                <el-avatar :size="36">
                  <el-icon><User /></el-icon>
                </el-avatar>
                <span class="username">管理员</span>
                <el-icon><ArrowDown /></el-icon>
              </div>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="profile">
                    <el-icon><User /></el-icon> 个人中心
                  </el-dropdown-item>
                  <el-dropdown-item command="settings">
                    <el-icon><Setting /></el-icon> 系统设置
                  </el-dropdown-item>
                  <el-dropdown-item divided command="logout">
                    <el-icon><SwitchButton /></el-icon> 退出登录
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </header>

      <!-- 内容区域 -->
      <div class="content-wrapper">
        <transition name="fade-slide" mode="out-in">
          <router-view :key="$route.fullPath" />
        </transition>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()

const menuItems = [
  { path: '/dashboard', title: '仪表盘', icon: 'DataLine' },
  { path: '/accounts', title: '账号管理', icon: 'User' },
  { path: '/items', title: '商品管理', icon: 'ShoppingCart' },
  { path: '/orders', title: '订单管理', icon: 'List' },
  { path: '/conversations', title: '对话消息', icon: 'ChatDotRound' },
  { path: '/auto-reply', title: '自动回复', icon: 'ChatLineRound' },
  { path: '/auto-delivery', title: '自动发货', icon: 'Box' },
  { path: '/notifications', title: '通知管理', icon: 'Bell' },
  { path: '/stats', title: '数据统计', icon: 'TrendCharts' },
  { path: '/settings', title: '系统设置', icon: 'Setting' }
]

const currentPageTitle = computed(() => {
  const item = menuItems.find(i => i.path === route.path)
  return item?.title || '仪表盘'
})

const handleCommand = (command) => {
  if (command === 'logout') {
    ElMessage.success('退出登录成功')
    router.push('/login')
  } else if (command === 'settings') {
    router.push('/settings')
  } else {
    ElMessage.info('功能开发中')
  }
}
</script>

<style scoped>
.layout-container {
  display: flex;
  height: 100vh;
  overflow: hidden;
  position: relative;
}

/* 动态背景 */
.animated-bg {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: -1;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  overflow: hidden;
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

@keyframes float {
  0%, 100% { transform: translate(0, 0) scale(1); }
  25% { transform: translate(50px, -50px) scale(1.1); }
  50% { transform: translate(-50px, 50px) scale(0.9); }
  75% { transform: translate(50px, 50px) scale(1.05); }
}

/* 侧边栏 */
.sidebar {
  width: 260px;
  display: flex;
  flex-direction: column;
  backdrop-filter: blur(20px);
  background: rgba(255, 255, 255, 0.1);
  border-right: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 4px 0 24px rgba(0, 0, 0, 0.1);
  z-index: 10;
}

.sidebar-header {
  padding: 30px 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo-wrapper {
  display: flex;
  align-items: center;
  gap: 16px;
}

.logo-emoji {
  font-size: 48px;
  animation: bounce 2s infinite;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.logo-text h1 {
  color: #fff;
  font-size: 22px;
  font-weight: 700;
  margin: 0;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.logo-subtitle {
  color: rgba(255, 255, 255, 0.8);
  font-size: 12px;
  margin-top: 4px;
  display: block;
}

/* 导航菜单 */
.sidebar-nav {
  flex: 1;
  padding: 20px 16px;
  overflow-y: auto;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 16px;
  margin-bottom: 8px;
  border-radius: 12px;
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.nav-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
  opacity: 0;
  transition: opacity 0.3s;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.15);
  transform: translateX(4px);
}

.nav-item:hover::before {
  opacity: 1;
}

.nav-item.active {
  background: linear-gradient(135deg, rgba(255,255,255,0.2) 0%, rgba(255,255,255,0.1) 100%);
  color: #fff;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.nav-indicator {
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 0;
  background: linear-gradient(180deg, #4facfe 0%, #00f2fe 100%);
  border-radius: 0 4px 4px 0;
  transition: height 0.3s;
}

.nav-item.active .nav-indicator {
  height: 60%;
}

.nav-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  flex-shrink: 0;
}

.nav-item.active .nav-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.nav-text {
  flex: 1;
  font-size: 15px;
  font-weight: 500;
}

/* 侧边栏底部 */
.sidebar-footer {
  padding: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.1);
}

.user-avatar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
}

.user-info {
  flex: 1;
}

.user-name {
  color: #fff;
  font-size: 14px;
  font-weight: 600;
}

.user-role {
  color: rgba(255, 255, 255, 0.7);
  font-size: 12px;
  margin-top: 2px;
}

/* 主内容区 */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 顶部导航栏 */
.top-header {
  height: 70px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32px;
  backdrop-filter: blur(20px);
  background: rgba(255, 255, 255, 0.15);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08);
}

.page-title {
  color: #fff;
  font-size: 24px;
  font-weight: 700;
  margin: 0;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 20px;
}

.notification-btn {
  position: relative;
}

.notification-btn :deep(.el-badge__content) {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  border: 2px solid rgba(255, 255, 255, 0.3);
}

.notification-btn .el-button {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: #fff;
}

.notification-btn .el-button:hover {
  background: rgba(255, 255, 255, 0.3);
}

.user-menu {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  padding: 8px 16px;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.15);
  transition: all 0.3s;
}

.user-menu:hover {
  background: rgba(255, 255, 255, 0.25);
  transform: translateY(-2px);
}

.username {
  color: #fff;
  font-weight: 600;
  font-size: 14px;
}

.user-menu .el-icon {
  color: rgba(255, 255, 255, 0.8);
}

/* 内容区域 */
.content-wrapper {
  flex: 1;
  overflow-y: auto;
  padding: 32px;
}

/* 页面切换动画 */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

/* 滚动条美化 */
.sidebar-nav::-webkit-scrollbar,
.content-wrapper::-webkit-scrollbar {
  width: 6px;
}

.sidebar-nav::-webkit-scrollbar-track,
.content-wrapper::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
}

.sidebar-nav::-webkit-scrollbar-thumb,
.content-wrapper::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 3px;
}

.sidebar-nav::-webkit-scrollbar-thumb:hover,
.content-wrapper::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}
</style>
