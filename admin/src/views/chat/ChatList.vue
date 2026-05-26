<template>
  <div class="page-container">
    <div class="page-header">
      <h1>对话记录</h1>
      <p>查看和管理用户对话历史</p>
    </div>

    <a-card :bordered="false">
      <a-table
        :columns="columns"
        :data-source="chatList"
        :loading="loading"
        :pagination="pagination"
        @change="handleTableChange"
        row-key="id"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'action'">
            <a-button type="link" @click="handleView(record)">查看详情</a-button>
          </template>
        </template>
      </a-table>
    </a-card>

    <!-- 对话详情弹窗（可拖拽缩放） -->
    <a-modal
      v-model:open="detailVisible"
      :title="detailTitle"
      :width="modalWidth"
      :footer="null"
      :bodyStyle="{ height: modalHeight + 'px', overflow: 'hidden', padding: '16px' }"
      :style="{ top: modalTop + 'px', left: modalLeft + 'px' }"
      :closable="true"
      :maskClosable="true"
      wrapClassName="draggable-modal"
      @cancel="resetModalPosition"
    >
      <template #title>
        <div class="modal-title-bar" @mousedown="startDrag">
          <span>{{ detailTitle }}</span>
          <span class="drag-hint">⣿ 拖拽移动</span>
        </div>
      </template>

      <a-spin :spinning="detailLoading">
        <div class="chat-detail">
          <!-- 统计信息 -->
          <div class="detail-meta">
            <a-descriptions :column="4" size="small" bordered>
              <a-descriptions-item label="用户">{{ detailData.username }}</a-descriptions-item>
              <a-descriptions-item label="模型">{{ detailData.model }}</a-descriptions-item>
              <a-descriptions-item label="消息数">{{ detailData.message_count }}</a-descriptions-item>
              <a-descriptions-item label="创建时间">{{ detailData.created_at }}</a-descriptions-item>
            </a-descriptions>

            <!-- Token和文本统计 -->
            <div class="stats-bar">
              <div class="stat-item">
                <span class="stat-label">总字符数</span>
                <span class="stat-value">{{ totalChars }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">用户输入</span>
                <span class="stat-value">{{ userChars }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">AI回复</span>
                <span class="stat-value">{{ aiChars }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">预估Token</span>
                <span class="stat-value highlight">{{ estimatedTokens }}</span>
              </div>
            </div>
          </div>

          <a-divider style="margin: 12px 0" />

          <!-- 消息列表 -->
          <div class="detail-messages" ref="messagesContainer">
            <div
              v-for="(msg, idx) in detailData.messages"
              :key="idx"
              class="message-item"
              :class="msg.role"
            >
              <div class="message-header">
                <a-tag :color="msg.role === 'user' ? 'blue' : 'green'">
                  {{ msg.role === 'user' ? '用户' : 'AI' }}
                </a-tag>
                <span class="msg-chars">{{ (msg.content || '').length }} 字</span>
                <span class="msg-time">{{ msg.time || msg.created_at }}</span>
              </div>
              <div class="message-content">{{ msg.content }}</div>
            </div>

            <a-empty v-if="!detailData.messages || detailData.messages.length === 0" description="暂无消息" />
          </div>
        </div>
      </a-spin>

      <!-- 缩放控制 -->
      <div class="resize-controls">
        <a-tooltip title="放大">
          <a-button size="small" @click="resizeModal(100, 80)"><zoom-in-outlined /></a-button>
        </a-tooltip>
        <a-tooltip title="缩小">
          <a-button size="small" @click="resizeModal(-100, -60)"><zoom-out-outlined /></a-button>
        </a-tooltip>
        <a-tooltip title="重置大小">
          <a-button size="small" @click="resetModalPosition"><expand-outlined /></a-button>
        </a-tooltip>
      </div>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { getChatList, getChatDetail } from '@/api/chat'

const loading = ref(false)
const chatList = ref([])
const detailVisible = ref(false)
const detailLoading = ref(false)
const detailTitle = ref('')
const detailData = ref({})

// 模态框尺寸与位置
const DEFAULT_WIDTH = 800
const DEFAULT_HEIGHT = 600
const modalWidth = ref(DEFAULT_WIDTH)
const modalHeight = ref(DEFAULT_HEIGHT)
const modalTop = ref(60)
const modalLeft = ref(0)

// 拖拽状态
const isDragging = ref(false)
const dragOffset = reactive({ x: 0, y: 0 })

const messagesContainer = ref(null)

const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0,
})

const columns = [
  { title: 'ID', dataIndex: 'id', key: 'id', width: 80 },
  { title: '用户', dataIndex: 'username', key: 'username' },
  { title: '标题', dataIndex: 'title', key: 'title', ellipsis: true },
  { title: '模型', dataIndex: 'model', key: 'model', width: 140 },
  { title: '消息数', dataIndex: 'message_count', key: 'message_count', width: 80 },
  { title: '创建时间', dataIndex: 'created_at', key: 'created_at', width: 150 },
  { title: '操作', key: 'action', width: 120 },
]

// 统计计算
const totalChars = computed(() => {
  if (!detailData.value.messages) return 0
  return detailData.value.messages.reduce((sum, m) => sum + (m.content || '').length, 0)
})

const userChars = computed(() => {
  if (!detailData.value.messages) return 0
  return detailData.value.messages.filter(m => m.role === 'user').reduce((sum, m) => sum + (m.content || '').length, 0)
})

const aiChars = computed(() => {
  if (!detailData.value.messages) return 0
  return detailData.value.messages.filter(m => m.role === 'assistant').reduce((sum, m) => sum + (m.content || '').length, 0)
})

const estimatedTokens = computed(() => {
  // 中文约1.5字/token，英文约4字符/token，取中间值估算
  return Math.ceil(totalChars.value / 2)
})

// 拖拽功能
const startDrag = (e) => {
  isDragging.value = true
  dragOffset.x = e.clientX - modalLeft.value
  dragOffset.y = e.clientY - modalTop.value

  const onMouseMove = (ev) => {
    if (!isDragging.value) return
    modalLeft.value = ev.clientX - dragOffset.x
    modalTop.value = ev.clientY - dragOffset.y
  }

  const onMouseUp = () => {
    isDragging.value = false
    document.removeEventListener('mousemove', onMouseMove)
    document.removeEventListener('mouseup', onMouseUp)
  }

  document.addEventListener('mousemove', onMouseMove)
  document.addEventListener('mouseup', onMouseUp)
}

// 缩放功能
const resizeModal = (deltaW, deltaH) => {
  modalWidth.value = Math.max(600, Math.min(1400, modalWidth.value + deltaW))
  modalHeight.value = Math.max(400, Math.min(900, modalHeight.value + deltaH))
}

const resetModalPosition = () => {
  modalWidth.value = DEFAULT_WIDTH
  modalHeight.value = DEFAULT_HEIGHT
  modalTop.value = 60
  modalLeft.value = 0
}

const loadData = async () => {
  loading.value = true
  try {
    const res = await getChatList({
      page: pagination.current,
      page_size: pagination.pageSize,
    })
    if (res.success) {
      chatList.value = res.data || []
      pagination.total = res.total || 0
    }
  } catch (error) {
    console.error('加载对话列表失败:', error)
    chatList.value = []
  } finally {
    loading.value = false
  }
}

const handleTableChange = (pag) => {
  pagination.current = pag.current
  pagination.pageSize = pag.pageSize
  loadData()
}

const handleView = async (record) => {
  detailTitle.value = `对话详情 - ${record.title || '未命名'}`
  detailData.value = { username: record.username, model: record.model, created_at: record.created_at, messages: [] }
  resetModalPosition()
  detailVisible.value = true
  detailLoading.value = true

  try {
    const res = await getChatDetail(record.id)
    if (res.success) {
      detailData.value = res.data
    }
  } catch (error) {
    console.error('加载对话详情失败:', error)
  } finally {
    detailLoading.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<style lang="scss" scoped>
.chat-detail {
  display: flex;
  flex-direction: column;
  height: 100%;

  .detail-meta {
    flex-shrink: 0;
  }

  .stats-bar {
    display: flex;
    gap: 16px;
    margin-top: 12px;
    padding: 10px 16px;
    background: linear-gradient(135deg, #f0f5ff 0%, #e6fffb 100%);
    border-radius: 8px;

    .stat-item {
      display: flex;
      flex-direction: column;
      align-items: center;
      flex: 1;

      .stat-label {
        font-size: 12px;
        color: #999;
        margin-bottom: 4px;
      }

      .stat-value {
        font-size: 18px;
        font-weight: 600;
        color: #333;

        &.highlight {
          color: #1890ff;
          font-size: 20px;
        }
      }
    }
  }

  .detail-messages {
    flex: 1;
    overflow-y: auto;
    padding-right: 4px;

    .message-item {
      margin-bottom: 12px;
      padding: 12px 16px;
      border-radius: 8px;
      background: #fafafa;

      &.user {
        background: #e6f7ff;
        border-left: 3px solid #1890ff;
      }

      &.assistant {
        background: #f6ffed;
        border-left: 3px solid #52c41a;
      }

      .message-header {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 8px;

        .msg-chars {
          font-size: 12px;
          color: #999;
        }

        .msg-time {
          font-size: 12px;
          color: #bbb;
          margin-left: auto;
        }
      }

      .message-content {
        font-size: 14px;
        line-height: 1.6;
        white-space: pre-wrap;
        word-break: break-all;
      }
    }
  }
}

.modal-title-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: move;
  user-select: none;

  .drag-hint {
    font-size: 12px;
    color: #bbb;
  }
}

.resize-controls {
  position: absolute;
  bottom: 12px;
  right: 24px;
  display: flex;
  gap: 4px;
  z-index: 10;
}
</style>

<style lang="scss">
/* 全局样式：让modal可拖拽 */
.draggable-modal {
  .ant-modal {
    position: absolute;
    margin: 0;
    top: 0;
    left: 0;
  }
}
</style>
