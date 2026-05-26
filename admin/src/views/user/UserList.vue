<template>
  <div class="page-container">
    <div class="page-header">
      <h1>用户管理</h1>
      <p>管理系统用户信息和状态</p>
    </div>

    <!-- 搜索区域 -->
    <div class="search-form">
      <a-form layout="inline" :model="searchForm">
        <a-form-item label="关键词">
          <a-input v-model:value="searchForm.keyword" placeholder="搜索昵称或ID" allow-clear style="width: 200px" />
        </a-form-item>
        <a-form-item label="状态">
          <a-select v-model:value="searchForm.status" placeholder="选择状态" style="width: 120px" allow-clear>
            <a-select-option value="active">正常</a-select-option>
            <a-select-option value="inactive">禁用</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item>
          <a-button type="primary" @click="handleSearch">
            <search-outlined />
            搜索
          </a-button>
          <a-button style="margin-left: 8px" @click="handleReset">重置</a-button>
        </a-form-item>
      </a-form>
    </div>

    <!-- 数据表格 -->
    <a-card :bordered="false">
      <a-table
        :columns="columns"
        :data-source="userList"
        :loading="loading"
        :pagination="pagination"
        @change="handleTableChange"
        row-key="id"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'avatar'">
            <a-avatar :src="record.avatar" :size="40">
              <template #icon><user-outlined /></template>
            </a-avatar>
          </template>
          <template v-if="column.key === 'status'">
            <a-tag :color="record.status === 'active' ? 'success' : 'error'">
              {{ record.status === 'active' ? '正常' : '禁用' }}
            </a-tag>
          </template>
          <template v-if="column.key === 'action'">
            <div class="table-actions">
              <a-button type="link" size="small" @click="handleView(record)">查看</a-button>
              <a-popconfirm
                :title="record.status === 'active' ? '确定禁用该用户?' : '确定启用该用户?'"
                @confirm="handleToggleStatus(record)"
              >
                <a-button type="link" size="small" :danger="record.status === 'active'">
                  {{ record.status === 'active' ? '禁用' : '启用' }}
                </a-button>
              </a-popconfirm>
            </div>
          </template>
        </template>
      </a-table>
    </a-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { getUserList, updateUserStatus } from '@/api/user'

const loading = ref(false)
const userList = ref([])

const searchForm = reactive({
  keyword: '',
  status: undefined,
})

const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0,
})

const columns = [
  { title: 'ID', dataIndex: 'id', key: 'id', width: 80 },
  { title: '头像', dataIndex: 'avatar', key: 'avatar', width: 80 },
  { title: '用户名', dataIndex: 'username', key: 'username' },
  { title: '昵称', dataIndex: 'nickname', key: 'nickname' },
  { title: '注册时间', dataIndex: 'created_at', key: 'created_at' },
  { title: '状态', dataIndex: 'status', key: 'status' },
  { title: '操作', key: 'action', width: 150 },
]

const loadData = async () => {
  loading.value = true
  try {
    const res = await getUserList({
      page: pagination.current,
      page_size: pagination.pageSize,
      keyword: searchForm.keyword,
      status: searchForm.status,
    })
    if (res.success) {
      userList.value = res.data || []
      pagination.total = res.total || 0
    }
  } catch (error) {
    console.error('加载用户列表失败:', error)
    userList.value = []
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.current = 1
  loadData()
}

const handleReset = () => {
  searchForm.keyword = ''
  searchForm.status = undefined
  handleSearch()
}

const handleTableChange = (pag) => {
  pagination.current = pag.current
  pagination.pageSize = pag.pageSize
  loadData()
}

const handleView = (record) => {
  message.info(`查看用户: ${record.nickname}`)
}

const handleToggleStatus = async (record) => {
  try {
    const newStatus = record.status === 'active' ? 'inactive' : 'active'
    const res = await updateUserStatus(record.id, newStatus)
    if (res.success) {
      message.success('操作成功')
      loadData()
    }
  } catch (error) {
    message.error('操作失败')
  }
}

onMounted(() => {
  loadData()
})
</script>
