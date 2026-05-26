<template>
  <view class="container">
    <!-- 状态栏占位 - 适配刘海屏 -->
    <view class="status-bar"></view>
    <!-- 自定义导航栏 -->
    <view class="custom-nav">
      <view class="nav-left" @click="goBack">
        <text class="icon-text">←</text>
      </view>
      <view class="nav-title" @click="openSessionPicker">
        <text class="title-icon">💬</text>
        <text class="title-text">{{ currentSessionTitle || 'AI对话' }}</text>
        <text class="title-arrow">▼</text>
      </view>
      <view class="nav-right">
        <text class="new-chat-btn" @click="createNewSession">➕</text>
      </view>
    </view>

    <!-- 模型选择器 -->
    <view class="model-selector" v-if="aiModels.length > 0">
      <view class="selector-wrapper" @click="showModelPicker = true">
        <image v-if="currentModel.icon" :src="currentModel.icon" class="model-icon" mode="aspectFit"></image>
        <text class="model-name">{{ currentModel.name || '选择模型' }}</text>
        <text class="selector-arrow">▼</text>
      </view>
    </view>
    
    <!-- 聊天内容区域 -->
    <scroll-view 
      class="chat-container" 
      scroll-y 
      :scroll-top="scrollTop"
      :scroll-with-animation="true"
      @scroll="onScroll"
    >
      <!-- 当前模型信息 -->
      <view class="current-model-info" v-if="currentModel.description">
        <text class="info-text">{{ currentModel.description }}</text>
      </view>

      <!-- 欢迎消息 -->
      <view class="welcome-msg" v-if="messages.length === 0">
        <view class="welcome-avatar">
          <image src="/static/logo.png" mode="aspectFit"></image>
          <view class="avatar-ring"></view>
        </view>
        <view class="welcome-bubble">
          <view class="welcome-text">你好！我是{{ currentModel.name || '识界AI助手' }}，有什么可以帮助你的吗？</view>
          <view class="welcome-tips">
            <text class="tip-item" v-for="(tip, i) in welcomeTips" :key="i" @click="useTip(tip)">{{ tip }}</text>
          </view>
        </view>
      </view>
      
      <!-- 消息列表 -->
      <view class="message-list">
        <view 
          class="message-item" 
          v-for="(msg, index) in messages" 
          :key="index"
          :class="{ 
            'user-msg': msg.role === 'user', 
            'ai-msg': msg.role === 'assistant',
            'msg-appear': msg.isNew 
          }"
        >
          <view class="msg-avatar" :class="{ 'avatar-pulse': msg.role === 'assistant' }">
            <image v-if="msg.role === 'assistant'" src="/static/logo.png" mode="aspectFit"></image>
            <text v-else class="user-icon">我</text>
          </view>
          <view class="msg-content">
            <view class="msg-bubble" :class="{ 'typing': msg.isTyping }">
              <!-- 图片消息 -->
              <view class="msg-images" v-if="msg.images && msg.images.length > 0">
                <image 
                  v-for="(img, imgIdx) in msg.images" 
                  :key="imgIdx"
                  :src="img" 
                  mode="aspectFill" 
                  class="msg-image"
                  @click="previewImage(img, msg.images)"
                ></image>
              </view>
              <!-- 文本内容 -->
              <text class="msg-text" v-if="msg.displayContent || msg.content">{{ msg.displayContent || msg.content }}</text>
              <view class="typing-cursor" v-if="msg.isTyping"></view>
            </view>
            <view class="msg-time" :class="{ 'time-fade': !msg.isNew }">{{ msg.time }}</view>
          </view>
        </view>
        
        <!-- 加载中 -->
        <view class="loading-msg" v-if="isLoading" :class="{ 'loading-appear': isLoading }">
          <view class="msg-avatar">
            <image src="/static/logo.png" mode="aspectFit"></image>
            <view class="thinking-ring"></view>
          </view>
          <view class="loading-content">
            <view class="loading-dots">
              <view class="dot"></view>
              <view class="dot"></view>
              <view class="dot"></view>
            </view>
            <view class="loading-text">{{ currentModel.name || 'AI' }}思考中...</view>
          </view>
        </view>
      </view>
      
      <view class="bottom-space"></view>
    </scroll-view>
    
    <!-- 输入区域 -->
    <view class="input-area">
      <!-- 已选图片预览 -->
      <view class="image-preview-area" v-if="selectedImages.length > 0">
        <view class="image-preview-list">
          <view class="image-preview-item" v-for="(img, idx) in selectedImages" :key="idx">
            <image :src="img" mode="aspectFill" class="preview-img"></image>
            <view class="remove-img-btn" @click="removeImage(idx)">
              <text class="remove-icon">✕</text>
            </view>
          </view>
        </view>
      </view>
      <view class="input-wrapper">
        <view class="input-left">
          <view class="image-btn" @click="chooseImage" v-if="selectedImages.length < 3">
            <text class="btn-icon">📷</text>
          </view>
          <textarea
            class="chat-input"
            v-model="inputMessage"
            :placeholder="selectedImages.length > 0 ? '描述一下图片内容...' : '请输入您的问题...'"
            :maxlength="500"
            :auto-height="true"
            :fixed="true"
            :cursor-spacing="20"
            @confirm="sendMessage"
            @focus="onInputFocus"
            @blur="onInputBlur"
          />
          <!-- 回写按钮 - 当输入框为空且有历史消息时显示 -->
          <view 
            class="rewrite-btn" 
            v-if="!inputMessage && lastSentMessage"
            @click="rewriteLastMessage"
            title="回写上次消息"
          >
            <text class="rewrite-icon">↩️</text>
          </view>
        </view>
        <view 
          class="send-btn" 
          :class="{ 'active': inputMessage.trim() || selectedImages.length > 0, 'sending': isSending }" 
          @click="sendMessage"
        >
          <text class="icon-text" v-if="!isSending">↑</text>
          <view class="send-spinner" v-else></view>
        </view>
      </view>
      
      <!-- 快捷提示 -->
      <view class="quick-tips" :class="{ 'tips-visible': showTips && !inputMessage }">
        <scroll-view scroll-x class="tips-scroll">
          <view class="tips-list">
            <view 
              class="tip-item" 
              v-for="(tip, index) in quickTips" 
              :key="index"
              :class="{ 'tip-fade': showTips }"
              :style="{ animationDelay: `${index * 0.05}s` }"
              @click="useTip(tip)"
            >
              {{ tip }}
            </view>
          </view>
        </scroll-view>
      </view>
    </view>
    
    <!-- 回到顶部按钮 -->
    <view 
      class="scroll-top-btn" 
      :class="{ 'btn-visible': showScrollTop }"
      @click="scrollToTop"
    >
      <text class="btn-icon">↑</text>
    </view>
    
    <!-- 模型选择弹窗 -->
    <view class="model-picker-mask" v-if="showModelPicker" @click="showModelPicker = false">
      <view class="model-picker" @click.stop>
        <view class="picker-header">
          <text class="picker-title">选择AI模型</text>
          <text class="picker-close" @click="showModelPicker = false">✕</text>
        </view>
        <scroll-view scroll-y class="picker-list">
          <view 
            class="picker-item" 
            v-for="(model, index) in aiModels" 
            :key="index"
            :class="{ 'item-active': currentModel.modelId === model.modelId }"
            @click="selectModel(model)"
          >
            <image v-if="model.icon" :src="model.icon" class="picker-item-icon" mode="aspectFit"></image>
            <view class="picker-item-info">
              <text class="picker-item-name">{{ model.name }}</text>
              <text class="picker-item-desc">{{ model.description }}</text>
            </view>
            <text class="picker-item-check" v-if="currentModel.modelId === model.modelId">✓</text>
          </view>
        </scroll-view>
      </view>
    </view>

    <!-- 会话列表弹窗 -->
    <view class="model-picker-mask" v-if="showSessionPicker" @click="showSessionPicker = false">
      <view class="model-picker session-picker" @click.stop>
        <view class="picker-header">
          <text class="picker-title">会话列表</text>
          <text class="picker-close" @click="showSessionPicker = false">✕</text>
        </view>
        <scroll-view scroll-y class="picker-list">
          <!-- 新建会话选项 -->
          <view class="picker-item new-session-item" @click="createNewSession">
            <view class="picker-item-icon new-icon">➕</view>
            <view class="picker-item-info">
              <text class="picker-item-name">新建会话</text>
              <text class="picker-item-desc">开始一个新的对话</text>
            </view>
          </view>
          
          <!-- 当前会话 -->
          <view 
            class="picker-item" 
            v-if="currentChatId"
            :class="{ 'item-active': true }"
          >
            <view class="picker-item-icon current-icon">💬</view>
            <view class="picker-item-info">
              <text class="picker-item-name">{{ currentSessionTitle || '当前会话' }}</text>
              <text class="picker-item-desc">{{ messages.length }} 条消息</text>
            </view>
            <text class="picker-item-check">✓</text>
          </view>
          
          <!-- 历史会话列表 -->
          <view 
            class="picker-item" 
            v-for="(session, index) in recentSessions" 
            :key="session.id"
            @click="switchSession(session)"
          >
            <view class="picker-item-icon history-icon">📄</view>
            <view class="picker-item-info">
              <text class="picker-item-name">{{ session.title || '未命名会话' }}</text>
              <text class="picker-item-desc">{{ session.preview || '暂无内容' }}</text>
            </view>
          </view>
        </scroll-view>
      </view>
    </view>
    <!-- 自定义TabBar -->
    <custom-tabbar :current="1" />
  </view>
