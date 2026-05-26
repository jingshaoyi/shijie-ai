/**
 * AI相关API - HTTP版本
 * 包含企业级SSE流式输出实现
 *
 * 核心机制：
 * 1. lastArrayBuffer - 处理UTF-8多字节字符跨chunk截断
 * 2. LegacyMessage - 处理不完整SSE消息（粘包/分包）
 * 3. requestTask.onChunkReceived() 绑定方式（非options内）
 * 4. responseType: 'arraybuffer' 明确指定
 * 5. enableHttp2: false 避免HTTP/2不稳定
 */
import { BASE_URL } from './request.js'

// ============================
// lastArrayBuffer 机制：处理 UTF-8 多字节字符跨 chunk 截断
// ============================
const lastArrayBufferMap = new Map()

/**
 * ArrayBuffer 转 String，处理 UTF-8 多字节字符被截断的情况
 * @param {ArrayBuffer} arr - 接收到的数据块
 * @param {string} uid - 请求唯一标识
 * @returns {string} 解码后的字符串
 */
function arrayBufferToString(arr, uid) {
  if (!arr || arr.byteLength === 0) return ''

  // 合并上次的不完整数据（如果有）
  if (lastArrayBufferMap.has(uid)) {
    const lastBuf = lastArrayBufferMap.get(uid)
    const combinedLength = lastBuf.byteLength + arr.byteLength
    const combinedBuffer = new ArrayBuffer(combinedLength)
    const combinedView = new Uint8Array(combinedBuffer)
    combinedView.set(new Uint8Array(lastBuf), 0)
    combinedView.set(new Uint8Array(arr), lastBuf.byteLength)
    arr = combinedBuffer
    lastArrayBufferMap.delete(uid)
  }

  const ints = new Uint8Array(arr)
  let str = ''
  let i = 0

  while (i < ints.length) {
    if (!ints[i]) {
      // 0值字节跳过
      i++
      continue
    }

    const byte = ints[i]

    if (byte < 0x80) {
      // 1字节字符 (ASCII)
      str += String.fromCharCode(byte)
      i++
    } else if (byte >= 0xC0 && byte < 0xE0) {
      // 2字节字符
      if (i + 1 >= ints.length) {
        // 不完整，保存剩余字节
        const remaining = ints.slice(i)
        const buf = new ArrayBuffer(remaining.length)
        new Uint8Array(buf).set(remaining)
        lastArrayBufferMap.set(uid, buf)
        break
      }
      str += String.fromCharCode(((byte & 0x1F) << 6) | (ints[i + 1] & 0x3F))
      i += 2
    } else if (byte >= 0xE0 && byte < 0xF0) {
      // 3字节字符（大部分中文）
      if (i + 2 >= ints.length) {
        const remaining = ints.slice(i)
        const buf = new ArrayBuffer(remaining.length)
        new Uint8Array(buf).set(remaining)
        lastArrayBufferMap.set(uid, buf)
        break
      }
      str += String.fromCharCode(
        ((byte & 0x0F) << 12) |
        ((ints[i + 1] & 0x3F) << 6) |
        (ints[i + 2] & 0x3F)
      )
      i += 3
    } else if (byte >= 0xF0) {
      // 4字节字符（emoji等）
      if (i + 3 >= ints.length) {
        const remaining = ints.slice(i)
        const buf = new ArrayBuffer(remaining.length)
        new Uint8Array(buf).set(remaining)
        lastArrayBufferMap.set(uid, buf)
        break
      }
      const codePoint =
        ((byte & 0x07) << 18) |
        ((ints[i + 1] & 0x3F) << 12) |
        ((ints[i + 2] & 0x3F) << 6) |
        (ints[i + 3] & 0x3F)
      str += String.fromCodePoint ? String.fromCodePoint(codePoint) : '\uFFFD'
      i += 4
    } else {
      // 无效字节
      str += '\uFFFD'
      i++
    }
  }

  return str
}

// ============================
// SSE 数据解析
// ============================

