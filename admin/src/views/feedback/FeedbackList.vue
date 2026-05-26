<template>
  <div class="page-container">
    <div class="page-header">
      <h1>反馈管理</h1>
      <p>处理用户反馈和意见</p>
    </div>

    <a-card :bordered="false">
      <a-table
        :columns="columns"
        :data-source="feedbackList"
        :loading="loading"
        :pagination="pagination"
        @change="handleTableChange"
        row-key="id"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'status'">
            <a-tag :color="record.status === 'pending' ? 'warning' : 'success'">
              {{ record.status === 'pending' ? '待处理' : '已处理' }}
            </a-tag>
          </template>
          <template v-if="column.key === 'action'">
            <a-button type="link" @click="handleReply(record)">
              {{ record.status === 'pending' ? '处理' : '查看' }}
            </a-button>
          </template>
        </template>
      </a-table>
    </a-card>

    <!-- 回复对话框 -->
    <a-modal
      v-model:open="replyModalVisible"
      title="回复反馈"
      @ok="submitReply"
      :confirm-loading="submitting"
    >
      <a-form :model="replyForm" layout="vertical">
        <a-form-item label="反馈内容">
          <p>{{ replyForm.content }}</p>
        </a-form-item>
        <a-form-item label="回复内容" required>
          <a-textarea v-model:value="replyForm.reply" :rows="4" placeholder="请输入回复内容" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { getFeedbackList, replyFeedback } from '@/api/feedback'

const loading = ref(false)
const feedbackList = ref([])
const replyModalVisible = ref(false)
const submitting = ref(false)

const replyForm = reactive({
  id: null,
  content: '',
  reply: '',
})

const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0,
})

const columns = [
  { title: 'ID', dataIndex: 'id', key: 'id', width: 80 },
  { title: '用户', dataIndex: 'username', key: 'username' },
  { title: '类型', dataIndex: 'type', key: 'type' },
  { title: '内容', dataIndex: 'content', key: 'content', ellipsis: true },
  { title: '状态', dataIndex: 'status', key: 'status' },
  { title: '时间', dataIndex: 'created_at', key: 'created_at' },
  { title: '操作', key: 'action', width: 100 },
]

const loadData = async () => {
  loading.value = true
  try {
    const res = await getFeedbackList({
      page: pagination.current,
      page_size: pagination.pageSize,
    })
    if (res.success) {
      feedbackList.value = res.data || []
      pagination.total = res.total || 0
    }
  } catch (error) {
    console.error('加载反馈列表失败:', error)
    feedbackList.value = []
  } finally {
    loading.value = false
  }
}

const handleTableChange = (pag) => {
  pagination.current = pag.current
  pagination.pageSize = pag.pageSize
  loadData()
}

const handleReply = (record) => {
  replyForm.id = record.id
  replyForm.content = record.content
  replyForm.reply = ''
  replyModalVisible.value = true
}

const submitReply = async () => {
  if (!replyForm.reply.trim()) {
    message.warning('请输入回复内容')
    return
  }

  submitting.value = true
  try {
    const res = await replyFeedback(replyForm.id, replyForm.reply)
    if (res.success) {
      message.success('回复成功')
      replyModalVisible.value = false
      loadData()
    }
  } catch (error) {
    message.error('回复失败')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>
