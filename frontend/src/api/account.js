import api from './index'

// 获取账号列表
export const getAccounts = (params) => api.get('/accounts', { params })

// 添加账号
export const addAccount = (data) => api.post('/accounts', data)

// 获取账号详情
export const getAccount = (id) => api.get(`/accounts/${id}`)

// 更新账号
export const updateAccount = (id, data) => api.put(`/accounts/${id}`, data)

// 删除账号
export const deleteAccount = (id) => api.delete(`/accounts/${id}`)

// 刷新账号
export const refreshAccount = (id) => api.post(`/accounts/${id}/refresh`)

// 重启账号
export const restartAccount = (id) => api.post(`/accounts/${id}/restart`)
