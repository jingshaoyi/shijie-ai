<template>
  <view class="container">
    <view class="custom-nav">
      <view class="nav-left" @click="goBack"><text class="icon-text">←</text></view>
      <view class="nav-title">产品描述</view>
      <view class="nav-right"></view>
    </view>

    <view class="header-section">
      <view class="header-icon">📦</view>
      <view class="header-title">产品描述生成</view>
      <view class="header-subtitle">专业文案，提升转化</view>
    </view>

    <!-- 产品类型 -->
    <view class="config-section">
      <view class="section-header">
        <text class="section-icon">🏷️</text>
        <text class="section-title">产品类型</text>
      </view>
      <view class="type-list">
        <view class="type-item" v-for="(item, index) in productTypes" :key="index"
          :class="{ active: selectedType === item.value }" @click="selectedType = item.value">
          <view class="type-icon">{{ item.icon }}</view>
          <view class="type-name">{{ item.name }}</view>
        </view>
      </view>
    </view>

    <!-- 描述风格 -->
    <view class="config-section">
      <view class="section-header">
        <text class="section-icon">✨</text>
        <text class="section-title">描述风格</text>
      </view>
      <view class="style-list">
        <view class="style-item" v-for="(item, index) in descStyles" :key="index"
          :class="{ active: selectedStyle === item.value }" @click="selectedStyle = item.value">
          <text class="style-name">{{ item.name }}</text>
        </view>
      </view>
    </view>

    <!-- 产品信息 -->
    <view class="input-section">
      <view class="section-header">
        <text class="section-icon">📝</text>
        <text class="section-title">产品信息</text>
      </view>
      <view class="textarea-wrapper">
        <textarea class="product-input" v-model="productInfo" placeholder="输入产品名称、功能特点、目标用户、核心卖点等..." :maxlength="500" />
        <view class="char-count">{{ productInfo.length }}/500</view>
      </view>
    </view>

    <!-- 生成按钮 -->
    <view class="btn-section">
      <view class="generate-btn" :class="{ loading: isGenerating, disabled: !canGenerate }" @click="generate">
        <text class="btn-icon" v-if="!isGenerating">✨</text>
        <view class="btn-spinner" v-else></view>
        <text class="btn-text">{{ isGenerating ? '生成中...' : '生成描述' }}</text>
      </view>
    </view>

    <!-- 结果 -->
    <view class="result-section" v-if="generatedContent">
      <view class="result-header">
        <view class="result-title"><text class="title-icon">📄</text> 产品描述</view>
        <view class="result-actions">
          <view class="action-btn" @click="copyResult"><text>📋</text><text>复制</text></view>
          <view class="action-btn" @click="generate"><text>🔄</text><text>重新生成</text></view>
        </view>
      </view>
      <view class="result-content">
        <text class="result-text">{{ generatedContent }}</text>
      </view>
    </view>

    <view class="safe-area-bottom"></view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { aiChat } from '@/api/cloud.js'
import { isLoggedIn } from '@/api/user.js'
import { generatePromptWithFallback } from '@/api/prompts.js'

const productTypes = [
  { name: '数码电子', value: 'digital', icon: '📱' }, { name: '服饰美妆', value: 'fashion', icon: '👗' },
  { name: '食品饮料', value: 'food', icon: '🍜' }, { name: '家居生活', value: 'home', icon: '🏠' },
  { name: '虚拟服务', value: 'service', icon: '☁️' }, { name: '其他', value: 'other', icon: '📌' }
]

const descStyles = [
  { name: '专业严谨', value: 'professional' }, { name: '生动活泼', value: 'lively' },
  { name: '简洁精炼', value: 'concise' }, { name: '情感共鸣', value: 'emotional' }
]

const selectedType = ref('digital')
const selectedStyle = ref('professional')
const productInfo = ref('')
const isGenerating = ref(false)
const generatedContent = ref('')

const canGenerate = computed(() => productInfo.value.trim().length >= 10)
const goBack = () => uni.navigateBack()

const generate = async () => {
  if (!isLoggedIn()) {
    uni.showModal({ title: '提示', content: '请先登录', showCancel: false, success: () => uni.reLaunch({ url: '/pages/login/login' }) })
    return
  }
  if (!canGenerate.value) { uni.showToast({ title: '请至少输入10个字符', icon: 'none' }); return }

  isGenerating.value = true
  generatedContent.value = ''

  const typeName = productTypes.find(t => t.value === selectedType.value)?.name
  const styleName = descStyles.find(s => s.value === selectedStyle.value)?.name

  try {
    const prompt = await generatePromptWithFallback('product_desc', {
      type: typeName, style: styleName, product_info: productInfo.value
    })
    const res = await aiChat(prompt, [], 'dashscope/qwen-plus')
    generatedContent.value = res
  } catch (error) {
    uni.showToast({ title: error.message || '生成失败', icon: 'none' })
  } finally { isGenerating.value = false }
}

const copyResult = () => {
  uni.setClipboardData({ data: generatedContent.value, success: () => uni.showToast({ title: '已复制', icon: 'success' }) })
}
</script>

