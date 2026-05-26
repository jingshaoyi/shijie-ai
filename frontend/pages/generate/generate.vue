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
        <text class="title-icon">✨</text>
        文本生成
      </view>
      <view class="nav-right"></view>
    </view>

    <!-- 生成类型选择 -->
    <view class="type-section">
      <view class="section-label">
        <text class="label-icon">📝</text>
        生成类型
      </view>
      <scroll-view scroll-x class="type-scroll">
        <view class="type-list">
          <view
            class="type-item"
            v-for="(item, index) in typeList"
            :key="index"
            :class="{ active: selectedType === item.value }"
            @click="selectType(item.value)"
          >
            <text class="item-icon">{{ item.icon }}</text>
            <text class="item-label">{{ item.label }}</text>
            <view class="active-indicator" v-if="selectedType === item.value"></view>
          </view>
        </view>
      </scroll-view>
    </view>

    <!-- 主题/标题输入 - 所有类型都需要 -->
    <view class="form-section">
      <view class="form-label">
        <text class="label-icon">💡</text>
        {{ currentTypeConfig.topicLabel }}
      </view>
      <view class="input-wrapper" :class="{ 'input-focused': topicFocused }">
        <textarea
          class="form-textarea"
          v-model="formData.topic"
          :placeholder="currentTypeConfig.topicPlaceholder"
          :maxlength="200"
          @focus="topicFocused = true"
          @blur="topicFocused = false"
        />
        <view class="input-border"></view>
      </view>
    </view>

    <!-- 目标受众 - 文章、文案、邮件、报告需要 -->
    <view class="form-section" v-if="showAudience">
      <view class="form-label">
        <text class="label-icon">👥</text>
        目标受众
      </view>
      <view class="option-list">
        <view
          class="option-item"
          v-for="(item, index) in audienceOptions"
          :key="index"
          :class="{ active: formData.audience === item.value }"
          @click="formData.audience = item.value"
        >
          {{ item.label }}
        </view>
      </view>
    </view>

    <!-- 文章类型专属：文章结构 -->
    <view class="form-section" v-if="selectedType === 'article'">
      <view class="form-label">
        <text class="label-icon">🏗️</text>
        文章结构
      </view>
      <view class="option-list">
        <view
          class="option-item"
          v-for="(item, index) in structureOptions"
          :key="index"
          :class="{ active: formData.structure === item.value }"
          @click="formData.structure = item.value"
        >
          {{ item.label }}
        </view>
      </view>
    </view>

    <!-- 文案类型专属：平台选择 -->
    <view class="form-section" v-if="selectedType === 'copywriting'">
      <view class="form-label">
        <text class="label-icon">📱</text>
        发布平台
      </view>
      <view class="option-list">
        <view
          class="option-item"
          v-for="(item, index) in platformOptions"
          :key="index"
          :class="{ active: formData.platform === item.value }"
          @click="formData.platform = item.value"
        >
          {{ item.label }}
        </view>
      </view>
    </view>

    <!-- 摘要类型专属：原文内容 -->
    <view class="form-section" v-if="selectedType === 'summary'">
      <view class="form-label">
        <text class="label-icon">📄</text>
        原文内容
      </view>
      <view class="input-wrapper" :class="{ 'input-focused': contentFocused }">
        <textarea
          class="form-textarea"
          v-model="formData.content"
          placeholder="请粘贴需要摘要的原文内容..."
          :maxlength="5000"
          @focus="contentFocused = true"
          @blur="contentFocused = false"
        />
        <view class="input-border"></view>
      </view>
    </view>

    <!-- 创意类型专属：创意方向 -->
    <view class="form-section" v-if="selectedType === 'idea'">
      <view class="form-label">
        <text class="label-icon">🎯</text>
        创意方向
      </view>
      <view class="option-list">
        <view
          class="option-item"
          v-for="(item, index) in ideaDirectionOptions"
          :key="index"
          :class="{ active: formData.ideaDirection === item.value }"
          @click="formData.ideaDirection = item.value"
        >
          {{ item.label }}
        </view>
      </view>
    </view>

    <!-- 诗歌类型专属：诗歌形式 -->
    <view class="form-section" v-if="selectedType === 'poem'">
      <view class="form-label">
        <text class="label-icon">📜</text>
        诗歌形式
      </view>
      <view class="option-list">
        <view
          class="option-item"
          v-for="(item, index) in poemFormOptions"
          :key="index"
          :class="{ active: formData.poemForm === item.value }"
          @click="formData.poemForm = item.value"
        >
          {{ item.label }}
        </view>
      </view>
    </view>

    <!-- 故事类型专属：故事类型 -->
    <view class="form-section" v-if="selectedType === 'story'">
      <view class="form-label">
        <text class="label-icon">📚</text>
        故事类型
      </view>
      <view class="option-list">
        <view
          class="option-item"
          v-for="(item, index) in storyTypeOptions"
          :key="index"
          :class="{ active: formData.storyType === item.value }"
          @click="formData.storyType = item.value"
        >
          {{ item.label }}
        </view>
      </view>
    </view>

    <!-- 邮件类型专属：邮件场景 -->
    <view class="form-section" v-if="selectedType === 'email'">
      <view class="form-label">
        <text class="label-icon">📧</text>
        邮件场景
      </view>
      <view class="option-list">
        <view
          class="option-item"
          v-for="(item, index) in emailSceneOptions"
          :key="index"
          :class="{ active: formData.emailScene === item.value }"
          @click="formData.emailScene = item.value"
        >
          {{ item.label }}
        </view>
      </view>
    </view>

    <!-- 报告类型专属：报告类型 -->
    <view class="form-section" v-if="selectedType === 'report'">
      <view class="form-label">
        <text class="label-icon">📊</text>
        报告类型
      </view>
      <view class="option-list">
        <view
          class="option-item"
          v-for="(item, index) in reportTypeOptions"
          :key="index"
          :class="{ active: formData.reportType === item.value }"
          @click="formData.reportType = item.value"
        >
          {{ item.label }}
        </view>
      </view>
    </view>

    <!-- 关键词 - 所有类型都需要 -->
    <view class="form-section">
      <view class="form-label">
        <text class="label-icon">🔑</text>
        关键词（可选）
      </view>
      <view class="input-wrapper">
        <input
          class="form-input"
          v-model="formData.keywords"
          placeholder="多个关键词用逗号分隔"
          @focus="keywordsFocused = true"
          @blur="keywordsFocused = false"
        />
        <view class="input-border" :class="{ 'border-active': keywordsFocused }"></view>
      </view>
    </view>

    <!-- 字数要求 - 所有类型都需要 -->
    <view class="form-section">
      <view class="form-label">
        <text class="label-icon">📏</text>
        字数要求
      </view>
      <view class="option-list">
        <view
          class="option-item"
          v-for="(item, index) in lengthOptions"
          :key="index"
          :class="{ active: formData.length === item.value }"
          @click="formData.length = item.value"
        >
          {{ item.label }}
        </view>
      </view>
    </view>

    <!-- 语气风格 - 所有类型都需要 -->
    <view class="form-section">
      <view class="form-label">
        <text class="label-icon">🎭</text>
        语气风格
      </view>
      <view class="option-list">
        <view
          class="option-item"
          v-for="(item, index) in toneOptions"
          :key="index"
          :class="{ active: formData.tone === item.value }"
          @click="formData.tone = item.value"
        >
          {{ item.label }}
        </view>
      </view>
    </view>

    <!-- 生成按钮 -->
    <view class="btn-section">
      <view
        class="generate-btn"
        :class="{ loading: isGenerating, 'btn-pulse': !isGenerating && canGenerate }"
        @click="handleGenerate"
      >
        <view class="btn-glow"></view>
        <view class="btn-content">
          <view class="btn-spinner" v-if="isGenerating">
            <view class="spinner-ring"></view>
          </view>
          <text class="btn-text">{{ isGenerating ? 'AI生成中...' : '开始生成' }}</text>
        </view>
      </view>
    </view>

    <!-- 生成结果 -->
    <view class="result-section" v-if="result">
      <view class="result-header">
        <view class="result-title">
          <text class="title-icon">🎉</text>
          生成结果
        </view>
        <view class="result-actions">
          <view class="action-btn" @click="copyResult" :class="{ 'btn-copied': copied }">
            <text class="action-icon">📋</text>
            <text class="action-text">{{ copied ? '已复制' : '复制' }}</text>
          </view>
        </view>
      </view>
      <view class="result-content">
        <text class="result-text">{{ result }}</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import { textGenerate } from '@/api/cloud.js'
