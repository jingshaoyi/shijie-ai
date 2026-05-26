<template>
  <view class="container">
    <view class="custom-nav">
      <view class="nav-left" @click="goBack"><text class="icon-text">←</text></view>
      <view class="nav-title">代码解释</view>
      <view class="nav-right"></view>
    </view>

    <view class="header-section">
      <view class="header-icon">💻</view>
      <view class="header-title">代码解释助手</view>
      <view class="header-subtitle">粘贴代码，秒懂原理</view>
    </view>

    <!-- 编程语言 -->
    <view class="config-section">
      <view class="section-header">
        <text class="section-icon">🔧</text>
        <text class="section-title">编程语言</text>
      </view>
      <view class="lang-list">
        <view class="lang-item" v-for="(item, index) in languages" :key="index"
          :class="{ active: selectedLang === item.value }" @click="selectedLang = item.value">
          <text class="lang-name">{{ item.name }}</text>
        </view>
      </view>
    </view>

    <!-- 解释深度 -->
    <view class="config-section">
      <view class="section-header">
        <text class="section-icon">🎯</text>
        <text class="section-title">解释深度</text>
      </view>
      <view class="depth-options">
        <view class="depth-item" v-for="(item, index) in depths" :key="index"
          :class="{ active: selectedDepth === item.value }" @click="selectedDepth = item.value">
          <view class="depth-icon">{{ item.icon }}</view>
          <view class="depth-name">{{ item.name }}</view>
          <view class="depth-desc">{{ item.desc }}</view>
        </view>
      </view>
    </view>

    <!-- 代码输入 -->
    <view class="input-section">
      <view class="section-header">
        <text class="section-icon">📝</text>
        <text class="section-title">粘贴代码</text>
      </view>
      <view class="code-wrapper">
        <textarea class="code-input" v-model="codeContent" placeholder="在此粘贴需要解释的代码..."
          :maxlength="3000" />
        <view class="char-count">{{ codeContent.length }}/3000</view>
      </view>
    </view>

    <!-- 补充问题 -->
    <view class="input-section">
      <view class="section-header">
        <text class="section-icon">❓</text>
        <text class="section-title">补充问题（选填）</text>
      </view>
      <input class="question-input" v-model="question" placeholder="例如：这段代码的时间复杂度是多少？" maxlength="200" />
    </view>

    <!-- 生成按钮 -->
    <view class="btn-section">
      <view class="generate-btn" :class="{ loading: isGenerating, disabled: !canGenerate }" @click="generate">
        <text class="btn-icon" v-if="!isGenerating">🔍</text>
        <view class="btn-spinner" v-else></view>
        <text class="btn-text">{{ isGenerating ? '分析中...' : '开始解释' }}</text>
      </view>
    </view>

    <!-- 结果 -->
    <view class="result-section" v-if="generatedContent">
      <view class="result-header">
        <view class="result-title"><text class="title-icon">💡</text> 代码解读</view>
        <view class="result-actions">
          <view class="action-btn" @click="copyResult"><text>📋</text><text>复制</text></view>
          <view class="action-btn" @click="generate"><text>🔄</text><text>重新解释</text></view>
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

const languages = [
  { name: 'Python', value: 'python' }, { name: 'JavaScript', value: 'javascript' },
  { name: 'Java', value: 'java' }, { name: 'C/C++', value: 'cpp' },
  { name: 'Go', value: 'go' }, { name: 'TypeScript', value: 'typescript' },
  { name: 'SQL', value: 'sql' }, { name: '其他', value: 'other' }
]

const depths = [
  { value: 'simple', name: '入门级', icon: '🌱', desc: '逐行解释' },
  { value: 'normal', name: '进阶级', icon: '📖', desc: '原理+逻辑' },
  { value: 'deep', name: '专家级', icon: '🔬', desc: '深度剖析' }
]

const selectedLang = ref('python')
const selectedDepth = ref('normal')
const codeContent = ref('')
const question = ref('')
const isGenerating = ref(false)
const generatedContent = ref('')

const canGenerate = computed(() => codeContent.value.trim().length >= 10)
const goBack = () => uni.navigateBack()