/**
 * 使用正则表达式提取 data: 开头的消息块
 * @param {string} sseData - 原始 SSE 数据字符串
 * @returns {string[]} 匹配到的 data: 消息数组
 */
function parseSSEData(sseData) {
  const regex = /data:([\s\S]*?)(?=\n\s*data:|$)/g
  const matches = [...sseData.matchAll(regex)]
  return matches.map(match => match[0].trim().replace(/\n/g, ''))
}

/**
 * 安全解析 data: 开头的 JSON 字符串
 * @param {string} str - 如 "data:{\"content\":\"hello\"}"
 * @returns {object|null} 解析后的 JSON 对象，失败返回 null
 */
function safeJsonParse(str) {
  const s = (str || '').trim()
  if (!s.startsWith('data:')) return null
  try {
    return JSON.parse(s.slice(5).trim())
  } catch (e) {
    return null
  }
}

// ============================
// LegacyMessage 机制：处理不完整 SSE 消息
// ============================
const legacyMessageMap = new Map()

/**
 * 获取AI模型列表
 */
export const getAIModels = async (provider = null) => {
  return new Promise((resolve, reject) => {
    const token = uni.getStorageSync('token')
    let url = `${BASE_URL}/models/list`
    if (provider) url += `?provider=${provider}`

    uni.request({
      url,
      method: 'GET',
      header: {
        'Content-Type': 'application/json',
        'Authorization': token ? `Bearer ${token}` : ''
      },
      success: (res) => {
        if (res.statusCode === 200) {
          resolve(res.data)
        } else {
          reject(new Error(res.data?.detail || '获取模型列表失败'))
        }
      },
      fail: (err) => reject(new Error(err.errMsg || '网络请求失败'))
    })
  })
}

/**
 * 上传图片到服务器
 * @param {string} filePath - 本地图片路径
 * @returns {Promise<string>} - 图片URL
 */
export const uploadImage = async (filePath) => {
  const token = uni.getStorageSync('token')

  return new Promise((resolve, reject) => {
    uni.uploadFile({
      url: `${BASE_URL}/upload/image`,
      filePath: filePath,
      name: 'file',
      header: {
        'Authorization': token ? `Bearer ${token}` : ''
      },
      success: (res) => {
        if (res.statusCode === 200) {
          const data = JSON.parse(res.data)
          if (data.code === 0 && data.url) {
            resolve(data.url)
          } else {
            reject(new Error(data.message || '上传失败'))
          }
        } else {
          reject(new Error('上传失败'))
        }
      },
      fail: (err) => reject(new Error(err.errMsg || '上传失败'))
    })
  })
}

/**
 * AI对话 - SSE流式输出（企业级实现）
 *
 * 核心改进：
 * 1. lastArrayBuffer 缓存处理UTF-8多字节字符截断
 * 2. LegacyMessage 缓存处理不完整SSE消息
 * 3. requestTask.onChunkReceived() 绑定方式
 * 4. responseType: 'arraybuffer' 明确指定
 * 5. enableHttp2: false 避免HTTP/2不稳定
 * 6. 支持图片上传和多模态对话
 */
