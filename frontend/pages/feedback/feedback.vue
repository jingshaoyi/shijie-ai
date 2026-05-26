<template>
  <view class="container">
    <!-- 自定义导航栏 -->
    <view class="custom-nav">
      <view class="nav-left" @click="goBack">
        <text class="icon-text">←</text>
      </view>
      <view class="nav-title">意见反馈</view>
      <view class="nav-right"></view>
    </view>

    <!-- 反馈类型选择 -->
    <view class="form-section">
      <view class="section-label">
        <text class="label-icon">🏷️</text>
        反馈类型
      </view>
      <view class="type-list">
        <view
          class="type-item"
          v-for="(item, index) in feedbackTypes"
          :key="index"
          :class="{ active: selectedType === item.value }"
          @click="selectedType = item.value"
        >
          <text class="type-icon">{{ item.icon }}</text>
          <text class="type-text">{{ item.label }}</text>
        </view>
      </view>
    </view>

    <!-- 反馈内容 -->
    <view class="form-section">
      <view class="section-label">
        <text class="label-icon">📝</text>
        反馈内容
      </view>
      <view class="textarea-wrapper">
        <textarea
          class="feedback-textarea"
          v-model="feedbackContent"
          placeholder="请详细描述您遇到的问题或建议，我们会认真阅读每一条反馈..."
          :maxlength="500"
          @input="onContentInput"
        />
        <view class="char-count">{{ contentLength }}/500</view>
      </view>
    </view>

    <!-- 联系方式 -->
    <view class="form-section">
      <view class="section-label">
        <text class="label-icon">📧</text>
        联系方式（选填）
      </view>
      <input
        class="contact-input"
        v-model="contactInfo"
        placeholder="手机号/邮箱/微信，方便我们联系您"
        maxlength="50"
      />
    </view>

    <!-- 图片上传 -->
    <view class="form-section">
      <view class="section-label">
        <text class="label-icon">📷</text>
        截图（选填，最多3张）
      </view>
      <view class="image-upload-list">
        <view 
          class="upload-item" 
          v-for="(img, index) in uploadedImages" 
          :key="index"
        >
          <image :src="img" mode="aspectFill" class="uploaded-img"></image>
          <view class="remove-btn" @click="removeImage(index)">
            <text class="remove-icon">✕</text>
          </view>
        </view>
        <view class="upload-btn" @click="chooseImage" v-if="uploadedImages.length < 3">
          <text class="upload-icon">+</text>
          <text class="upload-text">添加图片</text>
        </view>
      </view>
    </view>

    <!-- 提交按钮 -->
    <view class="submit-section">
      <view 
        class="submit-btn" 
        :class="{ active: canSubmit, loading: isSubmitting }"
        @click="submitFeedback"
      >
        <text v-if="!isSubmitting">提交反馈</text>
        <view class="btn-spinner" v-else></view>
      </view>
    </view>

    <!-- 成功提示 -->
    <view class="success-modal" v-if="showSuccess">
      <view class="modal-content">
        <view class="success-icon">✓</view>
        <view class="success-title">提交成功</view>
        <view class="success-desc">感谢您的反馈，我们会尽快处理</view>
        <view class="confirm-btn" @click="closeSuccess">确定</view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { submitFeedback as submitFeedbackApi } from '@/api/user.js'
import { uploadImage } from '@/api/cloud.js'
import { isLoggedIn } from '@/api/user.js'

const feedbackTypes = [
  { label: '功能建议', value: 'feature', icon: '💡' },
  { label: '问题反馈', value: 'bug', icon: '🐛' },
  { label: '使用体验', value: 'experience', icon: '😊' },
  { label: '其他', value: 'other', icon: '📝' }
]

const selectedType = ref('feature')
const feedbackContent = ref('')
const contactInfo = ref('')
const uploadedImages = ref([])
const isSubmitting = ref(false)
const showSuccess = ref(false)

const contentLength = computed(() => feedbackContent.value.length)

