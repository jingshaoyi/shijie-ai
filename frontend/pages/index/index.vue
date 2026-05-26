<template>
  <view class="container">
    <!-- 状态栏占位 -->
    <view class="status-bar"></view>
    
    <!-- 自定义导航栏 -->
    <view class="custom-nav">
      <view class="nav-title">识界AI</view>
    </view>

    <!-- 欢迎区域 -->
    <view class="welcome-section">
      <view class="welcome-title">
        <text class="title-text">探索认知边界</text>
        <view class="title-underline"></view>
      </view>
      <view class="welcome-subtitle">AI智能助手，让知识触手可及</view>
    </view>

    <!-- 功能卡片区域 -->
    <view class="features-grid">
      <view
        class="feature-card"
        v-for="(card, index) in featureCards"
        :key="index"
        :class="{ 'card-hover': hoveredCard === index }"
        @click="navigateTo(card.url)"
        @touchstart="hoveredCard = index"
        @touchend="hoveredCard = -1"
      >
        <view class="card-inner">
          <view class="card-front">
            <view class="feature-icon" :class="card.iconClass">
              <text class="icon-text">{{ card.icon }}</text>
              <view class="icon-glow"></view>
            </view>
            <view class="feature-title">{{ card.title }}</view>
            <view class="feature-desc">{{ card.desc }}</view>
          </view>
        </view>
        <view class="card-shine"></view>
      </view>
    </view>
    
    <!-- 快捷入口 -->
    <view class="quick-section">
      <view class="section-header">
        <view class="section-title">快捷功能</view>
        <view class="section-line"></view>
      </view>
      <view class="quick-list">
        <view
          class="quick-item"
          v-for="(item, index) in quickItems"
          :key="index"
          :class="{ 'item-active': activeQuick === index }"
          @click="navigateTo(item.path)"
          @touchstart="activeQuick = index"
          @touchend="activeQuick = -1"
        >
          <view class="quick-icon">{{ item.icon }}</view>
          <text class="quick-text">{{ item.text }}</text>
          <view class="quick-ripple" v-if="activeQuick === index"></view>
        </view>
      </view>
    </view>
    
    <!-- 热门推荐 -->
    <view class="hot-section">
      <view class="section-header">
        <view class="section-title">
          <text class="fire-icon">🔥</text>
          热门推荐
        </view>
        <view class="section-line"></view>
      </view>
      <view class="hot-list">
        <view
          class="hot-item"
          v-for="(item, index) in hotList"
          :key="index"
          @click="handleHotClick(item)"
          :class="{ 'item-pressed': pressedItem === index }"
          @touchstart="pressedItem = index"
          @touchend="pressedItem = -1"
        >
          <view class="hot-rank" :class="{'top-three': index < 3}">
            {{ index + 1 }}
          </view>
          <view class="hot-content">
            <view class="hot-title">{{ item.title }}</view>
            <view class="hot-desc">{{ item.desc }}</view>
          </view>
          <view class="hot-arrow">›</view>
        </view>
      </view>
    </view>
    
    <!-- 底部装饰 -->
    <view class="bottom-decoration">
      <view class="wave wave-1"></view>
      <view class="wave wave-2"></view>
    </view>

    <!-- 自定义TabBar -->
    <custom-tabbar :current="0" />
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import CustomTabbar from '@/components/custom-tabbar/custom-tabbar.vue'

const hoveredCard = ref(-1)
const activeQuick = ref(-1)
const pressedItem = ref(-1)

const featureCards = [
  { icon: '💬', title: 'AI对话', desc: '智能问答 多轮对话', url: '/pages/chat/chat', iconClass: 'chat-icon' },
  { icon: '✍️', title: '文本生成', desc: '文章创作 文案生成', url: '/pages/generate/generate', iconClass: 'generate-icon' },
  { icon: '🌐', title: '智能翻译', desc: '多语言互译 精准快速', url: '/pages/translate/translate', iconClass: 'translate-icon' },
  { icon: '📚', title: '知识查询', desc: '百科问答 知识检索', url: '/pages/knowledge/knowledge', iconClass: 'knowledge-icon' }
]

const quickItems = [
  { icon: '📝', text: '工作总结', path: '/pages/worksummary/worksummary' },
  { icon: '🌐', text: '中英翻译', path: '/pages/translate/translate' },
  { icon: '📚', text: '知识科普', path: '/pages/science/science' },
  { icon: '🎨', text: '诗歌创作', path: '/pages/poetry/poetry' }
]

const hotList = ref([
  { title: '小红书文案生成', desc: '生成爆款种草文案', path: '/pages/copywriting/copywriting' },
  { title: '代码解释助手', desc: '解读代码逻辑原理', path: '/pages/codeexplain/codeexplain' },
  { title: '邮件撰写', desc: '专业邮件模板生成', path: '/pages/email/email' },
  { title: '学习规划', desc: '制定高效学习计划', path: '/pages/studyplan/studyplan' },
  { title: '产品描述', desc: '电商产品详情文案', path: '/pages/productdesc/productdesc' }
])