import { isLoggedIn } from '@/api/user.js'

const topicFocused = ref(false)
const contentFocused = ref(false)
const keywordsFocused = ref(false)
const copied = ref(false)

// 生成类型列表
const typeList = [
  { label: '文章', value: 'article', icon: '📄', desc: '专业文章创作' },
  { label: '文案', value: 'copywriting', icon: '✍️', desc: '营销文案生成' },
  { label: '摘要', value: 'summary', icon: '📋', desc: '内容摘要提炼' },
  { label: '创意', value: 'idea', icon: '💡', desc: '创意灵感生成' },
  { label: '诗歌', value: 'poem', icon: '📜', desc: '诗歌文学创作' },
  { label: '故事', value: 'story', icon: '📚', desc: '故事小说创作' },
  { label: '邮件', value: 'email', icon: '📧', desc: '专业邮件撰写' },
  { label: '报告', value: 'report', icon: '📊', desc: '工作报告生成' }
]

// 各类型配置
const typeConfig = {
  article: {
    topicLabel: '文章主题',
    topicPlaceholder: '请输入文章主题，例如：人工智能的未来发展'
  },
  copywriting: {
    topicLabel: '产品/服务名称',
    topicPlaceholder: '请输入产品或服务名称，例如：智能空气净化器'
  },
  summary: {
    topicLabel: '摘要主题',
    topicPlaceholder: '请输入摘要主题，例如：2024年科技行业年度报告摘要'
  },
  idea: {
    topicLabel: '创意主题',
    topicPlaceholder: '请输入需要创意的主题，例如：新品发布会创意方案'
  },
  poem: {
    topicLabel: '诗歌主题',
    topicPlaceholder: '请输入诗歌主题，例如：秋天的思念'
  },
  story: {
    topicLabel: '故事主题',
    topicPlaceholder: '请输入故事主题，例如：一个关于勇气的冒险故事'
  },
  email: {
    topicLabel: '邮件主题',
    topicPlaceholder: '请输入邮件主题，例如：项目延期说明'
  },
  report: {
    topicLabel: '报告主题',
    topicPlaceholder: '请输入报告主题，例如：Q3季度销售业绩分析'
  }
}

