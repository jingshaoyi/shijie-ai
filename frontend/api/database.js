/**
 * 对话历史相关API - HTTP版本
 */
import { get, post, put, del } from './request.js'

/**
 * 保存对话历史（新建）
 * @param {Object} chatData - { messages, modelId, modelName }
 * @returns {Promise<Object>} - { success, id }
 */
export const saveChatToCloud = async (chatData) => {
  try {
    const messages = chatData.messages || (Array.isArray(chatData) ? chatData : [])
    if (!Array.isArray(messages) || messages.length === 0) {
      return { success: false, message: '消息不能为空' }
    }

    const cleanMessages = messages.map(msg => ({
      role: msg.role || 'user',
      content: msg.content || '',
      time: msg.time || ''
    })).filter(msg => msg.content)

    const res = await post('/chat/save', {
      messages: cleanMessages,
      model_id: chatData.modelId || '',
      model_name: chatData.modelName || ''
    })

    return { success: true, id: res.id, message: '保存成功' }
  } catch (error) {
    console.error('保存对话失败:', error)
    return { success: false, message: error.message || '保存失败' }
  }
}

/**
 * 更新对话历史
 * @param {number} chatId - 对话ID
 * @param {Object} chatData - { messages, modelId, modelName }
 * @returns {Promise<Object>}
 */
export const updateChatHistory = async (chatId, chatData) => {
  try {
    const messages = chatData.messages || []
    const cleanMessages = messages.map(msg => ({
      role: msg.role || 'user',
      content: msg.content || '',
      time: msg.time || ''
    })).filter(msg => msg.content)

    const res = await put(`/chat/update/${chatId}`, {
      messages: cleanMessages,
      model_id: chatData.modelId || '',
      model_name: chatData.modelName || ''
    })

    return { success: true, id: res.id, message: '更新成功' }
  } catch (error) {
    console.error('更新对话失败:', error)
    return { success: false, message: error.message || '更新失败' }
  }
}

/**
 * 获取对话历史列表
 * @param {number} page - 页码
 * @param {number} pageSize - 每页数量
 * @returns {Promise<Object>}
 */
export const getChatHistoryList = async (page = 1, pageSize = 20) => {
  try {
    const res = await get('/chat/list', { page, page_size: pageSize })
    return {
      success: true,
      data: res.data || [],
      total: res.total || 0
    }
  } catch (error) {
    console.error('获取对话历史失败:', error)
    return {
      success: false,
      message: error.message || '获取失败',
      data: []
    }
  }
}

/**
 * 获取单条对话详情
 * @param {number} id - 对话ID
 * @returns {Promise<Object>}
 */
export const getChatDetail = async (id) => {
  try {
    const res = await get(`/chat/detail/${id}`)
    if (res.code === 0 && res.data) {
      return {
        success: true,
        data: res.data
      }
    }
    return { success: false, message: '对话不存在' }
  } catch (error) {
    console.error('获取对话详情失败:', error)
    return {
      success: false,
      message: error.message || '获取失败'
    }
  }
}

/**
 * 删除对话历史
 * @param {number} id - 对话ID
 * @returns {Promise<Object>}
 */
export const deleteChatHistory = async (id) => {
  try {
    await del(`/chat/delete/${id}`)
    return { success: true, message: '删除成功' }
  } catch (error) {
    console.error('删除对话失败:', error)
    return { success: false, message: error.message || '删除失败' }
  }
}

/**
 * 清空所有对话历史
 * @returns {Promise<Object>}
 */
export const clearAllChatHistory = async () => {
  try {
    const res = await del('/chat/clear')
    return {
      success: true,
      message: '清空成功',
      count: res.count || 0
    }
  } catch (error) {
    console.error('清空对话历史失败:', error)
    return { success: false, message: error.message || '清空失败' }
  }
}

/**
 * 搜索对话历史（前端本地搜索，因为后端暂未实现搜索接口）
 * @param {string} keyword - 搜索关键词
 * @returns {Promise<Object>}
 */
export const searchChatHistory = async (keyword) => {
  if (!keyword) {
    return getChatHistoryList()
  }
  // 前端搜索：获取全部列表后本地过滤
  const result = await getChatHistoryList(1, 100)
  if (result.success && result.data) {
    const filtered = result.data.filter(item =>
      item.title && item.title.includes(keyword)
    )
    return { ...result, data: filtered, total: filtered.length }
  }
  return result
}

export default {
  saveChatToCloud,
  updateChatHistory,
  getChatHistoryList,
  getChatDetail,
  deleteChatHistory,
  clearAllChatHistory,
  searchChatHistory
}
