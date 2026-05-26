<template>
  <view class="container">
    <!-- 自定义导航栏 -->
    <view class="custom-nav">
      <view class="nav-left" @click="goBack">
        <text class="icon-text">←</text>
      </view>
      <view class="nav-title">智能翻译</view>
    </view>

    <!-- 语言选择 -->
    <view class="lang-section">
      <view class="lang-box">
        <view class="lang-label">源语言</view>
        <picker :range="langList" range-key="label" @change="onSourceLangChange">
          <view class="lang-picker">{{ sourceLangLabel }}</view>
        </picker>
      </view>
      <view class="swap-btn" @click="swapLang">
        <text class="icon-text">⇅</text>
      </view>
      <view class="lang-box">
        <view class="lang-label">目标语言</view>
        <picker :range="langList" range-key="label" @change="onTargetLangChange">
          <view class="lang-picker">{{ targetLangLabel }}</view>
        </picker>
      </view>
    </view>

    <!-- 输入区域 -->
    <view class="input-section">
      <view class="section-header">
        <text class="section-title">输入文本</text>
        <text class="clear-text" @click="sourceText = ''" v-if="sourceText">清空</text>
      </view>
      <textarea
        class="translate-input"
        v-model="sourceText"
        placeholder="请输入要翻译的文本"
        :maxlength="2000"
      />
      <view class="char-count">{{ sourceText.length }}/2000</view>
    </view>

    <!-- 翻译按钮 -->
    <view class="btn-section">
      <view class="translate-btn" :class="{ loading: isTranslating }" @click="handleTranslate">
        <text class="btn-text">{{ isTranslating ? '翻译中...' : '开始翻译' }}</text>
      </view>
    </view>

    <!-- 翻译结果 -->
    <view class="result-section" v-if="translatedText">
      <view class="section-header">
        <text class="section-title">翻译结果</text>
        <text class="copy-text" @click="copyResult">复制</text>
      </view>
      <view class="result-content">
        <text class="result-text">{{ translatedText }}</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { translate } from '@/api/cloud.js'
import { isLoggedIn } from '@/api/user.js'

const langList = [
  { label: '自动检测', value: 'auto' },
  { label: '中文', value: 'zh' },
  { label: '英语', value: 'en' },
  { label: '日语', value: 'ja' },
  { label: '韩语', value: 'ko' },
  { label: '法语', value: 'fr' },
  { label: '德语', value: 'de' },
  { label: '西班牙语', value: 'es' },
  { label: '俄语', value: 'ru' },
  { label: '意大利语', value: 'it' },
  { label: '葡萄牙语', value: 'pt' },
  { label: '阿拉伯语', value: 'ar' },
  { label: '泰语', value: 'th' },
  { label: '越南语', value: 'vi' }
]

const sourceLang = ref('auto')
const targetLang = ref('en')
const sourceText = ref('')
const translatedText = ref('')
const isTranslating = ref(false)

const sourceLangLabel = computed(() => langList.find(l => l.value === sourceLang.value)?.label || '自动检测')
const targetLangLabel = computed(() => langList.find(l => l.value === targetLang.value)?.label || '英语')

const goBack = () => { uni.navigateBack() }

const onSourceLangChange = (e) => { sourceLang.value = langList[e.detail.value].value }
const onTargetLangChange = (e) => { targetLang.value = langList[e.detail.value].value }

const swapLang = () => {
  if (sourceLang.value === 'auto') return
  const temp = sourceLang.value
  sourceLang.value = targetLang.value
  targetLang.value = temp
  // 同时交换文本
  const tempText = sourceText.value
  sourceText.value = translatedText.value
  translatedText.value = tempText
}

const handleTranslate = async () => {
  if (!isLoggedIn()) {
    uni.showModal({
      title: '提示', content: '请先登录后再使用', showCancel: false,
      success: () => { uni.reLaunch({ url: '/pages/login/login' }) }
    })
    return
  }

  if (!sourceText.value.trim()) {
    uni.showToast({ title: '请输入要翻译的文本', icon: 'none' })
    return
  }

  isTranslating.value = true
  translatedText.value = ''

  try {
    const res = await translate(sourceText.value.trim(), sourceLang.value, targetLang.value)
    translatedText.value = res || ''
  } catch (error) {
    uni.showToast({ title: error.message || '翻译失败', icon: 'none' })
  } finally {
    isTranslating.value = false
  }
}

const copyResult = () => {
  uni.setClipboardData({
    data: translatedText.value,
    success: () => { uni.showToast({ title: '已复制', icon: 'success' }) }
  })
}
</script>

<style lang="scss" scoped>
.container {
  min-height: 100vh;
  background: #f5f5f5;
  padding-bottom: 40rpx;
}

.custom-nav {
  height: 88rpx;
  display: flex;
  align-items: center;
  background: #fff;
  padding: 0 30rpx;
  box-shadow: 0 2rpx 10rpx rgba(0,0,0,0.05);
  .nav-left { width: 60rpx; .icon-text { font-size: 40rpx; color: #333; } }
  .nav-title { flex: 1; text-align: center; font-size: 36rpx; font-weight: 600; color: #333; }
}

.lang-section {
  display: flex;
  align-items: center;
  padding: 30rpx;
  gap: 16rpx;

  .lang-box {
    flex: 1;
    background: #fff;
    border-radius: 16rpx;
    padding: 20rpx;
    box-shadow: 0 2rpx 10rpx rgba(0,0,0,0.04);

    .lang-label { font-size: 22rpx; color: #999; margin-bottom: 8rpx; }
    .lang-picker { font-size: 30rpx; font-weight: 600; color: #333; }
  }

  .swap-btn {
    width: 64rpx;
    height: 64rpx;
    border-radius: 50%;
    background: #2979FF;
    display: flex;
    align-items: center;
    justify-content: center;
    .icon-text { font-size: 32rpx; color: #fff; }
  }
}

.input-section, .result-section {
  padding: 0 30rpx;
  margin-top: 24rpx;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16rpx;
  .section-title { font-size: 28rpx; font-weight: 600; color: #333; }
  .clear-text { font-size: 26rpx; color: #FA3534; }
  .copy-text { font-size: 26rpx; color: #2979FF; }
}

.translate-input {
  width: 100%;
  min-height: 240rpx;
  background: #fff;
  border-radius: 16rpx;
  padding: 24rpx;
  font-size: 28rpx;
  color: #333;
  box-sizing: border-box;
  line-height: 1.6;
}

.char-count {
  text-align: right;
  font-size: 22rpx;
  color: #999;
  margin-top: 8rpx;
}

.btn-section { padding: 30rpx; }

.translate-btn {
  background: linear-gradient(135deg, #2979FF, #5C9DFF);
  border-radius: 50rpx;
  height: 88rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 10rpx 30rpx rgba(41,121,255,0.3);
  &.loading { opacity: 0.7; }
  .btn-text { font-size: 32rpx; font-weight: 600; color: #fff; }
}

.result-content {
  background: #fff;
  border-radius: 16rpx;
  padding: 24rpx;
  box-shadow: 0 2rpx 10rpx rgba(0,0,0,0.04);
  .result-text { font-size: 28rpx; color: #333; line-height: 1.8; white-space: pre-wrap; word-break: break-all; }
}
</style>
