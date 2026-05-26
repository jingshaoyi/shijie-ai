<template>
  <div class="page-container">
    <div class="page-header">
      <h1>数据概览</h1>
      <p>实时监控系统运行状态和用户数据</p>
    </div>

    <!-- 统计卡片 -->
    <a-row :gutter="[24, 24]" class="stat-row">
      <a-col :xs="24" :sm="12" :lg="6">
        <a-card class="stat-card" :bordered="false">
          <div class="stat-icon blue">
            <user-outlined />
          </div>
          <div class="stat-title">总用户数</div>
          <div class="stat-value">{{ formatNumber(statistics.totalUsers) }}</div>
          <div class="stat-trend up">
            <arrow-up-outlined /> {{ statistics.userGrowth }}% 较上月
          </div>
        </a-card>
      </a-col>

      <a-col :xs="24" :sm="12" :lg="6">
        <a-card class="stat-card" :bordered="false">
          <div class="stat-icon green">
            <message-outlined />
          </div>
          <div class="stat-title">今日对话</div>
          <div class="stat-value">{{ formatNumber(statistics.todayChats) }}</div>
          <div class="stat-trend up">
            <arrow-up-outlined /> {{ statistics.chatGrowth }}% 较昨日
          </div>
        </a-card>
      </a-col>

      <a-col :xs="24" :sm="12" :lg="6">
        <a-card class="stat-card" :bordered="false">
          <div class="stat-icon orange">
            <file-text-outlined />
          </div>
          <div class="stat-title">总对话数</div>
          <div class="stat-value">{{ formatNumber(statistics.totalChats) }}</div>
          <div class="stat-trend up">
            <arrow-up-outlined /> {{ statistics.totalChatGrowth }}% 较上月
          </div>
        </a-card>
      </a-col>

      <a-col :xs="24" :sm="12" :lg="6">
        <a-card class="stat-card" :bordered="false">
          <div class="stat-icon purple">
            <comment-outlined />
          </div>
          <div class="stat-title">待处理反馈</div>
          <div class="stat-value">{{ statistics.pendingFeedbacks }}</div>
          <div class="stat-trend" :class="statistics.feedbackTrend > 0 ? 'up' : 'down'">
            <arrow-up-outlined v-if="statistics.feedbackTrend > 0" />
            <arrow-down-outlined v-else />
            {{ Math.abs(statistics.feedbackTrend) }}% 较上周
          </div>
        </a-card>
      </a-col>
    </a-row>

    <!-- 图表区域 -->
    <a-row :gutter="[24, 24]" class="chart-row">
      <a-col :xs="24" :lg="16">
        <a-card title="用户增长趋势" :bordered="false" class="chart-card">
          <div ref="trendChartRef" class="chart-container"></div>
        </a-card>
      </a-col>

      <a-col :xs="24" :lg="8">
        <a-card title="模型使用分布" :bordered="false" class="chart-card">
          <div ref="modelChartRef" class="chart-container"></div>
        </a-card>
      </a-col>
    </a-row>

    <!-- 最近活动 -->
    <a-row :gutter="[24, 24]">
      <a-col :xs="24" :lg="12">
        <a-card title="最近活动" :bordered="false">
          <a-timeline v-if="recentActivities.length > 0">
            <a-timeline-item
              v-for="(activity, index) in recentActivities"
              :key="index"
              :color="activity.type === 'user' ? 'blue' : 'green'"
            >
              <p>{{ activity.content }}</p>
              <span class="activity-time">{{ activity.time }}</span>
            </a-timeline-item>
          </a-timeline>
          <a-empty v-else description="暂无活动记录" />
        </a-card>
      </a-col>

      <a-col :xs="24" :lg="12">
        <a-card title="快捷操作" :bordered="false">
          <a-space direction="vertical" style="width: 100%">
            <a-button type="primary" block @click="$router.push('/users')">
              <user-outlined />
              查看用户列表
            </a-button>
            <a-button block @click="$router.push('/chats')">
              <message-outlined />
              查看对话记录
            </a-button>
            <a-button block @click="$router.push('/feedbacks')">
              <comment-outlined />
              处理用户反馈
            </a-button>
            <a-button block @click="$router.push('/prompts')">
              <file-text-outlined />
              管理提示词模板
            </a-button>
          </a-space>
        </a-card>
      </a-col>
    </a-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import { getStatistics, getTrendData, getModelStats, getRecentActivities } from '@/api/dashboard'

