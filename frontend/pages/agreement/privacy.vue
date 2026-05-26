<template>
  <view class="container">
    <!-- 导航栏 -->
    <view class="nav-bar">
      <view class="nav-left" @click="goBack">
        <text class="back-icon">←</text>
      </view>
      <view class="nav-title">隐私政策</view>
      <view class="nav-right"></view>
    </view>

    <!-- 内容区域 -->
    <scroll-view class="content" scroll-y>
      <view class="content-wrapper">
        <view class="policy-header">
          <view class="header-title">隐私政策</view>
          <view class="update-time">更新日期：2026年5月21日</view>
          <view class="effective-time">生效日期：2026年5月21日</view>
        </view>

        <view class="policy-body">
          <view class="section">
            <view class="section-title">一、引言</view>
            <view class="section-content">
              <text class="text">识界AI（以下简称"本小程序"）由识界AI团队（以下简称"我们"）运营。我们深知个人信息对您的重要性，并会尽全力保护您的个人信息安全。我们致力于维持您对我们的信任，恪守以下原则保护您的个人信息：权责一致原则、目的明确原则、选择同意原则、最少够用原则、确保安全原则、主体参与原则、公开透明原则等。</text>
            </view>
          </view>

          <view class="section">
            <view class="section-title">二、我们收集的信息</view>
            <view class="section-content">
              <text class="text">在您使用本小程序服务时，我们可能会收集以下类型的个人信息：</text>
              <text class="text bold">1. 账号信息</text>
              <text class="text">当您使用微信登录时，我们会收集您的微信OpenID、UnionID（如有）、昵称和头像信息，用于创建和管理您的账号。这些信息来源于微信开放平台，我们仅在您授权同意后获取。</text>
              <text class="text bold">2. 对话内容</text>
              <text class="text">您与AI助手的对话内容会被记录并存储，用于提供对话历史查询、上下文连贯对话等服务。您的对话内容是我们提供AI服务所必需的信息。</text>
              <text class="text bold">3. 设备信息</text>
              <text class="text">我们可能会收集您的设备型号、操作系统版本、小程序版本号等信息，用于服务优化和故障排查。</text>
              <text class="text bold">4. 日志信息</text>
              <text class="text">当您使用本小程序时，我们会自动收集您的操作日志信息，包括您访问的页面、操作时间、功能使用记录等，用于改善用户体验和服务质量。</text>
            </view>
          </view>

          <view class="section">
            <view class="section-title">三、我们如何使用收集的信息</view>
            <view class="section-content">
              <text class="text">我们可能将收集到的信息用于以下用途：</text>
              <text class="text">（1）向您提供AI对话、文本生成、智能翻译、知识查询等核心服务功能；</text>
              <text class="text">（2）保存和管理您的对话历史记录，支持您随时查看和回顾；</text>
              <text class="text">（3）优化和改进我们的产品和服务，提升用户体验；</text>
              <text class="text">（4）进行服务安全监测，防范安全风险；</text>
              <text class="text">（5）遵守法律法规的要求，履行法定义务。</text>
              <text class="text">我们承诺不会将您的个人信息用于上述用途以外的任何目的。</text>
            </view>
          </view>

          <view class="section">
            <view class="section-title">四、信息的存储</view>
            <view class="section-content">
              <text class="text bold">1. 存储地点</text>
              <text class="text">您的个人信息存储在中华人民共和国境内的阿里云服务器上。我们不会将您的个人信息传输至境外。</text>
              <text class="text bold">2. 存储期限</text>
              <text class="text">我们仅在为您提供服务所必需的期间内保留您的个人信息。在您注销账号后，我们将在30日内删除或匿名化处理您的个人信息，法律法规另有规定的除外。</text>
              <text class="text bold">3. 安全措施</text>
              <text class="text">我们采用行业标准的安全技术措施保护您的个人信息，包括但不限于：数据加密传输（HTTPS/TLS）、数据加密存储、访问权限控制、安全审计等。</text>
            </view>
          </view>

          <view class="section">
            <view class="section-title">五、信息的共享与披露</view>
            <view class="section-content">
              <text class="text">我们不会向第三方出售、出租或以其他方式共享您的个人信息，但以下情况除外：</text>
              <text class="text">（1）事先获得您的明确同意；</text>
              <text class="text">（2）根据法律法规的要求，或应政府主管部门的强制性要求；</text>
              <text class="text">（3）为维护我们、其他用户或公众的合法权益免受损害而合理必要；</text>
              <text class="text">（4）与我们的关联公司共享，但仅限于本政策所述的目的，且关联公司需遵守同等的个人信息保护义务。</text>
              <text class="text">我们与AI服务提供商（阿里云百炼平台）共享您的对话内容，仅用于提供AI对话服务。该服务提供商已签署严格的数据保密协议，不会将您的数据用于其他目的。</text>
            </view>
          </view>

          <view class="section">
            <view class="section-title">六、您的权利</view>
            <view class="section-content">
              <text class="text">根据相关法律法规，您享有以下权利：</text>
              <text class="text bold">1. 访问权</text>
              <text class="text">您可以在"个人中心"页面查看和访问您的个人信息。</text>
              <text class="text bold">2. 更正权</text>
              <text class="text">如发现您的个人信息有误，您可以联系我们进行更正。</text>
              <text class="text bold">3. 删除权</text>
              <text class="text">您可以在"个人中心"中清空对话历史记录。如需注销账号并删除全部个人信息，请通过本政策底部提供的联系方式与我们联系。</text>
              <text class="text bold">4. 撤回同意权</text>
              <text class="text">您可以在系统设置中关闭小程序的授权，或通过我们撤回您的授权同意。撤回同意不影响此前基于您同意的处理活动。</text>
              <text class="text bold">5. 投诉举报权</text>
              <text class="text">如您认为我们处理个人信息的方式损害了您的合法权益，您可以向网信部门或其他监管部门进行投诉举报。</text>
            </view>
          </view>

          <view class="section">
            <view class="section-title">七、未成年人保护</view>
            <view class="section-content">
              <text class="text">本小程序的产品和服务主要面向成年人。如果您是未满18周岁的未成年人，请在监护人的陪同和指导下使用本小程序，并在监护人明确同意后向我们提供您的个人信息。</text>
              <text class="text">我们高度重视未成年人的个人信息保护。如我们发现在事先未获得监护人同意的情况下收集了未成年人的个人信息，我们将尽快删除相关信息。</text>
            </view>
          </view>

          <view class="section">
            <view class="section-title">八、隐私政策的更新</view>
            <view class="section-content">
              <text class="text">我们可能会不时更新本隐私政策。当政策发生重大变更时，我们会在小程序内以弹窗通知或显著位置提示的方式告知您。若您在政策更新后继续使用本小程序，即视为您同意受更新后的政策约束。</text>
              <text class="text">建议您定期查阅本隐私政策，以了解我们如何保护您的个人信息。</text>
            </view>
          </view>

          <view class="section">
            <view class="section-title">九、联系我们</view>
            <view class="section-content">
              <text class="text">如您对本隐私政策有任何疑问、意见或建议，您可以通过以下方式与我们联系：</text>
              <text class="text">电子邮件：majic_jing@163.com</text>
              <text class="text">我们将在收到您的请求后5个工作日内予以回复。</text>
            </view>
          </view>
        </view>

        <view class="policy-footer">
          <text class="footer-text">识界AI团队</text>
          <text class="footer-text">© 2026 识界AI 版权所有</text>
        </view>
      </view>

      <view class="bottom-space"></view>
    </scroll-view>
  </view>
