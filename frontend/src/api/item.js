import api from './index'

// 获取商品列表
export const getItems = (params) => api.get('/items', { params })

// 获取商品详情
export const getItem = (id) => api.get(`/items/${id}`)

// 修改商品价格
export const updateItemPrice = (id, price) => api.post(`/items/${id}/price`, { price })

// 上架/下架商品
export const toggleItem = (id, action) => api.post(`/items/${id}/toggle`, { action })

// 删除商品
export const deleteItem = (id) => api.delete(`/items/${id}`)
