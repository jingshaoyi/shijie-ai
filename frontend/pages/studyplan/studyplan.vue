<template>
  <view class="container">
    <view class="custom-nav">
      <view class="nav-left" @click="goBack"><text class="icon-text">←</text></view>
      <view class="nav-title">学习规划</view>
      <view class="nav-right"></view>
    </view>

    <view class="header-section">
      <view class="header-icon">📚</view>
      <view class="header-title">智能学习规划</view>
      <view class="header-subtitle">定制专属学习路线</view>
    </view>

    <!-- 学习目标 -->
    <view class="config-section">
      <view class="section-header">
        <text class="section-icon">🎯</text>
        <text class="section-title">学习目标</text>
      </view>
      <view class="goal-list">
        <view class="goal-item" v-for="(item, index) in goals" :key="index"
          :class="{ active: selectedGoal === item.value }" @click="selectedGoal = item.value">
          <view class="goal-icon">{{ item.icon }}</view>
          <view class="goal-name">{{ item.name }}</view>
        </view>
      </view>
    </view>

    <!-- 学习周期 -->
    <view class="config-section">
      <view class="section-header">
        <text class="section-icon">⏰</text>
        <text class="section-title">学习周期</text>
      </view>
      <view class="period-list">
        <view class="period-item" v-for="(item, index) in periods" :key="index"
          :class="{ active: selectedPeriod === item.value }" @click="selectedPeriod = item.value">
          <text class="period-name">{{ item.name }}</text>
        </view>
      </view>
    </view>

    <!-- 每日时长 -->
    <view class="config-section">
      <view class="section-header">
        <text class="section-icon">⏳</text>
        <text class="section-title">每日学习时长</text>
      </view>
      <view class="time-list">
        <view class="time-item" v-for="(item, index) in timeOptions" :key="index"
          :class="{ active: selectedTime === item.value }" @click="selectedTime = item.value">
          <text class="time-name">{{ item.name }}</text>
        </view>
      </view>
    </view>

    <!-- 当前水平 -->
    <view class="config-section">
      <view class="section-header">
        <text class="section-icon">📊</text>
        <text class="section-title">当前水平</text>
      </view>
      <view class="level-options">
        <view class="level-item" v-for="(item, index) in levels" :key="index"
          :class="{ active: selectedLevel === item.value }" @click="selectedLevel = item.value">
          <view class="level-icon">{{ item.icon }}</view>
          <view class="level-name">{{ item.name }}</view>
        </view>
      </view>
    </view>

    <!-- 补充说明 -->
    <view class="input-section">
      <view class="section-header">
        <text class="section-icon">💬</text>
        <text class="section-title">补充说明（选填）</text>
      </view>
      <view class="textarea-wrapper">
        <textarea class="extra-input" v-model="extraInfo" placeholder="例如：想转行做前端开发、准备考研、英语基础薄弱等..." :maxlength="300" />
        <view class="char-count">{{ extraInfo.length }}/300</view>
      </view>
    </view>

    <!-- 生成按钮 -->
    <view class="btn-section">
      <view class="generate-btn" :class="{ loading: isGenerating }" @click="generate">
        <text class="btn-icon" v-if="!isGenerating">📋</text>
        <view class="btn-spinner" v-else></view>
        <text class="btn-text">{{ isGenerating ? '规划中...' : '生成学习计划' }}</text>
      </view>
    </view>

    <!-- 结果 -->
    <view class="result-section" v-if="generatedContent">
      <view class="result-header">
        <view class="result-title"><text class="title-icon">📖</text> 学习计划</view>
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
import { ref } from 'vue'
import { aiChat } from '@/api/cloud.js'
import { isLoggedIn } from '@/api/user.js'
import { generatePromptWithFallback } from '@/api/prompts.js'

const goals = [
  { name: '编程开发', value: 'coding', icon: '💻' }, { name: '外语学习', value: 'language', icon: '🌍' },
  { name: '考研升学', value: 'exam', icon: '🎓' }, { name: '职业技能', value: 'skill', icon: '🔧' },
  { name: '兴趣爱好', value: 'hobby', icon: '🎨' }, { name: '其他', value: 'other', icon: '📌' }
]

const periods = [
  { name: '1周', value: '1week' }, { name: '1个月', value: '1month' },
  { name: '3个月', value: '3months' }, { name: '6个月', value: '6months' },
  { name: '1年', value: '1year' }
]

const timeOptions = [
  { name: '30分钟', value: '30min' }, { name: '1小时', value: '1hour' },
  { name: '2小时', value: '2hours' }, { name: '3小时+', value: '3hours' }
]

