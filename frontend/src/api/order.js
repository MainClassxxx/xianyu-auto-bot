import api from './index'

// 获取订单列表
export const getOrders = (params) => api.get('/orders', { params })

// 获取订单详情
export const getOrder = (id) => api.get(`/orders/${id}`)

// 发货
export const deliverOrder = (id, content) => api.post(`/orders/${id}/deliver`, { content })

// 刷新订单状态
export const refreshOrder = (id) => api.post(`/orders/${id}/refresh`)

// 删除订单
export const deleteOrder = (id) => api.delete(`/orders/${id}`)
