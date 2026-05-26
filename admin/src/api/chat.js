import request from '@/utils/request'

// 获取对话列表
export function getChatList(params) {
  return request({
    url: '/admin/chats',
    method: 'get',
    params,
  })
}

// 获取对话详情
export function getChatDetail(id) {
  return request({
    url: `/admin/chats/${id}`,
    method: 'get',
  })
}
