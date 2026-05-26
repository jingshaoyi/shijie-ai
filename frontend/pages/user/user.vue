<template>
  <view class="container">
    <!-- 动态背景 -->
    <view class="bg-decoration">
      <view class="gradient-orb orb-1"></view>
      <view class="gradient-orb orb-2"></view>
    </view>

    <!-- 状态栏占位 - 适配刘海屏 -->
    <view class="status-bar"></view>

    <!-- 自定义导航栏 -->
    <view class="custom-nav">
      <view class="nav-title">个人中心</view>
    </view>

    <!-- 用户信息卡片 -->
    <view class="user-card">
      <view class="card-bg"></view>
      <view class="user-content">
        <!-- 点击头像区域 -->
        <view class="user-avatar-wrapper" @click="editAvatar">
          <view class="user-avatar">
            <image v-if="userAvatar" :src="userAvatar" mode="aspectFill" class="avatar-img"/>
            <open-data v-else type="userAvatarUrl"></open-data>
            <view class="avatar-ring"></view>
          </view>
          <view class="edit-badge">
            <text class="badge-icon">✏️</text>
          </view>
        </view>
        <!-- 点击名称区域 -->
        <view class="user-info" @click="editNickname">
          <view class="user-name-wrapper">
            <text v-if="userNickname" class="user-name">{{ userNickname }}</text>
            <open-data v-else type="userNickName" class="user-name"></open-data>
          </view>
          <view class="user-badge">
            <text class="badge-icon">🆔</text>
            <text class="user-id">{{ userId }}</text>
            <text class="edit-hint">点击编辑</text>
          </view>
        </view>
      </view>
      <view class="card-shine"></view>
    </view>

    <!-- 统计信息 -->
    <view class="stats-section">
      <view class="stat-item" v-for="(stat, index) in stats" :key="index">
        <view class="stat-value">{{ stat.value }}</view>
        <view class="stat-label">{{ stat.label }}</view>
      </view>
    </view>

    <!-- 功能列表 -->
    <view class="menu-section">
      <view class="menu-group" v-for="(group, gIndex) in menuGroups" :key="gIndex">
        <view
          class="menu-item"
          v-for="(item, index) in group.items"
          :key="index"
          :class="{ 'item-pressed': pressedItem === item.id }"
          @click="handleItemClick(item)"
          @touchstart="pressedItem = item.id"
          @touchend="pressedItem = null"
        >
          <view class="menu-icon" :class="item.iconClass">
            <text class="icon-text">{{ item.icon }}</text>
          </view>
          <text class="menu-text">{{ item.text }}</text>
          <view class="menu-arrow">
            <text class="arrow-icon">›</text>
          </view>
          <view class="item-ripple" v-if="pressedItem === item.id"></view>
        </view>
      </view>
    </view>

    <!-- 版本信息 -->
    <view class="version-info">
      <text class="version-text">识界AI v1.0.0</text>
      <view class="version-dot"></view>
    </view>



    <!-- 编辑头像弹窗 -->
    <view class="modal-overlay" v-if="showAvatarModal" @click="closeAvatarModal">
      <view class="modal-content avatar-modal" :class="{ 'modal-fade': showAvatarModal }" @click.stop>
        <view class="modal-title">设置头像</view>
        <view class="avatar-preview">
          <image v-if="userAvatar" :src="userAvatar" mode="aspectFill" class="preview-avatar-img"/>
          <open-data v-else type="userAvatarUrl" class="preview-avatar"></open-data>
        </view>
        <view class="avatar-tips">使用微信头像或选择新头像</view>
        <!-- 微信官方头像选择按钮 -->
        <button class="avatar-btn wechat-avatar-btn" open-type="chooseAvatar" @chooseavatar="onChooseWechatAvatar">使用微信头像</button>
        <button class="avatar-btn" @click="chooseAvatar">从相册选择</button>
        <view class="modal-buttons">
          <view class="modal-btn confirm" @click="closeAvatarModal">关闭</view>
        </view>
      </view>
    </view>

    <!-- 编辑昵称弹窗（使用微信昵称） -->
    <view class="modal-overlay" v-if="showNicknameModal" @click="closeNicknameModal">
      <view class="modal-content" :class="{ 'modal-fade': showNicknameModal }" @click.stop>
        <view class="modal-title">编辑昵称</view>
        <!-- 微信官方昵称输入 -->
        <input
          type="nickname"
          class="nickname-input"
          v-model="tempNickname"
          placeholder="请输入昵称"
          maxlength="20"
          @blur="onNicknameBlur"
          focus
        />
        <view class="nickname-tips">支持使用微信昵称或自定义</view>
        <view class="modal-buttons">
          <view class="modal-btn cancel" @click="closeNicknameModal">取消</view>
          <view class="modal-btn confirm" @click="saveNickname">保存</view>
        </view>
      </view>
    </view>
    <!-- 自定义TabBar -->
    <custom-tabbar :current="3" />
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { logout as userLogout, updateUserInfo, getUserNickname, getUserAvatar, isLoggedIn, getUserId } from '@/api/user.js'
import { clearAllChatHistory, getChatHistoryList } from '@/api/database.js'
import CustomTabbar from '@/components/custom-tabbar/custom-tabbar.vue'

