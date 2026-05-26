<template>
  <a-layout class="main-layout">
    <!-- 侧边栏 -->
    <a-layout-sider
      v-model:collapsed="collapsed"
      :trigger="null"
      collapsible
      class="sidebar"
      width="240"
    >
      <div class="logo">
        <img src="/logo.svg" alt="logo" v-if="!collapsed" />
        <span class="logo-text" v-if="!collapsed">识界AI后台</span>
        <span class="logo-short" v-else>AI</span>
      </div>
      <a-menu
        v-model:selectedKeys="selectedKeys"
        mode="inline"
        theme="dark"
        :items="menuItems"
        @click="handleMenuClick"
      />
    </a-layout-sider>

    <a-layout>
      <!-- 顶部导航 -->
      <a-layout-header class="header">
        <div class="header-left">
          <menu-unfold-outlined
            v-if="collapsed"
            class="trigger"
            @click="() => (collapsed = !collapsed)"
          />
          <menu-fold-outlined v-else class="trigger" @click="() => (collapsed = !collapsed)" />
          <breadcrumb class="breadcrumb" />
        </div>
        <div class="header-right">
          <a-space size="large">
            <!-- 通知 -->
            <a-dropdown>
              <a-badge :count="notificationCount" class="notification-badge">
                <bell-outlined class="header-icon" />
              </a-badge>
              <template #overlay>
                <a-menu>
                  <a-menu-item v-for="(notif, idx) in notifications" :key="idx">
                    <a-badge :color="notif.color" :text="notif.content" />
                  </a-menu-item>
                  <a-menu-divider v-if="notifications.length > 0" />
                  <a-menu-item @click="$router.push('/feedbacks')">查看全部</a-menu-item>
                </a-menu>
              </template>
            </a-dropdown>

            <!-- 用户菜单 -->
            <a-dropdown>
              <a-space class="user-info">
                <a-avatar :size="32">
                  <template #icon><user-outlined /></template>
                </a-avatar>
                <span class="username">{{ userStore.username || '管理员' }}</span>
                <down-outlined />
              </a-space>
              <template #overlay>
                <a-menu @click="handleUserMenuClick">
                  <a-menu-item key="profile">
                    <user-outlined />
                    个人中心
                  </a-menu-item>
                  <a-menu-item key="settings">
                    <setting-outlined />
                    系统设置
                  </a-menu-item>
                  <a-menu-divider />
                  <a-menu-item key="logout">
                    <logout-outlined />
                    退出登录
                  </a-menu-item>
                </a-menu>
              </template>
            </a-dropdown>
          </a-space>
        </div>
      </a-layout-header>

      <!-- 内容区域 -->
      <a-layout-content class="content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </a-layout-content>

      <!-- 页脚 -->
      <a-layout-footer class="footer">
        识界AI Admin ©2026 Created by 识界AI团队
      </a-layout-footer>
    </a-layout>
  </a-layout>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { message } from 'ant-design-vue'
import Breadcrumb from './Breadcrumb.vue'
import request from '@/utils/request'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const collapsed = ref(false)
const selectedKeys = ref([])

// 通知相关
const notifications = ref([])
const notificationCount = computed(() => notifications.value.length)

// 加载通知
const loadNotifications = async () => {
  try {
    const res = await request({ url: '/admin/notifications', method: 'get', params: { limit: 5 } })
    if (res.success) {
      notifications.value = res.data || []
    }
  } catch (error) {
    console.error('加载通知失败:', error)
  }
}

// 监听路由变化更新选中菜单
watch(
  () => route.path,
  (path) => {
    selectedKeys.value = [path]
  },
  { immediate: true }
)

// 菜单配置
const menuItems = computed(() => [
  {
    key: '/dashboard',
    icon: () => h('DashboardOutlined'),
    label: '数据概览',
  },
  {
    key: '/users',
    icon: () => h('UserOutlined'),
    label: '用户管理',
  },
  {
    key: '/chats',
    icon: () => h('MessageOutlined'),
    label: '对话记录',
  },
  {
    key: '/feedbacks',
    icon: () => h('CommentOutlined'),
    label: '反馈管理',
  },
  {
    key: '/prompts',
    icon: () => h('FileTextOutlined'),
    label: '提示词管理',
  },
  {
    key: '/system',
    icon: () => h('SettingOutlined'),
    label: '系统设置',
  },
])

// 菜单点击
const handleMenuClick = ({ key }) => {
  router.push(key)
}

// 用户菜单点击
const handleUserMenuClick = ({ key }) => {
  switch (key) {
    case 'profile':
      router.push('/profile')
      break
    case 'settings':
      router.push('/system')
      break
    case 'logout':
      userStore.logout()
      message.success('已退出登录')
      router.push('/login')
      break
  }
}

// h函数用于渲染图标
import { h } from 'vue'

onMounted(() => {
  loadNotifications()
})
</script>

<style lang="scss" scoped>
.main-layout {
  min-height: 100vh;

  .sidebar {
    background: #001529;

    .logo {
      height: 64px;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 0 16px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);

      img {
        width: 32px;
        height: 32px;
        margin-right: 12px;
      }

      .logo-text {
        color: #fff;
        font-size: 18px;
        font-weight: 600;
      }

      .logo-short {
        color: #fff;
        font-size: 20px;
        font-weight: 700;
      }
    }
  }

  .header {
    background: #fff;
    padding: 0 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);

    .header-left {
      display: flex;
      align-items: center;

      .trigger {
        font-size: 18px;
        cursor: pointer;
        transition: color 0.3s;
        margin-right: 16px;

        &:hover {
          color: #1890ff;
        }
      }

      .breadcrumb {
        margin-left: 16px;
      }
    }

    .header-right {
      .notification-badge {
        cursor: pointer;

        .header-icon {
          font-size: 18px;
          color: rgba(0, 0, 0, 0.65);

          &:hover {
            color: #1890ff;
          }
        }
      }

      .user-info {
        cursor: pointer;
        padding: 0 8px;
        border-radius: 4px;
        transition: background 0.3s;

        &:hover {
          background: rgba(0, 0, 0, 0.025);
        }

        .username {
          color: rgba(0, 0, 0, 0.65);
        }
      }
    }
  }

  .content {
    margin: 24px;
    background: #fff;
    border-radius: 8px;
    min-height: calc(100vh - 184px);
    overflow: auto;
  }

  .footer {
    text-align: center;
    padding: 16px 50px;
    color: rgba(0, 0, 0, 0.45);
  }
}
</style>
