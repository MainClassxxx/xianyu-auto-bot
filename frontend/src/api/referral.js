import api from './index'

/**
 * 获取推广链接
 */
export function getReferralLink() {
  return api.get('/referral/link')
}

/**
 * 创建推广链接
 */
export function createReferralLink() {
  return api.post('/referral/link/create')
}

/**
 * 获取推广统计
 */
export function getReferralStats() {
  return api.get('/referral/stats')
}

/**
 * 获取用户余额
 */
export function getBalance() {
  return api.get('/referral/balance')
}

/**
 * 获取充值套餐
 */
export function getRechargePackages() {
  return api.get('/referral/balance/packages')
}

/**
 * 创建充值订单
 */
export function createRechargeOrder(data) {
  return api.post('/referral/recharge/create', data)
}

/**
 * 支付充值订单
 */
export function payRechargeOrder(orderNo, transactionId = null) {
  return api.post(`/referral/recharge/${orderNo}/pay`, null, {
    params: { transaction_id: transactionId }
  })
}

/**
 * 获取余额交易记录
 */
export function getBalanceTransactions(params) {
  return api.get('/referral/balance/transactions', { params })
}

/**
 * 使用余额支付
 */
export function useBalance(data) {
  return api.post('/referral/balance/use', data)
}

/**
 * 追踪推广注册
 */
export function trackReferralRegistration(referralCode) {
  return api.post('/referral/register/track', null, {
    params: { referral_code: referralCode }
  })
}
