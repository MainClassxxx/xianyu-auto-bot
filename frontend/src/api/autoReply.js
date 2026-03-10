import api from './index'

// 获取自动回复规则列表
export const getReplyRules = (params) => api.get('/auto-reply/rules', { params })

// 创建自动回复规则
export const createReplyRule = (data) => api.post('/auto-reply/rules', data)

// 更新自动回复规则
export const updateReplyRule = (id, data) => api.put(`/auto-reply/rules/${id}`, data)

// 删除自动回复规则
export const deleteReplyRule = (id) => api.delete(`/auto-reply/rules/${id}`)

// 启用/禁用规则
export const toggleReplyRule = (id) => api.post(`/auto-reply/rules/${id}/toggle`)