// 选项配置
const audienceOptions = [
  { label: '专业人士', value: 'professional' },
  { label: '普通大众', value: 'general' },
  { label: '学生群体', value: 'student' },
  { label: '企业客户', value: 'enterprise' }
]

const structureOptions = [
  { label: '总分总', value: 'total-sub-total' },
  { label: '并列式', value: 'parallel' },
  { label: '递进式', value: 'progressive' },
  { label: '对比式', value: 'contrast' }
]

const platformOptions = [
  { label: '小红书', value: 'xiaohongshu' },
  { label: '微信公众号', value: 'wechat' },
  { label: '抖音', value: 'douyin' },
  { label: '微博', value: 'weibo' },
  { label: '淘宝/京东', value: 'ecommerce' },
  { label: 'LinkedIn', value: 'linkedin' }
]

const ideaDirectionOptions = [
  { label: '创新突破', value: 'innovative' },
  { label: '实用可行', value: 'practical' },
  { label: '趣味娱乐', value: 'entertaining' },
  { label: '情感共鸣', value: 'emotional' }
]

const poemFormOptions = [
  { label: '现代诗', value: 'modern' },
  { label: '古诗', value: 'classical' },
  { label: '散文诗', value: 'prose' },
  { label: '自由诗', value: 'free' }
]

const storyTypeOptions = [
  { label: '科幻', value: 'scifi' },
  { label: '悬疑', value: 'mystery' },
  { label: '爱情', value: 'romance' },
  { label: '冒险', value: 'adventure' },
  { label: '励志', value: 'inspirational' },
  { label: '童话', value: 'fairytale' }
]

const emailSceneOptions = [
  { label: '商务沟通', value: 'business' },
  { label: '求职应聘', value: 'job' },
  { label: '客户维护', value: 'customer' },
  { label: '内部通知', value: 'internal' },
  { label: '投诉建议', value: 'complaint' },
  { label: '感谢信', value: 'thanks' }
]

const reportTypeOptions = [
  { label: '工作总结', value: 'summary' },
  { label: '数据分析', value: 'analysis' },
  { label: '项目汇报', value: 'project' },
  { label: '市场调研', value: 'research' },
  { label: '年度规划', value: 'plan' }
]

const lengthOptions = [
  { label: '简短', value: 'short' },
  { label: '中等', value: 'medium' },
  { label: '详细', value: 'long' }
]

const toneOptions = [
  { label: '专业', value: 'professional' },
  { label: '轻松', value: 'casual' },
  { label: '幽默', value: 'humorous' },
  { label: '正式', value: 'formal' }
]

