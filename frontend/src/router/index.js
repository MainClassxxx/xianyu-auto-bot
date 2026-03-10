import { createRouter, createWebHistory } from 'vue-router'
import Layout from '@/components/Layout.vue'

const routes = [
  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
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

export default router
