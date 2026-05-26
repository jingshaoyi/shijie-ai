import request from '@/utils/request'

// 获取提示词列表
export function getPromptList(params) {
  return request({
    url: '/admin/prompts',
    method: 'get',
    params,
  })
}

// 创建提示词
export function createPrompt(data) {
  return request({
    url: '/admin/prompts',
    method: 'post',
    data,
  })
}

// 更新提示词
export function updatePrompt(id, data) {
  return request({
    url: `/admin/prompts/${id}`,
    method: 'put',
    data,
  })
}

// 删除提示词
export function deletePrompt(id) {
  return request({
    url: `/admin/prompts/${id}`,
    method: 'delete',
  })
}