// 表单数据
const selectedType = ref('article')
const formData = reactive({
  topic: '',
  keywords: '',
  length: 'medium',
  tone: 'professional',
  // 各类型专属字段
  audience: 'general',
  structure: 'total-sub-total',
  platform: 'wechat',
  content: '',
  ideaDirection: 'innovative',
  poemForm: 'modern',
  storyType: 'adventure',
  emailScene: 'business',
  reportType: 'summary'
})

const result = ref('')
const isGenerating = ref(false)

// 计算属性
const currentTypeConfig = computed(() => typeConfig[selectedType.value])

const showAudience = computed(() => {
  return ['article', 'copywriting', 'email', 'report'].includes(selectedType.value)
})

const canGenerate = computed(() => {
  if (selectedType.value === 'summary') {
    return formData.topic.trim().length > 0 && formData.content.trim().length > 0 && !isGenerating.value
  }
  return formData.topic.trim().length > 0 && !isGenerating.value
})

// 选择类型时重置相关字段
const selectType = (value) => {
  selectedType.value = value
  // 重置表单
  formData.topic = ''
  formData.keywords = ''
  formData.content = ''
  // 设置默认值
  formData.length = 'medium'
  formData.tone = 'professional'
  formData.audience = 'general'
  formData.structure = 'total-sub-total'
  formData.platform = 'wechat'
  formData.ideaDirection = 'innovative'
  formData.poemForm = 'modern'
  formData.storyType = 'adventure'
  formData.emailScene = 'business'
  formData.reportType = 'summary'
}

const goBack = () => {
  uni.navigateBack()
}

// 构建提示词
const buildPrompt = () => {
  const typeLabel = typeList.find(t => t.value === selectedType.value)?.label
  const toneLabel = toneOptions.find(t => t.value === formData.tone)?.label
  const lengthLabel = lengthOptions.find(l => l.value === formData.length)?.label

  let prompt = ''

  switch (selectedType.value) {
    case 'article':
      prompt = `请撰写一篇${toneLabel}风格的文章，主题：${formData.topic}`
      prompt += `。文章结构采用${structureOptions.find(s => s.value === formData.structure)?.label}式`
      prompt += `，目标受众为${audienceOptions.find(a => a.value === formData.audience)?.label}`
      break

    case 'copywriting':
      prompt = `请为"${formData.topic}"撰写一篇${platformOptions.find(p => p.value === formData.platform)?.label}平台的营销文案`
      prompt += `，风格${toneLabel}，目标受众为${audienceOptions.find(a => a.value === formData.audience)?.label}`
      break

    case 'summary':
      prompt = `请对以下内容进行摘要，主题：${formData.topic}\n\n原文：\n${formData.content}`
      prompt += `\n\n要求：${toneLabel}风格，${lengthLabel}篇幅`
      break

    case 'idea':
      prompt = `请围绕"${formData.topic}"提供创意方案`
      prompt += `，创意方向：${ideaDirectionOptions.find(i => i.value === formData.ideaDirection)?.label}`
      prompt += `，风格${toneLabel}`
      break

    case 'poem':
      prompt = `请创作一首${poemFormOptions.find(p => p.value === formData.poemForm)?.label}`
      prompt += `，主题：${formData.topic}，风格${toneLabel}`
      break

    case 'story':
      prompt = `请创作一个${storyTypeOptions.find(s => s.value === formData.storyType)?.label}故事`
      prompt += `，主题：${formData.topic}，风格${toneLabel}`
      break

    case 'email':
      prompt = `请撰写一封${emailSceneOptions.find(e => e.value === formData.emailScene)?.label}邮件`
      prompt += `，主题：${formData.topic}`
      prompt += `，语气${toneLabel}，面向${audienceOptions.find(a => a.value === formData.audience)?.label}`
      break

    case 'report':
      prompt = `请撰写一份${reportTypeOptions.find(r => r.value === formData.reportType)?.label}报告`
      prompt += `，主题：${formData.topic}`
      prompt += `，风格${toneLabel}，面向${audienceOptions.find(a => a.value === formData.audience)?.label}`
      break

    default:
      prompt = `请生成一篇${typeLabel}，主题：${formData.topic}，风格${toneLabel}，篇幅${lengthLabel}`
  }

  if (formData.keywords.trim()) {
    prompt += `。需要包含以下关键词：${formData.keywords.trim()}`
  }

  prompt += `。字数要求：${lengthLabel}。`

  return prompt
}

