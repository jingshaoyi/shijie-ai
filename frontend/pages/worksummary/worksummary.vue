<template>
  <view class="container">
    <!-- 自定义导航栏 -->
    <view class="custom-nav">
      <view class="nav-left" @click="goBack">
        <text class="icon-text">←</text>
      </view>
      <view class="nav-title">工作总结</view>
      <view class="nav-right"></view>
    </view>

    <!-- 头部装饰 -->
    <view class="header-decoration">
      <view class="gradient-bg"></view>
      <view class="floating-icon">📊</view>
      <view class="header-title">智能工作总结</view>
      <view class="header-subtitle">专业、高效、一键生成</view>
    </view>

    <!-- 配置区域 -->
    <view class="config-section">
      <!-- 岗位类型 -->
      <view class="config-item">
        <view class="config-label">
          <text class="label-icon">💼</text>
          岗位类型
        </view>
        <view class="options-list">
          <view
            class="option-tag"
            v-for="(item, index) in positionTypes"
            :key="index"
            :class="{ active: selectedPosition === item.value }"
            @click="selectedPosition = item.value"
          >
            {{ item.label }}
          </view>
        </view>
      </view>

      <!-- 总结周期 -->
      <view class="config-item">
        <view class="config-label">
          <text class="label-icon">📅</text>
          总结周期
        </view>
        <view class="options-list">
          <view
            class="option-tag"
            v-for="(item, index) in periodTypes"
            :key="index"
            :class="{ active: selectedPeriod === item.value }"
            @click="selectedPeriod = item.value"
          >
            {{ item.label }}
          </view>
        </view>
      </view>

      <!-- 写作风格 -->
      <view class="config-item">
        <view class="config-label">
          <text class="label-icon">✨</text>
          写作风格
        </view>
        <view class="options-list">
          <view
            class="option-tag"
            v-for="(item, index) in styleTypes"
            :key="index"
            :class="{ active: selectedStyle === item.value }"
            @click="selectedStyle = item.value"
          >
            {{ item.label }}
          </view>
        </view>
      </view>
    </view>

    <!-- 工作内容输入 -->
    <view class="input-section">
      <view class="section-header">
        <view class="section-title">
          <text class="title-icon">📝</text>
          工作内容
        </view>
        <text class="section-tip">描述您的工作内容和成果</text>
      </view>
      <view class="textarea-wrapper">
        <textarea
          class="content-textarea"
          v-model="workContent"
          placeholder="请简要描述您的工作内容、完成的项目、取得的成果、遇到的问题等，例如：完成了XX项目的开发和上线"
          :maxlength="1000"
        />
        <view class="char-count">{{ workContent.length }}/1000</view>
      </view>
    </view>

    <!-- 生成按钮 -->
    <view class="btn-section">
      <view 
        class="generate-btn" 
        :class="{ loading: isGenerating, disabled: !canGenerate }"
        @click="generateSummary"
      >
        <text class="btn-icon" v-if="!isGenerating">✨</text>
        <view class="btn-spinner" v-else></view>
        <text class="btn-text">{{ isGenerating ? '生成中...' : '生成工作总结' }}</text>
      </view>
    </view>

    <!-- 生成结果 -->
    <view class="result-section" v-if="generatedContent">
      <view class="result-header">
        <view class="result-title">
          <text class="title-icon">📄</text>
          生成结果
        </view>
        <view class="result-actions">
          <view class="action-btn" @click="copyResult">
            <text class="action-icon">📋</text>
            <text class="action-text">复制</text>
          </view>
          <view class="action-btn" @click="regenerate">
            <text class="action-icon">🔄</text>
            <text class="action-text">重新生成</text>
          </view>
        </view>
      </view>
      <view class="result-content">
        <text class="result-text">{{ generatedContent }}</text>
      </view>
    </view>

    <!-- 底部安全区域 -->
    <view class="safe-area-bottom"></view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { aiChat } from '@/api/cloud.js'
import { isLoggedIn } from '@/api/user.js'
import { generatePromptWithFallback } from '@/api/prompts.js'