const pressedItem = ref(null)
const userId = ref('')
const showNicknameModal = ref(false)
const showAvatarModal = ref(false)
const tempNickname = ref('')
const isUserLoggedIn = ref(false)
const userNickname = ref('')
const userAvatar = ref('')

// 刷新用户信息
const refreshUserInfo = () => {
  const userInfo = uni.getStorageSync('userInfo')
  if (userInfo) {
    userNickname.value = userInfo.nickname || userInfo.nickName || ''
    userAvatar.value = userInfo.avatar || userInfo.avatarUrl || ''
  }
}

const stats = ref([
  { value: '0', label: '对话次数' },
  { value: '0', label: '生成文本' },
  { value: '0', label: '使用天数' }
])

const menuGroups = ref([
  {
    items: [
      { id: 'history', icon: '💬', text: '对话历史', iconClass: 'blue', action: 'history' },
      { id: 'clear', icon: '🗑️', text: '清空历史记录', iconClass: 'red', action: 'clear' }
    ]
  },
  {
    items: [
      { id: 'feedback', icon: '📧', text: '意见反馈', iconClass: 'green', action: 'feedback' },
      { id: 'about', icon: 'ℹ️', text: '关于识界AI', iconClass: 'purple', action: 'about' },
      { id: 'privacy', icon: '📜', text: '隐私政策', iconClass: 'orange', action: 'privacy' }
    ]
  },
  {
    items: [
      { id: 'logout', icon: '🚪', text: '退出登录', iconClass: 'gray', action: 'logout' }
    ]
  }
])

const editNickname = () => {
  tempNickname.value = userNickname.value || ''
  showNicknameModal.value = true
}

const editAvatar = () => {
  showAvatarModal.value = true
}

const closeNicknameModal = () => {
  showNicknameModal.value = false
  tempNickname.value = ''
}

const closeAvatarModal = () => {
  showAvatarModal.value = false
}

const saveNickname = async () => {
  if (!tempNickname.value.trim()) {
    uni.showToast({ title: '请输入昵称', icon: 'none' })
    return
  }

  const nickname = tempNickname.value.trim()
  
  // 同步到后端并更新本地存储
  const success = await updateUserInfo({ nickname })
  if (success) {
    // 立即刷新显示
    userNickname.value = nickname
    uni.showToast({ title: '昵称已更新', icon: 'success' })
    closeNicknameModal()
  } else {
    uni.showToast({ title: '保存失败', icon: 'none' })
  }
}

// 微信官方头像选择回调
const onChooseWechatAvatar = async (e) => {
  const avatarUrl = e.detail.avatarUrl
  if (avatarUrl) {
    // 立即更新显示
    userAvatar.value = avatarUrl
    // 同步到后端
    const success = await updateUserInfo({ avatar: avatarUrl })
    if (success) {
      uni.showToast({ title: '头像已更新', icon: 'success' })
    } else {
      uni.showToast({ title: '保存失败', icon: 'none' })
    }
  }
}

// 昵称输入回调（type="nickname" 会自动获取微信昵称）
const onNicknameBlur = (e) => {
  tempNickname.value = e.detail.value
}