export const aiChatStream = (message, history = [], onChunk, onDone, onError, modelId = null, images = []) => {
  const token = uni.getStorageSync('token')
  const url = `${BASE_URL}/ai/chat/stream`
  const uid = Math.random().toString(36).substring(2, 10) + Date.now().toString(36)

  let fullText = ''
  let doneCalled = false

  const callDone = (text) => {
    if (doneCalled) return
    doneCalled = true
    // 清理缓存
    lastArrayBufferMap.delete(uid)
    legacyMessageMap.delete(uid)
    onDone(text || fullText)
  }

  const callError = (err) => {
    if (doneCalled) return
    // 清理缓存
    lastArrayBufferMap.delete(uid)
    legacyMessageMap.delete(uid)
    onError(err)
  }

  /**
   * 处理接收到的 chunk 数据
   * @param {ArrayBuffer|string} data - 原始数据（可能是 ArrayBuffer 或字符串）
   */
  const handleChunk = (data) => {
    // 第一步：转字符串（兼容 ArrayBuffer 和 string 两种类型）
    let str1 = ''
    if (typeof data === 'string') {
      str1 = data
    } else if (data && data.byteLength !== undefined) {
      str1 = arrayBufferToString(data, uid)
    }
    if (!str1) return

    // 第二步：拼接遗留消息（如果有）
    let prefix = ''
    if (legacyMessageMap.has(uid)) {
      prefix = legacyMessageMap.get(uid)
    }
    const str2 = prefix + str1

    // 第三步：SSE 协议解析
    const jsonStrings = parseSSEData(str2)

    if (!jsonStrings.length) {
      // 解析为空 -> 该部分为片段，缓存起来
      legacyMessageMap.set(uid, str2)
    } else {
      // 解析到内容，清除遗留消息
      legacyMessageMap.delete(uid)

      // 非最后一项：直接解析并回调
      for (let i = 0; i < jsonStrings.length - 1; i++) {
        const parsed = safeJsonParse(jsonStrings[i])
        if (!parsed) continue

        if (parsed.content) {
          fullText += parsed.content
          onChunk(parsed.content)
        }
      }

      // 最后一项特殊处理：尝试解析，失败则缓存为遗留消息
      const last = jsonStrings[jsonStrings.length - 1]
      const lastParsed = safeJsonParse(last)

      if (lastParsed) {
        if (lastParsed.content) {
          fullText += lastParsed.content
          onChunk(lastParsed.content)
        }
        // 检查是否是 [DONE] 信号
        const lastStr = last.trim()
        if (lastStr === 'data:[DONE]' || lastStr === 'data: [DONE]') {
          callDone(fullText)
        }
      } else {
        // JSON解析失败，说明是半条消息，缓存
        legacyMessageMap.set(uid, last)
      }
    }
  }

  // 判断是否在微信小程序环境
  const isWx = typeof wx !== 'undefined' && wx.request

  if (isWx) {
    // 微信小程序：使用 wx.request + onChunkReceived（绑定方式）
    let requestTask = null

    try {
      requestTask = wx.request({
        url,
        method: 'POST',
        header: {
          'Content-Type': 'application/json',
          'Authorization': token ? `Bearer ${token}` : '',
          'Accept': 'text/event-stream'
        },
        data: {
          message,
          history: history.map(m => ({ role: m.role, content: m.content })),
          model_id: modelId || undefined,
          images: images && images.length > 0 ? images : undefined
        },
        enableChunked: true,
        // 不设置 responseType，让微信自动处理
        // responseType: 'arraybuffer' 在部分微信版本会导致 onChunkReceived 不触发
        enableHttp2: false,
        timeout: 120000, // 120秒超时

        success: (res) => {
          if (res.statusCode !== 200) {
            callError(new Error(res.data?.detail || `请求失败(${res.statusCode})`))
            return
          }
          // success 回调时处理可能残留的数据
          if (res.data) {
            if (typeof res.data === 'string' && res.data) {
              handleChunk(res.data)
            } else if (res.data.byteLength > 0) {
              handleChunk(res.data)
            }
          }
          callDone(fullText)
        },

        fail: (err) => {
          console.error('AI对话请求失败:', err)
          callError(new Error(err.errMsg || '网络请求失败'))
        },

        complete: () => {
          // 请求完成时清理缓存
          lastArrayBufferMap.delete(uid)
          legacyMessageMap.delete(uid)
        }
      })

      // 关键：通过 requestTask.onChunkReceived 绑定（而非 options 内）
      if (requestTask && requestTask.onChunkReceived) {
        requestTask.onChunkReceived((res) => {
          handleChunk(res.data)
        })
      }
    } catch (err) {
      console.error('SSE请求异常:', err)
      callError(new Error('请求异常'))
    }

    return requestTask
  } else {
    // H5/其他环境：使用 uni.request（降级为非流式）
    const requestTask = uni.request({
      url,
      method: 'POST',
      header: {
        'Content-Type': 'application/json',
        'Authorization': token ? `Bearer ${token}` : '',
        'Accept': 'text/event-stream'
      },
      data: {
        message,
        history: history.map(m => ({ role: m.role, content: m.content })),
        model_id: modelId || undefined
      },
      timeout: 120000,

      success: (res) => {
        if (res.statusCode !== 200) {
          onError(new Error(res.data?.detail || '请求失败'))
          return
        }

        // 非流式降级：从完整响应中解析
        if (res.data) {
          let text = ''
          if (res.data instanceof ArrayBuffer) {
            text = arrayBufferToString(res.data, uid)
          } else if (typeof res.data === 'string') {
            text = res.data
          }

          if (text) {
            // 按 \n\n 分割 SSE 消息
            const blocks = text.split('\n\n').filter(b => b.trim())
            for (const block of blocks) {
              const lines = block.split('\n')
              for (const line of lines) {
                const trimmed = line.trim()
                if (!trimmed.startsWith('data:')) continue
                const jsonStr = trimmed.slice(5).trim()
                if (jsonStr === '[DONE]') continue
                try {
                  const parsed = JSON.parse(jsonStr)
                  if (parsed.content) {
                    fullText += parsed.content
                    onChunk(parsed.content)
                  }
                } catch (e) {
                  // 忽略解析失败
                }
              }
            }
          }
        }

        onDone(fullText)
      },

      fail: (err) => {
        console.error('AI对话请求失败:', err)
        onError(new Error(err.errMsg || '网络请求失败'))
      }
    })

    return requestTask
  }
}

