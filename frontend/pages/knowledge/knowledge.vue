<template>
  <view class="container">
    <!-- 动态背景 -->
    <view class="bg-decoration">
      <view class="gradient-orb orb-1"></view>
      <view class="gradient-orb orb-2"></view>
    </view>

    <!-- 自定义导航栏 -->
    <view class="custom-nav">
      <view class="nav-left" @click="goBack">
        <text class="icon-text">←</text>
      </view>
      <view class="nav-title">
        <text class="title-icon">📚</text>
        知识查询
      </view>
      <view class="nav-right"></view>
    </view>

    <!-- 搜索框 -->
    <view class="search-section">
      <view class="search-box" :class="{ 'search-focused': isSearchFocused }">
        <text class="search-icon">🔍</text>
        <input
          class="search-input"
          v-model="query"
          placeholder="输入你想了解的知识..."
          confirm-type="search"
          @focus="isSearchFocused = true"
          @blur="isSearchFocused = false"
          @confirm="handleSearch"
        />
        <view class="search-btn" @click="handleSearch" v-if="query.trim()">
          <text>搜索</text>
        </view>
        <view class="clear-btn" @click="clearSearch" v-if="query">
          <text class="clear-icon">✕</text>
        </view>
      </view>
    </view>

    <!-- 热门话题 -->
    <view class="hot-section" v-if="!result && !isSearching">
      <view class="section-header">
        <view class="section-title">
          <text class="title-icon">🔥</text>
          热门知识
        </view>
        <view class="section-line"></view>
      </view>
      <view class="hot-grid">
        <view 
          class="hot-item" 
          v-for="(item, index) in hotList" 
          :key="index" 
          @tap="quickSearch(item)"
          :class="{ 'item-pressed': pressedItem === index }"
          @touchstart="pressedItem = index"
          @touchend="pressedItem = -1"
        >
          <view class="hot-rank" :class="{'top-three': index < 3}">
            {{ index + 1 }}
          </view>
          <text class="hot-text">{{ item }}</text>
          <view class="hot-arrow">›</view>
        </view>
      </view>
    </view>

    <!-- 查询结果 -->
    <scroll-view 
      class="result-section" 
      scroll-y 
      v-if="result"
      :scroll-top="resultScrollTop"
    >
      <view class="result-card">
        <view class="result-header">
          <view class="result-title">
            <text class="title-icon">💡</text>
            查询结果
          </view>
          <view class="result-actions">
            <view class="action-btn" @click="copyResult" :class="{ 'btn-copied': copied }">
              <text class="btn-icon">📋</text>
              <text class="btn-text">{{ copied ? '已复制' : '复制' }}</text>
            </view>
            <view class="action-btn secondary" @click="newSearch">
              <text class="btn-icon">🔍</text>
              <text class="btn-text">新搜索</text>
            </view>
          </view>
        </view>
        <view class="result-content">
          <text class="result-text">{{ result }}</text>
        </view>
        <view class="result-footer">
          <text class="footer-text">内容由AI生成，仅供参考</text>
        </view>
      </view>
    </scroll-view>

    <!-- 加载中 -->
    <view class="loading-section" v-if="isSearching">
      <view class="loading-animation">
        <view class="loading-circle circle-1"></view>
        <view class="loading-circle circle-2"></view>
        <view class="loading-circle circle-3"></view>
      </view>
      <text class="loading-text">正在搜索知识库...</text>
      <text class="loading-subtext">AI正在为您整理答案</text>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { aiChat } from '@/api/cloud.js'
import { isLoggedIn } from '@/api/user.js'

const query = ref('')
const result = ref('')
const isSearching = ref(false)
const isSearchFocused = ref(false)
const pressedItem = ref(-1)
const copied = ref(false)
const resultScrollTop = ref(0)

const hotList = [
  '什么是人工智能',
  '量子计算原理',
  '区块链技术详解',
  '太阳系有几颗行星',
  '人类基因组计划',
  '相对论是什么',
  '深度学习和机器学习的区别',
  '元宇宙概念解释'
]

const goBack = () => { uni.navigateBack() }

const clearSearch = () => {
  query.value = ''
  result.value = ''
}

const newSearch = () => {
  query.value = ''
  result.value = ''
  resultScrollTop.value = 0
}

const quickSearch = (item) => {
  query.value = item
  handleSearch()
}

