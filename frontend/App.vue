<script setup>
import { onLaunch, onShow, onHide } from '@dcloudio/uni-app'

onLaunch(() => {
  console.log('App Launch')
})

onShow(() => {
  console.log('App Show')
})

onHide(() => {
  console.log('App Hide')
})
</script>

<style lang="scss">
/* 全局样式 */
page {
  background-color: #f5f5f5;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

/* 自定义主题色 */
:root {
  --primary-color: #2979FF;
  --primary-light: #5C9DFF;
  --primary-dark: #1E5ACC;
  --success-color: #19BE6B;
  --warning-color: #FF9900;
  --error-color: #FA3534;
  --info-color: #909399;
}

/* 通用样式 */
view, text, image, input, textarea, button {
  box-sizing: border-box;
}

button::after {
  border: none;
}
</style>
