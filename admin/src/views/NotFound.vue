<template>
  <div class="not-found">
    <div class="content">
      <h1>404</h1>
      <p>抱歉，您访问的页面不存在</p>
      <a-button type="primary" @click="$router.push('/')">返回首页</a-button>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.not-found {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f0f2f5;

  .content {
    text-align: center;

    h1 {
      font-size: 120px;
      font-weight: 700;
      color: #1890ff;
      margin-bottom: 24px;
      line-height: 1;
    }

    p {
      font-size: 18px;
      color: #666;
      margin-bottom: 32px;
    }
  }
}
</style>
