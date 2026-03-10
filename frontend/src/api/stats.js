import api from './index'

// 获取统计概览
export const getOverview = (params) => api.get('/stats/overview', { params })

// 获取订单统计
export const getOrderStats = (params) => api.get('/stats/orders', { params })

// 获取收入统计
export const getRevenueStats = (params) => api.get('/stats/revenue', { params })

// 获取消息统计
export const getMessageStats = (params) => api.get('/stats/messages', { params })
