<template>
  <view class="container">
    <!-- 自定义导航栏 -->
    <view class="custom-nav">
      <view class="nav-left" @click="goBack">
        <text class="icon-text">←</text>
      </view>
      <view class="nav-title">诗歌创作</view>
      <view class="nav-right"></view>
    </view>

    <!-- 头部区域 -->
    <view class="header-section">
      <view class="header-bg">
        <view class="gradient-orb orb-1"></view>
        <view class="gradient-orb orb-2"></view>
        <view class="gradient-orb orb-3"></view>
      </view>
      <view class="header-content">
        <view class="header-icon">🎨</view>
        <view class="header-title">灵感 Poetry</view>
        <view class="header-subtitle">用文字描绘心中的画卷</view>
      </view>
    </view>

    <!-- 诗歌体裁 -->
    <view class="genre-section">
      <view class="section-header">
        <text class="section-icon">📜</text>
        <text class="section-title">选择体裁</text>
      </view>
      <view class="genre-list">
        <view
          class="genre-item"
          v-for="(item, index) in genres"
          :key="index"
          :class="{ active: selectedGenre === item.value }"
          @click="selectedGenre = item.value"
        >
          <view class="genre-icon">{{ item.icon }}</view>
          <view class="genre-name">{{ item.name }}</view>
          <view class="genre-desc">{{ item.desc }}</view>
        </view>
      </view>
    </view>

    <!-- 诗歌风格 -->
    <view class="style-section">
      <view class="section-header">
        <text class="section-icon">✨</text>
        <text class="section-title">诗歌风格</text>
      </view>
      <view class="style-options">
        <view
          class="style-tag"
          v-for="(item, index) in styles"
          :key="index"
          :class="{ active: selectedStyle === item.value }"
          @click="selectedStyle = item.value"
        >
          {{ item.name }}
        </view>
      </view>
    </view>

    <!-- 主题输入 -->
    <view class="theme-section">
      <view class="section-header">
        <text class="section-icon">💭</text>
        <text class="section-title">创作主题</text>
      </view>
      <view class="theme-input-wrapper">
        <input
          class="theme-input"
          v-model="theme"
          placeholder="输入你想表达的主题或情感..."
          maxlength="50"
        />
        <view class="char-count">{{ theme.length }}/50</view>
      </view>
      <!-- 快捷主题 -->
      <view class="quick-themes">
        <text class="quick-label">热门主题：</text>
        <view
          class="quick-tag"
          v-for="(item, index) in quickThemes"
          :key="index"
          @click="theme = item"
        >
          {{ item }}
        </view>
      </view>
    </view>

    <!-- 创作要求 -->
    <view class="requirement-section">
      <view class="section-header">
        <text class="section-icon">📝</text>
        <text class="section-title">创作要求（选填）</text>
      </view>
      <view class="requirement-input-wrapper">
        <textarea
          class="requirement-input"
          v-model="requirement"
          placeholder="描述你对诗歌的具体要求，如：想要表达的情感、特定的意象、字数限制等..."
          :maxlength="200"
        />
        <view class="char-count">{{ requirement.length }}/200</view>
      </view>
    </view>

    <!-- 生成按钮 -->
    <view class="btn-section">
      <view 
        class="generate-btn" 
        :class="{ loading: isGenerating, disabled: !canGenerate }"
        @click="generatePoetry"
      >
        <text class="btn-icon" v-if="!isGenerating">✨</text>
        <view class="btn-spinner" v-else></view>
        <text class="btn-text">{{ isGenerating ? '创作中...' : '开始创作' }}</text>
      </view>
    </view>

    <!-- 生成结果 -->
    <view class="result-section" v-if="generatedContent">
      <view class="result-header">
        <view class="result-title">
          <text class="title-icon">🌸</text>
          诗作
        </view>
        <view class="result-actions">
          <view class="action-btn" @click="copyResult">
            <text class="action-icon">📋</text>
            <text>复制</text>
          </view>
          <view class="action-btn" @click="regenerate">
            <text class="action-icon">🔄</text>
            <text>重新创作</text>
          </view>
        </view>
      </view>
      <view class="result-content">
        <view class="poetry-title" v-if="poetryTitle">《{{ poetryTitle }}》</view>
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

const genres = [
  { value: 'modern', name: '现代诗', icon: '🌊', desc: '自由奔放' },
  { value: 'classical', name: '古诗词', icon: '🏮', desc: '典雅含蓄' },
  { value: 'haiku', name: '俳句', icon: '🎋', desc: '简洁意境' },
  { value: 'sonnet', name: '十四行诗', icon: '🌹', desc: '浪漫抒情' }
]

const styles = [
  { value: 'romantic', name: '浪漫抒情' },
  { value: 'melancholy', name: '忧郁深沉' },
  { value: 'fresh', name: '清新自然' },
  { value: 'magnificent', name: '雄浑壮阔' },
  { value: 'elegant', name: '婉约含蓄' },
  { value: 'philosophical', name: '哲理思辨' }
]

const quickThemes = [
  '春天', '雨夜', '离别', '思念', '梦想', '故乡', '爱情', '时光'
]

const selectedGenre = ref('modern')
const selectedStyle = ref('romantic')
const theme = ref('')
const requirement = ref('')
const isGenerating = ref(false)
const generatedContent = ref('')
const poetryTitle = ref('')

const canGenerate = computed(() => theme.value.trim().length >= 2)

const goBack = () => { uni.navigateBack() }