const navigateTo = (url) => {
  // Tabbar页面使用switchTab跳转
  const tabbarPages = ['/pages/index/index', '/pages/chat/chat', '/pages/history/history', '/pages/user/user']
  if (tabbarPages.includes(url)) {
    uni.switchTab({ url })
  } else {
    uni.navigateTo({ url })
  }
}

const handleHotClick = (item) => {
  // 如果有专属页面，跳转到对应页面
  if (item.path) {
    navigateTo(item.path)
  } else if (item.prompt) {
    // 如果有prompt，发送到对话页面
    uni.$emit('quickChatPrompt', item.prompt)
    uni.switchTab({ url: '/pages/chat/chat' })
  }
}

onShow(() => {
  // 页面显示时的逻辑
})
</script>

<style lang="scss" scoped>
.container {
  min-height: 100vh;
  background: linear-gradient(180deg, #f0f5ff 0%, #f5f5f5 100%);
  padding-bottom: 150rpx;
  position: relative;
  overflow: hidden;
}

/* 状态栏占位 - 适配刘海屏 */
.status-bar {
  height: var(--status-bar-height);
  width: 100%;
}

/* 导航栏 */
.custom-nav {
  height: 88rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;

  .nav-title {
    font-size: 36rpx;
    font-weight: 600;
    color: #333;
  }
}

/* 欢迎区域 */
.welcome-section {
  padding: 40rpx 30rpx;
  text-align: center;

  .welcome-title {
    position: relative;
    display: inline-block;
    margin-bottom: 16rpx;
    
    .title-text {
      font-size: 48rpx;
      font-weight: bold;
      color: #2979FF;
      background: linear-gradient(135deg, #2979FF, #5C9DFF);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }
    
    .title-underline {
      position: absolute;
      bottom: -8rpx;
      left: 0;
      width: 0;
      height: 4rpx;
      background: linear-gradient(90deg, #2979FF, #5C9DFF);
      border-radius: 2rpx;
      transition: width 0.8s ease 0.3s;
    }
  }
  
  &.animate-in .title-underline {
    width: 100%;
  }
  
  .welcome-subtitle {
    font-size: 28rpx;
    color: #666;
  }
}

@keyframes fade-in-up {
  from {
    opacity: 0;
    }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 功能卡片区域 */
.features-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20rpx;
  padding: 0 30rpx;
  margin-bottom: 40rpx;
}

.feature-card {
  background: #fff;
  border-radius: 20rpx;
  padding: 30rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.06);
  position: relative;
  overflow: hidden;
  transition: all 0.4s ease-out;

  &.card-hover {
    transform: scale(1.02);
    box-shadow: 0 12rpx 40rpx rgba(41, 121, 255, 0.15);
  }
  
  &:active {
    }
  
  .card-shine {
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
    transition: left 0.5s;
  }
  
  &:hover .card-shine,
  &:active .card-shine {
    left: 100%;
  }
  
  .card-inner {
    position: relative;
    z-index: 1;
  }
  
  .feature-icon {
    width: 80rpx;
    height: 80rpx;
    border-radius: 20rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 20rpx;
    position: relative;
    overflow: hidden;
    
    &.chat-icon {
      background: linear-gradient(135deg, #2979FF, #5C9DFF);
      animation: icon-glow-blue 2s ease-in-out infinite;
    }
    
    &.generate-icon {
      background: linear-gradient(135deg, #19BE6B, #4CD964);
      animation: icon-glow-green 2s ease-in-out infinite;
    }
    
    &.translate-icon {
      background: linear-gradient(135deg, #FF6B6B, #FF8E8E);
      animation: icon-glow-red 2s ease-in-out infinite;
    }
    
    &.knowledge-icon {
      background: linear-gradient(135deg, #9C27B0, #CE93D8);
      animation: icon-glow-purple 2s ease-in-out infinite;
    }
    
    .icon-text {
      font-size: 40rpx;
      z-index: 1;
    }
    
    .icon-glow {
      position: absolute;
      top: 50%;
      left: 50%;
      width: 60rpx;
      height: 60rpx;
      background: rgba(255,255,255,0.3);
      border-radius: 50%;
      transform: translate(-50%, -50%);
      filter: blur(10rpx);
    }
  }
  
  .feature-title {
    font-size: 32rpx;
    font-weight: 600;
    color: #333;
    margin-bottom: 8rpx;
  }
  
  .feature-desc {
    font-size: 24rpx;
    color: #999;
  }
}

@keyframes icon-glow-blue {
  0%, 100% { box-shadow: 0 0 20rpx rgba(41, 121, 255, 0.3); }
  50% { box-shadow: 0 0 40rpx rgba(41, 121, 255, 0.6); }
}

@keyframes icon-glow-green {
  0%, 100% { box-shadow: 0 0 20rpx rgba(25, 190, 107, 0.3); }
  50% { box-shadow: 0 0 40rpx rgba(25, 190, 107, 0.6); }
}

@keyframes icon-glow-red {
  0%, 100% { box-shadow: 0 0 20rpx rgba(255, 107, 107, 0.3); }
  50% { box-shadow: 0 0 40rpx rgba(255, 107, 107, 0.6); }
}

@keyframes icon-glow-purple {
  0%, 100% { box-shadow: 0 0 20rpx rgba(156, 39, 176, 0.3); }
  50% { box-shadow: 0 0 40rpx rgba(156, 39, 176, 0.6); }
}

/* 快捷入口 */
.quick-section {
  padding: 0 30rpx;
  margin-bottom: 40rpx;
  
  .section-header {
    display: flex;
    align-items: center;
    margin-bottom: 20rpx;
    
    .section-title {
      font-size: 32rpx;
      font-weight: 600;
      color: #333;
      margin-right: 16rpx;
    }
    
    .section-line {
      flex: 1;
      height: 2rpx;
      background: linear-gradient(90deg, #ddd, transparent);
    }
  }
  
  .quick-list {
    display: flex;
    flex-wrap: wrap;
    gap: 16rpx;
  }
  
  .quick-item {
    display: flex;
    align-items: center;
    background: #fff;
    padding: 16rpx 24rpx;
    border-radius: 30rpx;
    box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.06);
    position: relative;
    overflow: hidden;
    transition: all 0.3s;
    
    &.item-active {
      transform: scale(0.95);
      background: #f0f5ff;
    }
    
    .quick-icon {
      font-size: 32rpx;
      margin-right: 12rpx;
    }
    
    .quick-text {
      font-size: 26rpx;
      color: #333;
    }
    
    .quick-ripple {
      position: absolute;
      top: 50%;
      left: 50%;
      width: 10rpx;
      height: 10rpx;
      background: rgba(41, 121, 255, 0.2);
      border-radius: 50%;
      transform: translate(-50%, -50%);
      animation: ripple-expand 0.5s ease-out;
    }
  }
}

/* 热门推荐 */
.hot-section {
  padding: 0 30rpx;
  
  .section-header {
    display: flex;
    align-items: center;
    margin-bottom: 20rpx;
    
    .section-title {
      font-size: 32rpx;
      font-weight: 600;
      color: #333;
      margin-right: 16rpx;
      display: flex;
      align-items: center;
      
      .fire-icon {
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
  
  .hot-list {
    background: #fff;
    border-radius: 20rpx;
    padding: 20rpx;
    box-shadow: 0 4rpx 20rpx rgba(0,0,0,0.06);
  }
  
  .hot-item {
    display: flex;
    align-items: center;
    padding: 24rpx 0;
    border-bottom: 1rpx solid #f5f5f5;
    position: relative;
    overflow: hidden;
    transition: all 0.2s;
    
    &:last-child {
      border-bottom: none;
    }
    
    &.item-pressed {
      background: #f8faff;
      margin: 0 -20rpx;
      padding-left: 20rpx;
      padding-right: 20rpx;
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
      }
    }
    
    .hot-content {
      flex: 1;
      
      .hot-title {
        font-size: 30rpx;
        font-weight: 600;
        color: #333;
        margin-bottom: 8rpx;
      }
      
      .hot-desc {
        font-size: 24rpx;
        color: #999;
      }
    }
    
    .hot-arrow {
      font-size: 36rpx;
      color: #ccc;
    }
  }
}

/* 底部装饰 */
.bottom-decoration {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 200rpx;
  pointer-events: none;
  z-index: -1;
  
  .wave {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 100rpx;
    background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1440 320'%3E%3Cpath fill='%232979FF' fill-opacity='0.05' d='M0,192L48,197.3C96,203,192,213,288,229.3C384,245,480,267,576,250.7C672,235,768,181,864,181.3C960,181,1056,235,1152,234.7C1248,235,1344,181,1392,154.7L1440,128L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z'%3E%3C/path%3E%3C/svg%3E") no-repeat bottom;
    background-size: cover;
    
    &.wave-2 {
      bottom: 20rpx;
      opacity: 0.5;
      animation: wave-move 8s ease-in-out infinite;
    }
  }
}

@keyframes wave-move {
  0%, 100% { transform: translateX(0); }
  50% { transform: translateX(-20rpx); }
}

@keyframes ripple-expand {
  to {
    width: 200rpx;
    height: 200rpx;
    opacity: 0;
  }
}
</style>