const positionTypes = [
  { label: '技术开发', value: 'tech' },
  { label: '产品经理', value: 'product' },
  { label: '运营推广', value: 'operation' },
  { label: '市场销售', value: 'sales' },
  { label: '行政人事', value: 'hr' },
  { label: '财务会计', value: 'finance' },
  { label: '设计创意', value: 'design' },
  { label: '其他岗位', value: 'other' }
]

const periodTypes = [
  { label: '日报', value: 'daily' },
  { label: '周报', value: 'weekly' },
  { label: '月报', value: 'monthly' },
  { label: '季度报', value: 'quarterly' },
  { label: '年报', value: 'yearly' }
]

const styleTypes = [
  { label: '正式严谨', value: 'formal' },
  { label: '简洁明了', value: 'concise' },
  { label: '详细全面', value: 'detailed' },
  { label: '数据导向', value: 'data' }
]

const selectedPosition = ref('tech')
const selectedPeriod = ref('weekly')
const selectedStyle = ref('formal')
const workContent = ref('')
const isGenerating = ref(false)
const generatedContent = ref('')

const canGenerate = computed(() => workContent.value.trim().length >= 10)

const goBack = () => { uni.navigateBack() }

const generateSummary = async () => {
  if (!isLoggedIn()) {
    uni.showModal({
      title: '提示',
      content: '请先登录后再使用',
      showCancel: false,
      success: () => { uni.reLaunch({ url: '/pages/login/login' }) }
    })
    return
  }

  if (!canGenerate.value) {
    uni.showToast({ title: '请至少输入10个字符', icon: 'none' })
    return
  }

  isGenerating.value = true
  generatedContent.value = ''

  const positionLabel = positionTypes.find(p => p.value === selectedPosition.value)?.label
  const periodLabel = periodTypes.find(p => p.value === selectedPeriod.value)?.label
  const styleLabel = styleTypes.find(s => s.value === selectedStyle.value)?.label

  try {
    // 使用动态提示词生成
    const prompt = await generatePromptWithFallback('work_summary', {
      position: positionLabel,
      period: periodLabel,
      style: styleLabel,
      content: workContent.value
    })

    const res = await aiChat(prompt, [], 'dashscope/qwen-plus')
    generatedContent.value = res
  } catch (error) {
    uni.showToast({ title: error.message || '生成失败', icon: 'none' })
  } finally {
    isGenerating.value = false
  }
}

const copyResult = () => {
  uni.setClipboardData({
    data: generatedContent.value,
    success: () => { uni.showToast({ title: '已复制', icon: 'success' }) }
  })
}

const regenerate = () => {
  generateSummary()
}
</script>

<style lang="scss" scoped>
.container {
  min-height: 100vh;
  background: linear-gradient(180deg, #f8faff 0%, #f5f5f5 100%);
}

/* 导航栏 */
.custom-nav {
  height: 88rpx;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10rpx);
  padding: 0 30rpx;
  box-shadow: 0 2rpx 20rpx rgba(0, 0, 0, 0.05);
  position: sticky;
  top: 0;
  z-index: 100;

  .nav-left {
    width: 60rpx;
    .icon-text { font-size: 40rpx; color: #333; }
  }

  .nav-title {
    font-size: 36rpx;
    font-weight: 600;
    color: #333;
  }

  .nav-right { width: 60rpx; }
}

/* 头部装饰 */
.header-decoration {
  position: relative;
  padding: 60rpx 30rpx;
  text-align: center;
  overflow: hidden;

  .gradient-bg {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    opacity: 0.1;
  }

  .floating-icon {
    font-size: 80rpx;
    margin-bottom: 20rpx;
    animation: float 3s ease-in-out infinite;
  }

  .header-title {
    font-size: 40rpx;
    font-weight: 700;
    color: #333;
    margin-bottom: 12rpx;
  }

  .header-subtitle {
    font-size: 26rpx;
    color: #666;
  }
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10rpx); }
}

/* 配置区域 */
.config-section {
  padding: 0 30rpx;
  margin-bottom: 30rpx;
}