/**
 * AI对话 - 非流式（返回完整结果）
 */
export const aiChat = async (message, history = [], modelId = null) => {
  const token = uni.getStorageSync('token')

  return new Promise((resolve, reject) => {
    uni.request({
      url: `${BASE_URL}/ai/chat`,
      method: 'POST',
      header: {
        'Content-Type': 'application/json',
        'Authorization': token ? `Bearer ${token}` : ''
      },
      data: {
        message,
        history: history.map(m => ({ role: m.role, content: m.content })),
        model_id: modelId || undefined
      },
      success: (res) => {
        if (res.statusCode === 200 && res.data && res.data.code === 0) {
          resolve(res.data.data)
        } else {
          reject(new Error(res.data?.detail || res.data?.message || '请求失败'))
        }
      },
      fail: (err) => reject(new Error(err.errMsg || '网络请求失败'))
    })
  })
}

/**
 * 文本生成
 */
export const textGenerate = async (params, modelId = null) => {
  const token = uni.getStorageSync('token')

  return new Promise((resolve, reject) => {
    uni.request({
      url: `${BASE_URL}/ai/text-gen`,
      method: 'POST',
      header: {
        'Content-Type': 'application/json',
        'Authorization': token ? `Bearer ${token}` : ''
      },
      data: { ...params, model_id: modelId || undefined },
      success: (res) => {
        if (res.statusCode === 200 && res.data && res.data.code === 0) {
          resolve(res.data.data)
        } else {
          reject(new Error(res.data?.detail || '生成失败'))
        }
      },
      fail: (err) => reject(new Error(err.errMsg || '网络请求失败'))
    })
  })
}

/**
 * 翻译
 */
export const translate = async (text, sourceLang = 'auto', targetLang = 'en', modelId = null) => {
  const token = uni.getStorageSync('token')

  return new Promise((resolve, reject) => {
    uni.request({
      url: `${BASE_URL}/ai/translate`,
      method: 'POST',
      header: {
        'Content-Type': 'application/json',
        'Authorization': token ? `Bearer ${token}` : ''
      },
      data: { text, source_lang: sourceLang, target_lang: targetLang, model_id: modelId || undefined },
      success: (res) => {
        if (res.statusCode === 200 && res.data && res.data.code === 0) {
          resolve(res.data.data)
        } else {
          reject(new Error(res.data?.detail || '翻译失败'))
        }
      },
      fail: (err) => reject(new Error(err.errMsg || '网络请求失败'))
    })
  })
}
