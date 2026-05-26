<template>
  <div class="login-page">
    <div class="login-container">
      <div class="login-header">
        <div class="logo">
          <img src="/logo.svg" alt="logo" />
        </div>
        <h1>识界AI后台管理</h1>
        <p>基于AI技术的智能助手平台</p>
      </div>

      <a-card class="login-card" :bordered="false">
        <a-form
          :model="formState"
          name="login"
          autocomplete="off"
          @finish="handleLogin"
          class="login-form"
        >
          <a-form-item
            name="username"
            :rules="[{ required: true, message: '请输入用户名' }]"
          >
            <a-input
              v-model:value="formState.username"
              size="large"
              placeholder="用户名"
            >
              <template #prefix>
                <user-outlined />
              </template>
            </a-input>
          </a-form-item>

          <a-form-item
            name="password"
            :rules="[{ required: true, message: '请输入密码' }]"
          >
            <a-input-password
              v-model:value="formState.password"
              size="large"
              placeholder="密码"
            >
              <template #prefix>
                <lock-outlined />
              </template>
            </a-input-password>
          </a-form-item>

          <a-form-item>
            <a-button
              type="primary"
              html-type="submit"
              size="large"
              block
              :loading="userStore.loading"
              class="login-btn"
            >
              登录
            </a-button>
          </a-form-item>
        </a-form>

        <div class="login-tips">
          <p>默认管理员账号: admin / admin123</p>
        </div>
      </a-card>
    </div>

    <div class="login-footer">
      <p>© 2026 识界AI. All rights reserved.</p>
    </div>
  </div>
</template>

<script setup>
import { reactive } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const formState = reactive({
  username: '',
  password: '',
})

const handleLogin = async (values) => {
  const result = await userStore.login(values)
  if (result.success) {
    message.success('登录成功')
    router.push('/')
  } else {
    message.error(result.message || '登录失败')
  }
}
</script>

<style lang="scss" scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 24px;

  .login-container {
    width: 100%;
    max-width: 420px;

    .login-header {
      text-align: center;
      margin-bottom: 40px;

      .logo {
        width: 80px;
        height: 80px;
        margin: 0 auto 24px;
        background: #fff;
        border-radius: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);

        img {
          width: 48px;
          height: 48px;
        }
      }

      h1 {
        color: #fff;
        font-size: 28px;
        font-weight: 600;
        margin-bottom: 8px;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
      }

      p {
        color: rgba(255, 255, 255, 0.8);
        font-size: 16px;
      }
    }

    .login-card {
      background: #fff;
      border-radius: 16px;
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);

      .login-form {
        .ant-input-affix-wrapper {
          border-radius: 8px;
        }

        .login-btn {
          border-radius: 8px;
          height: 48px;
          font-size: 16px;
          font-weight: 500;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          border: none;

          &:hover {
            opacity: 0.9;
          }
        }
      }

      .login-tips {
        text-align: center;
        margin-top: 24px;
        padding-top: 24px;
        border-top: 1px solid #f0f0f0;

        p {
          color: #999;
          font-size: 14px;
          margin: 0;
        }
      }
    }
  }

  .login-footer {
    position: absolute;
    bottom: 24px;

    p {
      color: rgba(255, 255, 255, 0.6);
      font-size: 14px;
    }
  }
}
</style>