// 统计数据
const statistics = reactive({
  totalUsers: 0,
  todayUsers: 0,
  userGrowth: 0,
  todayChats: 0,
  chatGrowth: 0,
  totalChats: 0,
  pendingFeedbacks: 0,
})

// 图表引用
const trendChartRef = ref(null)
const modelChartRef = ref(null)
let trendChart = null
let modelChart = null

// 最近活动
const recentActivities = ref([])

// 格式化数字
const formatNumber = (num) => {
  if (num >= 10000) {
    return (num / 10000).toFixed(1) + '万'
  }
  return num.toLocaleString()
}

// 初始化趋势图
const initTrendChart = (trendData) => {
  if (!trendChartRef.value) return

  trendChart = echarts.init(trendChartRef.value)
  const option = {
    tooltip: {
      trigger: 'axis',
    },
    legend: {
      data: ['新增用户', '活跃对话'],
      bottom: 0,
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: trendData.map(item => item.date),
    },
    yAxis: {
      type: 'value',
    },
    series: [
      {
        name: '新增用户',
        type: 'line',
        smooth: true,
        data: trendData.map(item => item.users),
        itemStyle: { color: '#1890ff' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(24, 144, 255, 0.3)' },
            { offset: 1, color: 'rgba(24, 144, 255, 0.05)' },
          ]),
        },
      },
      {
        name: '活跃对话',
        type: 'line',
        smooth: true,
        data: trendData.map(item => item.chats),
        itemStyle: { color: '#52c41a' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(82, 196, 26, 0.3)' },
            { offset: 1, color: 'rgba(82, 196, 26, 0.05)' },
          ]),
        },
      },
    ],
  }
  trendChart.setOption(option)
}

// 初始化模型使用图
const initModelChart = (modelData) => {
  if (!modelChartRef.value) return

  modelChart = echarts.init(modelChartRef.value)
  const colors = ['#1890ff', '#52c41a', '#fa8c16', '#722ed1', '#bfbfbf']
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c}%',
    },
    legend: {
      orient: 'vertical',
      left: 'left',
    },
    series: [
      {
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2,
        },
        label: {
          show: false,
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 16,
            fontWeight: 'bold',
          },
        },
        data: modelData.map((item, index) => ({
          value: item.percentage,
          name: item.name,
          itemStyle: { color: colors[index % colors.length] },
        })),
      },
    ],
  }
  modelChart.setOption(option)
}

// 加载数据
const loadData = async () => {
  try {
    // 获取统计数据
    const statsRes = await getStatistics()
    if (statsRes.success) {
      Object.assign(statistics, statsRes.data)
    }

    // 获取趋势数据
    const trendRes = await getTrendData(7)
    if (trendRes.success && trendRes.data) {
      initTrendChart(trendRes.data)
      recentActivities.value = []
    }

    // 获取模型统计数据
    const modelRes = await getModelStats()
    if (modelRes.success && modelRes.data) {
      initModelChart(modelRes.data)
    }

    // 获取最近活动
    const activityRes = await getRecentActivities(10)
    if (activityRes.success && activityRes.data) {
      recentActivities.value = activityRes.data
    }
  } catch (error) {
    console.error('加载数据失败:', error)
  }
}

// 窗口大小改变时重新渲染图表
const handleResize = () => {
  trendChart?.resize()
  modelChart?.resize()
}

onMounted(() => {
  loadData()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  trendChart?.dispose()
  modelChart?.dispose()
})
</script>

<style lang="scss" scoped>
.stat-row {
  margin-bottom: 24px;
}

.chart-row {
  margin-bottom: 24px;
}

.chart-card {
  .chart-container {
    height: 350px;
  }
}

.activity-time {
  color: #999;
  font-size: 12px;
}
</style>
