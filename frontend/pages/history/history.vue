<template>
  <view class="container">
    <view class="custom-nav">
      <view class="nav-title">历史记录</view>
      <view class="nav-right" @click="clearAll" v-if="historyList.length > 0">
        <text class="clear-text">清空</text>
      </view>
    </view>

    <!-- 加载状态 -->
    <view class="loading-state" v-if="isLoading">
      <view class="loading-spinner"></view>
      <text class="loading-text">加载中...</text>
    </view>

    <!-- 历史列表 -->
    <view class="history-list" v-else-if="historyList.length > 0">
      <view
        class="history-item"
        v-for="(item, index) in historyList"
        :key="index"
        @click="viewDetail(item)"
      >
        <view class="item-header">
          <text class="item-title">{{ item.title }}</text>
          <text class="item-delete" @click.stop="deleteItem(item.id)">删除</text>
        </view>
        <view class="item-preview">{{ item.preview }}</view>
        <view class="item-footer">
          <text class="item-time">{{ formatTime(item.created_at) }}</text>
        </view>
      </view>

      <!-- 加载更多 -->
      <view class="load-more" v-if="hasMore" @click="loadMore">
        <text>{{ isLoadingMore ? '加载中...' : '加载更多' }}</text>
      </view>
    </view>

    <!-- 空状态 -->
    <view class="empty-state" v-else>
      <view class="empty-icon">
        <text class="icon-text">📝</text>
      </view>
      <text class="empty-text">暂无历史记录</text>
      <text class="empty-hint">开始对话后会自动保存</text>
    </view>
    <!-- 自定义TabBar -->
    <custom-tabbar :current="2" />
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { getChatHistoryList, deleteChatHistory, clearAllChatHistory } from '@/api/database.js'
import { isLoggedIn } from '@/api/user.js'
import CustomTabbar from '@/components/custom-tabbar/custom-tabbar.vue'

const historyList = ref([])
const isLoading = ref(true)
const isLoadingMore = ref(false)
const hasMore = ref(false)
const currentPage = ref(1)

onShow(() => {
  if (!isLoggedIn()) {
    uni.showModal({
      title: '提示',
      content: '请先登录后查看历史记录',
      showCancel: false,
      success: () => {
        uni.reLaunch({ url: '/pages/login/login' })
      }
    })
    return
  }
  loadHistory()
})

const loadHistory = async () => {
  isLoading.value = true
  currentPage.value = 1

  const result = await getChatHistoryList(1, 20)

  isLoading.value = false

  if (result.success) {
    historyList.value = result.data
    hasMore.value = result.total > 20
  } else {
    uni.showToast({
      title: result.message || '加载失败',
      icon: 'none'
    })
  }
}

const loadMore = async () => {
  if (isLoadingMore.value || !hasMore.value) return

  isLoadingMore.value = true
  currentPage.value++

  const result = await getChatHistoryList(currentPage.value, 20)

  isLoadingMore.value = false

  if (result.success) {
    historyList.value = [...historyList.value, ...result.data]
    hasMore.value = result.total > currentPage.value * 20
  }
}

const viewDetail = (item) => {
  // chat是tabbar页面，需要先保存historyId到本地，再switchTab跳转
  uni.setStorageSync('pendingHistoryId', String(item.id))
  uni.switchTab({
    url: '/pages/chat/chat'
  })
}

const deleteItem = (id) => {
  uni.showModal({
    title: '确认删除',
    content: '确定要删除这条对话记录吗？',
    success: async (res) => {
      if (res.confirm) {
        const result = await deleteChatHistory(id)
        if (result.success) {
          uni.showToast({
            title: '已删除',
            icon: 'success'
          })
          // 从列表中移除
          historyList.value = historyList.value.filter(item => item.id !== id)
        } else {
          uni.showToast({
            title: result.message || '删除失败',
            icon: 'none'
          })
        }
      }
    }
  })
}

const clearAll = () => {
  uni.showModal({
    title: '确认清空',
    content: '确定要清空所有对话历史吗？此操作不可恢复！',
    success: async (res) => {
      if (res.confirm) {
        const result = await clearAllChatHistory()
        if (result.success) {
          uni.showToast({
            title: `已清空${result.count}条记录`,
            icon: 'success'
          })
          historyList.value = []
        } else {
          uni.showToast({
            title: result.message || '清空失败',
            icon: 'none'
          })
        }
      }
    }
  })
}

