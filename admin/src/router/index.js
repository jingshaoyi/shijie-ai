import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login/LoginView.vue'),
    meta: { public: true },
  },
  {
    path: '/',
    name: 'Layout',
    component: () => import('@/components/Layout/MainLayout.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/DashboardView.vue'),
        meta: { title: '数据概览', icon: 'DashboardOutlined' },
      },
      {
        path: 'users',
        name: 'Users',
        component: () => import('@/views/user/UserList.vue'),
        meta: { title: '用户管理', icon: 'UserOutlined' },
      },
      {
        path: 'chats',
        name: 'Chats',
        component: () => import('@/views/chat/ChatList.vue'),
        meta: { title: '对话记录', icon: 'MessageOutlined' },
      },
      {
        path: 'feedbacks',
        name: 'Feedbacks',
        component: () => import('@/views/feedback/FeedbackList.vue'),
        meta: { title: '反馈管理', icon: 'CommentOutlined' },
      },
      {
        path: 'prompts',
        name: 'Prompts',
        component: () => import('@/views/prompt/PromptList.vue'),
        meta: { title: '提示词管理', icon: 'FileTextOutlined' },
      },
      {
        path: 'system',
        name: 'System',
        component: () => import('@/views/system/SystemSettings.vue'),
        meta: { title: '系统设置', icon: 'SettingOutlined' },
      },
    ],
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()

  if (!to.meta.public && !userStore.token) {
    next('/login')
  } else if (to.path === '/login' && userStore.token) {
    next('/')
  } else {
    next()
  }
})

export default router
