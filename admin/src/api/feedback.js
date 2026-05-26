import request from '@/utils/request'

// 获取反馈列表
export function getFeedbackList(params) {
  return request({
    url: '/admin/feedbacks',
    method: 'get',
    params,
  })
}

// 回复反馈
export function replyFeedback(id, reply) {
  return request({
    url: `/admin/feedbacks/${id}/reply`,
    method: 'put',
    data: { reply },
  })
}
