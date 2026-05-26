import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as loginApi, getUserInfo } from '@/api/auth'

export const useUserStore = defineStore('user', () => {
  // State
  const token = ref(localStorage.getItem('admin_token') || '')
  const userInfo = ref(null)
  const loading = ref(false)

  // Getters
  const isLoggedIn = computed(() => !!token.value)
  const username = computed(() => userInfo.value?.username || '')

  // Actions
  const setToken = (newToken) => {
    token.value = newToken
    localStorage.setItem('admin_token', newToken)
  }

  const clearToken = () => {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('admin_token')
  }

  const login = async (credentials) => {
    loading.value = true
    try {
      const res = await loginApi(credentials)
      if (res.success) {
        setToken(res.token)
        userInfo.value = res.user
        return { success: true }
      }
      return { success: false, message: res.message }
    } catch (error) {
      return { success: false, message: error.message }
    } finally {
      loading.value = false
    }
  }

  const logout = () => {
    clearToken()
  }

  const checkLoginStatus = async () => {
    if (token.value) {
      try {
        const res = await getUserInfo()
        if (res.success) {
          userInfo.value = res.data
        } else {
          clearToken()
        }
      } catch {
        clearToken()
      }
    }
  }

  return {
    token,
    userInfo,
    loading,
    isLoggedIn,
    username,
    login,
    logout,
    checkLoginStatus,
    setToken,
    clearToken,
  }
})