</template>

<script setup>
import { ref, nextTick, onMounted, onUnmounted, computed } from 'vue'
import { onLoad, onShow } from '@dcloudio/uni-app'
import { aiChatStream, getAIModels, uploadImage } from '@/api/cloud.js'
import { saveChatToCloud, updateChatHistory, getChatDetail, getChatHistoryList } from '@/api/database.js'
import { isLoggedIn, getUserId } from '@/api/user.js'
import CustomTabbar from '@/components/custom-tabbar/custom-tabbar.vue'

const messages = ref([])
const inputMessage = ref('')
const isLoading = ref(false)
const isSending = ref(false)
const scrollTop = ref(0)
const currentChatId = ref(null)
const showTips = ref(true)
const showScrollTop = ref(false)
const selectedImages = ref([])  // 已选择的图片列表
const showSessionPicker = ref(false)  // 会话列表弹窗
const recentSessions = ref([])  // 最近会话列表

// 模型相关
const aiModels = ref([])
const currentModel = ref({})
const showModelPicker = ref(false)

// 显示会话列表弹窗
const openSessionPicker = async () => {
  await loadRecentSessions()
  showSessionPicker.value = true
}

// 计算当前会话标题
const currentSessionTitle = computed(() => {
  if (messages.value.length === 0) return null
  // 找到第一条用户消息作为标题
  const firstUserMsg = messages.value.find(m => m.role === 'user')
  if (firstUserMsg) {
    const title = firstUserMsg.content || firstUserMsg.displayContent || ''
    return title.slice(0, 15) + (title.length > 15 ? '...' : '')
  }
  return null
})

