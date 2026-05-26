<template>
  <view class="login-container">
    <!-- 动态背景装饰 -->
    <view class="bg-decoration">
      <view class="circle circle-1"></view>
      <view class="circle circle-2"></view>
      <view class="circle circle-3"></view>
      <view class="particle" v-for="n in 20" :key="n" :style="particleStyle(n)"></view>
    </view>
    
    <!-- Logo区域 -->
    <view class="logo-section">
      <view class="logo-wrapper" :class="{ 'pulse': !isLoading }">
        <image class="logo" src="/static/logo.png" mode="aspectFit"></image>
        <view class="logo-glow"></view>
      </view>
      <view class="app-slogan">探索认知边界，智能触手可及</view>
    </view>

    <!-- 登录按钮 -->
    <view class="login-section">
      <view class="welcome-text">欢迎使用识界AI</view>
      <view class="desc-text">登录后即可体验完整的AI对话服务<br/>您的对话历史将安全保存在云端</view>
      
      <button
        class="login-btn"
        :class="{ loading: isLoading, 'btn-animate': !isLoading }"
        @click="handleLogin"
        :disabled="isLoading"
      >
        <view class="btn-shine"></view>
        <text class="btn-text">{{ isLoading ? '登录中...' : '微信一键登录' }}</text>
      </button>

      <view class="agreement">
        <view class="checkbox" :class="{ checked: agreed }" @click="toggleAgreement">
          <text v-if="agreed" class="icon-text">✓</text>
        </view>
        <view class="agreement-text">
          登录即表示同意
          <text class="link" @click="showPrivacy">《隐私政策》</text>
          和
          <text class="link" @click="showTerms">《用户协议》</text>
        </view>
      </view>
    </view>
    
    <!-- 功能介绍 -->
    <view class="features-section">
      <view
        class="feature-item"
        v-for="(item, index) in features"
        :key="index"
      >
        <view class="feature-icon">
          <text class="icon-text">{{ item.icon }}</text>
        </view>
        <view class="feature-title">{{ item.title }}</view>
        <view class="feature-desc">{{ item.desc }}</view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { weixinLogin, isLoggedIn } from '@/api/user.js'

const isLoading = ref(false)
const agreed = ref(false)

const features = [
  { icon: '🤖', title: 'AI智能对话', desc: '随时随地，与AI对话' },
  { icon: '☁️', title: '云端同步', desc: '对话历史自动保存' },
  { icon: '🔒', title: '隐私保护', desc: '您的数据安全加密' }
]

const particleStyle = (n) => {
  const size = Math.random() * 6 + 2
  const left = Math.random() * 100
  const delay = Math.random() * 5
  const duration = Math.random() * 3 + 4
  return {
    width: `${size}rpx`,
    height: `${size}rpx`,
    left: `${left}%`,
    animationDelay: `${delay}s`,
    animationDuration: `${duration}s`
  }
}

const toggleAgreement = () => {
  agreed.value = !agreed.value
}

const showPrivacy = () => {
  uni.navigateTo({ url: '/pages/agreement/privacy' })
}

const showTerms = () => {
  uni.navigateTo({ url: '/pages/agreement/terms' })
}

const handleLogin = async () => {
  if (!agreed.value) {
    uni.showToast({ title: '请先同意用户协议和隐私政策', icon: 'none' })
    return
  }

  isLoading.value = true

  try {
    const result = await weixinLogin({})
    if (result.success) {
      uni.showToast({ title: '登录成功', icon: 'success' })
      setTimeout(() => {
        uni.switchTab({ url: '/pages/index/index' })
      }, 1500)
    } else {
      uni.showToast({ title: result.message || '登录失败', icon: 'none' })
    }
  } catch (error) {
    console.error('登录错误:', error)
    uni.showToast({ title: '登录失败，请重试', icon: 'none' })
  } finally {
    isLoading.value = false
  }
}

onLoad(() => {
  if (isLoggedIn()) {
    uni.switchTab({ url: '/pages/index/index' })
  }
})
</script>

