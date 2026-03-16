import api from './index'

/**
 * 获取会员套餐列表
 */
export function getMembershipPlans() {
  return api.get('/membership/plans')
}

/**
 * 创建会员订单
 */
export function createOrder(data) {
  return api.post('/membership/order/create', data)
}

/**
 * 获取订单详情
 */
export function getOrderDetail(orderNo) {
  return api.get(`/membership/order/${orderNo}`)
}

/**
 * 获取用户订单列表
 */
export function getUserOrders(params) {
  return api.get('/membership/orders', { params })
}

/**
 * 取消订单
 */
export function cancelOrder(orderNo) {
  return api.post(`/membership/order/${orderNo}/cancel`)
}

/**
 * 支付订单
 */
export function payOrder(orderNo, transactionId = null) {
  return api.post(`/membership/order/${orderNo}/pay`, null, {
    params: { transaction_id: transactionId }
  })
}

/**
 * 管理员开通会员
 */
export function adminGrantMembership(userId, level, days, reason = null) {
  return api.post('/membership/admin/grant', null, {
    params: { user_id: userId, level, days, reason }
  })
}

/**
 * 获取会员开通日志（管理员）
 */
export function getGrantLogs(params) {
  return api.get('/membership/admin/grant-logs', { params })
}