<style lang="scss" scoped>
.container { min-height: 100vh; background: linear-gradient(180deg, #fff5f0 0%, #f5f5f5 100%); }
.custom-nav { height: 88rpx; display: flex; align-items: center; justify-content: space-between; background: rgba(255,255,255,0.95); backdrop-filter: blur(10rpx); padding: 0 30rpx; box-shadow: 0 2rpx 20rpx rgba(0,0,0,0.05); position: sticky; top: 0; z-index: 100;
  .nav-left { width: 60rpx; .icon-text { font-size: 40rpx; color: #333; } }
  .nav-title { font-size: 36rpx; font-weight: 600; color: #333; }
  .nav-right { width: 60rpx; }
}
.header-section { padding: 60rpx 30rpx; text-align: center;
  .header-icon { font-size: 80rpx; margin-bottom: 20rpx; animation: pulse 2s ease-in-out infinite; }
  .header-title { font-size: 40rpx; font-weight: 700; color: #333; margin-bottom: 12rpx; }
  .header-subtitle { font-size: 26rpx; color: #666; }
}
@keyframes pulse { 0%,100% { transform: scale(1); } 50% { transform: scale(1.1); } }

.config-section { padding: 0 30rpx; margin-bottom: 30rpx;
  .section-header { display: flex; align-items: center; margin-bottom: 20rpx;
    .section-icon { font-size: 32rpx; margin-right: 12rpx; }
    .section-title { font-size: 30rpx; font-weight: 600; color: #333; }
  }
}
.type-list { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16rpx;
  .type-item { background: #fff; border-radius: 20rpx; padding: 24rpx 16rpx; text-align: center; box-shadow: 0 4rpx 20rpx rgba(0,0,0,0.06); transition: all 0.3s;
    &.active { background: linear-gradient(135deg, #f093fb, #f5576c); transform: scale(1.05);
      .type-icon, .type-name { color: #fff; }
    }
    &:active:not(.active) { transform: scale(0.95); }
    .type-icon { font-size: 44rpx; margin-bottom: 8rpx; }
    .type-name { font-size: 26rpx; color: #333; font-weight: 500; }
  }
}
.style-list { display: flex; flex-wrap: wrap; gap: 16rpx;
  .style-item { padding: 14rpx 28rpx; background: #fff; border-radius: 30rpx; font-size: 26rpx; color: #666; box-shadow: 0 4rpx 20rpx rgba(0,0,0,0.06); transition: all 0.3s;
    &.active { background: linear-gradient(135deg, #f093fb, #f5576c); color: #fff; box-shadow: 0 4rpx 16rpx rgba(240,147,251,0.3); }
    &:active:not(.active) { transform: scale(0.95); }
    .style-name { color: inherit; }
  }
}
.input-section { padding: 0 30rpx; margin-bottom: 30rpx;
  .section-header { display: flex; align-items: center; margin-bottom: 16rpx;
    .section-icon { font-size: 32rpx; margin-right: 12rpx; }
    .section-title { font-size: 30rpx; font-weight: 600; color: #333; }
  }
}
.textarea-wrapper { position: relative; background: #fff; border-radius: 20rpx; padding: 24rpx; box-shadow: 0 4rpx 20rpx rgba(0,0,0,0.06);
  .product-input { width: 100%; min-height: 240rpx; font-size: 28rpx; color: #333; line-height: 1.6; }
  .char-count { text-align: right; font-size: 24rpx; color: #999; margin-top: 12rpx; }
}
.btn-section { padding: 0 30rpx 30rpx; }
.generate-btn { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); border-radius: 50rpx; height: 96rpx; display: flex; align-items: center; justify-content: center; box-shadow: 0 10rpx 30rpx rgba(240,147,251,0.3); transition: all 0.3s;
  &.disabled { opacity: 0.5; }
  &.loading { opacity: 0.8; }
  &:active:not(.disabled) { transform: scale(0.98); }
  .btn-icon { font-size: 36rpx; margin-right: 12rpx; }
  .btn-text { font-size: 32rpx; font-weight: 600; color: #fff; }
  .btn-spinner { width: 36rpx; height: 36rpx; border: 4rpx solid rgba(255,255,255,0.3); border-top-color: #fff; border-radius: 50%; margin-right: 12rpx; animation: spin 0.8s linear infinite; }
}
@keyframes spin { to { transform: rotate(360deg); } }

.result-section { padding: 0 30rpx; margin-bottom: 30rpx;
  .result-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16rpx;
    .result-title { font-size: 30rpx; font-weight: 600; color: #333; display: flex; align-items: center;
      .title-icon { font-size: 32rpx; margin-right: 12rpx; }
    }
    .result-actions { display: flex; gap: 16rpx;
      .action-btn { display: flex; align-items: center; padding: 8rpx 16rpx; background: #fff0f5; border-radius: 24rpx; font-size: 24rpx; color: #f093fb;
        &:active { background: #ffe0f0; }
        text { margin-right: 6rpx; }
        text:last-child { margin-right: 0; }
      }
    }
  }
  .result-content { background: #fff; border-radius: 20rpx; padding: 30rpx; box-shadow: 0 4rpx 20rpx rgba(0,0,0,0.06);
    .result-text { font-size: 28rpx; color: #333; line-height: 1.8; white-space: pre-wrap; word-break: break-all; }
  }
}
.safe-area-bottom { height: calc(40rpx + env(safe-area-inset-bottom)); }
</style>
