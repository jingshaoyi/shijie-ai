<template>
  <view class="custom-tabbar" :class="{ 'safe-area': hasSafeArea }">
    <view
      class="tabbar-item"
      v-for="(item, index) in tabList"
      :key="index"
      :class="{ active: currentIndex === index }"
      @tap="switchTab(index)"
    >
      <view class="tabbar-icon-wrap">
        <view v-if="item.key === 'home'" class="icon-wrap">
          <!-- 首页图标 - 可爱房子 -->
          <view class="icon-home" :class="{ active: currentIndex === index }">
            <view class="house-body">
              <view class="house-window"></view>
              <view class="house-door"></view>
            </view>
            <view class="house-roof">
              <view class="chimney"></view>
            </view>
          </view>
        </view>
        <view v-else-if="item.key === 'chat'" class="icon-wrap">
          <!-- 对话图标 - 可爱气泡 -->
          <view class="icon-chat" :class="{ active: currentIndex === index }">
            <view class="chat-bubble">
              <view class="bubble-face">
                <view class="eye left"></view>
                <view class="eye right"></view>
                <view class="mouth"></view>
              </view>
            </view>
          </view>
        </view>
        <view v-else-if="item.key === 'history'" class="icon-wrap">
          <!-- 记录图标 - 可爱时钟 -->
          <view class="icon-clock" :class="{ active: currentIndex === index }">
            <view class="clock-body">
              <view class="clock-face">
                <view class="clock-hand hour"></view>
                <view class="clock-hand minute"></view>
                <view class="clock-center"></view>
              </view>
            </view>
          </view>
        </view>
        <view v-else-if="item.key === 'user'" class="icon-wrap">
          <!-- 我的图标 - 可爱小人 -->
          <view class="icon-user" :class="{ active: currentIndex === index }">
            <view class="user-body">
              <view class="user-head">
                <view class="face">
                  <view class="eye left"></view>
                  <view class="eye right"></view>
                  <view class="smile"></view>
                </view>
              </view>
            </view>
          </view>
        </view>
      </view>
      <text class="tabbar-label">{{ item.text }}</text>
      <!-- 活跃指示器 -->
      <view class="active-indicator" v-if="currentIndex === index"></view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  current: {
    type: Number,
    default: 0
  }
})

const hasSafeArea = ref(false)

// 隐藏原生 tabBar
uni.hideTabBar({ animation: false })

uni.getWindowInfo({
  success: (res) => {
    hasSafeArea.value = !!(res.safeAreaInsets && res.safeAreaInsets.bottom > 0)
  }
})

const currentIndex = computed(() => props.current)

const tabList = ref([
  { key: 'home', text: '首页', pagePath: '/pages/index/index' },
  { key: 'chat', text: '对话', pagePath: '/pages/chat/chat' },
  { key: 'history', text: '记录', pagePath: '/pages/history/history' },
  { key: 'user', text: '我的', pagePath: '/pages/user/user' }
])

const switchTab = (index) => {
  if (currentIndex.value === index) return
  uni.switchTab({ url: tabList.value[index].pagePath })
}
</script>

<style lang="scss" scoped>
$tab-height: 100rpx;
$icon-size: 52rpx;
$color-normal: #b0b0b0;
$color-active: #2979FF;
$safe-bottom: env(safe-area-inset-bottom);