const welcomeTips = ['写一段文案', '翻译一下', '解释概念', '给我建议']

const quickTips = ref([
  '帮我写一段文案',
  '解释一下这个概念',
  '翻译这句话',
  '给我一些建议',
  '总结一下要点'
])

onLoad((options) => {
  if (!isLoggedIn()) {
    uni.showModal({
      title: '提示',
      content: '请先登录后再使用AI对话功能',
      showCancel: false,
      success: () => { uni.reLaunch({ url: '/pages/login/login' }) }
    })
    return
  }

  // 加载AI模型列表
  loadAIModels()

  // 加载本地保存的对话历史
  loadLocalChat()

  // 从URL参数获取historyId
  let historyId = options.historyId || ''

  // 如果没有URL参数，从本地存储获取（从历史记录页面跳转过来时使用）
  if (!historyId) {
    historyId = uni.getStorageSync('pendingHistoryId') || ''
    if (historyId) {
      uni.removeStorageSync('pendingHistoryId')
    }
  }

  if (historyId) {
    loadHistory(historyId)
  }
  
  if (options.prompt) {
    inputMessage.value = decodeURIComponent(options.prompt)
    setTimeout(() => sendMessage(), 500)
  }
})

// onShow: 每次页面显示时检查是否有待加载的历史记录或需要新建会话
onShow(() => {
  // 检查是否需要新建会话（从首页新建会话按钮进入时）
  const shouldNewChat = uni.getStorageSync('shouldNewChat')
  if (shouldNewChat) {
    uni.removeStorageSync('shouldNewChat')
    clearCurrentChat()
    return
  }

  const pendingHistoryId = uni.getStorageSync('pendingHistoryId')
  if (pendingHistoryId) {
    uni.removeStorageSync('pendingHistoryId')
    loadHistory(pendingHistoryId)
  }
})

// 从本地存储加载对话历史
const loadLocalChat = () => {
  try {
    const savedMessages = uni.getStorageSync('currentChatMessages')
    if (savedMessages && Array.isArray(savedMessages) && savedMessages.length > 0) {
      messages.value = savedMessages
      const savedChatId = uni.getStorageSync('currentChatId')
      if (savedChatId) {
        currentChatId.value = savedChatId
      }
    }
  } catch (e) {
    console.error('加载本地对话失败:', e)
  }
}

// 保存对话到本地存储
const saveToLocalStorage = () => {
  try {
    uni.setStorageSync('currentChatMessages', messages.value)
    if (currentChatId.value) {
      uni.setStorageSync('currentChatId', currentChatId.value)
    }
  } catch (e) {
    console.error('保存本地对话失败:', e)
  }
}

onMounted(() => {
  // 监听从首页传来的快捷聊天 prompt
  uni.$on('quickChatPrompt', (prompt) => {
    inputMessage.value = prompt
    setTimeout(() => sendMessage(), 500)
  })
})

onUnmounted(() => {
  // 移除事件监听，防止内存泄漏
  uni.$off('quickChatPrompt')
})

// 加载AI模型列表
const loadAIModels = async () => {
  try {
    const result = await getAIModels()
    if (result.models && result.models.length > 0) {
      aiModels.value = result.models
      // 设置默认模型
      const defaultModel = result.defaultModel || result.models[0]
      currentModel.value = defaultModel
      // 保存到本地存储
      const savedModelId = uni.getStorageSync('currentModelId')
      if (savedModelId) {
        const savedModel = result.models.find(m => m.modelId === savedModelId)
        if (savedModel) {
          currentModel.value = savedModel
        }
      }
    }
  } catch (error) {
    console.error('加载AI模型列表失败:', error)
    uni.showToast({ title: '加载模型列表失败', icon: 'none' })
  }
}

// 选择模型
const selectModel = (model) => {
  currentModel.value = model
  uni.setStorageSync('currentModelId', model.modelId)
  showModelPicker.value = false
  uni.showToast({ title: `已切换到${model.name}`, icon: 'none' })
}

const loadHistory = async (id) => {
  const result = await getChatDetail(id)
  if (result.success && result.data) {
    messages.value = (result.data.messages || []).map(msg => ({
      role: msg.role,
      content: msg.content,
      time: msg.time || '',
      isNew: false
    }))
    currentChatId.value = id
    scrollToBottom()
  }
}

const goBack = () => {
  if (messages.value.length > 0) {
    saveToCloud()
  }
  uni.navigateBack()
}

const clearChat = () => {
  uni.showModal({
    title: '提示',
    content: '确定要清空所有对话吗？',
    success: async (res) => {
      if (res.confirm) {
        clearCurrentChat()
        uni.showToast({ title: '已清空', icon: 'success' })
      }
    }
  })
}

// 清空当前会话（不弹确认）
const clearCurrentChat = () => {
  messages.value = []
  currentChatId.value = null
  selectedImages.value = []
  // 清除本地存储
  uni.removeStorageSync('currentChatMessages')
  uni.removeStorageSync('currentChatId')
}