<style lang="scss" scoped>
.login-container {
  min-height: 100vh;
  background: linear-gradient(180deg, #f0f5ff 0%, #e8f0ff 100%);
  position: relative;
  overflow: hidden;
}

.bg-decoration {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 600rpx;
  pointer-events: none;

  .circle {
    position: absolute;
    border-radius: 50%;
    background: linear-gradient(135deg, rgba(41, 121, 255, 0.1), rgba(41, 121, 255, 0.05));
    animation: float 6s ease-in-out infinite;
  }

  .circle-1 { width: 300rpx; height: 300rpx; top: -100rpx; right: -50rpx; }
  .circle-2 { width: 200rpx; height: 200rpx; top: 50rpx; left: -80rpx; animation-delay: 2s; }
  .circle-3 { width: 150rpx; height: 150rpx; top: 150rpx; right: 100rpx; animation-delay: 4s; }

  .particle {
    position: absolute;
    background: rgba(41, 121, 255, 0.3);
    border-radius: 50%;
    bottom: 0;
    animation: particle-rise linear infinite;
  }
}

@keyframes float {
  0%, 100% { transform: translateY(0) rotate(0deg); }
  50% { transform: translateY(-20rpx) rotate(5deg); }
}

@keyframes particle-rise {
  0% { transform: translateY(0) scale(1); opacity: 0; }
  10% { opacity: 1; }
  90% { opacity: 0.5; }
  100% { transform: translateY(-600rpx) scale(0.5); opacity: 0; }
}

.logo-section {
  padding: 120rpx 0 60rpx;
  text-align: center;
  position: relative;
  z-index: 1;

  .logo-wrapper {
    width: 160rpx;
    height: 160rpx;
    margin: 0 auto 30rpx;
    background: linear-gradient(135deg, #2979FF, #5C9DFF);
    border-radius: 36rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 20rpx 40rpx rgba(41, 121, 255, 0.3);
    position: relative;
    overflow: hidden;

    &.pulse { animation: pulse 2s ease-in-out infinite; }

    .logo { width: 100rpx; height: 100rpx; }

    .logo-glow {
      position: absolute;
      top: -50%;
      left: -50%;
      width: 200%;
      height: 200%;
      background: radial-gradient(circle, rgba(255,255,255,0.3) 0%, transparent 60%);
      animation: glow-rotate 4s linear infinite;
    }
  }

  .app-slogan {
    font-size: 28rpx;
    color: #666;
  }
}

@keyframes pulse {
  0%, 100% { transform: scale(1); box-shadow: 0 20rpx 40rpx rgba(41, 121, 255, 0.3); }
  50% { transform: scale(1.02); box-shadow: 0 25rpx 50rpx rgba(41, 121, 255, 0.4); }
}

@keyframes glow-rotate {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.login-section {
  padding: 40rpx 60rpx;
  position: relative;
  z-index: 1;

  .welcome-text {
    font-size: 40rpx;
    font-weight: 600;
    color: #333;
    text-align: center;
    margin-bottom: 20rpx;
  }

  .desc-text {
    font-size: 26rpx;
    color: #666;
    text-align: center;
    line-height: 1.6;
    margin-bottom: 40rpx;
  }

  .login-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #07C160, #10B981);
    border: none;
    border-radius: 50rpx;
    height: 96rpx;
    margin-bottom: 30rpx;
    box-shadow: 0 10rpx 30rpx rgba(7, 193, 96, 0.3);
    position: relative;
    overflow: hidden;
    transition: all 0.3s ease;

    &.btn-animate { animation: btn-shine 3s ease-in-out infinite; }
    &:active { transform: scale(0.98); }
    &.loading { opacity: 0.8; animation: btn-pulse 1.5s ease-in-out infinite; }

    .btn-shine {
      position: absolute;
      top: 0;
      left: -100%;
      width: 100%;
      height: 100%;
      background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
      animation: shine 2s infinite;
    }

    .btn-text {
      font-size: 32rpx;
      font-weight: 600;
      color: #fff;
      position: relative;
      z-index: 1;
    }

    &::after { border: none; }
  }
}

@keyframes btn-shine {
  0%, 100% { box-shadow: 0 10rpx 30rpx rgba(7, 193, 96, 0.3); }
  50% { box-shadow: 0 15rpx 40rpx rgba(7, 193, 96, 0.5); }
}

@keyframes btn-pulse {
  0%, 100% { opacity: 0.8; }
  50% { opacity: 1; }
}

@keyframes shine {
  0% { left: -100%; }
  100% { left: 100%; }
}

.agreement {
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: 0 20rpx;

  .checkbox {
    width: 36rpx;
    height: 36rpx;
    border: 2rpx solid #ccc;
    border-radius: 8rpx;
    margin-right: 12rpx;
    margin-top: 4rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s ease;

    &.checked { background: #2979FF; border-color: #2979FF; }

    .icon-text { font-size: 24rpx; color: #fff; }
  }

  .agreement-text {
    font-size: 24rpx;
    color: #999;
    line-height: 1.5;
    flex: 1;

    .link { color: #2979FF; }
  }
}

.features-section {
  display: flex;
  justify-content: space-around;
  padding: 60rpx 30rpx;
  position: relative;
  z-index: 1;

  .feature-item {
    flex: 1;
    text-align: center;
    padding: 20rpx;

    &:active { transform: scale(0.95); }

    .feature-icon {
      width: 80rpx;
      height: 80rpx;
      margin: 0 auto 16rpx;
      background: linear-gradient(135deg, #2979FF, #5C9DFF);
      border-radius: 20rpx;
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 8rpx 20rpx rgba(41, 121, 255, 0.2);
      transition: all 0.3s ease;

      .icon-text { font-size: 36rpx; }
    }

    .feature-title { font-size: 28rpx; font-weight: 600; color: #333; margin-bottom: 8rpx; }
    .feature-desc { font-size: 22rpx; color: #999; }
  }
}


</style>
