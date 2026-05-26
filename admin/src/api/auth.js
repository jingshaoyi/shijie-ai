import request from '@/utils/request'

export function login(data) {
  return request({
    url: '/auth/admin/login',
    method: 'post',
    data,
  })
}

export function getUserInfo() {
  return request({
    url: '/auth/admin/info',
    method: 'get',
  })
}

export function logout() {
  return request({
    url: '/auth/admin/logout',
    method: 'post',
  })
}