// 创建新会话
const createNewSession = async () => {
  // 先保存当前会话
  if (messages.value.length > 0 && currentChatId.value) {
    await saveToCloud()
  }
  // 清空当前会话
  clearCurrentChat()
  showSessionPicker.value = false
  uni.showToast({ title: '已创建新会话', icon: 'success' })
}

// 加载最近会话列表
const loadRecentSessions = async () => {
  try {
    const result = await getChatHistoryList(1, 10)
    if (result.success && result.data) {
      // 过滤掉当前会话
      recentSessions.value = result.data.filter(s => s.id !== currentChatId.value)
    }
  } catch (error) {
    console.error('加载会话列表失败:', error)
  }
}

// 切换到指定会话
const switchSession = async (session) => {
  // 先保存当前会话
  if (messages.value.length > 0 && currentChatId.value) {
    await saveToCloud()
  }
  // 加载新会话
  showSessionPicker.value = false
  await loadHistory(session.id)
}

const useTip = (tip) => {
  inputMessage.value = tip
  showTips.value = false
}

// 选择图片
const chooseImage = () => {
  const remainCount = 3 - selectedImages.value.length
  if (remainCount <= 0) {
    uni.showToast({ title: '最多选择3张图片', icon: 'none' })
    return
  }
  
  uni.chooseMedia({
    count: remainCount,
    mediaType: ['image'],
    sourceType: ['album', 'camera'],
    success: (res) => {
      const tempFiles = res.tempFiles || []
      tempFiles.forEach(file => {
        if (selectedImages.value.length < 3) {
          selectedImages.value.push(file.tempFilePath)
        }
      })
    },
    fail: (err) => {
      console.error('选择图片失败:', err)
    }
  })
}

// 移除已选图片
const removeImage = (index) => {
  selectedImages.value.splice(index, 1)
}

// 预览图片
const previewImage = (current, urls) => {
  uni.previewImage({
    current,
    urls
  })
}

const onInputFocus = () => { showTips.value = false }
const onInputBlur = () => { if (!inputMessage.value) showTips.value = true }

// 保存最后发送的消息用于回写
const lastSentMessage = ref('')

const sendMessage = async () => {
  const message = inputMessage.value.trim()
  const hasImages = selectedImages.value.length > 0

  if ((!message && !hasImages) || isLoading.value || isSending.value) return

  if (!isLoggedIn()) {
    uni.showModal({
      title: '提示',
      content: '请先登录后再使用',
      showCancel: false,
      success: () => { uni.reLaunch({ url: '/pages/login/login' }) }
    })
    return
  }

  isSending.value = true

  // 保存发送的消息用于回写功能
  lastSentMessage.value = message

  // 如果有图片，先上传图片
  let uploadedImageUrls = []
  if (hasImages) {
    uni.showLoading({ title: '上传图片中...', mask: true })
    try {
      const uploadPromises = selectedImages.value.map(imgPath => uploadImage(imgPath))
      uploadedImageUrls = await Promise.all(uploadPromises)
      console.log('图片上传成功:', uploadedImageUrls)
    } catch (error) {
      uni.hideLoading()
      uni.showToast({ title: '图片上传失败: ' + error.message, icon: 'none' })
      isSending.value = false
      return
    }
    uni.hideLoading()
  }

  const userMsgIndex = messages.value.length
  const userMsg = {
    role: 'user',
    content: message,
    displayContent: message,
    images: [...selectedImages.value],  // 显示本地图片预览
    time: getCurrentTime(),
    isNew: true
  }
  messages.value.push(userMsg)

  // 清空输入
  inputMessage.value = ''
  const imagesToSend = uploadedImageUrls  // 使用上传后的URL
  selectedImages.value = []
  showTips.value = false

  // 300ms后清除 isNew 状态（触发动画）
  setTimeout(() => {
    if (messages.value[userMsgIndex]) {
      messages.value[userMsgIndex].isNew = false
    }
    isSending.value = false
  }, 300)

  scrollToBottom()

  isLoading.value = true

  // 创建AI消息占位
  const aiMsgIndex = messages.value.length
  const aiMsg = {
    role: 'assistant',
    content: '',
    displayContent: '',
    time: getCurrentTime(),
    isTyping: true
  }
  messages.value.push(aiMsg)

  // 使用流式API
  // 注意：aiMsgIndex 是响应式数组的索引，messages.value[aiMsgIndex] 是响应式引用
  aiChatStream(
    message,
    // 过滤掉系统消息和当前正在生成的AI消息，保留完整的对话历史
    messages.value.filter((m, idx) => m.role !== 'system' && idx !== aiMsgIndex),
    // onChunk: 每收到一块文本
    (chunk) => {
      // 收到第一个chunk时关闭加载状态
      if (isLoading.value) {
        isLoading.value = false
      }
      // 直接修改响应式对象的属性 - Vue3 会自动追踪
      const msg = messages.value[aiMsgIndex]
      if (msg) {
        // 使用 Vue 的响应式更新
        msg.content = msg.content + chunk
        msg.displayContent = msg.content
        // 触发视图更新
        scrollToBottom()
      }
    },
    // onDone: 完成
    async (fullText) => {
      const msg = messages.value[aiMsgIndex]
      if (msg) {
        msg.content = fullText
        msg.displayContent = msg.content
        msg.isTyping = false
      }
      isLoading.value = false
      await saveToCloud()
    },
    // onError: 错误 - 也要保存已有内容
    (error) => {
      const msg = messages.value[aiMsgIndex]
      if (msg) {
        msg.isTyping = false
        // 如果AI已有部分回复，保留并标记为不完整
        if (msg.content) {
          msg.displayContent = msg.content + '\n\n[回复不完整，请重试]'
        } else {
          // 完全没有回复，移除空的AI消息
          messages.value.splice(aiMsgIndex, 1)
        }
      }
      isLoading.value = false
      // 即使出错也保存已有内容
      saveToCloud()
      uni.showToast({ title: error.message || '请求失败，请重试', icon: 'none' })
    },
    currentModel.value.modelId,
    imagesToSend  // 传递图片
  )
}