const canSubmit = computed(() => {
  return feedbackContent.value.trim().length >= 10 && !isSubmitting.value
})

const goBack = () => {
  uni.navigateBack()
}

const onContentInput = () => {
  // 输入时触发
}

const chooseImage = () => {
  const remainCount = 3 - uploadedImages.value.length
  uni.chooseMedia({
    count: remainCount,
    mediaType: ['image'],
    sourceType: ['album', 'camera'],
    success: (res) => {
      const tempFiles = res.tempFiles || []
      tempFiles.forEach(file => {
        if (uploadedImages.value.length < 3) {
          uploadedImages.value.push(file.tempFilePath)
        }
      })
    }
  })
}

const removeImage = (index) => {
  uploadedImages.value.splice(index, 1)
}

const submitFeedback = async () => {
  if (!isLoggedIn()) {
    uni.showModal({
      title: '提示',
      content: '请先登录后再提交反馈',
      showCancel: false,
      success: () => { uni.reLaunch({ url: '/pages/login/login' }) }
    })
    return
  }

  if (!canSubmit.value) {
    uni.showToast({ title: '请至少输入10个字符', icon: 'none' })
    return
  }

  isSubmitting.value = true
  uni.showLoading({ title: '提交中...', mask: true })

  try {
    // 上传图片
    let imageUrls = []
    if (uploadedImages.value.length > 0) {
      const uploadPromises = uploadedImages.value.map(path => uploadImage(path))
      imageUrls = await Promise.all(uploadPromises)
    }

    // 提交反馈
    await submitFeedbackApi({
      type: selectedType.value,
      content: feedbackContent.value.trim(),
      contact: contactInfo.value.trim(),
      images: imageUrls
    })

    uni.hideLoading()
    showSuccess.value = true
  } catch (error) {
    uni.hideLoading()
    uni.showToast({ title: error.message || '提交失败', icon: 'none' })
  } finally {
    isSubmitting.value = false
  }
}

const closeSuccess = () => {
  showSuccess.value = false
  uni.navigateBack()
}
</script>

<style lang="scss" scoped>
.container {
  min-height: 100vh;
  background: linear-gradient(180deg, #f8faff 0%, #f5f5f5 100%);
}

/* 导航栏 */
.custom-nav {
  height: 88rpx;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10rpx);
  padding: 0 30rpx;
  box-shadow: 0 2rpx 20rpx rgba(0, 0, 0, 0.05);

  .nav-left {
    width: 60rpx;
    .icon-text { font-size: 40rpx; color: #333; }
  }

  .nav-title {
    font-size: 36rpx;
    font-weight: 600;
    color: #333;
  }

  .nav-right { width: 60rpx; }
}

/* 表单区域 */
.form-section {
  padding: 30rpx;
  background: #fff;
  margin-bottom: 20rpx;

  .section-label {
    font-size: 30rpx;
    font-weight: 600;
    color: #333;
    margin-bottom: 20rpx;
    display: flex;
    align-items: center;

    .label-icon {
      margin-right: 12rpx;
      font-size: 32rpx;
    }
  }
}

/* 反馈类型 */
.type-list {
  display: flex;
  flex-wrap: wrap;
  gap: 20rpx;

  .type-item {
    display: flex;
    align-items: center;
    padding: 20rpx 32rpx;
    background: #f5f7fa;
    border-radius: 16rpx;
    transition: all 0.3s ease;

    &.active {
      background: linear-gradient(135deg, #2979FF, #5C9DFF);
      box-shadow: 0 4rpx 20rpx rgba(41, 121, 255, 0.3);

      .type-icon, .type-text {
        color: #fff;
      }
    }

    &:active:not(.active) {
      transform: scale(0.95);
    }

    .type-icon {
      font-size: 32rpx;
      margin-right: 12rpx;
    }

    .type-text {
      font-size: 28rpx;
      color: #666;
    }
  }
}

/* 文本输入 */
.textarea-wrapper {
  position: relative;

  .feedback-textarea {
    width: 100%;
    height: 300rpx;
    background: #f8f9fa;
    border-radius: 16rpx;
    padding: 24rpx;
    font-size: 28rpx;
    color: #333;
    line-height: 1.6;
    box-sizing: border-box;
  }

  .char-count {
    position: absolute;
    bottom: 16rpx;
    right: 20rpx;
    font-size: 24rpx;
    color: #999;
  }
}

/* 联系方式 */
.contact-input {
  width: 100%;
  height: 88rpx;
  background: #f8f9fa;
  border-radius: 16rpx;
  padding: 0 24rpx;
  font-size: 28rpx;
  color: #333;
  box-sizing: border-box;
}

/* 图片上传 */
.image-upload-list {
  display: flex;
  flex-wrap: wrap;
  gap: 20rpx;

  .upload-item {
    position: relative;
    width: 200rpx;
    height: 200rpx;
    border-radius: 16rpx;
    overflow: hidden;
    box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.1);

    .uploaded-img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }

    .remove-btn {
      position: absolute;
      top: 8rpx;
      right: 8rpx;
      width: 44rpx;
      height: 44rpx;
      background: rgba(0, 0, 0, 0.5);
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;

      .remove-icon {
        font-size: 24rpx;
        color: #fff;
        font-weight: 600;
      }
    }
  }

  .upload-btn {
    width: 200rpx;
    height: 200rpx;
    border: 2rpx dashed #ddd;
    border-radius: 16rpx;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    transition: all 0.3s ease;

    &:active {
      background: #f5f7fa;
      border-color: #2979FF;
    }

    .upload-icon {
      font-size: 48rpx;
      color: #999;
      margin-bottom: 8rpx;
    }

    .upload-text {
      font-size: 24rpx;
      color: #999;
    }
  }
}

