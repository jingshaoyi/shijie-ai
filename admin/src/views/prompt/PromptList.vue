<template>
  <div class="page-container">
    <div class="page-header">
      <h1>提示词管理</h1>
      <p>管理AI提示词模板</p>
    </div>

    <a-card :bordered="false">
      <template #extra>
        <a-button type="primary" @click="handleAdd">
          <plus-outlined />
          新增模板
        </a-button>
      </template>
      <a-table
        :columns="columns"
        :data-source="promptList"
        :loading="loading"
        :pagination="pagination"
        @change="handleTableChange"
        row-key="id"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'category'">
            <a-tag :color="getCategoryColor(record.category)">{{ getCategoryName(record.category) }}</a-tag>
          </template>
          <template v-if="column.key === 'is_active'">
            <a-tag :color="record.is_active ? 'success' : 'error'">
              {{ record.is_active ? '启用' : '禁用' }}
            </a-tag>
          </template>
          <template v-if="column.key === 'action'">
            <a-space>
              <a-button type="link" size="small" @click="handleView(record)">查看</a-button>
              <a-button type="link" size="small" @click="handleEdit(record)">编辑</a-button>
              <a-popconfirm title="确定删除该模板?" @confirm="handleDelete(record)">
                <a-button type="link" size="small" danger>删除</a-button>
              </a-popconfirm>
            </a-space>
          </template>
        </template>
      </a-table>
    </a-card>

    <!-- 查看/编辑对话框 -->
    <a-modal
      v-model:open="modalVisible"
      :title="isView ? '查看模板' : (isEdit ? '编辑模板' : '新增模板')"
      @ok="submitForm"
      :confirm-loading="submitting"
      width="700px"
      :ok-text="isView ? '关闭' : '确定'"
      :cancel-text="isView ? '' : '取消'"
      :show-cancel="!isView"
    >
      <a-form :model="form" layout="vertical">
        <a-form-item label="模板标识(template_key)" required>
          <a-input v-model:value="form.template_key" placeholder="如: work_summary_manager" :disabled="isView" />
        </a-form-item>
        <a-form-item label="分类(category)" required>
          <a-select v-model:value="form.category" placeholder="请选择分类" :disabled="isView">
            <a-select-option value="work_summary">工作总结</a-select-option>
            <a-select-option value="science">知识科普</a-select-option>
            <a-select-option value="poetry">诗歌创作</a-select-option>
            <a-select-option value="copywriting">文案生成</a-select-option>
            <a-select-option value="email">邮件撰写</a-select-option>
            <a-select-option value="code">代码相关</a-select-option>
            <a-select-option value="study">学习规划</a-select-option>
            <a-select-option value="product">产品描述</a-select-option>
            <a-select-option value="other">其他</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="子分类(sub_key)">
          <a-input v-model:value="form.sub_key" placeholder="如: manager, technician" :disabled="isView" />
        </a-form-item>
        <a-form-item label="描述">
          <a-input v-model:value="form.description" placeholder="请输入模板描述" :disabled="isView" />
        </a-form-item>
        <a-form-item label="模板内容" required>
          <a-textarea v-model:value="form.template_content" :rows="10" placeholder="请输入提示词内容，支持{变量}格式" :disabled="isView" />
        </a-form-item>
        <a-form-item label="是否启用" v-if="isEdit">
          <a-switch v-model:checked="form.is_active" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { getPromptList, createPrompt, updatePrompt, deletePrompt } from '@/api/prompt'

const loading = ref(false)
const promptList = ref([])
const modalVisible = ref(false)
const submitting = ref(false)
const isEdit = ref(false)
const isView = ref(false)

const form = reactive({
  id: null,
  template_key: '',
  category: '',
  sub_key: '',
  template_content: '',
  description: '',
  is_active: true,
})

const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0,
})