.config-item {
  background: #fff;
  border-radius: 20rpx;
  padding: 24rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.06);

  .config-label {
    font-size: 28rpx;
    font-weight: 600;
    color: #333;
    margin-bottom: 16rpx;
    display: flex;
    align-items: center;

    .label-icon {
      font-size: 32rpx;
      margin-right: 12rpx;
    }
  }
}

.options-list {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;

  .option-tag {
    padding: 12rpx 24rpx;
    background: #f5f7fa;
    border-radius: 30rpx;
    font-size: 26rpx;
    color: #666;
    transition: all 0.3s ease;

    &.active {
      background: linear-gradient(135deg, #667eea, #764ba2);
      color: #fff;
      box-shadow: 0 4rpx 16rpx rgba(102, 126, 234, 0.3);
    }

    &:active:not(.active) {
      transform: scale(0.95);
    }
  }
}

/* 输入区域 */
.input-section {
  padding: 0 30rpx;
  margin-bottom: 30rpx;

  .section-header {
    margin-bottom: 16rpx;

    .section-title {
      font-size: 30rpx;
      font-weight: 600;
      color: #333;
      display: flex;
      align-items: center;
      margin-bottom: 8rpx;

      .title-icon {
        font-size: 32rpx;
        margin-right: 12rpx;
      }
    }

    .section-tip {
      font-size: 24rpx;
      color: #999;
      margin-left: 44rpx;
    }
  }
}

.textarea-wrapper {
  position: relative;
  background: #fff;
  border-radius: 20rpx;
  padding: 24rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.06);

  .content-textarea {
    width: 100%;
    min-height: 300rpx;
    font-size: 28rpx;
    color: #333;
    line-height: 1.6;
  }

  .char-count {
    text-align: right;
    font-size: 24rpx;
    color: #999;
    margin-top: 12rpx;
  }
}

/* 按钮区域 */
.btn-section {
  padding: 0 30rpx 30rpx;
}

.generate-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50rpx;
  height: 96rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 10rpx 30rpx rgba(102, 126, 234, 0.3);
  transition: all 0.3s ease;

  &.disabled {
    opacity: 0.5;
  }

  &.loading {
    opacity: 0.8;
  }

  &:active:not(.disabled) {
    transform: scale(0.98);
  }

  .btn-icon {
    font-size: 36rpx;
    margin-right: 12rpx;
  }

  .btn-text {
    font-size: 32rpx;
    font-weight: 600;
    color: #fff;
  }

  .btn-spinner {
    width: 36rpx;
    height: 36rpx;
    border: 4rpx solid rgba(255, 255, 255, 0.3);
    border-top-color: #fff;
    border-radius: 50%;
    margin-right: 12rpx;
    animation: spin 0.8s linear infinite;
  }
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 结果区域 */
.result-section {
  padding: 0 30rpx;
  margin-bottom: 30rpx;

  .result-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16rpx;

    .result-title {
      font-size: 30rpx;
      font-weight: 600;
      color: #333;
      display: flex;
      align-items: center;

      .title-icon {
        font-size: 32rpx;
        margin-right: 12rpx;
      }
    }

    .result-actions {
      display: flex;
      gap: 16rpx;

      .action-btn {
        display: flex;
        align-items: center;
        padding: 8rpx 16rpx;
        background: #f0f5ff;
        border-radius: 24rpx;

        &:active {
          background: #e0ebff;
        }

        .action-icon {
          font-size: 24rpx;
          margin-right: 6rpx;
        }

        .action-text {
          font-size: 24rpx;
          color: #2979FF;
        }
      }
    }
  }

  .result-content {
    background: #fff;
    border-radius: 20rpx;
    padding: 30rpx;
    box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.06);

    .result-text {
      font-size: 28rpx;
      color: #333;
      line-height: 1.8;
      white-space: pre-wrap;
      word-break: break-all;
    }
  }
}

.safe-area-bottom {
  height: calc(40rpx + env(safe-area-inset-bottom));
}
</style>
