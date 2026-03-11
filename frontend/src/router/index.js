import { createRouter, createWebHistory } from 'vue-router'
import Layout from '@/components/Layout.vue'
import { useUserStore } from '@/store/user'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录', requiresAuth: false }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue'),
    meta: { title: '注册', requiresAuth: false }
  },
  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    meta: { requiresAuth: true },
    children: [
      {
        path: '/dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '仪表盘', icon: 'DataLine' }
      },
      {
        path: '/accounts',
        name: 'Accounts',
        component: () => import('@/views/Accounts.vue'),
        meta: { title: '账号管理', icon: 'User' }
      },
      {
        path: '/items',
        name: 'Items',
        component: () => import('@/views/Items.vue'),
        meta: { title: '商品管理', icon: 'ShoppingCart' }
      },
      {
        path: '/orders',
        name: 'Orders',
        component: () => import('@/views/Orders.vue'),
        meta: { title: '订单管理', icon: 'List' }
      },
      {
        path: '/conversations',
        name: 'Conversations',
        component: () => import('@/views/Conversations.vue'),
        meta: { title: '对话消息', icon: 'ChatDotRound' }
      },
      {
        path: '/auto-reply',
        name: 'AutoReply',
        component: () => import('@/views/AutoReply.vue'),
        meta: { title: '自动回复', icon: 'ChatLineRound' }
      },
      {
        path: '/auto-delivery',
        name: 'AutoDelivery',
        component: () => import('@/views/AutoDelivery.vue'),
        meta: { title: '自动发货', icon: 'Box' }
      },
      {
        path: '/notifications',
        name: 'Notifications',
        component: () => import('@/views/Notifications.vue'),
        meta: { title: '通知管理', icon: 'Bell' }
      },
      {
        path: '/stats',
        name: 'Stats',
        component: () => import('@/views/Stats.vue'),
        meta: { title: '数据统计', icon: 'TrendCharts' }
      },
      {
        path: '/settings',
        name: 'Settings',
        component: () => import('@/views/Settings.vue'),
        meta: { title: '系统设置', icon: 'Setting' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  console.log('路由守卫:', to.path, 'from:', from.path)
  
  // 设置页面标题
  document.title = to.meta.title ? `${to.meta.title} - 闲鱼机器人` : '闲鱼自动售货机器人'
  
  const userStore = useUserStore()
  const requiresAuth = to.meta.requiresAuth !== false
  const isLoggedIn = userStore.isLoggedIn
  
  console.log('requiresAuth:', requiresAuth, 'isLoggedIn:', isLoggedIn)
  
  if (requiresAuth && !isLoggedIn) {
    // 需要登录但未登录，跳转到登录页
    console.log('未登录，跳转到登录页')
    next({
      path: '/login',
      query: { redirect: to.fullPath }
    })
  } else if (to.path === '/login' && isLoggedIn) {
    // 已登录访问登录页，重定向到首页
    console.log('已登录，跳转到仪表盘')
    next({ path: '/dashboard' })
  } else {
    console.log('允许访问')
    next()
  }
})

export default router
