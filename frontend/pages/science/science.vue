<template>
  <view class="container">
    <!-- 自定义导航栏 -->
    <view class="custom-nav">
      <view class="nav-left" @click="goBack">
        <text class="icon-text">←</text>
      </view>
      <view class="nav-title">知识科普</view>
      <view class="nav-right"></view>
    </view>

    <!-- 头部区域 -->
    <view class="header-section">
      <view class="header-bg">
        <view class="gradient-orb orb-1"></view>
        <view class="gradient-orb orb-2"></view>
      </view>
      <view class="header-content">
        <view class="header-icon">🔬</view>
        <view class="header-title">探索知识的奥秘</view>
        <view class="header-subtitle">让复杂的知识变得简单有趣</view>
      </view>
    </view>

    <!-- 热门话题 -->
    <view class="hot-topics-section">
      <view class="section-header">
        <text class="section-icon">🔥</text>
        <text class="section-title">热门科普话题</text>
      </view>
      <view class="topics-grid">
        <view
          class="topic-card"
          v-for="(topic, index) in hotTopics"
          :key="index"
          :class="{ 'card-active': selectedTopic === topic }"
          @click="selectTopic(topic)"
        >
          <view class="topic-icon">{{ topic.icon }}</view>
          <view class="topic-name">{{ topic.name }}</view>
        </view>
      </view>
    </view>

    <!-- 知识领域 -->
    <view class="category-section">
      <view class="section-header">
        <text class="section-icon">📚</text>
        <text class="section-title">选择知识领域</text>
      </view>
      <view class="category-list">
        <view
          class="category-item"
          v-for="(cat, index) in categories"
          :key="index"
          :class="{ active: selectedCategory === cat.value }"
          @click="selectedCategory = cat.value"
        >
          <view class="category-icon" :style="{ background: cat.color }">
            <text class="icon-text">{{ cat.icon }}</text>
          </view>
          <view class="category-name">{{ cat.name }}</view>
        </view>
      </view>
    </view>

    <!-- 难度选择 -->
    <view class="difficulty-section">
      <view class="section-header">
        <text class="section-icon">🎯</text>
        <text class="section-title">理解难度</text>
      </view>
      <view class="difficulty-options">
        <view
          class="difficulty-item"
          v-for="(item, index) in difficulties"
          :key="index"
          :class="{ active: selectedDifficulty === item.value }"
          @click="selectedDifficulty = item.value"
        >
          <view class="difficulty-icon">{{ item.icon }}</view>
          <view class="difficulty-name">{{ item.name }}</view>
          <view class="difficulty-desc">{{ item.desc }}</view>
        </view>
      </view>
    </view>

    <!-- 问题输入 -->
    <view class="input-section">
      <view class="section-header">
        <text class="section-icon">❓</text>
        <text class="section-title">我想了解</text>
      </view>
      <view class="input-wrapper">
        <textarea
          class="question-input"
          v-model="question"
          placeholder="输入你想了解的知识或概念，例如：黑洞是怎么形成的？"
          :maxlength="500"
        />
        <view class="char-count">{{ question.length }}/500</view>
      </view>
    </view>

    <!-- 生成按钮 -->
    <view class="btn-section">
      <view 
        class="generate-btn" 
        :class="{ loading: isGenerating, disabled: !canGenerate }"
        @click="generateScience"
      >
        <text class="btn-icon" v-if="!isGenerating">🚀</text>
        <view class="btn-spinner" v-else></view>
        <text class="btn-text">{{ isGenerating ? '科普生成中...' : '开始科普' }}</text>
      </view>
    </view>

    <!-- 生成结果 -->
    <view class="result-section" v-if="generatedContent">
      <view class="result-header">
        <view class="result-title">
          <text class="title-icon">💡</text>
          科普解读
        </view>
        <view class="result-actions">
          <view class="action-btn" @click="copyResult">
            <text class="action-icon">📋</text>
            <text>复制</text>
          </view>
          <view class="action-btn" @click="regenerate">
            <text class="action-icon">🔄</text>
            <text>重新生成</text>
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

const hotTopics = [
  { icon: '🌌', name: '宇宙奥秘' },
  { icon: '🧬', name: '生命科学' },
  { icon: '⚛️', name: '量子物理' },
  { icon: '🤖', name: '人工智能' },
  { icon: '🌍', name: '地球科学' },
  { icon: '🧠', name: '脑科学' }
]

