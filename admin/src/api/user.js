import request from '@/utils/request'

// 获取用户列表
export function getUserList(params) {
  return request({
    url: '/admin/users',
    method: 'get',
    params,
  })
}

// 获取用户详情
export function getUserDetail(id) {
  return request({
    url: `/admin/users/${id}`,
    method: 'get',
  })
}

// 更新用户状态
export function updateUserStatus(id, status) {
  return request({
    url: `/admin/users/${id}/status`,
    method: 'put',
    data: { status },
  })
}

// 删除用户
export function deleteUser(id) {
  return request({
    url: `/admin/users/${id}`,
    method: 'delete',
  })
}

// 获取用户统计
export function getUserStats() {
  return request({
    url: '/admin/user-stats',
    method: 'get',
  })
}