.custom-tabbar {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  height: $tab-height;
  background: linear-gradient(180deg, #ffffff 0%, #fafbff 100%);
  display: flex;
  align-items: center;
  justify-content: space-around;
  border-top: 1rpx solid rgba(41, 121, 255, 0.08);
  box-shadow: 0 -4rpx 20rpx rgba(0, 0, 0, 0.04);
  z-index: 999;
  padding-bottom: 0;

  &.safe-area {
    padding-bottom: $safe-bottom;
    height: calc(#{$tab-height} + #{$safe-bottom});
  }
}

.tabbar-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: $tab-height;
  position: relative;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

  &:active {
    transform: scale(0.92);
  }

  .tabbar-icon-wrap {
    width: $icon-size;
    height: $icon-size;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 6rpx;
    position: relative;
  }

  .tabbar-label {
    font-size: 20rpx;
    color: $color-normal;
    line-height: 1;
    transition: all 0.3s ease;
    font-weight: 500;
  }

  &.active .tabbar-label {
    color: $color-active;
    font-weight: 600;
    transform: scale(1.05);
  }

  /* 活跃指示器 */
  .active-indicator {
    position: absolute;
    bottom: 12rpx;
    width: 20rpx;
    height: 4rpx;
    background: linear-gradient(90deg, #2979FF, #5C9DFF);
    border-radius: 2rpx;
    animation: indicator-appear 0.3s ease;
  }
}

@keyframes indicator-appear {
  from {
    transform: scaleX(0);
    opacity: 0;
  }
  to {
    transform: scaleX(1);
    opacity: 1;
  }
}

/* ===== 图标通用 ===== */
.icon-wrap {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

/* ===== 首页图标 - 可爱房子 ===== */
.icon-home {
  position: relative;
  width: 44rpx;
  height: 40rpx;

  .house-body {
    position: absolute;
    bottom: 0;
    left: 50%;
    transform: translateX(-50%);
    width: 36rpx;
    height: 24rpx;
    background: $color-normal;
    border-radius: 4rpx;
    transition: all 0.3s ease;

    .house-window {
      position: absolute;
      top: 6rpx;
      left: 6rpx;
      width: 10rpx;
      height: 8rpx;
      background: rgba(255, 255, 255, 0.6);
      border-radius: 2rpx;
    }

    .house-door {
      position: absolute;
      bottom: 0;
      right: 6rpx;
      width: 8rpx;
      height: 12rpx;
      background: rgba(255, 255, 255, 0.4);
      border-radius: 4rpx 4rpx 0 0;
    }
  }

  .house-roof {
    position: absolute;
    top: 0;
    left: 50%;
    transform: translateX(-50%);
    width: 0;
    height: 0;
    border-left: 22rpx solid transparent;
    border-right: 22rpx solid transparent;
    border-bottom: 18rpx solid $color-normal;
    transition: all 0.3s ease;

    .chimney {
      position: absolute;
      top: 6rpx;
      right: -8rpx;
      width: 6rpx;
      height: 10rpx;
      background: $color-normal;
      border-radius: 2rpx;
      transition: all 0.3s ease;
    }
  }

  &.active {
    animation: house-bounce 0.4s ease;

    .house-body {
      background: $color-active;
      box-shadow: 0 4rpx 12rpx rgba(41, 121, 255, 0.3);
    }

    .house-roof {
      border-bottom-color: $color-active;

      .chimney {
        background: $color-active;
      }
    }
  }
}

@keyframes house-bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-4rpx); }
}

/* ===== 对话图标 - 可爱气泡 ===== */
.icon-chat {
  position: relative;
  width: 44rpx;
  height: 40rpx;

  .chat-bubble {
    position: absolute;
    top: 2rpx;
    left: 50%;
    transform: translateX(-50%);
    width: 40rpx;
    height: 32rpx;
    background: $color-normal;
    border-radius: 16rpx 16rpx 16rpx 4rpx;
    transition: all 0.3s ease;

    &::after {
      content: '';
      position: absolute;
      bottom: -6rpx;
      left: 4rpx;
      width: 0;
      height: 0;
      border-left: 6rpx solid transparent;
      border-right: 6rpx solid transparent;
      border-top: 8rpx solid $color-normal;
      transition: all 0.3s ease;
    }

    .bubble-face {
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      width: 24rpx;
      height: 16rpx;

      .eye {
        position: absolute;
        top: 2rpx;
        width: 5rpx;
        height: 5rpx;
        background: rgba(255, 255, 255, 0.9);
        border-radius: 50%;
        animation: eye-blink 3s infinite;

        &.left { left: 2rpx; }
        &.right { right: 2rpx; }
      }

      .mouth {
        position: absolute;
        bottom: 2rpx;
        left: 50%;
        transform: translateX(-50%);
        width: 10rpx;
        height: 5rpx;
        background: rgba(255, 255, 255, 0.9);
        border-radius: 0 0 10rpx 10rpx;
      }
    }
  }

  &.active {
    animation: bubble-wiggle 0.4s ease;

    .chat-bubble {
      background: $color-active;
      box-shadow: 0 4rpx 12rpx rgba(41, 121, 255, 0.3);

      &::after {
        border-top-color: $color-active;
      }

      .bubble-face {
        .eye {
          animation: eye-blink-active 2s infinite;
        }
      }
    }
  }
}

@keyframes bubble-wiggle {
  0%, 100% { transform: rotate(0); }
  25% { transform: rotate(-5deg); }
  75% { transform: rotate(5deg); }
}

