<template>
  <div class="page-container">
    <div class="page-header">
      <h1>系统设置</h1>
      <p>配置系统参数和运行环境</p>
    </div>

    <a-row :gutter="[24, 24]">
      <a-col :xs="24" :lg="12">
        <a-card title="基础设置" :bordered="false">
          <a-form :model="basicForm" layout="vertical">
            <a-form-item label="系统名称">
              <a-input v-model:value="basicForm.systemName" placeholder="请输入系统名称" />
            </a-form-item>
            <a-form-item label="系统版本">
              <a-input v-model:value="basicForm.version" disabled />
            </a-form-item>
            <a-form-item label="维护模式">
              <a-switch v-model:checked="basicForm.maintenance" />
              <span style="margin-left: 8px; color: #999">开启后用户将无法使用系统</span>
            </a-form-item>
            <a-form-item>
              <a-button type="primary" @click="saveBasic" :loading="savingBasic">保存设置</a-button>
            </a-form-item>
          </a-form>
        </a-card>
      </a-col>

      <a-col :xs="24" :lg="12">
        <a-card title="AI模型配置" :bordered="false">
          <a-form :model="aiForm" layout="vertical">
            <a-form-item label="默认模型">
              <a-select v-model:value="aiForm.defaultModel" placeholder="请选择默认模型" show-search>
                <a-select-opt-group v-for="group in modelGroups" :key="group.provider" :label="group.provider">
                  <a-select-option v-for="model in group.models" :key="model.id" :value="model.id">
                    {{ model.name }}
                  </a-select-option>
                </a-select-opt-group>
              </a-select>
            </a-form-item>
            <a-form-item label="最大上下文长度">
              <a-input-number v-model:value="aiForm.maxContext" :min="1000" :max="32000" :step="1000" style="width: 100%" />
            </a-form-item>
            <a-form-item label="温度系数 (Temperature)">
              <a-slider v-model:value="aiForm.temperature" :min="0" :max="1" :step="0.1" />
              <span style="color: #999">值越低回复越确定，值越高回复越随机</span>
            </a-form-item>
            <a-form-item>
              <a-button type="primary" @click="saveAI" :loading="savingAI">保存配置</a-button>
            </a-form-item>
          </a-form>
        </a-card>
      </a-col>
    </a-row>

    <!-- 模型说明 -->
    <a-row :gutter="[24, 24]" style="margin-top: 24px">
      <a-col :span="24">
        <a-card title="模型说明" :bordered="false">
          <a-table :columns="modelColumns" :data-source="allModels" :pagination="false" size="small" row-key="id">
            <template #bodyCell="{ column, record }">
              <template v-if="column.key === 'default'">
                <a-tag v-if="record.id === aiForm.defaultModel" color="success">当前默认</a-tag>
              </template>
            </template>
          </a-table>
        </a-card>
      </a-col>
    </a-row>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import request from '@/utils/request'

const savingBasic = ref(false)
const savingAI = ref(false)

const basicForm = reactive({
  systemName: '识界AI',
  version: '1.1.0',
  maintenance: false,
})

const aiForm = reactive({
  defaultModel: 'qwen-plus',
  maxContext: 4000,
  temperature: 0.7,
})

// 所有模型列表
const allModels = ref([])

// 按提供商分组的模型
const modelGroups = computed(() => {
  const groups = {}
  allModels.value.forEach(model => {
    if (!groups[model.provider]) {
      groups[model.provider] = {
        provider: model.provider,
        models: []
      }
    }
    groups[model.provider].models.push(model)
  })
  return Object.values(groups)
})

const modelColumns = [
  { title: '模型ID', dataIndex: 'id', key: 'id', width: 180 },
  { title: '模型名称', dataIndex: 'name', key: 'name' },
  { title: '提供商', dataIndex: 'provider', key: 'provider', width: 120 },
  { title: '默认', key: 'default', width: 100 },
]

// 加载设置
const loadSettings = async () => {
  try {
    // 获取系统设置
    const settingsRes = await request({ url: '/admin/settings', method: 'get' })
    if (settingsRes.success) {
      basicForm.systemName = settingsRes.data.system_name
      basicForm.maintenance = settingsRes.data.maintenance
      aiForm.defaultModel = settingsRes.data.default_model
      aiForm.maxContext = settingsRes.data.max_context
      aiForm.temperature = settingsRes.data.temperature
    }

    // 获取模型列表
    const modelsRes = await request({ url: '/admin/models', method: 'get' })
    if (modelsRes.success) {
      allModels.value = modelsRes.data
    }
  } catch (error) {
    console.error('加载设置失败:', error)
  }
}

// 保存基础设置
const saveBasic = async () => {
  savingBasic.value = true
  try {
    const res = await request({
      url: '/admin/settings/batch',
      method: 'put',
      data: {
        system_name: basicForm.systemName,
        maintenance: basicForm.maintenance ? 'true' : 'false',
      }
    })
    if (res.success) {
      message.success('基础设置已保存')
    }
  } catch (error) {
    message.error('保存失败')
  } finally {
    savingBasic.value = false
  }
}

// 保存AI配置
const saveAI = async () => {
  savingAI.value = true
  try {
    const res = await request({
      url: '/admin/settings/batch',
      method: 'put',
      data: {
        default_model: aiForm.defaultModel,
        max_context: aiForm.maxContext.toString(),
        temperature: aiForm.temperature.toString(),
      }
    })
    if (res.success) {
      message.success('AI配置已保存，将应用到小程序端')
    }
  } catch (error) {
    message.error('保存失败')
  } finally {
    savingAI.value = false
  }
}

onMounted(() => {
  loadSettings()
})
</script>