const chooseAvatar = () => {
  uni.chooseImage({
    count: 1,
    sizeType: ['compressed'],
    sourceType: ['album', 'camera'],
    success: async (res) => {
      const tempFilePath = res.tempFilePaths[0]
      // 立即更新显示
      userAvatar.value = tempFilePath
      // 同步到后端
      const success = await updateUserInfo({ avatar: tempFilePath })
      if (success) {
        uni.showToast({ title: '头像已更新', icon: 'success' })
      } else {
        uni.showToast({ title: '保存失败', icon: 'none' })
      }
    }
  })
}

const handleItemClick = (item) => {
  switch (item.action) {
    case 'history':
      uni.switchTab({ url: '/pages/history/history' })
      break
    case 'clear':
      clearHistory()
      break
    case 'feedback':
      feedback()
      break
    case 'about':
      about()
      break
    case 'privacy':
      showPrivacy()
      break
    case 'logout':
      handleLogout()
      break
  }
}

const clearHistory = () => {
  uni.showModal({
    title: '确认清空',
    content: '确定要清空所有对话历史吗？此操作不可恢复！',
    success: async (res) => {
      if (res.confirm) {
        const result = await clearAllChatHistory()
        if (result.success) {
          uni.showToast({
            title: `已清空${result.count}条记录`,
            icon: 'success'
          })
        } else {
          uni.showToast({
            title: result.message || '清空失败',
            icon: 'none'
          })
        }
      }
    }
  })
}

const feedback = () => {
  uni.navigateTo({ url: '/pages/feedback/feedback' })
}

const about = () => {
  uni.showModal({
    title: '关于识界AI',
    content: '识界AI v1.0.0\n\n基于人工智能技术的智能助手小程序，提供AI问答对话、文本生成、知识查询、智能翻译等核心服务。\n\n您的对话历史已安全保存在云端，可在任何设备随时访问。',
    showCancel: false
  })
}

const showPrivacy = () => {
  uni.navigateTo({
    url: '/pages/agreement/privacy'
  })
}

const handleLogout = () => {
  uni.showModal({
    title: '确认退出',
    content: '确定要退出登录吗？',
    success: (res) => {
      if (res.confirm) {
        // 清除所有本地存储
        uni.clearStorageSync()
        // 调用退出登录函数
        userLogout()
        uni.showToast({ title: '已退出登录', icon: 'success' })
        setTimeout(() => {
          uni.reLaunch({ url: '/pages/login/login' })
        }, 1500)
      }
    }
  })
}