@keyframes eye-blink {
  0%, 45%, 55%, 100% { transform: scaleY(1); }
  50% { transform: scaleY(0.1); }
}

@keyframes eye-blink-active {
  0%, 40%, 60%, 100% { transform: scaleY(1); }
  50% { transform: scaleY(0.1); }
}

/* ===== 时钟图标 - 可爱时钟 ===== */
.icon-clock {
  position: relative;
  width: 44rpx;
  height: 40rpx;

  .clock-body {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 38rpx;
    height: 38rpx;
    background: $color-normal;
    border-radius: 50%;
    transition: all 0.3s ease;

    .clock-face {
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      width: 30rpx;
      height: 30rpx;
      background: #fff;
      border-radius: 50%;

      .clock-hand {
        position: absolute;
        top: 50%;
        left: 50%;
        transform-origin: bottom center;
        background: $color-normal;
        border-radius: 2rpx;
        transition: all 0.3s ease;

        &.hour {
          width: 3rpx;
          height: 8rpx;
          transform: translateX(-50%) translateY(-100%) rotate(45deg);
        }

        &.minute {
          width: 2rpx;
          height: 11rpx;
          transform: translateX(-50%) translateY(-100%) rotate(-30deg);
          animation: clock-tick 2s linear infinite;
        }
      }

      .clock-center {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 5rpx;
        height: 5rpx;
        background: $color-normal;
        border-radius: 50%;
        transition: all 0.3s ease;
      }
    }
  }

  &.active {
    animation: clock-spin 0.5s ease;

    .clock-body {
      background: $color-active;
      box-shadow: 0 4rpx 12rpx rgba(41, 121, 255, 0.3);

      .clock-face {
        .clock-hand {
          background: $color-active;
        }

        .clock-center {
          background: $color-active;
        }
      }
    }
  }
}

@keyframes clock-spin {
  0% { transform: rotate(0); }
  100% { transform: rotate(360deg); }
}

@keyframes clock-tick {
  0% { transform: translateX(-50%) translateY(-100%) rotate(-30deg); }
  100% { transform: translateX(-50%) translateY(-100%) rotate(330deg); }
}

/* ===== 用户图标 - 可爱小人 ===== */
.icon-user {
  position: relative;
  width: 44rpx;
  height: 40rpx;

  .user-body {
    position: absolute;
    bottom: 0;
    left: 50%;
    transform: translateX(-50%);
    width: 28rpx;
    height: 16rpx;
    background: $color-normal;
    border-radius: 14rpx 14rpx 8rpx 8rpx;
    transition: all 0.3s ease;

    .user-head {
      position: absolute;
      top: -14rpx;
      left: 50%;
      transform: translateX(-50%);
      width: 22rpx;
      height: 22rpx;
      background: $color-normal;
      border-radius: 50%;
      transition: all 0.3s ease;

      .face {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 16rpx;
        height: 12rpx;

        .eye {
          position: absolute;
          top: 3rpx;
          width: 3rpx;
          height: 3rpx;
          background: rgba(255, 255, 255, 0.9);
          border-radius: 50%;
          animation: user-eye-blink 4s infinite;

          &.left { left: 2rpx; }
          &.right { right: 2rpx; }
        }

        .smile {
          position: absolute;
          bottom: 2rpx;
          left: 50%;
          transform: translateX(-50%);
          width: 8rpx;
          height: 4rpx;
          border-bottom: 2rpx solid rgba(255, 255, 255, 0.9);
          border-radius: 0 0 8rpx 8rpx;
        }
      }
    }
  }

  &.active {
    animation: user-bounce 0.4s ease;

    .user-body {
      background: $color-active;
      box-shadow: 0 4rpx 12rpx rgba(41, 121, 255, 0.3);

      .user-head {
        background: $color-active;

        .face {
          .eye {
            animation: user-eye-blink-active 2s infinite;
          }
        }
      }
    }
  }
}

@keyframes user-bounce {
  0%, 100% { transform: translateY(0) scale(1); }
  50% { transform: translateY(-4rpx) scale(1.05); }
}

@keyframes user-eye-blink {
  0%, 45%, 55%, 100% { transform: scaleY(1); }
  50% { transform: scaleY(0.1); }
}

@keyframes user-eye-blink-active {
  0%, 40%, 60%, 100% { transform: scaleY(1); }
  50% { transform: scaleY(0.1); }
}
</style>
