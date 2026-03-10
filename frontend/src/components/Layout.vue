<template>
  <el-container class="layout-container">
    <!-- 侧边栏 -->
    <el-aside :width="isCollapse ? '64px' : '220px'" class="sidebar">
      <div class="logo">
        <el-icon :size="28" color="#409EFF"><FishFish /></el-icon>
        <span v-show="!isCollapse" class="logo-text">闲鱼机器人</span>
      </div>
      
      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapse"
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
        router
        :unique-opened="true"
      >
        <el-menu-item
          v-for="route in menuRoutes"
          :key="route.path"
          :index="route.path"
        >
          <el-icon><component :is="route.meta.icon" /></el-icon>
          <template #title>{{ route.meta.title }}</template>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <!-- 主内容区 -->
    <el-container>
      <!-- 顶部导航 -->
      <el-header class="header">
        <div class="header-left">
          <el-icon class="collapse-btn" @click="toggleCollapse">
            <component :is="isCollapse ? 'Expand' : 'Fold'" />
          </el-icon>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item>{{ currentRoute.meta.title }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        
        <div class="header-right">
          <el-badge :value="3" :hidden="!hasNotifications" class="notification">
            <el-icon :size="20"><Bell /></el-icon>
          </el-badge>
          
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              <el-avatar :size="36" src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png" />
              <span class="username">管理员</span>
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人设置</el-dropdown-item>
                <el-dropdown-item command="docs">帮助文档</el-dropdown-item>
                <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- 内容区域 -->
      <el-main class="main-content">
        <transition name="fade" mode="out-in">
          <router-view :key="$route.fullPath" />
        </transition>
      </el-main>

      <!-- 页脚 -->
      <el-footer class="footer">
        <div class="footer-content">
          <span>© 2026 闲鱼自动售货机器人 v3.1</span>
          <span>Powered by 易拉罐</span>
        </div>
      </el-footer>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const isCollapse = ref(false)
const currentRoute = computed(() => route)
const activeMenu = computed(() => route.path)
const hasNotifications = ref(true)

const menuRoutes = computed(() => {
  return [
    { path: '/dashboard', meta: { title: '仪表盘', icon: 'DataLine' } },
    { path: '/accounts', meta: { title: '账号管理', icon: 'User' } },
    { path: '/items', meta: { title: '商品管理', icon: 'ShoppingCart' } },
    { path: '/orders', meta: { title: '订单管理', icon: 'List' } },
    { path: '/conversations', meta: { title: '对话消息', icon: 'ChatDotRound' } },
    { path: '/auto-reply', meta: { title: '自动回复', icon: 'ChatLineRound' } },
    { path: '/auto-delivery', meta: { title: '自动发货', icon: 'Box' } },
    { path: '/notifications', meta: { title: '通知管理', icon: 'Bell' } },
    { path: '/stats', meta: { title: '数据统计', icon: 'TrendCharts' } },
    { path: '/settings', meta: { title: '系统设置', icon: 'Setting' } }
  ]
})

const toggleCollapse = () => {
  isCollapse.value = !isCollapse.value
}

const handleCommand = (command) => {
  if (command === 'logout') {
    // TODO: 退出登录逻辑
    router.push('/login')
  } else if (command === 'docs') {
    window.open('https://github.com/MainClassxxx/xianyu-auto-bot', '_blank')
  } else if (command === 'profile') {
    router.push('/settings')
  }
}

// 监听路由变化，确保菜单高亮正确
watch(() => route.path, (newPath) => {
  // 路由变化时自动更新菜单
  console.log('路由变化:', newPath)
})
</script>

<style scoped>
.layout-container {
  height: 100vh;
  background-color: #f0f2f5;
}

.sidebar {
  background: linear-gradient(180deg, #304156 0%, #1f2d3d 100%);
  transition: width 0.3s;
  overflow-x: hidden;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
}

.logo {
  height: 70px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  background-color: rgba(0, 0, 0, 0.2);
}

.logo-text {
  color: #fff;
  font-size: 18px;
  font-weight: 600;
  letter-spacing: 1px;
}

.el-menu {
  border-right: none;
}

.el-menu-item {
  transition: all 0.3s;
}

.el-menu-item:hover {
  background-color: rgba(64, 158, 255, 0.1) !important;
}

.el-menu-item.is-active {
  background-color: #409EFF !important;
}

.header {
  background-color: #fff;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 25px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  height: 60px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 25px;
}

.collapse-btn {
  font-size: 22px;
  cursor: pointer;
  transition: color 0.3s;
  color: #606266;
}

.collapse-btn:hover {
  color: #409EFF;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 25px;
}

.notification {
  cursor: pointer;
  transition: transform 0.3s;
}

.notification:hover {
  transform: scale(1.1);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 20px;
  transition: background-color 0.3s;
}

.user-info:hover {
  background-color: #f5f7fa;
}

.username {
  color: #606266;
  font-weight: 500;
}

.main-content {
  padding: 20px;
  overflow-y: auto;
  min-height: calc(100vh - 60px - 50px);
}

.footer {
  height: 50px;
  background-color: #fff;
  border-top: 1px solid #e6e6e6;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  color: #909399;
}

.footer-content {
  display: flex;
  gap: 30px;
}

/* 页面切换动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header {
    padding: 0 15px;
  }
  
  .username {
    display: none;
  }
  
  .footer-content {
    flex-direction: column;
    gap: 5px;
    text-align: center;
  }
}
</style>