const columns = [
  { title: 'ID', dataIndex: 'id', key: 'id', width: 60 },
  { title: '模板标识', dataIndex: 'template_key', key: 'template_key', width: 180 },
  { title: '分类', dataIndex: 'category', key: 'category', width: 100 },
  { title: '子分类', dataIndex: 'sub_key', key: 'sub_key', width: 100 },
  { title: '描述', dataIndex: 'description', key: 'description', ellipsis: true },
  { title: '状态', dataIndex: 'is_active', key: 'is_active', width: 80 },
  { title: '使用次数', dataIndex: 'usage_count', key: 'usage_count', width: 80 },
  { title: '更新时间', dataIndex: 'updated_at', key: 'updated_at', width: 150 },
  { title: '操作', key: 'action', width: 180 },
]

const getCategoryName = (category) => {
  const map = {
    'work_summary': '工作总结',
    'science': '知识科普',
    'poetry': '诗歌创作',
    'copywriting': '文案生成',
    'email': '邮件撰写',
    'code': '代码相关',
    'study': '学习规划',
    'product': '产品描述',
    'other': '其他',
  }
  return map[category] || category
}

const getCategoryColor = (category) => {
  const map = {
    'work_summary': 'blue',
    'science': 'green',
    'poetry': 'purple',
    'copywriting': 'orange',
    'email': 'cyan',
    'code': 'geekblue',
    'study': 'magenta',
    'product': 'gold',
    'other': 'default',
  }
  return map[category] || 'default'
}

const loadData = async () => {
  loading.value = true
  try {
    const res = await getPromptList({
      page: pagination.current,
      page_size: pagination.pageSize,
    })
    if (res.success) {
      promptList.value = res.data || []
      pagination.total = res.total || 0
    }
  } catch (error) {
    console.error('加载提示词列表失败:', error)
    promptList.value = []
  } finally {
    loading.value = false
  }
}

const handleTableChange = (pag) => {
  pagination.current = pag.current
  pagination.pageSize = pag.pageSize
  loadData()
}

const resetForm = () => {
  form.id = null
  form.template_key = ''
  form.category = ''
  form.sub_key = ''
  form.template_content = ''
  form.description = ''
  form.is_active = true
}

const handleAdd = () => {
  resetForm()
  isEdit.value = false
  isView.value = false
  modalVisible.value = true
}

const handleView = (record) => {
  form.id = record.id
  form.template_key = record.template_key
  form.category = record.category
  form.sub_key = record.sub_key || ''
  form.template_content = record.template_content || record.template_content_preview || ''
  form.description = record.description || ''
  form.is_active = record.is_active
  isEdit.value = false
  isView.value = true
  modalVisible.value = true
}

const handleEdit = (record) => {
  form.id = record.id
  form.template_key = record.template_key
  form.category = record.category
  form.sub_key = record.sub_key || ''
  form.template_content = record.template_content || record.template_content_preview || ''
  form.description = record.description || ''
  form.is_active = record.is_active
  isEdit.value = true
  isView.value = false
  modalVisible.value = true
}

const submitForm = async () => {
  if (isView.value) {
    modalVisible.value = false
    return
  }

  if (!form.template_key || !form.category || !form.template_content) {
    message.warning('请填写完整信息')
    return
  }

  submitting.value = true
  try {
    let res
    if (isEdit.value) {
      res = await updatePrompt(form.id, {
        template_key: form.template_key,
        category: form.category,
        sub_key: form.sub_key,
        template_content: form.template_content,
        description: form.description,
        is_active: form.is_active ? 1 : 0,
      })
    } else {
      res = await createPrompt({
        template_key: form.template_key,
        category: form.category,
        sub_key: form.sub_key,
        template_content: form.template_content,
        description: form.description,
      })
    }

    if (res.success) {
      message.success(isEdit.value ? '更新成功' : '创建成功')
      modalVisible.value = false
      loadData()
    }
  } catch (error) {
    message.error('操作失败')
  } finally {
    submitting.value = false
  }
}

const handleDelete = async (record) => {
  try {
    const res = await deletePrompt(record.id)
    if (res.success) {
      message.success('删除成功')
      loadData()
    }
  } catch (error) {
    message.error('删除失败')
  }
}

onMounted(() => {
  loadData()
})
</script>