// 回写最后发送的消息到输入框
const rewriteLastMessage = () => {
  if (lastSentMessage.value && !inputMessage.value) {
    inputMessage.value = lastSentMessage.value
    uni.showToast({ title: '已回写上次消息', icon: 'none', duration: 1500 })
  }
}

const saveToCloud = async () => {
  if (messages.value.length === 0) return
  try {
    // 保存到本地存储
    saveToLocalStorage()

    const cleanMessages = messages.value.map(msg => ({
      role: msg.role || 'user',
      content: msg.content || '',
      time: msg.time || ''
    })).filter(msg => msg.content)

    const chatData = {
      messages: cleanMessages,
      modelId: currentModel.value.modelId,
      modelName: currentModel.value.name
    }

    let result
    if (currentChatId.value) {
      // 已有对话ID，更新
      result = await updateChatHistory(currentChatId.value, chatData)
    } else {
      // 新对话，创建
      result = await saveChatToCloud(chatData)
    }

    if (result.success && result.id) {
      currentChatId.value = result.id
      uni.setStorageSync('currentChatId', result.id)
    }
  } catch (error) {
    console.error('保存对话失败:', error)
  }
}

const scrollToBottom = () => {
  nextTick(() => {
    // 使用递增方式确保值变化触发滚动
    scrollTop.value = scrollTop.value === 0 ? 1 : 0
    nextTick(() => {
      scrollTop.value = 999999
    })
  })
}

const scrollToTop = () => { scrollTop.value = 0; showScrollTop.value = false }

// 滚动监听，显示/隐藏回到顶部按钮
const onScroll = (e) => {
  const scrollTopValue = e.detail.scrollTop
  // 滚动超过 500rpx 显示回到顶部按钮
  showScrollTop.value = scrollTopValue > 200
}

