import request from '@/api'

/**
 * 获取概览统计
 */
export function getOverview() {
  return request({
    url: '/stats/overview',
    method: 'get'
  })
}

/**
 * 获取订单统计
 */
export function getOrderStats(days = 7) {
  return request({
    url: `/stats/orders?days=${days}`,
    method: 'get'
  })
}

/**
 * 获取收入统计
 */
export function getRevenueStats(days = 7) {
  return request({
    url: `/stats/revenue?days=${days}`,
    method: 'get'
  })
}

/**
 * 获取账号统计
 */
export function getAccountStats() {
  return request({
    url: '/stats/accounts',
    method: 'get'
  })
}

/**
 * 获取商品统计
 */
export function getItemStats() {
  return request({
    url: '/stats/items',
    method: 'get'
  })
}