const levels = [
  { name: '零基础', value: 'beginner', icon: '🌱' },
  { name: '有一定基础', value: 'intermediate', icon: '🌿' },
  { name: '较熟练', value: 'advanced', icon: '🌳' }
]

const selectedGoal = ref('coding')
const selectedPeriod = ref('3months')
const selectedTime = ref('2hours')
const selectedLevel = ref('beginner')
const extraInfo = ref('')
const isGenerating = ref(false)
const generatedContent = ref('')

const goBack = () => uni.navigateBack()

const generate = async () => {
  if (!isLoggedIn()) {
    uni.showModal({ title: '提示', content: '请先登录', showCancel: false, success: () => uni.reLaunch({ url: '/pages/login/login' }) })
    return
  }

  isGenerating.value = true
  generatedContent.value = ''

  const goalName = goals.find(g => g.value === selectedGoal.value)?.name
  const periodName = periods.find(p => p.value === selectedPeriod.value)?.name
  const timeName = timeOptions.find(t => t.value === selectedTime.value)?.name
  const levelName = levels.find(l => l.value === selectedLevel.value)?.name

  try {
    const prompt = await generatePromptWithFallback('study_plan', {
      goal: goalName, period: periodName, daily_time: timeName,
      level: levelName, extra: extraInfo.value || '无'
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
.container { min-height: 100vh; background: linear-gradient(180deg, #f0fff4 0%, #f5f5f5 100%); }
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
.goal-list { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16rpx;
  .goal-item { background: #fff; border-radius: 20rpx; padding: 24rpx 16rpx; text-align: center; box-shadow: 0 4rpx 20rpx rgba(0,0,0,0.06); transition: all 0.3s;
    &.active { background: linear-gradient(135deg, #43e97b, #38f9d7); transform: scale(1.05);
      .goal-icon, .goal-name { color: #fff; }
    }
    &:active:not(.active) { transform: scale(0.95); }
    .goal-icon { font-size: 44rpx; margin-bottom: 8rpx; }
    .goal-name { font-size: 26rpx; color: #333; font-weight: 500; }
  }
}
.period-list, .time-list { display: flex; flex-wrap: wrap; gap: 16rpx;
  .period-item, .time-item { padding: 14rpx 28rpx; background: #fff; border-radius: 30rpx; font-size: 26rpx; color: #666; box-shadow: 0 4rpx 20rpx rgba(0,0,0,0.06); transition: all 0.3s;
    &.active { background: linear-gradient(135deg, #43e97b, #38f9d7); color: #fff; box-shadow: 0 4rpx 16rpx rgba(67,233,123,0.3); }
    &:active:not(.active) { transform: scale(0.95); }
    .period-name, .time-name { color: inherit; }
  }
}
.level-options { display: flex; gap: 16rpx;
  .level-item { flex: 1; background: #fff; border-radius: 20rpx; padding: 24rpx 16rpx; text-align: center; box-shadow: 0 4rpx 20rpx rgba(0,0,0,0.06); transition: all 0.3s;
    &.active { background: linear-gradient(135deg, #43e97b, #38f9d7);
      .level-icon, .level-name { color: #fff; }
    }
    &:active:not(.active) { transform: scale(0.95); }
    .level-icon { font-size: 44rpx; margin-bottom: 8rpx; }
    .level-name { font-size: 26rpx; color: #333; font-weight: 600; }
  }
}
.input-section { padding: 0 30rpx; margin-bottom: 30rpx;
  .section-header { display: flex; align-items: center; margin-bottom: 16rpx;
    .section-icon { font-size: 32rpx; margin-right: 12rpx; }
    .section-title { font-size: 30rpx; font-weight: 600; color: #333; }
  }
}
.textarea-wrapper { position: relative; background: #fff; border-radius: 20rpx; padding: 24rpx; box-shadow: 0 4rpx 20rpx rgba(0,0,0,0.06);
  .extra-input { width: 100%; min-height: 160rpx; font-size: 28rpx; color: #333; line-height: 1.6; }
  .char-count { text-align: right; font-size: 24rpx; color: #999; margin-top: 12rpx; }
}
.btn-section { padding: 0 30rpx 30rpx; }
.generate-btn { background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); border-radius: 50rpx; height: 96rpx; display: flex; align-items: center; justify-content: center; box-shadow: 0 10rpx 30rpx rgba(67,233,123,0.3); transition: all 0.3s;
  &.loading { opacity: 0.8; }
  &:active { transform: scale(0.98); }
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
      .action-btn { display: flex; align-items: center; padding: 8rpx 16rpx; background: #e8f8f0; border-radius: 24rpx; font-size: 24rpx; color: #43e97b;
        &:active { background: #d0f0e0; }
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