// 加载用户统计数据
const loadUserStats = async () => {
  try {
    // 获取对话历史统计
    const chatResult = await getChatHistoryList(1, 1000)
    let chatCount = 0
    let textGenCount = 0
    
    if (chatResult.success && chatResult.data) {
      chatCount = chatResult.total || chatResult.data.length
      // 统计生成的文本数量（估算）
      chatResult.data.forEach(chat => {
        if (chat.preview) {
          textGenCount += Math.ceil(chat.preview.length / 100)
        }
      })
    }
    
    // 计算使用天数
    const loginTime = uni.getStorageSync('loginTime')
    let useDays = 1
    if (loginTime) {
      const days = Math.floor((Date.now() - loginTime) / (1000 * 60 * 60 * 24)) + 1
      useDays = Math.max(1, days)
    }
    
    // 更新统计数据
    stats.value = [
      { value: String(chatCount), label: '对话次数' },
      { value: String(textGenCount * 100), label: '生成文本' },
      { value: String(useDays), label: '使用天数' }
    ]
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

onShow(() => {
  // 检查登录状态
  isUserLoggedIn.value = isLoggedIn()
  
  // 刷新用户信息
  refreshUserInfo()
  
  // 获取用户信息
  const userInfo = uni.getStorageSync('userInfo')
  if (userInfo && userInfo.id) {
    userId.value = String(userInfo.id).slice(-8).toUpperCase()
  } else {
    userId.value = 'GUEST'
  }
  
  // 加载统计数据
  loadUserStats()
})
</script>

<style lang="scss" scoped>
.container {
  min-height: 100vh;
  background: linear-gradient(180deg, #f8faff 0%, #f0f5ff 100%);
  position: relative;
  overflow: hidden;
}

/* 状态栏占位 - 适配刘海屏 */
.status-bar {
  height: var(--status-bar-height);
  width: 100%;
}

/* 动态背景 */
.bg-decoration {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  overflow: hidden;

  .gradient-orb {
    position: absolute;
    border-radius: 50%;
    filter: blur(100rpx);
    opacity: 0.3;
    animation: orb-float 10s ease-in-out infinite;
  }

  .orb-1 {
    width: 500rpx;
    height: 500rpx;
    background: linear-gradient(135deg, #2979FF, #5C9DFF);
    top: -200rpx;
    right: -200rpx;
    animation-delay: 0s;
  }

  .orb-2 {
    width: 400rpx;
    height: 400rpx;
    background: linear-gradient(135deg, #9C27B0, #CE93D8);
    bottom: 100rpx;
    left: -150rpx;
    animation-delay: 5s;
  }
}

@keyframes orb-float {
  0%, 100% { transform: translate(0, 0) scale(1); }
  50% { transform: translate(40rpx, -40rpx) scale(1.1); }
}

/* 导航栏 */
.custom-nav {
  height: 88rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  position: relative;
  z-index: 10;

  .nav-title {
    font-size: 36rpx;
    font-weight: 600;
    color: #333;
  }
}

/* 用户卡片 */
.user-card {
  margin: 20rpx 30rpx;
  background: linear-gradient(135deg, #2979FF, #5C9DFF);
  border-radius: 24rpx;
  padding: 40rpx;
  position: relative;
  overflow: hidden;
  box-shadow: 0 20rpx 40rpx rgba(41, 121, 255, 0.2);

  .card-bg {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, transparent 50%);
  }

  .user-content {
    display: flex;
    align-items: center;
    position: relative;
    z-index: 1;
  }

  .user-avatar-wrapper {
    position: relative;
    margin-right: 30rpx;

    .user-avatar {
      width: 120rpx;
      height: 120rpx;
      border-radius: 50%;
      overflow: hidden;
      border: 4rpx solid rgba(255, 255, 255, 0.3);
      position: relative;

      .avatar-img {
        width: 100%;
        height: 100%;
      }

      .avatar-ring {
        position: absolute;
        top: -8rpx;
        left: -8rpx;
        right: -8rpx;
        bottom: -8rpx;
        border: 2rpx solid rgba(255, 255, 255, 0.5);
        border-radius: 50%;
        animation: ring-pulse 2s ease-in-out infinite;
      }
    }

    .edit-badge {
      position: absolute;
      bottom: 0;
      right: 0;
      width: 40rpx;
      height: 40rpx;
      background: #fff;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.1);
      .badge-icon {
        font-size: 20rpx;
      }
    }
  }

  .user-info {
    flex: 1;
    position: relative;

    .user-name {
      display: block;
      font-size: 40rpx;
      font-weight: 600;
      color: #fff;
      margin-bottom: 12rpx;
    }

    .user-badge {
      display: inline-flex;
      align-items: center;
      background: rgba(255, 255, 255, 0.2);
      padding: 8rpx 16rpx;
      border-radius: 20rpx;

      .badge-icon {
        font-size: 24rpx;
        margin-right: 6rpx;
      }

      .user-id {
        font-size: 24rpx;
        color: rgba(255, 255, 255, 0.9);
      }

      .edit-hint {
        font-size: 22rpx;
        color: rgba(255, 255, 255, 0.7);
        margin-left: 12rpx;
        padding-left: 12rpx;
        border-left: 1rpx solid rgba(255, 255, 255, 0.3);
      }
    }
  }

  .card-shine {
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(255,255,255,0.2) 0%, transparent 60%);
    animation: shine-rotate 6s linear infinite;
  }
}

@keyframes ring-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

@keyframes shine-rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 统计信息 */
.stats-section {
  display: flex;
  justify-content: space-around;
  margin: 30rpx;
  padding: 30rpx;
  background: #fff;
  border-radius: 20rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.06);

  .stat-item {
    text-align: center;

    .stat-value {
      font-size: 40rpx;
      font-weight: 700;
      color: #2979FF;
      margin-bottom: 8rpx;
    }

    .stat-label {
      font-size: 24rpx;
      color: #999;
    }
  }
}

/* 菜单区域 */
.menu-section {
  padding: 0 30rpx;
}

.menu-group {
  background: #fff;
  border-radius: 20rpx;
  overflow: hidden;
  margin-bottom: 20rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.06);
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 30rpx;
  border-bottom: 1rpx solid #f5f5f5;
  position: relative;
  overflow: hidden;
  transition: all 0.2s ease;

  &.item-pressed {
    background: #f8faff;
  }

  &:last-child {
    border-bottom: none;
  }

  .menu-icon {
    width: 48rpx;
    height: 48rpx;
    border-radius: 12rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 20rpx;
    transition: transform 0.2s;

    &.blue { background: #f0f5ff; }
    &.red { background: #FFF2F0; }
    &.green { background: #F0FFF4; }
    &.purple { background: #F3E5F5; }
    &.orange { background: #FFF3E0; }
    &.gray { background: #F5F5F5; }

    .icon-text {
      font-size: 28rpx;
    }
  }

  &:active .menu-icon {
    }

  .menu-text {
    flex: 1;
    font-size: 30rpx;
    color: #333;
  }

  .menu-arrow {
    .arrow-icon {
      font-size: 32rpx;
      color: #ccc;
      transition: all 0.2s;
    }
  }

  &:active .arrow-icon {
    color: #2979FF;
    }

  .item-ripple {
    position: absolute;
    top: 50%;
    left: 50%;
    width: 10rpx;
    height: 10rpx;
    background: rgba(41, 121, 255, 0.1);
    border-radius: 50%;
    transform: translate(-50%, -50%);
    animation: ripple-expand 0.6s ease-out;
  }
}

@keyframes ripple-expand {
  to {
    width: 400rpx;
    height: 400rpx;
    opacity: 0;
  }
}

/* 版本信息 */
.version-info {
  text-align: center;
  padding: 40rpx;

  .version-text {
    font-size: 24rpx;
    color: #999;
  }

  .version-dot {
    width: 8rpx;
    height: 8rpx;
    background: #19BE6B;
    border-radius: 50%;
    margin: 16rpx auto 0;
    animation: dot-pulse 2s ease-in-out infinite;
  }
}

@keyframes dot-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* 弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: overlay-fade-in 0.3s ease;
}

@keyframes overlay-fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal-content {
  width: 600rpx;
  background: #fff;
  border-radius: 24rpx;
  padding: 40rpx;
  animation: modal-fade-in 0.4s ease-out;

  &.avatar-modal {
    text-align: center;
  }

  .modal-title {
    font-size: 34rpx;
    font-weight: 600;
    color: #333;
    text-align: center;
    margin-bottom: 30rpx;
  }

  .nickname-input {
    width: 100%;
    height: 88rpx;
    background: #f5f5f5;
    border-radius: 16rpx;
    padding: 0 24rpx;
    font-size: 30rpx;
    color: #333;
    box-sizing: border-box;
    margin-bottom: 30rpx;
  }

  .avatar-preview {
    width: 200rpx;
    height: 200rpx;
    margin: 0 auto 20rpx;
    border-radius: 50%;
    overflow: hidden;
    border: 6rpx solid #f0f5ff;

    .preview-avatar {
      width: 100%;
      height: 100%;
    }

    .preview-avatar-img {
      width: 100%;
      height: 100%;
      border-radius: 50%;
    }
  }

  .avatar-tips {
    font-size: 26rpx;
    color: #999;
    margin-bottom: 20rpx;
  }

  .avatar-btn {
    width: 100%;
    height: 80rpx;
    line-height: 80rpx;
    background: linear-gradient(135deg, #2979FF, #5C9DFF);
    color: #fff;
    border-radius: 40rpx;
    font-size: 30rpx;
    margin-bottom: 20rpx;
    border: none;

    &.wechat-avatar-btn {
      background: linear-gradient(135deg, #07C160, #10B981);
    }

    &::after { border: none; }
  }

  .nickname-tips {
    font-size: 24rpx;
    color: #999;
    text-align: center;
    margin-bottom: 20rpx;
  }

  .modal-buttons {
    display: flex;
    gap: 20rpx;

    .modal-btn {
      flex: 1;
      height: 80rpx;
      border-radius: 40rpx;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 30rpx;
      font-weight: 500;
      transition: all 0.2s ease;

      &.cancel {
        background: #f5f5f5;
        color: #666;

        &:active {
          background: #e0e0e0;
        }
      }

      &.confirm {
        background: linear-gradient(135deg, #2979FF, #5C9DFF);
        color: #fff;

        &:active {
          }
      }
    }
  }
}

@keyframes modal-fade-in {
  from {
    opacity: 0;
    transform: translateY(20rpx);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>