const handleSearch = async () => {
  if (!isLoggedIn()) {
    uni.showModal({
      title: '提示', 
      content: '请先登录后再使用', 
      showCancel: false,
      success: () => { uni.reLaunch({ url: '/pages/login/login' }) }
    })
    return
  }

  if (!query.value.trim()) {
    uni.showToast({ title: '请输入查询内容', icon: 'none' })
    return
  }

  isSearching.value = true
  result.value = ''

  try {
    const prompt = `请详细解答以下知识问题，要求内容准确、条理清晰、通俗易懂：\n\n${query.value.trim()}`
    const res = await aiChat(prompt)
    result.value = res
  } catch (error) {
    uni.showToast({ title: error.message || '查询失败', icon: 'none' })
  } finally {
    isSearching.value = false
  }
}

const copyResult = () => {
  uni.setClipboardData({
    data: result.value,
    success: () => { 
      copied.value = true
      uni.showToast({ title: '已复制', icon: 'success' })
      setTimeout(() => {
        copied.value = false
      }, 2000)
    }
  })
}
</script>

<style lang="scss" scoped>
.container {
  min-height: 100vh;
  background: linear-gradient(180deg, #f8faff 0%, #f5f5f5 100%);
  position: relative;
  overflow: hidden;
}

/* 动态背景 */
.bg-decoration {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  overflow: hidden;

  .gradient-orb {
    position: absolute;
    border-radius: 50%;
    filter: blur(100rpx);
    opacity: 0.3;
    animation: orb-float 10s ease-in-out infinite;
  }

  .orb-1 {
    width: 500rpx;
    height: 500rpx;
    background: linear-gradient(135deg, #2979FF, #5C9DFF);
    top: -200rpx;
    right: -200rpx;
    animation-delay: 0s;
  }

  .orb-2 {
    width: 400rpx;
    height: 400rpx;
    background: linear-gradient(135deg, #9C27B0, #CE93D8);
    bottom: 100rpx;
    left: -150rpx;
    animation-delay: 5s;
  }
}

@keyframes orb-float {
  0%, 100% { transform: translate(0, 0) scale(1); }
  50% { transform: translate(40rpx, -40rpx) scale(1.1); }
}

/* 导航栏 */
.custom-nav {
  height: 88rpx;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10rpx);
  padding: 0 30rpx;
  box-shadow: 0 2rpx 20rpx rgba(0, 0, 0, 0.05);
  position: relative;
  z-index: 10;

  .nav-left {
    width: 60rpx;
    .icon-text { font-size: 40rpx; color: #333; }
  }

  .nav-title {
    font-size: 36rpx;
    font-weight: 600;
    color: #333;
    display: flex;
    align-items: center;

    .title-icon {
      margin-right: 12rpx;
      font-size: 36rpx;
    }
  }

  .nav-right { width: 60rpx; }
}

/* 搜索框 */
.search-section { 
  padding: 30rpx; 
}

.search-box {
  display: flex;
  align-items: center;
  background: linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%);
  border-radius: 50rpx;
  padding: 8rpx 8rpx 8rpx 24rpx;
  box-shadow: 
    0 4rpx 20rpx rgba(0, 0, 0, 0.06),
    inset 0 2rpx 4rpx rgba(255, 255, 255, 0.8);
  transition: all 0.3s ease;
  border: 2rpx solid transparent;

  &.search-focused {
    border-color: rgba(41, 121, 255, 0.3);
    box-shadow: 
      0 4rpx 20rpx rgba(41, 121, 255, 0.15),
      inset 0 2rpx 4rpx rgba(255, 255, 255, 0.8);
  }

  .search-icon { 
    font-size: 32rpx; 
    color: #999; 
    margin-right: 16rpx; 
  }

  .search-input { 
    flex: 1; 
    font-size: 28rpx; 
    color: #333; 
    height: 72rpx; 
  }

  .search-btn {
    background: linear-gradient(135deg, #2979FF, #5C9DFF);
    color: #fff;
    font-size: 26rpx;
    padding: 16rpx 32rpx;
    border-radius: 40rpx;
    font-weight: 600;
    box-shadow: 0 4rpx 16rpx rgba(41, 121, 255, 0.3);
    transition: all 0.2s ease;

    &:active {
      transform: scale(0.95);
      box-shadow: 0 2rpx 8rpx rgba(41, 121, 255, 0.2);
    }
  }

  .clear-btn {
    width: 48rpx;
    height: 48rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-left: 12rpx;

    .clear-icon {
      font-size: 24rpx;
      color: #999;
    }
  }
}

/* 热门知识区域 */
.hot-section { 
  padding: 0 30rpx; 
}

.section-header {
  display: flex;
  align-items: center;
  margin-bottom: 24rpx;

  .section-title {
    font-size: 32rpx;
    font-weight: 600;
    color: #333;
    margin-right: 16rpx;
    display: flex;
    align-items: center;

    .title-icon {
      font-size: 36rpx;
      margin-right: 8rpx;
    }
  }

  .section-line {
    flex: 1;
    height: 2rpx;
    background: linear-gradient(90deg, #ddd, transparent);
  }
}

.hot-grid {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.hot-item {
  display: flex;
  align-items: center;
  background: linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%);
  border-radius: 16rpx;
  padding: 24rpx;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.06);
  transition: all 0.2s ease;
  position: relative;
  overflow: hidden;

  &.item-pressed {
    background: #f0f5ff;
    transform: scale(0.98);
  }

  .hot-rank {
    width: 48rpx;
    height: 48rpx;
    border-radius: 12rpx;
    background: #f5f5f5;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 28rpx;
    font-weight: bold;
    color: #999;
    margin-right: 20rpx;

    &.top-three {
      background: linear-gradient(135deg, #2979FF, #5C9DFF);
      color: #fff;
      box-shadow: 0 4rpx 12rpx rgba(41, 121, 255, 0.3);
    }
  }

  .hot-text { 
    font-size: 28rpx; 
    color: #333; 
    flex: 1; 
  }

  .hot-arrow {
    font-size: 32rpx;
    color: #ccc;
  }
}

/* 结果区域 */
.result-section {
  flex: 1;
  padding: 0 30rpx;
  height: calc(100vh - 300rpx);
}

.result-card {
  background: linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%);
  border-radius: 24rpx;
  box-shadow: 0 8rpx 40rpx rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 30rpx;
  border-bottom: 1rpx solid #f0f0f0;
  background: linear-gradient(135deg, #f8faff 0%, #f0f5ff 100%);

  .result-title {
    font-size: 32rpx;
    font-weight: 600;
    color: #333;
    display: flex;
    align-items: center;

    .title-icon {
      margin-right: 12rpx;
      font-size: 32rpx;
    }
  }

  .result-actions {
    display: flex;
    gap: 16rpx;

    .action-btn {
      display: flex;
      align-items: center;
      gap: 8rpx;
      padding: 12rpx 24rpx;
      background: linear-gradient(135deg, #2979FF, #5C9DFF);
      border-radius: 30rpx;
      transition: all 0.2s ease;
      box-shadow: 0 4rpx 12rpx rgba(41, 121, 255, 0.3);

      &:active {
        transform: scale(0.95);
      }

      &.btn-copied {
        background: linear-gradient(135deg, #19BE6B, #4CD964);
        box-shadow: 0 4rpx 12rpx rgba(25, 190, 107, 0.3);
      }

      &.secondary {
        background: #f5f5f5;
        box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.06);

        .btn-icon, .btn-text {
          color: #666;
        }
      }

      .btn-icon {
        font-size: 24rpx;
      }

      .btn-text {
        font-size: 24rpx;
        color: #fff;
        font-weight: 500;
      }
    }
  }
}

.result-content {
  padding: 30rpx;
  min-height: 300rpx;

  .result-text { 
    font-size: 28rpx; 
    color: #333; 
    line-height: 1.8; 
    white-space: pre-wrap; 
    word-break: break-all; 
  }
}

.result-footer {
  padding: 20rpx 30rpx;
  background: #f8f9fa;
  text-align: center;

  .footer-text {
    font-size: 24rpx;
    color: #999;
  }
}

/* 加载中 */
.loading-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 100rpx 60rpx;

  .loading-animation {
    display: flex;
    gap: 16rpx;
    margin-bottom: 40rpx;

    .loading-circle {
      width: 20rpx;
      height: 20rpx;
      border-radius: 50%;
      background: linear-gradient(135deg, #2979FF, #5C9DFF);
      animation: bounce 1.4s ease-in-out infinite both;

      &.circle-1 {
        animation-delay: -0.32s;
      }

      &.circle-2 {
        animation-delay: -0.16s;
      }
    }
  }

  .loading-text { 
    font-size: 32rpx; 
    color: #333;
    font-weight: 600;
    margin-bottom: 12rpx;
  }

  .loading-subtext {
    font-size: 26rpx;
    color: #999;
  }
}

@keyframes bounce {
  0%, 80%, 100% { 
    transform: scale(0.6);
    opacity: 0.5;
  }
  40% { 
    transform: scale(1);
    opacity: 1;
  }
}
</style>