const categories = [
  { name: '物理学', value: 'physics', icon: '⚛️', color: 'linear-gradient(135deg, #667eea, #764ba2)' },
  { name: '化学', value: 'chemistry', icon: '🧪', color: 'linear-gradient(135deg, #f093fb, #f5576c)' },
  { name: '生物学', value: 'biology', icon: '🧬', color: 'linear-gradient(135deg, #4facfe, #00f2fe)' },
  { name: '天文学', value: 'astronomy', icon: '🌌', color: 'linear-gradient(135deg, #43e97b, #38f9d7)' },
  { name: '地理学', value: 'geography', icon: '🌍', color: 'linear-gradient(135deg, #fa709a, #fee140)' },
  { name: '历史学', value: 'history', icon: '📜', color: 'linear-gradient(135deg, #a8edea, #fed6e3)' },
  { name: '心理学', value: 'psychology', icon: '🧠', color: 'linear-gradient(135deg, #ff9a9e, #fecfef)' },
  { name: '经济学', value: 'economics', icon: '📈', color: 'linear-gradient(135deg, #ffecd2, #fcb69f)' }
]

const difficulties = [
  { value: 'simple', name: '通俗易懂', icon: '🌱', desc: '像讲故事一样讲解' },
  { value: 'normal', name: '标准科普', icon: '📖', desc: '专业但易懂' },
  { value: 'detailed', name: '深入解析', icon: '🔍', desc: '详细专业解读' }
]

const selectedTopic = ref('')
const selectedCategory = ref('physics')
const selectedDifficulty = ref('normal')
const question = ref('')
const isGenerating = ref(false)
const generatedContent = ref('')

const canGenerate = computed(() => question.value.trim().length >= 5)

const goBack = () => { uni.navigateBack() }

const selectTopic = (topic) => {
  selectedTopic.value = topic
  question.value = topic.name + '是什么？'
}

