# 识界AI 管理员后台

基于 Vue 3 + Ant Design Vue 构建的管理员后台系统。

## 技术栈

- **框架**: Vue 3 (Composition API)
- **UI组件库**: Ant Design Vue 4.x
- **状态管理**: Pinia
- **路由**: Vue Router 4
- **构建工具**: Vite 5
- **图表**: ECharts 5
- **HTTP客户端**: Axios

## 功能模块

- 📊 **数据概览** - 实时监控系统运行状态、用户增长趋势、模型使用分布
- 👥 **用户管理** - 查看用户信息、管理用户状态
- 💬 **对话记录** - 查看用户对话历史，支持拖拽缩放弹窗，显示Token消耗和文本字数统计
- 💭 **反馈管理** - 处理用户反馈和建议
- 📝 **提示词管理** - 管理AI提示词模板
- ⚙️ **系统设置** - 配置系统参数和AI模型，支持配置默认AI模型（通义千问Plus等14个模型）、系统名称修改保存

## 快速开始

### 安装依赖

```bash
cd admin
npm install
```

### 开发环境运行

```bash
npm run dev
```

### 构建生产环境

```bash
npm run build
```

### 预览生产构建

```bash
npm run preview
```

## 项目结构

```
admin/
├── src/
│   ├── api/           # API接口
│   ├── assets/        # 静态资源
│   ├── components/    # 公共组件
│   ├── router/        # 路由配置
│   ├── stores/        # Pinia状态管理
│   ├── utils/         # 工具函数
│   ├── views/         # 页面视图
│   │   ├── dashboard/ # 数据概览
│   │   ├── user/      # 用户管理
│   │   ├── chat/      # 对话记录
│   │   ├── feedback/  # 反馈管理
│   │   ├── prompt/    # 提示词管理
│   │   ├── system/    # 系统设置
│   │   └── login/     # 登录页
│   ├── App.vue
│   └── main.js
├── index.html
├── package.json
├── vite.config.js
└── README.md
```

## 默认账号

- 用户名: `admin`
- 密码: `admin123`

## API代理配置

在 `vite.config.js` 中配置代理:

```javascript
server: {
  proxy: {
    '/api': {
      // ⚠️ 请将此地址替换为您的后端API地址
      target: 'https://YOUR_BACKEND_DOMAIN',
      changeOrigin: true,
      rewrite: (path) => path.replace(/^\/api/, ''),
    },
  },
}
```

## 浏览器支持

- Chrome >= 90
- Firefox >= 88
- Safari >= 14
- Edge >= 90

## 许可证

MIT