const generatePoetry = async () => {
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
    uni.showToast({ title: '请至少输入2个字符', icon: 'none' })
    return
  }

  isGenerating.value = true
  generatedContent.value = ''
  poetryTitle.value = ''

  const genreName = genres.find(g => g.value === selectedGenre.value)?.name
  const styleName = styles.find(s => s.value === selectedStyle.value)?.name

  try {
    // 使用动态提示词生成
    const prompt = await generatePromptWithFallback('poetry', {
      genre: genreName,
      style: styleName,
      theme: theme.value,
      requirement: requirement.value ? '创作要求：' + requirement.value : ''
    })

    const res = await aiChat(prompt, [], 'dashscope/qwen-plus')
    // 尝试提取标题
    const lines = res.split('\n')
    const titleMatch = lines[0].match(/[《【](.+?)[》】]/)
    if (titleMatch) {
      poetryTitle.value = titleMatch[1]
      generatedContent.value = lines.slice(1).join('\n').trim()
    } else {
      generatedContent.value = res
    }
  } catch (error) {
    uni.showToast({ title: error.message || '创作失败', icon: 'none' })
  } finally {
    isGenerating.value = false
  }
}

const copyResult = () => {
  const fullText = poetryTitle.value 
    ? `《${poetryTitle.value}》\n${generatedContent.value}`
    : generatedContent.value
  uni.setClipboardData({
    data: fullText,
    success: () => { uni.showToast({ title: '已复制', icon: 'success' }) }
  })
}

const regenerate = () => {
  generatePoetry()
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
      background: linear-gradient(135deg, #fa709a, #fee140);
      top: -100rpx;
      left: -50rpx;
    }

    .orb-2 {
      width: 250rpx;
      height: 250rpx;
      background: linear-gradient(135deg, #667eea, #764ba2);
      top: -50rpx;
      right: -50rpx;
    }

    .orb-3 {
      width: 200rpx;
      height: 200rpx;
      background: linear-gradient(135deg, #4facfe, #00f2fe);
      bottom: -50rpx;
      left: 50%;
      transform: translateX(-50%);
    }
  }

  .header-content {
    position: relative;
    z-index: 1;

    .header-icon {
      font-size: 80rpx;
      margin-bottom: 20rpx;
      animation: float 3s ease-in-out infinite;
    }

    .header-title {
      font-size: 44rpx;
      font-weight: 700;
      background: linear-gradient(135deg, #667eea, #764ba2);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
      margin-bottom: 12rpx;
    }

    .header-subtitle {
      font-size: 26rpx;
      color: #666;
    }
  }
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10rpx); }
}

/* 诗歌体裁 */
.genre-section {
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

.genre-list {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16rpx;

  .genre-item {
    background: #fff;
    border-radius: 20rpx;
    padding: 24rpx 12rpx;
    text-align: center;
    box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.06);
    transition: all 0.3s ease;

    &.active {
      background: linear-gradient(135deg, #fa709a, #fee140);
      transform: scale(1.05);

      .genre-icon, .genre-name, .genre-desc {
        color: #fff;
      }
    }

    &:active:not(.active) {
      transform: scale(0.95);
    }

    .genre-icon {
      font-size: 48rpx;
      margin-bottom: 12rpx;
    }

    .genre-name {
      font-size: 28rpx;
      color: #333;
      font-weight: 600;
      margin-bottom: 8rpx;
    }

    .genre-desc {
      font-size: 22rpx;
      color: #999;
    }
  }
}

/* 诗歌风格 */
.style-section {
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

.style-options {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;

  .style-tag {
    padding: 16rpx 32rpx;
    background: #fff;
    border-radius: 30rpx;
    font-size: 28rpx;
    color: #666;
    box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.06);
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

/* 主题输入 */
.theme-section {
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

.theme-input-wrapper {
  position: relative;
  background: #fff;
  border-radius: 20rpx;
  padding: 24rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.06);
  margin-bottom: 16rpx;

  .theme-input {
    width: 100%;
    height: 60rpx;
    font-size: 28rpx;
    color: #333;
  }

  .char-count {
    position: absolute;
    right: 24rpx;
    top: 50%;
    transform: translateY(-50%);
    font-size: 24rpx;
    color: #999;
  }
}

.quick-themes {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 12rpx;

  .quick-label {
    font-size: 24rpx;
    color: #999;
  }

  .quick-tag {
    padding: 8rpx 20rpx;
    background: #f0f5ff;
    border-radius: 24rpx;
    font-size: 24rpx;
    color: #2979FF;
    transition: all 0.3s ease;

    &:active {
      background: #2979FF;
      color: #fff;
    }
  }
}

/* 创作要求 */
.requirement-section {
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

.requirement-input-wrapper {
  position: relative;
  background: #fff;
  border-radius: 20rpx;
  padding: 24rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.06);

  .requirement-input {
    width: 100%;
    min-height: 160rpx;
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
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
  border-radius: 50rpx;
  height: 96rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 10rpx 30rpx rgba(250, 112, 154, 0.3);
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
    background: linear-gradient(135deg, #fff5f7 0%, #fff 100%);
    border-radius: 20rpx;
    padding: 40rpx;
    box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.06);
    text-align: center;

    .poetry-title {
      font-size: 36rpx;
      font-weight: 600;
      color: #333;
      margin-bottom: 24rpx;
    }

    .result-text {
      font-size: 30rpx;
      color: #333;
      line-height: 2;
      white-space: pre-wrap;
      word-break: break-all;
      font-family: 'KaiTi', 'STKaiti', serif;
    }
  }
}

.safe-area-bottom {
  height: calc(40rpx + env(safe-area-inset-bottom));
}
</style>
