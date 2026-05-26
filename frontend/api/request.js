/**
 * API基础配置
 * 注意：部署时请将此地址替换为您的后端API地址
 */

// 从环境变量或配置文件读取API地址，默认为本地开发地址
const BASE_URL = (function() {
  // #ifdef MP-WEIXIN
  // 小程序环境使用配置的地址
  return 'https://YOUR_BACKEND_DOMAIN/api'
  // #endif
  
  // H5/其他环境使用本地开发地址
  return 'http://localhost:9090/api'
})()

// 开发环境使用本地地址
// const BASE_URL = 'http://localhost:9090/api'

/**
 * 通用请求封装
 */
const request = (options) => {
  return new Promise((resolve, reject) => {
    const token = uni.getStorageSync('token')

    const header = {
      'Content-Type': 'application/json',
      ...options.header
    }

    // 如果有token，添加到请求头
    if (token) {
      header['Authorization'] = `Bearer ${token}`
    }

    uni.request({
      url: `${BASE_URL}${options.url}`,
      method: options.method || 'GET',
      data: options.data,
      header,
      success: (res) => {
        if (res.statusCode === 401) {
          // token过期或无效，清除登录状态
          uni.removeStorageSync('token')
          uni.removeStorageSync('userInfo')
          uni.removeStorageSync('loginTime')
          uni.showModal({
            title: '提示',
            content: '登录已过期，请重新登录',
            showCancel: false,
            success: () => {
              uni.reLaunch({ url: '/pages/login/login' })
            }
          })
          reject(new Error('登录已过期'))
          return
        }

        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data)
        } else {
          const errorMsg = res.data?.detail || res.data?.message || '请求失败'
          reject(new Error(errorMsg))
        }
      },
      fail: (err) => {
        console.error('请求失败:', options.url, err)
        reject(new Error(err.errMsg || '网络请求失败'))
      }
    })
  })
}

export const get = (url, data) => request({ url, method: 'GET', data })
export const post = (url, data) => request({ url, method: 'POST', data })
export const put = (url, data) => request({ url, method: 'PUT', data })
export const del = (url, data) => request({ url, method: 'DELETE', data })

export { BASE_URL }
export default request
