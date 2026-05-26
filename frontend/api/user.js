/**
 * 用户相关操作 - HTTP版本
 */
import { post, get, put } from './request.js'

/**
 * 微信一键登录
 * 流程：uni.login获取code → 后端用code换openid → 查询/创建用户 → 返回token
 * @param {Object} options - 可选参数 { nickname, avatar }
 * @returns {Promise<Object>} - 登录结果
 */
export const weixinLogin = async (options = {}) => {
  try {
    // 第一步：调用 uni.login 获取微信登录凭证 code
    const loginRes = await new Promise((resolve, reject) => {
      uni.login({
        provider: 'weixin',
        success: resolve,
        fail: (err) => {
          console.error('uni.login失败:', err)
          reject(new Error('获取微信登录凭证失败'))
        }
      })
    })

    if (!loginRes.code) {
      return { success: false, message: '获取微信登录凭证失败' }
    }

    // 第二步：将 code 传给后端，后端向微信服务器换取 openid
    const res = await post('/auth/wx-login', {
      code: loginRes.code,
      nickname: options.nickname || options.nickName || '',
      avatar: options.avatar || options.avatarUrl || ''
    })

    // 登录成功，保存用户信息和 token 到本地
    const userInfo = {
      id: res.user_id,
      nickname: res.nickname,
      avatar: res.avatar
    }
    uni.setStorageSync('userInfo', userInfo)
    uni.setStorageSync('token', res.token)
    uni.setStorageSync('loginTime', Date.now())

    return {
      success: true,
      data: userInfo,
      message: '登录成功'
    }
  } catch (error) {
    console.error('微信登录失败:', error)
    return {
      success: false,
      message: error.message || '登录失败，请重试'
    }
  }
}

/**
 * 检查 token 是否存在且有效
 * @returns {boolean}
 */
export const checkToken = () => {
  const token = uni.getStorageSync('token')
  const loginTime = uni.getStorageSync('loginTime')

  if (!token) return false
  if (!loginTime) return true

  // 检查是否在7天内
  const sevenDays = 7 * 24 * 60 * 60 * 1000
  const isExpired = (Date.now() - loginTime) > sevenDays

  if (isExpired) {
    logout()
    return false
  }

  return true
}

/**
 * 获取当前用户信息（从后端刷新）
 * @returns {Promise<Object>}
 */
export const fetchCurrentUser = async () => {
  try {
    const res = await get('/auth/me')
    const userInfo = {
      id: res.id,
      nickname: res.nickname,
      avatar: res.avatar
    }
    uni.setStorageSync('userInfo', userInfo)
    return userInfo
  } catch (e) {
    console.error('获取用户信息失败:', e)
    return null
  }
}

/**
 * 获取当前用户信息（本地缓存）
 * @returns {Object|null}
 */
export const getCurrentUser = () => {
  const userInfo = uni.getStorageSync('userInfo')
  const token = uni.getStorageSync('token')

  if (userInfo && token && checkToken()) {
    return { ...userInfo, token }
  }
  return null
}

/**
 * 检查是否已登录
 * @returns {boolean}
 */
export const isLoggedIn = () => {
  return !!uni.getStorageSync('token') && !!uni.getStorageSync('userInfo') && checkToken()
}

/**
 * 获取用户ID
 * @returns {number|null}
 */
export const getUserId = () => {
  const userInfo = uni.getStorageSync('userInfo')
  return userInfo?.id || null
}

/**
 * 退出登录
 */
export const logout = () => {
  uni.removeStorageSync('userInfo')
  uni.removeStorageSync('token')
  uni.removeStorageSync('loginTime')
}

/**
 * 获取用户昵称
 * @returns {string}
 */
export const getUserNickname = () => {
  const userInfo = uni.getStorageSync('userInfo')
  return userInfo?.nickname || userInfo?.nickName || '用户'
}

/**
 * 获取用户头像
 * @returns {string}
 */
export const getUserAvatar = () => {
  const userInfo = uni.getStorageSync('userInfo')
  return userInfo?.avatar || userInfo?.avatarUrl || ''
}

/**
 * 更新用户信息（同步到后端）
 * @param {Object} userData - 要更新的用户数据 { nickname, avatar }
 * @returns {Promise<boolean>}
 */
export const updateUserInfo = async (userData) => {
  try {
    // 先更新本地缓存
    const userInfo = uni.getStorageSync('userInfo') || {}
    const updatedInfo = { ...userInfo, ...userData }
    uni.setStorageSync('userInfo', updatedInfo)

    // 同步到后端
    await put('/auth/me', {
      nickname: userData.nickname || '',
      avatar: userData.avatar || ''
    })

    return true
  } catch (e) {
    console.error('更新用户信息失败:', e)
    return false
  }
}

/**
 * 提交意见反馈
 * @param {Object} feedbackData - { type, content, contact, images }
 * @returns {Promise<Object>}
 */
export const submitFeedback = async (feedbackData) => {
  try {
    const res = await post('/feedback/submit', feedbackData)
    return { success: true, data: res }
  } catch (error) {
    console.error('提交反馈失败:', error)
    return { success: false, message: error.message || '提交失败' }
  }
}

/**
 * 获取用户反馈列表
 * @param {number} page - 页码
 * @param {number} pageSize - 每页数量
 * @returns {Promise<Object>}
 */
export const getFeedbackList = async (page = 1, pageSize = 10) => {
  try {
    const res = await get('/feedback/list', { page, page_size: pageSize })
    return { success: true, data: res.data || [], total: res.total || 0 }
  } catch (error) {
    console.error('获取反馈列表失败:', error)
    return { success: false, message: error.message || '获取失败', data: [] }
  }
}

/**
 * 获取用户反馈统计
 * @returns {Promise<Object>}
 */
export const getFeedbackStats = async () => {
  try {
    const res = await get('/feedback/stats')
    return { success: true, data: res.data || { total: 0, pending: 0, resolved: 0 } }
  } catch (error) {
    console.error('获取反馈统计失败:', error)
    return { success: false, message: error.message || '获取失败' }
  }
}

export default {
  weixinLogin,
  checkToken,
  fetchCurrentUser,
  getCurrentUser,
  isLoggedIn,
  getUserId,
  logout,
  getUserNickname,
  getUserAvatar,
  updateUserInfo,
  submitFeedback,
  getFeedbackList,
  getFeedbackStats
}