</template>

<script setup>
const goBack = () => {
  uni.navigateBack()
}
</script>

<style lang="scss" scoped>
.container {
  min-height: 100vh;
  background: linear-gradient(180deg, #f8faff 0%, #f0f5ff 100%);
}

.nav-bar {
  height: 88rpx;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10rpx);
  padding: 0 30rpx;
  box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.05);
  position: sticky;
  top: 0;
  z-index: 100;

  .nav-left {
    width: 60rpx;

    .back-icon {
      font-size: 40rpx;
      color: #333;
    }
  }

  .nav-title {
    font-size: 34rpx;
    font-weight: 600;
    color: #333;
  }

  .nav-right {
    width: 60rpx;
  }
}

.content {
  height: calc(100vh - 88rpx);
}

.content-wrapper {
  max-width: 750rpx;
  margin: 0 auto;
  padding: 30rpx;
}

.policy-header {
  background: #fff;
  border-radius: 20rpx;
  padding: 40rpx 30rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.06);
  text-align: center;

  .header-title {
    font-size: 40rpx;
    font-weight: 700;
    color: #333;
    margin-bottom: 20rpx;
  }

  .update-time, .effective-time {
    font-size: 26rpx;
    color: #999;
    line-height: 1.8;
  }
}

.policy-body {
  background: #fff;
  border-radius: 20rpx;
  padding: 30rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.06);
}

.section {
  margin-bottom: 36rpx;

  &:last-child {
    margin-bottom: 0;
  }

  .section-title {
    font-size: 30rpx;
    font-weight: 700;
    color: #333;
    margin-bottom: 16rpx;
    padding-left: 16rpx;
    border-left: 6rpx solid #2979FF;
  }

  .section-content {
    .text {
      display: block;
      font-size: 28rpx;
      color: #555;
      line-height: 1.9;
      margin-bottom: 12rpx;
      text-align: justify;

      &.bold {
        font-weight: 600;
        color: #333;
        margin-top: 16rpx;
      }
    }
  }
}

.policy-footer {
  text-align: center;
  padding: 40rpx 0 20rpx;

  .footer-text {
    display: block;
    font-size: 26rpx;
    color: #999;
    line-height: 1.8;
  }
}

.bottom-space {
  height: 60rpx;
}
</style>