const handleGenerate = async () => {
  if (!isLoggedIn()) {
    uni.showModal({
      title: '提示',
      content: '请先登录后再使用',
      showCancel: false,
      success: () => { uni.reLaunch({ url: '/pages/login/login' }) }
    })
    return
  }

  if (!formData.topic.trim()) {
    uni.showToast({ title: currentTypeConfig.value.topicLabel + '不能为空', icon: 'none' })
    return
  }

  if (selectedType.value === 'summary' && !formData.content.trim()) {
    uni.showToast({ title: '请输入原文内容', icon: 'none' })
    return
  }

  isGenerating.value = true
  result.value = ''

  try {
    const prompt = buildPrompt()

    // 映射字数要求到 max_tokens
    const maxTokensMap = { short: 500, medium: 1000, long: 2000 }
    const maxTokens = maxTokensMap[formData.length] || 1000

    const res = await textGenerate({ prompt, max_tokens: maxTokens })

    result.value = res || ''
  } catch (error) {
    uni.showToast({ title: error.message || '生成失败', icon: 'none' })
  } finally {
    isGenerating.value = false
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

onMounted(() => {
  // 页面挂载完成
})
</script>

<style lang="scss" scoped>
.container {
  min-height: 100vh;
  background: linear-gradient(180deg, #f8faff 0%, #f0f5ff 100%);
  padding-bottom: 40rpx;
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
    filter: blur(80rpx);
    opacity: 0.4;
    animation: orb-float 8s ease-in-out infinite;
  }

  .orb-1 {
    width: 400rpx;
    height: 400rpx;
    background: linear-gradient(135deg, #2979FF, #5C9DFF);
    top: -100rpx;
    right: -100rpx;
    animation-delay: 0s;
  }

  .orb-2 {
    width: 300rpx;
    height: 300rpx;
    background: linear-gradient(135deg, #19BE6B, #4CD964);
    bottom: 200rpx;
    left: -100rpx;
    animation-delay: 4s;
  }
}

@keyframes orb-float {
  0%, 100% { transform: translate(0, 0) scale(1); }
  50% { transform: translate(30rpx, -30rpx) scale(1.1); }
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
    transition: transform 0.2s;

    &:active {
      transform: scale(0.9);
    }

    .icon-text {
      font-size: 40rpx;
      color: #333;
    }
  }

  .nav-title {
    font-size: 36rpx;
    font-weight: 600;
    color: #333;
    display: flex;
    align-items: center;

    .title-icon {
      margin-right: 8rpx;
      animation: sparkle 2s ease-in-out infinite;
    }
  }

  .nav-right {
    width: 60rpx;
  }
}

@keyframes sparkle {
  0%, 100% { transform: rotate(0deg); }
  50% { transform: rotate(10deg); }
}

/* 区域通用样式 */
.type-section, .form-section, .btn-section, .result-section {
  padding: 0 30rpx;
  margin-top: 24rpx;
}

.section-label, .form-label {
  font-size: 28rpx;
  font-weight: 600;
  color: #333;
  margin-bottom: 16rpx;
  display: flex;
  align-items: center;

  .label-icon {
    margin-right: 8rpx;
    font-size: 28rpx;
  }
}

/* 类型选择 */
.type-scroll { white-space: nowrap; }
.type-list {
  display: flex;
  gap: 16rpx;
  padding: 4rpx 0;
}

.type-item {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  padding: 20rpx 24rpx;
  background: #fff;
  border-radius: 20rpx;
  min-width: 120rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;

  &.active {
    background: linear-gradient(135deg, #2979FF, #5C9DFF);
    box-shadow: 0 8rpx 30rpx rgba(41, 121, 255, 0.3);

    .item-icon, .item-label {
      color: #fff;
    }
  }

  &:active:not(.active) {
    transform: scale(0.95);
  }

  .item-icon {
    font-size: 40rpx;
    margin-bottom: 8rpx;
    transition: color 0.3s;
  }

  .item-label {
    font-size: 24rpx;
    color: #666;
    transition: color 0.3s;
  }

  .active-indicator {
    position: absolute;
    bottom: 0;
    left: 50%;
    transform: translateX(-50%);
    width: 20rpx;
    height: 4rpx;
    background: rgba(255, 255, 255, 0.8);
    border-radius: 2rpx;
    animation: indicator-pulse 1.5s ease-in-out infinite;
  }
}

@keyframes indicator-pulse {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}

/* 输入框 */
.input-wrapper {
  position: relative;

  &.input-focused {
    .form-textarea, .form-input {
      box-shadow: 0 0 0 3rpx rgba(41, 121, 255, 0.1);
    }

    .input-border {
      transform: scaleX(1);
    }
  }
}

.form-textarea {
  width: 100%;
  min-height: 160rpx;
  background: #fff;
  border-radius: 16rpx;
  padding: 24rpx;
  font-size: 28rpx;
  color: #333;
  box-sizing: border-box;
  line-height: 1.6;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
}

.form-input {
  width: 100%;
  height: 88rpx;
  background: #fff;
  border-radius: 16rpx;
  padding: 0 24rpx;
  font-size: 28rpx;
  color: #333;
  box-sizing: border-box;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
}

.input-border {
  position: absolute;
  bottom: 0;
  left: 24rpx;
  right: 24rpx;
  height: 3rpx;
  background: linear-gradient(90deg, #2979FF, #5C9DFF);
  border-radius: 2rpx;
  transform: scaleX(0);
  transition: transform 0.3s ease;

  &.border-active {
    transform: scaleX(1);
  }
}

/* 选项列表 */
.option-list {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
}

.option-item {
  padding: 16rpx 32rpx;
  background: #fff;
  border-radius: 30rpx;
  font-size: 26rpx;
  color: #666;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;

  &.active {
    background: linear-gradient(135deg, #2979FF, #5C9DFF);
    color: #fff;
    box-shadow: 0 8rpx 30rpx rgba(41, 121, 255, 0.3);
  }

  &:active:not(.active) {
    transform: scale(0.95);
  }
}

/* 生成按钮 */
.generate-btn {
  background: linear-gradient(135deg, #2979FF, #5C9DFF);
  border-radius: 50rpx;
  height: 96rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 10rpx 30rpx rgba(41, 121, 255, 0.3);
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;

  &.btn-pulse {
    animation: btn-pulse 2s ease-in-out infinite;
  }

  &.loading {
    opacity: 0.9;
  }

  &:active:not(.loading) {
    box-shadow: 0 5rpx 20rpx rgba(41, 121, 255, 0.2);
  }

  .btn-glow {
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(255,255,255,0.3) 0%, transparent 60%);
    animation: glow-rotate 4s linear infinite;
  }

  .btn-content {
    display: flex;
    align-items: center;
    gap: 12rpx;
    position: relative;
    z-index: 1;
  }

  .btn-spinner {
    width: 36rpx;
    height: 36rpx;
    position: relative;

    .spinner-ring {
      width: 100%;
      height: 100%;
      border: 3rpx solid rgba(255, 255, 255, 0.3);
      border-top-color: #fff;
      border-radius: 50%;
      animation: spinner-rotate 0.8s linear infinite;
    }
  }

  .btn-text {
    font-size: 32rpx;
    font-weight: 600;
    color: #fff;
  }
}

@keyframes btn-pulse {
  0%, 100% { box-shadow: 0 10rpx 30rpx rgba(41, 121, 255, 0.3); }
  50% { box-shadow: 0 15rpx 40rpx rgba(41, 121, 255, 0.5); }
}

@keyframes glow-rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@keyframes spinner-rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 结果区域 */
.result-section {
  margin-top: 40rpx;

  .result-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16rpx;

    .result-title {
      font-size: 28rpx;
      font-weight: 600;
      color: #333;
      display: flex;
      align-items: center;

      .title-icon {
        margin-right: 8rpx;
        animation: celebrate 0.5s ease;
      }
    }

    .result-actions {
      .action-btn {
        display: flex;
        align-items: center;
        gap: 6rpx;
        padding: 12rpx 20rpx;
        background: #f0f5ff;
        border-radius: 24rpx;
        transition: all 0.3s ease;

        &.btn-copied {
          background: #19BE6B;

          .action-icon, .action-text {
            color: #fff;
          }
        }

        &:active {
          transform: scale(0.95);
        }

        .action-icon {
          font-size: 24rpx;
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
    box-shadow: 0 4rpx 30rpx rgba(0, 0, 0, 0.08);

    .result-text {
      font-size: 28rpx;
      color: #333;
      line-height: 1.8;
      white-space: pre-wrap;
      word-break: break-all;
    }
  }
}

@keyframes celebrate {
  0% { transform: rotate(-180deg); }
  50% { transform: rotate(10deg); }
  100% { transform: rotate(0deg); }
}
</style>