const getCurrentTime = () => {
  const now = new Date()
  return `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
}
</script>

<style lang="scss" scoped>
.container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(180deg, #f8faff 0%, #f0f5ff 100%);
  overflow: hidden;
  box-sizing: border-box;
}

.status-bar {
  height: var(--status-bar-height);
  width: 100%;
  flex-shrink: 0;
}

.custom-nav {
  height: 88rpx;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10rpx);
  padding: 0 30rpx;
  box-shadow: 0 2rpx 20rpx rgba(0, 0, 0, 0.05);

  .nav-left {
    width: 60rpx;
    .icon-text { font-size: 40rpx; color: #333; }
  }

  .nav-title {
    font-size: 32rpx;
    font-weight: 600;
    color: #333;
    display: flex;
    align-items: center;
    cursor: pointer;
    padding: 8rpx 16rpx;
    border-radius: 30rpx;
    transition: all 0.2s;

    &:active {
      background: rgba(41, 121, 255, 0.1);
    }

    .title-icon { margin-right: 8rpx; animation: icon-float 2s ease-in-out infinite; }

    .title-text {
      max-width: 200rpx;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .title-arrow {
      font-size: 20rpx;
      color: #999;
      margin-left: 8rpx;
    }
  }

  .nav-right {
    width: 80rpx;
    text-align: right;

    .new-chat-btn {
      font-size: 36rpx;
      padding: 8rpx;
      border-radius: 50%;
      transition: all 0.2s;

      &:active {
        background: rgba(41, 121, 255, 0.1);
        transform: scale(0.9);
      }
    }

    .clear-text { font-size: 28rpx; color: #999; }
  }
}

@keyframes icon-float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-3rpx); }
}

// 模型选择器
.model-selector {
  flex-shrink: 0;
  background: rgba(255, 255, 255, 0.95);
  padding: 16rpx 30rpx;
  border-bottom: 1rpx solid #f0f0f0;

  &.selector-visible { opacity: 1; }
  
  .selector-wrapper {
    display: flex;
    align-items: center;
    background: #f5f7fa;
    border-radius: 32rpx;
    padding: 12rpx 24rpx;
    
    .model-icon {
      width: 40rpx;
      height: 40rpx;
      margin-right: 12rpx;
    }
    
    .model-name {
      flex: 1;
      font-size: 28rpx;
      color: #333;
      font-weight: 500;
    }
    
    .selector-arrow {
      font-size: 20rpx;
      color: #999;
      margin-left: 8rpx;
    }
  }
}

// 当前模型信息
.current-model-info {
  padding: 16rpx 30rpx;
  text-align: center;
  
  .info-text {
    font-size: 24rpx;
    color: #999;
    background: rgba(255, 255, 255, 0.8);
    padding: 8rpx 20rpx;
    border-radius: 20rpx;
  }
}

.chat-container { flex: 1; min-height: 0; padding: 20rpx; }

.welcome-msg {
  display: flex;
  align-items: flex-start;
  margin-bottom: 30rpx;

  .welcome-avatar {
    width: 80rpx;
    height: 80rpx;
    border-radius: 50%;
    background: linear-gradient(135deg, #2979FF, #5C9DFF);
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 20rpx;
    flex-shrink: 0;

    image { width: 60rpx; height: 60rpx; }

    .avatar-ring {
      position: absolute;
      top: -8rpx;
      left: -8rpx;
      right: -8rpx;
      bottom: -8rpx;
      border: 2rpx solid rgba(41, 121, 255, 0.3);
      border-radius: 50%;
      animation: ring-pulse 2s ease-in-out infinite;
    }
  }

  .welcome-bubble {
    flex: 1;
    background: #fff;
    padding: 24rpx;
    border-radius: 20rpx;
    box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.06);

    .welcome-text { font-size: 28rpx; color: #333; line-height: 1.6; margin-bottom: 16rpx; }

    .welcome-tips {
      display: flex;
      flex-wrap: wrap;
      gap: 12rpx;

      .tip-item {
        padding: 8rpx 16rpx;
        background: #f0f5ff;
        border-radius: 20rpx;
        font-size: 24rpx;
        color: #2979FF;

        &:active { background: #2979FF; color: #fff; }
      }
    }
  }
}

@keyframes ring-pulse { 0%, 100% { transform: scale(1); opacity: 1; } 50% { transform: scale(1.1); opacity: 0.5; } }

.message-list { padding-bottom: 20rpx; }

.message-item {
  display: flex;
  margin-bottom: 30rpx;
  opacity: 1;
  transform: translateY(0);

  &.msg-appear { animation: msg-slide-up 0.4s ease-out forwards; }

  &.user-msg {
    flex-direction: row-reverse;
    .msg-avatar { margin-right: 0; margin-left: 20rpx; }
    .msg-content { align-items: flex-end; }
    .msg-bubble {
      background: linear-gradient(135deg, #2979FF, #5C9DFF);
      color: #fff;
      border-bottom-right-radius: 8rpx;
    }
  }

  &.ai-msg {
    .msg-bubble {
      background: #fff;
      color: #333;
      border-bottom-left-radius: 8rpx;
    }
  }

  .msg-avatar {
    width: 80rpx;
    height: 80rpx;
    border-radius: 50%;
    background: linear-gradient(135deg, #2979FF, #5C9DFF);
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 20rpx;
    flex-shrink: 0;

    &.avatar-pulse { animation: avatar-pulse 2s ease-in-out infinite; }

    image { width: 60rpx; height: 60rpx; }
    .user-icon { font-size: 32rpx; color: #fff; font-weight: 600; }
  }

  .msg-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    max-width: 70%;
  }

  .msg-bubble {
    padding: 24rpx;
    border-radius: 20rpx;
    font-size: 28rpx;
    line-height: 1.6;
    box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.06);
    word-break: break-all;

    // 消息中的图片
    .msg-images {
      display: flex;
      flex-wrap: wrap;
      gap: 12rpx;
      margin-bottom: 16rpx;

      .msg-image {
        width: 200rpx;
        height: 200rpx;
        border-radius: 12rpx;
        object-fit: cover;
        cursor: pointer;
        transition: transform 0.2s;

        &:active {
          transform: scale(0.95);
        }
      }
    }

    &.typing .typing-cursor {
      display: inline-block;
      width: 2rpx;
      height: 1em;
      background: currentColor;
      margin-left: 4rpx;
      animation: cursor-blink 0.8s infinite;
    }
  }

  .msg-time {
    font-size: 22rpx;
    color: #999;
    margin-top: 8rpx;
    opacity: 0;
    transition: opacity 0.3s 0.5s;
    &.time-fade { opacity: 1; }
  }
}

@keyframes msg-slide-up { from { opacity: 0; transform: translateY(20rpx); } to { opacity: 1; transform: translateY(0); } }
@keyframes avatar-pulse { 0%, 100% { box-shadow: 0 0 0 0 rgba(41, 121, 255, 0.4); } 50% { box-shadow: 0 0 0 10rpx rgba(41, 121, 255, 0); } }
@keyframes cursor-blink { 0%, 50% { opacity: 1; } 51%, 100% { opacity: 0; } }

.loading-msg {
  display: flex;
  align-items: center;
  margin-bottom: 30rpx;
  opacity: 0;

  &.loading-appear { animation: loading-fade-in 0.3s ease forwards; }

  .msg-avatar {
    width: 80rpx;
    height: 80rpx;
    border-radius: 50%;
    background: linear-gradient(135deg, #2979FF, #5C9DFF);
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 20rpx;
    position: relative;

    image { width: 60rpx; height: 60rpx; }

    .thinking-ring {
      position: absolute;
      top: -4rpx; left: -4rpx; right: -4rpx; bottom: -4rpx;
      border: 2rpx solid transparent;
      border-top-color: #2979FF;
      border-radius: 50%;
      animation: thinking-rotate 1s linear infinite;
    }
  }

  .loading-content {
    display: flex;
    align-items: center;
    gap: 16rpx;
    background: #fff;
    padding: 20rpx 24rpx;
    border-radius: 20rpx;
    box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.06);
  }

  .loading-dots {
    display: flex;
    .dot {
      width: 10rpx; height: 10rpx;
      border-radius: 50%;
      background: #2979FF;
      margin: 0 4rpx;
      animation: dot-bounce 1.4s infinite ease-in-out both;
      &:nth-child(1) { animation-delay: -0.32s; }
      &:nth-child(2) { animation-delay: -0.16s; }
    }
  }

  .loading-text { font-size: 24rpx; color: #999; }
}

@keyframes loading-fade-in { from { opacity: 0; } to { opacity: 1; } }
@keyframes thinking-rotate { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
@keyframes dot-bounce { 0%, 80%, 100% { transform: scale(0); } 40% { transform: scale(1); } }

.input-area {
  flex-shrink: 0;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.98) 0%, rgba(250, 250, 250, 0.98) 100%);
  backdrop-filter: blur(20rpx);
  padding: 24rpx 30rpx;
  padding-bottom: calc(24rpx + env(safe-area-inset-bottom));
  box-shadow: 0 -8rpx 40rpx rgba(0, 0, 0, 0.08);
  border-top: 1rpx solid rgba(0, 0, 0, 0.03);
}

// 图片预览区域
.image-preview-area {
  padding: 0 0 20rpx 0;

  .image-preview-list {
    display: flex;
    gap: 16rpx;

    .image-preview-item {
      position: relative;
      width: 140rpx;
      height: 140rpx;
      border-radius: 16rpx;
      overflow: hidden;
      box-shadow: 
        0 4rpx 16rpx rgba(0, 0, 0, 0.1),
        0 2rpx 8rpx rgba(0, 0, 0, 0.05);
      border: 2rpx solid rgba(255, 255, 255, 0.8);
      transition: all 0.25s ease;

      &:active {
        transform: scale(0.95);
      }

      .preview-img {
        width: 100%;
        height: 100%;
        object-fit: cover;
      }

      .remove-img-btn {
        position: absolute;
        top: 6rpx;
        right: 6rpx;
        width: 40rpx;
        height: 40rpx;
        background: linear-gradient(135deg, rgba(0, 0, 0, 0.6) 0%, rgba(0, 0, 0, 0.4) 100%);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        backdrop-filter: blur(4rpx);
        transition: all 0.2s ease;

        &:active {
          background: linear-gradient(135deg, rgba(255, 59, 48, 0.9) 0%, rgba(255, 59, 48, 0.7) 100%);
          transform: scale(0.9);
        }

        .remove-icon {
          font-size: 20rpx;
          color: #fff;
          font-weight: 600;
        }
      }
    }
  }
}

.input-wrapper {
  display: flex;
  align-items: flex-end;
  background: linear-gradient(145deg, #f8f9fa 0%, #f0f2f5 100%);
  border-radius: 44rpx;
  padding: 12rpx 12rpx 12rpx 16rpx;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 
    inset 0 2rpx 4rpx rgba(0, 0, 0, 0.02),
    0 2rpx 8rpx rgba(0, 0, 0, 0.04);

  &:focus-within { 
    background: linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%);
    box-shadow: 
      0 0 0 3rpx rgba(41, 121, 255, 0.15),
      0 4rpx 16rpx rgba(41, 121, 255, 0.1);
    transform: translateY(-2rpx);
  }

  .input-left {
      flex: 1;
      display: flex;
      align-items: flex-end;
      min-width: 0;
      position: relative;

      .image-btn {
        width: 64rpx;
        height: 64rpx;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 10rpx;
        border-radius: 50%;
        background: linear-gradient(135deg, #f0f5ff 0%, #e8f0ff 100%);
        transition: all 0.25s ease;
        box-shadow: 0 2rpx 8rpx rgba(41, 121, 255, 0.15);
        flex-shrink: 0;

        &:active {
          background: linear-gradient(135deg, #2979FF 0%, #5C9DFF 100%);
          transform: scale(0.92);
          box-shadow: 0 4rpx 16rpx rgba(41, 121, 255, 0.3);

          .btn-icon {
            filter: brightness(0) invert(1);
          }
        }

        .btn-icon {
          font-size: 30rpx;
          transition: all 0.25s ease;
        }
      }

      /* 回写按钮 */
      .rewrite-btn {
        position: absolute;
        right: 10rpx;
        bottom: 10rpx;
        width: 56rpx;
        height: 56rpx;
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #fff9e6 0%, #fff3cd 100%);
        border-radius: 50%;
        box-shadow: 0 2rpx 8rpx rgba(255, 193, 7, 0.2);
        transition: all 0.25s ease;
        animation: rewrite-btn-appear 0.3s ease;
        z-index: 10;

        &:active {
          transform: scale(0.9);
          background: linear-gradient(135deg, #ffc107 0%, #ffb300 100%);
          box-shadow: 0 4rpx 16rpx rgba(255, 193, 7, 0.4);
        }

        .rewrite-icon {
          font-size: 26rpx;
        }
      }

      @keyframes rewrite-btn-appear {
        from {
          opacity: 0;
          transform: scale(0.8);
        }
        to {
          opacity: 1;
          transform: scale(1);
        }
      }
    }

  .chat-input {
    flex: 1;
    min-height: 64rpx;
    max-height: 160rpx;
    font-size: 28rpx;
    color: #333;
    padding: 14rpx 10rpx;
    line-height: 1.5;
    background: transparent;
    width: 100%;

    &::placeholder {
      color: #aab2bd;
      font-size: 26rpx;
    }
  }

  .send-btn {
    width: 72rpx; 
    height: 72rpx;
    border-radius: 50%;
    background: linear-gradient(135deg, #e0e5ec 0%, #d1d9e6 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    margin-left: 10rpx;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 
      0 2rpx 8rpx rgba(0, 0, 0, 0.08),
      inset 0 1rpx 2rpx rgba(255, 255, 255, 0.8);
    flex-shrink: 0;

    &.active {
      background: linear-gradient(135deg, #2979FF 0%, #5C9DFF 100%);
      box-shadow: 
        0 4rpx 20rpx rgba(41, 121, 255, 0.4),
        0 2rpx 8rpx rgba(41, 121, 255, 0.2);
      
      &:active { 
        transform: scale(0.92);
        box-shadow: 0 2rpx 12rpx rgba(41, 121, 255, 0.3);
      }
    }

    &.sending { 
      background: linear-gradient(135deg, #2979FF 0%, #5C9DFF 100%);
      animation: send-pulse 1.5s ease-in-out infinite;
    }

    .icon-text { 
      font-size: 32rpx; 
      color: #fff;
      font-weight: 600;
      text-shadow: 0 1rpx 2rpx rgba(0, 0, 0, 0.1);
    }

    .send-spinner {
      width: 28rpx; 
      height: 28rpx;
      border: 3rpx solid rgba(255, 255, 255, 0.3);
      border-top-color: #fff;
      border-radius: 50%;
      animation: spinner-rotate 0.8s linear infinite;
    }
  }
}

@keyframes send-pulse {
  0%, 100% { 
    box-shadow: 0 4rpx 20rpx rgba(41, 121, 255, 0.4);
  }
  50% { 
    box-shadow: 0 4rpx 30rpx rgba(41, 121, 255, 0.6);
  }
}

@keyframes spinner-rotate { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }

.quick-tips {
  margin-top: 16rpx;
  opacity: 0;
  transition: all 0.3s ease;

  &.tips-visible { opacity: 1; }

  .tips-scroll { white-space: nowrap; }
  .tips-list { display: flex; gap: 16rpx; }

  .tip-item {
    display: inline-block;
    padding: 12rpx 24rpx;
    background: #f0f5ff;
    border-radius: 30rpx;
    font-size: 24rpx;
    color: #2979FF;
    border: 1rpx solid #e0ebff;
    opacity: 0;

    &.tip-fade { animation: tip-fade 0.3s ease-out forwards; }
    &:active { background: #2979FF; color: #fff; }
  }
}

@keyframes tip-fade { from { opacity: 0; } to { opacity: 1; } }

.scroll-top-btn {
  position: fixed;
  right: 30rpx;
  bottom: 280rpx;
  width: 80rpx; height: 80rpx;
  background: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.1);
  opacity: 0;
  transform: scale(0) translateY(20rpx);
  transition: all 0.3s ease;
  z-index: 100;

  &.btn-visible { opacity: 1; transform: scale(1) translateY(0); }
  &:active { transform: scale(0.9); }
  .btn-icon { font-size: 36rpx; color: #2979FF; }
}

.bottom-space { height: 40rpx; }

// 模型选择弹窗
.model-picker-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1000;
  display: flex;
  align-items: flex-end;
  animation: mask-fade-in 0.3s ease;
}

@keyframes mask-fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

.model-picker {
  width: 100%;
  max-height: 70vh;
  background: #fff;
  border-radius: 32rpx 32rpx 0 0;
  animation: picker-slide-up 0.3s ease;
  
  .picker-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 30rpx;
    border-bottom: 1rpx solid #f0f0f0;
    
    .picker-title {
      font-size: 32rpx;
      font-weight: 600;
      color: #333;
    }
    
    .picker-close {
      font-size: 36rpx;
      color: #999;
      padding: 10rpx;
    }
  }
  
  .picker-list {
    max-height: 60vh;
    padding: 20rpx 0;
    
    .picker-item {
      display: flex;
      align-items: center;
      padding: 24rpx 30rpx;
      margin: 0 20rpx;
      border-radius: 16rpx;
      transition: all 0.2s ease;
      
      &:active {
        background: #f5f7fa;
      }
      
      &.item-active {
        background: #f0f5ff;
      }
      
      .picker-item-icon {
        width: 48rpx;
        height: 48rpx;
        margin-right: 20rpx;
      }
      
      .picker-item-info {
        flex: 1;
        
        .picker-item-name {
          display: block;
          font-size: 30rpx;
          color: #333;
          font-weight: 500;
          margin-bottom: 6rpx;
        }
        
        .picker-item-desc {
          display: block;
          font-size: 24rpx;
          color: #999;
        }
      }
      
      .picker-item-check {
        font-size: 32rpx;
        color: #2979FF;
        font-weight: bold;
      }
    }
  }
}

@keyframes picker-slide-up {
  from { transform: translateY(100%); }
  to { transform: translateY(0); }
}

// 会话列表弹窗样式
.session-picker {
  .picker-item {
    &.new-session-item {
      background: linear-gradient(135deg, #f0f5ff, #e8f0ff);
      margin-bottom: 20rpx;

      &:active {
        background: linear-gradient(135deg, #e0ebff, #d8e4ff);
      }

      .new-icon {
        width: 48rpx;
        height: 48rpx;
        display: flex;
        align-items: center;
        justify-content: center;
        background: #2979FF;
        border-radius: 50%;
        font-size: 28rpx;
        margin-right: 20rpx;
      }
    }

    .current-icon, .history-icon {
      width: 48rpx;
      height: 48rpx;
      display: flex;
      align-items: center;
      justify-content: center;
      background: #f5f5f5;
      border-radius: 50%;
      font-size: 28rpx;
      margin-right: 20rpx;
    }

    .current-icon {
      background: #e8f5e9;
    }
  }
}
</style>
