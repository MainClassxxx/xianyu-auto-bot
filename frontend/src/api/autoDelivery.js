import api from './index'

// 获取自动发货规则列表
export const getDeliveryRules = (params) => api.get('/auto-delivery/rules', { params })

// 创建自动发货规则
export const createDeliveryRule = (data) => api.post('/auto-delivery/rules', data)

// 更新自动发货规则
export const updateDeliveryRule = (id, data) => api.put(`/auto-delivery/rules/${id}`, data)

// 删除自动发货规则
export const deleteDeliveryRule = (id) => api.delete(`/auto-delivery/rules/${id}`)

// 查询库存
export const getStock = (ruleId) => api.get(`/auto-delivery/stock/${ruleId}`)

// 重置库存
export const resetStock = (ruleId, stock) => api.post(`/auto-delivery/stock/${ruleId}/reset`, { stock })

// 获取发货历史
export const getDeliveryHistory = (params) => api.get('/auto-delivery/history', { params })
