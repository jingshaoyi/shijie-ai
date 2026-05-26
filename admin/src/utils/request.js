import axios from 'axios'
import { message } from 'ant-design-vue'
import { useUserStore } from '@/stores/user'

// 创建 axios 实例
const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    const userStore = useUserStore()
    if (userStore.token) {
      config.headers.Authorization = `Bearer ${userStore.token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    const res = response.data

    // 如果响应成功
    if (res.success !== false) {
      return res
    }

    // 处理错误
    message.error(res.message || '请求失败')

    // 处理特定错误码
    if (res.code === 401) {
      const userStore = useUserStore()
      userStore.logout()
      window.location.href = '/login'
    }

    return Promise.reject(new Error(res.message || '请求失败'))
  },
  (error) => {
    const { response } = error

    if (response) {
      const { status, data } = response

      switch (status) {
        case 401:
          message.error('登录已过期，请重新登录')
          {
            const userStore = useUserStore()
            userStore.logout()
            window.location.href = '/login'
          }
          break
        case 403:
          message.error('没有权限执行此操作')
          break
        case 404:
          message.error('请求的资源不存在')
          break
        case 500:
          message.error(data?.message || '服务器内部错误')
          break
        default:
          message.error(data?.message || `请求失败 (${status})`)
      }
    } else {
      message.error('网络错误，请检查网络连接')
    }

    return Promise.reject(error)
  }
)

export default request