const generateScience = async () => {
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
    uni.showToast({ title: '请至少输入5个字符', icon: 'none' })
    return
  }

  isGenerating.value = true
  generatedContent.value = ''

  const categoryName = categories.find(c => c.value === selectedCategory.value)?.name
  const difficultyName = difficulties.find(d => d.value === selectedDifficulty.value)?.name

  try {
    // 使用动态提示词生成
    const prompt = await generatePromptWithFallback('science', {
      category: categoryName,
      difficulty: difficultyName,
      question: question.value
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
  generateScience()
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

/* 头部区域 */
.header-section {
  position: relative;
  padding: 60rpx 30rpx;
  text-align: center;
  overflow: hidden;

  .header-bg {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;

    .gradient-orb {
      position: absolute;
      border-radius: 50%;
      filter: blur(60rpx);
      opacity: 0.4;
    }

    .orb-1 {
      width: 300rpx;
      height: 300rpx;
      background: linear-gradient(135deg, #667eea, #764ba2);
      top: -100rpx;
      right: -50rpx;
    }

    .orb-2 {
      width: 250rpx;
      height: 250rpx;
      background: linear-gradient(135deg, #f093fb, #f5576c);
      bottom: -50rpx;
      left: -50rpx;
    }
  }

  .header-content {
    position: relative;
    z-index: 1;

    .header-icon {
      font-size: 80rpx;
      margin-bottom: 20rpx;
      animation: pulse 2s ease-in-out infinite;
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
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

/* 热门话题 */
.hot-topics-section {
  padding: 0 30rpx;
  margin-bottom: 30rpx;

  .section-header {
    display: flex;
    align-items: center;
    margin-bottom: 20rpx;

    .section-icon {
      font-size: 32rpx;
      margin-right: 12rpx;
    }

    .section-title {
      font-size: 30rpx;
      font-weight: 600;
      color: #333;
    }
  }
}

.topics-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16rpx;

  .topic-card {
    background: #fff;
    border-radius: 20rpx;
    padding: 24rpx 16rpx;
    text-align: center;
    box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.06);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
    border: 2rpx solid transparent;

    /* 选中状态 - 增强效果 */
    &.card-active {
      background: linear-gradient(135deg, #667eea, #764ba2);
      transform: scale(1.08);
      box-shadow: 0 8rpx 30rpx rgba(102, 126, 234, 0.4);
      border-color: rgba(255, 255, 255, 0.3);
      animation: topic-selected 0.4s ease;

      .topic-icon, .topic-name {
        color: #fff;
      }

      /* 选中指示器 */
      &::after {
        content: '✓';
        position: absolute;
        top: 8rpx;
        right: 8rpx;
        width: 28rpx;
        height: 28rpx;
        background: #fff;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18rpx;
        color: #667eea;
        font-weight: bold;
        animation: check-appear 0.3s ease;
      }
    }

    &:active:not(.card-active) {
      transform: scale(0.95);
    }

    /* 悬停效果 */
    &:hover, &:active {
      box-shadow: 0 6rpx 24rpx rgba(0, 0, 0, 0.1);
    }

    .topic-icon {
      font-size: 48rpx;
      margin-bottom: 12rpx;
      transition: transform 0.3s ease;
    }

    &.card-active .topic-icon {
      transform: scale(1.1);
      animation: icon-bounce 0.5s ease;
    }

    .topic-name {
      font-size: 26rpx;
      color: #333;
      font-weight: 500;
      transition: color 0.3s ease;
    }
  }
}

@keyframes topic-selected {
  0% {
    transform: scale(1);
    box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.06);
  }
  50% {
    transform: scale(1.12);
  }
  100% {
    transform: scale(1.08);
    box-shadow: 0 8rpx 30rpx rgba(102, 126, 234, 0.4);
  }
}

@keyframes check-appear {
  0% {
    transform: scale(0);
    opacity: 0;
  }
  50% {
    transform: scale(1.2);
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

@keyframes icon-bounce {
  0%, 100% { transform: scale(1.1) translateY(0); }
  50% { transform: scale(1.1) translateY(-4rpx); }
}

/* 知识领域 */
.category-section {
  padding: 0 30rpx;
  margin-bottom: 30rpx;

  .section-header {
    display: flex;
    align-items: center;
    margin-bottom: 20rpx;

    .section-icon {
      font-size: 32rpx;
      margin-right: 12rpx;
    }

    .section-title {
      font-size: 30rpx;
      font-weight: 600;
      color: #333;
    }
  }
}

.category-list {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16rpx;

  .category-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 16rpx;
    background: #fff;
    border-radius: 20rpx;
    box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.06);
    transition: all 0.3s ease;

    &.active {
      background: linear-gradient(135deg, #667eea, #764ba2);

      .category-name {
        color: #fff;
      }
    }

    &:active:not(.active) {
      transform: scale(0.95);
    }

    .category-icon {
      width: 80rpx;
      height: 80rpx;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      margin-bottom: 12rpx;

      .icon-text {
        font-size: 40rpx;
      }
    }

    .category-name {
      font-size: 24rpx;
      color: #333;
      font-weight: 500;
    }
  }
}

/* 难度选择 */
.difficulty-section {
  padding: 0 30rpx;
  margin-bottom: 30rpx;

  .section-header {
    display: flex;
    align-items: center;
    margin-bottom: 20rpx;

    .section-icon {
      font-size: 32rpx;
      margin-right: 12rpx;
    }

    .section-title {
      font-size: 30rpx;
      font-weight: 600;
      color: #333;
    }
  }
}

.difficulty-options {
  display: flex;
  gap: 16rpx;

  .difficulty-item {
    flex: 1;
    background: #fff;
    border-radius: 20rpx;
    padding: 24rpx 16rpx;
    text-align: center;
    box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.06);
    transition: all 0.3s ease;

    &.active {
      background: linear-gradient(135deg, #667eea, #764ba2);

      .difficulty-icon, .difficulty-name, .difficulty-desc {
        color: #fff;
      }
    }

    &:active:not(.active) {
      transform: scale(0.95);
    }

    .difficulty-icon {
      font-size: 48rpx;
      margin-bottom: 12rpx;
    }

    .difficulty-name {
      font-size: 28rpx;
      color: #333;
      font-weight: 600;
      margin-bottom: 8rpx;
    }

    .difficulty-desc {
      font-size: 22rpx;
      color: #999;
    }
  }
}

/* 输入区域 */
.input-section {
  padding: 0 30rpx;
  margin-bottom: 30rpx;

  .section-header {
    display: flex;
    align-items: center;
    margin-bottom: 16rpx;

    .section-icon {
      font-size: 32rpx;
      margin-right: 12rpx;
    }

    .section-title {
      font-size: 30rpx;
      font-weight: 600;
      color: #333;
    }
  }
}

.input-wrapper {
  position: relative;
  background: #fff;
  border-radius: 20rpx;
  padding: 24rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.06);

  .question-input {
    width: 100%;
    min-height: 200rpx;
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
        font-size: 24rpx;
        color: #2979FF;

        &:active {
          background: #e0ebff;
        }

        .action-icon {
          margin-right: 6rpx;
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