/* 提交按钮 */
.submit-section {
  padding: 40rpx 30rpx;

  .submit-btn {
    background: linear-gradient(135deg, #e0e5ec 0%, #d1d9e6 100%);
    border-radius: 50rpx;
    height: 96rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 32rpx;
    color: #999;
    font-weight: 600;
    transition: all 0.3s ease;
    box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.08);

    &.active {
      background: linear-gradient(135deg, #2979FF 0%, #5C9DFF 100%);
      color: #fff;
      box-shadow: 0 8rpx 30rpx rgba(41, 121, 255, 0.3);

      &:active {
        transform: scale(0.98);
      }
    }

    &.loading {
      background: linear-gradient(135deg, #2979FF 0%, #5C9DFF 100%);
    }

    .btn-spinner {
      width: 40rpx;
      height: 40rpx;
      border: 4rpx solid rgba(255, 255, 255, 0.3);
      border-top-color: #fff;
      border-radius: 50%;
      animation: spin 0.8s linear infinite;
    }
  }
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 成功弹窗 */
.success-modal {
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

  .modal-content {
    background: #fff;
    border-radius: 24rpx;
    padding: 60rpx 80rpx;
    text-align: center;
    animation: modal-pop 0.3s ease;

    .success-icon {
      width: 120rpx;
      height: 120rpx;
      background: linear-gradient(135deg, #19BE6B, #4CD964);
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 60rpx;
      color: #fff;
      margin: 0 auto 30rpx;
    }

    .success-title {
      font-size: 36rpx;
      font-weight: 600;
      color: #333;
      margin-bottom: 16rpx;
    }

    .success-desc {
      font-size: 28rpx;
      color: #999;
      margin-bottom: 40rpx;
    }

    .confirm-btn {
      background: linear-gradient(135deg, #2979FF, #5C9DFF);
      color: #fff;
      font-size: 30rpx;
      padding: 24rpx 80rpx;
      border-radius: 50rpx;
      font-weight: 600;

      &:active {
        transform: scale(0.95);
      }
    }
  }
}

@keyframes modal-pop {
  from {
    opacity: 0;
    transform: scale(0.8);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}
</style>
