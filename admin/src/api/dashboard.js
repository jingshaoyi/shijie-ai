import request from '@/utils/request'

// 获取统计数据
export function getStatistics() {
  return request({
    url: '/admin/statistics',
    method: 'get',
  })
}

// 获取趋势数据
export function getTrendData(days = 7) {
  return request({
    url: '/admin/trend',
    method: 'get',
    params: { days },
  })
}

// 获取模型使用统计
export function getModelStats() {
  return request({
    url: '/admin/model-stats',
    method: 'get',
  })
}

// 获取最近活动
export function getRecentActivities(limit = 10) {
  return request({
    url: '/admin/activities',
    method: 'get',
    params: { limit },
  })
}