const generate = async () => {
  if (!isLoggedIn()) {
    uni.showModal({ title: '提示', content: '请先登录', showCancel: false, success: () => uni.reLaunch({ url: '/pages/login/login' }) })
    return
  }
  if (!canGenerate.value) { uni.showToast({ title: '请粘贴至少10个字符的代码', icon: 'none' }); return }

  isGenerating.value = true
  generatedContent.value = ''

  const langName = languages.find(l => l.value === selectedLang.value)?.name
  const depthName = depths.find(d => d.value === selectedDepth.value)?.name

  try {
    const prompt = await generatePromptWithFallback('code_explain', {
      language: langName, depth: depthName, code: codeContent.value,
      question: question.value || '请解释这段代码的功能和原理'
    })
    const res = await aiChat(prompt, [], 'dashscope/qwen-plus')
    generatedContent.value = res
  } catch (error) {
    uni.showToast({ title: error.message || '解释失败', icon: 'none' })
  } finally { isGenerating.value = false }
}

const copyResult = () => {
  uni.setClipboardData({ data: generatedContent.value, success: () => uni.showToast({ title: '已复制', icon: 'success' }) })
}
</script>

<style lang="scss" scoped>
.container { min-height: 100vh; background: linear-gradient(180deg, #f0f4ff 0%, #f5f5f5 100%); }
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
.lang-list { display: flex; flex-wrap: wrap; gap: 16rpx;
  .lang-item { padding: 14rpx 28rpx; background: #fff; border-radius: 30rpx; font-size: 26rpx; color: #666; box-shadow: 0 4rpx 20rpx rgba(0,0,0,0.06); transition: all 0.3s;
    &.active { background: linear-gradient(135deg, #667eea, #764ba2); color: #fff; box-shadow: 0 4rpx 16rpx rgba(102,126,234,0.3); }
    &:active:not(.active) { transform: scale(0.95); }
    .lang-name { color: inherit; }
  }
}
.depth-options { display: flex; gap: 16rpx;
  .depth-item { flex: 1; background: #fff; border-radius: 20rpx; padding: 24rpx 16rpx; text-align: center; box-shadow: 0 4rpx 20rpx rgba(0,0,0,0.06); transition: all 0.3s;
    &.active { background: linear-gradient(135deg, #667eea, #764ba2);
      .depth-icon, .depth-name, .depth-desc { color: #fff; }
    }
    &:active:not(.active) { transform: scale(0.95); }
    .depth-icon { font-size: 44rpx; margin-bottom: 8rpx; }
    .depth-name { font-size: 26rpx; color: #333; font-weight: 600; margin-bottom: 6rpx; }
    .depth-desc { font-size: 22rpx; color: #999; }
  }
}
.input-section { padding: 0 30rpx; margin-bottom: 30rpx;
  .section-header { display: flex; align-items: center; margin-bottom: 16rpx;
    .section-icon { font-size: 32rpx; margin-right: 12rpx; }
    .section-title { font-size: 30rpx; font-weight: 600; color: #333; }
  }
}
.code-wrapper { position: relative; background: #1e1e2e; border-radius: 20rpx; padding: 24rpx; box-shadow: 0 4rpx 20rpx rgba(0,0,0,0.1);
  .code-input { width: 100%; min-height: 300rpx; font-size: 26rpx; color: #a6e3a1; line-height: 1.6; font-family: 'Consolas', 'Monaco', monospace; }
  .char-count { text-align: right; font-size: 24rpx; color: #666; margin-top: 12rpx; }
}
.question-input { width: 100%; height: 80rpx; background: #fff; border-radius: 16rpx; padding: 0 24rpx; font-size: 28rpx; color: #333; box-shadow: 0 4rpx 20rpx rgba(0,0,0,0.06); }

.btn-section { padding: 0 30rpx 30rpx; }
.generate-btn { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 50rpx; height: 96rpx; display: flex; align-items: center; justify-content: center; box-shadow: 0 10rpx 30rpx rgba(102,126,234,0.3); transition: all 0.3s;
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
      .action-btn { display: flex; align-items: center; padding: 8rpx 16rpx; background: #f0f5ff; border-radius: 24rpx; font-size: 24rpx; color: #2979FF;
        &:active { background: #e0ebff; }
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