const formatTime = (timestamp) => {
  if (!timestamp) return ''

  let date
  if (typeof timestamp === 'string') {
    date = new Date(timestamp)
  } else if (typeof timestamp === 'number') {
    date = new Date(timestamp)
  } else {
    return ''
  }

  if (isNaN(date.getTime())) return ''

  const now = new Date()
  const diff = now - date

  // 小于1天显示相对时间
  if (diff < 24 * 60 * 60 * 1000) {
    const hours = Math.floor(diff / (60 * 60 * 1000))
    if (hours > 0) return `${hours}小时前`
    const minutes = Math.floor(diff / (60 * 1000))
    if (minutes > 0) return `${minutes}分钟前`
    return '刚刚'
  }

  // 超过1天显示日期
  const month = (date.getMonth() + 1).toString().padStart(2, '0')
  const day = date.getDate().toString().padStart(2, '0')
  return `${month}-${day}`
}
</script>

<style lang="scss" scoped>
.container {
  min-height: 100vh;
  background: linear-gradient(180deg, #f8faff 0%, #f5f5f5 100%);
}

.custom-nav {
  height: 88rpx;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10rpx);
  padding-top: var(--status-bar-height);
  padding: 0 30rpx;
  box-shadow: 0 2rpx 20rpx rgba(0, 0, 0, 0.05);
  position: sticky;
  top: 0;
  z-index: 100;

  .nav-title {
    font-size: 36rpx;
    font-weight: 600;
    color: #333;
  }

  .nav-right {
    padding: 8rpx 16rpx;
    border-radius: 24rpx;
    transition: all 0.2s ease;

    &:active {
      background: rgba(250, 53, 52, 0.1);
    }

    .clear-text {
      font-size: 28rpx;
      color: #FA3534;
      font-weight: 500;
    }
  }
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 200rpx;

  .loading-spinner {
    width: 60rpx;
    height: 60rpx;
    border: 4rpx solid #f0f0f0;
    border-top-color: #2979FF;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  .loading-text {
    margin-top: 20rpx;
    font-size: 28rpx;
    color: #999;
  }
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.history-list {
  padding: 20rpx;
}

.history-item {
  background: #fff;
  border-radius: 20rpx;
  padding: 28rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.06);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 2rpx solid transparent;
  position: relative;
  overflow: hidden;

  &:active {
    transform: scale(0.98);
    background: #f8faff;
    box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.04);
  }

  /* 左侧装饰条 */
  &::before {
    content: '';
    position: absolute;
    left: 0;
    top: 20rpx;
    bottom: 20rpx;
    width: 4rpx;
    background: linear-gradient(180deg, #2979FF, #5C9DFF);
    border-radius: 0 2rpx 2rpx 0;
    opacity: 0;
    transition: opacity 0.3s ease;
  }

  &:active::before {
    opacity: 1;
  }

  .item-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16rpx;

    .item-title {
      font-size: 30rpx;
      font-weight: 600;
      color: #333;
      flex: 1;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      padding-right: 20rpx;
    }

    .item-delete {
      font-size: 24rpx;
      color: #FA3534;
      padding: 8rpx 16rpx;
      border-radius: 20rpx;
      transition: all 0.2s ease;
      font-weight: 500;

      &:active {
        background: rgba(250, 53, 52, 0.1);
      }
    }
  }

  .item-preview {
    font-size: 26rpx;
    color: #666;
    line-height: 1.6;
    overflow: hidden;
    text-overflow: ellipsis;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    margin-bottom: 16rpx;
  }

  .item-footer {
    display: flex;
    align-items: center;

    .item-time {
      font-size: 24rpx;
      color: #999;
      display: flex;
      align-items: center;

      &::before {
        content: '🕐';
        margin-right: 8rpx;
        font-size: 22rpx;
      }
    }
  }
}

.load-more {
  text-align: center;
  padding: 30rpx;

  text {
    font-size: 28rpx;
    color: #2979FF;
  }
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 200rpx;

  .empty-icon {
    width: 160rpx;
    height: 160rpx;
    border-radius: 50%;
    background: #f0f5ff;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 30rpx;

    .icon-text {
      font-size: 80rpx;
      color: #2979FF;
    }
  }

  .empty-text {
    font-size: 32rpx;
    font-weight: 600;
    color: #333;
    margin-bottom: 16rpx;
  }

  .empty-hint {
    font-size: 26rpx;
    color: #999;
  }
}
</style>
