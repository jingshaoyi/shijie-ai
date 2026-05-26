/**
 * 提示词模板API
 * 提示词模板存储在后端数据库，前端通过API获取
 * 本地仅保留最简备用模板（API不可用时使用）
 * 
 * 注意：部署时请将 API_BASE 替换为您的后端API地址
 */
const API_BASE = 'https://YOUR_BACKEND_DOMAIN/api'

/**
 * 从后端API获取动态提示词（主要方式）
 */
export function generatePrompt(category, variables, subKey = null) {
  return new Promise((resolve, reject) => {
    uni.request({
      url: `${API_BASE}/prompts/generate`,
      method: 'POST',
      header: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${uni.getStorageSync('token') || ''}`
      },
      data: { category, variables, sub_key: subKey },
      success: (res) => {
        if (res.statusCode === 200 && res.data.success) {
          resolve(res.data.prompt)
        } else {
          reject(new Error(res.data.detail || '生成提示词失败'))
        }
      },
      fail: reject
    })
  })
}

/**
 * 获取提示词统计
 */
export function getPromptStats() {
  return new Promise((resolve, reject) => {
    uni.request({
      url: `${API_BASE}/prompts/stats`,
      method: 'GET',
      header: { 'Authorization': `Bearer ${uni.getStorageSync('token') || ''}` },
      success: (res) => {
        if (res.statusCode === 200) resolve(res.data)
        else reject(new Error('获取统计失败'))
      },
      fail: reject
    })
  })
}

/**
 * 初始化默认模板（管理员使用）
 */
export function initializeTemplates() {
  return new Promise((resolve, reject) => {
    uni.request({
      url: `${API_BASE}/prompts/initialize`,
      method: 'POST',
      header: { 'Authorization': `Bearer ${uni.getStorageSync('token') || ''}` },
      success: (res) => {
        if (res.statusCode === 200) resolve(res.data)
        else reject(new Error('初始化失败'))
      },
      fail: reject
    })
  })
}

/**
 * 本地备用模板（仅API不可用时使用）
 */
const FALLBACK_TEMPLATES = {
  work_summary: `你是一位专业的{position}工作顾问。请根据以下信息生成一份{period}工作总结。\n\n写作风格：{style}\n工作内容：\n{content}\n\n要求：\n1. 按照{style}的风格撰写\n2. 包含工作概述、主要成果、存在问题、下阶段计划\n3. 语言专业、条理清晰\n\n请直接输出工作总结内容：`,
  science: `你是一位{category}领域的科普作家。请用{difficulty}的方式解释以下知识：\n\n问题：{question}\n知识领域：{category}\n\n要求：\n1. 用通俗易懂的语言解释复杂概念\n2. 适当使用类比和例子\n3. 内容有趣且准确\n\n请开始科普：`,
  poetry: `你是一位诗人。请创作一首{genre}，风格为{style}。\n\n主题：{theme}\n{requirement}\n\n要求：紧扣主题，语言优美，符合{genre}特点，请为诗歌起一个标题。\n\n请直接输出诗歌内容（含标题）：`,
  copywriting: `请帮我写一篇小红书风格的{type}文案。\n\n产品/主题信息：\n{product_info}\n\n文案风格：{style}\n\n要求：符合小红书风格，适当使用emoji，添加话题标签。\n\n请直接输出文案内容：`,
  email: `请帮我写一封{type}，语气要求：{tone}。\n\n邮件概要：\n{content}\n\n要求：格式规范，语言得体，包含称呼、正文、落款。\n\n请直接输出邮件内容：`,
  code_explain: `你是一位资深{language}开发工程师。请用{depth}的方式解释以下代码：\n\n代码：\n{code}\n\n{question}\n\n要求：概括功能、逐段解释、指出设计模式和优化建议。\n\n请开始解释：`,
  study_plan: `你是一位专业的学习规划师。请帮我制定一份学习计划。\n\n学习目标：{goal}\n学习周期：{period}\n每日时长：{daily_time}\n当前水平：{level}\n补充说明：{extra}\n\n要求：分阶段规划，列出学习内容和资源，设置里程碑。\n\n请直接输出学习计划：`,
  product_desc: `请为以下产品撰写一段{style}风格的描述文案。\n\n产品类型：{type}\n产品信息：\n{product_info}\n\n要求：标题吸引眼球，核心卖点分点描述，有行动引导。\n\n请直接输出产品描述：`
}

/**
 * 替换模板变量
 */
function replaceVariables(template, variables) {
  let result = template
  for (const [key, value] of Object.entries(variables)) {
    result = result.replace(new RegExp(`\\{${key}\\}`, 'g'), value || '')
  }
  return result.replace(/\{[^}]+\}/g, '')
}

/**
 * 本地备用生成（API不可用时）
 */
export function generateLocalPrompt(category, variables) {
  const template = FALLBACK_TEMPLATES[category]
  if (!template) throw new Error(`未找到分类 ${category} 的模板`)
  return replaceVariables(template, variables)
}

/**
 * 获取动态提示词
 * 优先从后端API获取（数据库中有多个模板变体，服务端随机选择）
 * API不可用时回退到本地备用模板
 */
export async function generatePromptWithFallback(category, variables, subKey = null) {
  try {
    return await generatePrompt(category, variables, subKey)
  } catch (error) {
    console.warn('API生成提示词失败，使用本地备用模板:', error)
    return generateLocalPrompt(category, variables)
  }
}
