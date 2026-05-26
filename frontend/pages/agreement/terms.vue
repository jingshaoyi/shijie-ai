<template>
  <view class="container">
    <!-- 导航栏 -->
    <view class="nav-bar">
      <view class="nav-left" @click="goBack">
        <text class="back-icon">←</text>
      </view>
      <view class="nav-title">用户协议</view>
      <view class="nav-right"></view>
    </view>

    <!-- 内容区域 -->
    <scroll-view class="content" scroll-y>
      <view class="content-wrapper">
        <view class="policy-header">
          <view class="header-title">用户协议</view>
          <view class="update-time">更新日期：2026年5月21日</view>
          <view class="effective-time">生效日期：2026年5月21日</view>
        </view>

        <view class="policy-body">
          <view class="section">
            <view class="section-title">一、引言</view>
            <view class="section-content">
              <text class="text">欢迎使用识界AI小程序（以下简称"本小程序"）。本协议是您与识界AI团队（以下简称"我们"）之间关于使用本小程序服务所订立的协议。请您在使用本小程序之前，仔细阅读本协议的全部内容。如果您对本协议的任何条款有异议，您可选择不使用本小程序。当您注册成功后，无论是进入本小程序，还是在本小程序上发布任何内容，均意味着您已完全接受本协议项下的全部条款。</text>
            </view>
          </view>

          <view class="section">
            <view class="section-title">二、服务内容</view>
            <view class="section-content">
              <text class="text">本小程序为用户提供以下AI智能服务：</text>
              <text class="text bold">1. AI智能对话</text>
              <text class="text">基于人工智能技术，为用户提供智能问答、多轮对话等服务。用户可以通过文字输入的方式与AI助手进行交互，获取信息查询、问题解答、创意建议等。</text>
              <text class="text bold">2. 文本生成</text>
              <text class="text">根据用户输入的主题和要求，自动生成各类文本内容，包括但不限于文章、文案、摘要、诗歌、邮件、报告等。</text>
              <text class="text bold">3. 智能翻译</text>
              <text class="text">提供多语言之间的互译服务，支持中文、英语、日语、韩语、法语、德语、西班牙语等多种语言。</text>
              <text class="text bold">4. 知识查询</text>
              <text class="text">基于AI知识库，为用户提供百科知识查询、概念解释、知识科普等服务。</text>
              <text class="text">我们有权随时对服务内容进行变更、升级或调整，且无需事先通知用户，但重大变更除外。</text>
            </view>
          </view>

          <view class="section">
            <view class="section-title">三、账号注册与管理</view>
            <view class="section-content">
              <text class="text bold">1. 注册条件</text>
              <text class="text">您需要通过微信授权登录的方式注册并使用本小程序。您确认在注册时已年满18周岁，或已获得监护人的同意。</text>
              <text class="text bold">2. 账号安全</text>
              <text class="text">您的账号通过微信授权登录，账号安全与您的微信账号绑定。请妥善保管您的微信账号信息，因您个人原因导致账号泄露所引起的一切损失由您自行承担。</text>
              <text class="text bold">3. 账号使用</text>
              <text class="text">每个微信账号仅能注册一个本小程序账号。您不得将账号以任何方式转让、赠与、借用或出售给他人。</text>
            </view>
          </view>

          <view class="section">
            <view class="section-title">四、用户行为规范</view>
            <view class="section-content">
              <text class="text">您在使用本小程序时，应遵守以下行为规范：</text>
              <text class="text">（1）遵守中华人民共和国相关法律法规，包括但不限于《中华人民共和国网络安全法》《中华人民共和国数据安全法》《中华人民共和国个人信息保护法》等；</text>
              <text class="text">（2）不得利用本小程序从事任何违法违规活动，包括但不限于发布危害国家安全、传播淫秽色情信息、赌博、诈骗、侵犯他人合法权益等；</text>
              <text class="text">（3）不得利用本小程序生成、传播虚假信息、垃圾信息或恶意代码；</text>
              <text class="text">（4）不得对本小程序进行反编译、反汇编、修改、破解或其他任何形式的逆向工程；</text>
              <text class="text">（5）不得利用技术手段干扰、破坏本小程序的正常运行；</text>
              <text class="text">（6）不得利用本小程序的AI服务生成侵犯他人知识产权的内容；</text>
              <text class="text">（7）不得将本小程序用于任何商业用途，包括但不限于转售、商业化运营等，除非获得我们的书面授权。</text>
            </view>
          </view>

          <view class="section">
            <view class="section-title">五、知识产权</view>
            <view class="section-content">
              <text class="text bold">1. 平台知识产权</text>
              <text class="text">本小程序的所有内容，包括但不限于界面设计、图标、文字、软件、技术架构等，均受中华人民共和国知识产权法律法规保护。未经我们书面许可，任何人均不得以任何形式使用上述内容。</text>
              <text class="text bold">2. 用户生成内容</text>
              <text class="text">您通过本小程序AI服务生成的内容，其知识产权归您所有。但您理解并同意，AI生成的内容可能存在不准确或不完整的情况，您应对使用这些内容承担全部责任。</text>
              <text class="text bold">3. AI生成内容的免责</text>
              <text class="text">AI生成的内容仅供参考，不构成专业建议（包括但不限于法律、医疗、财务等领域的专业建议）。对于因使用AI生成内容而造成的任何直接或间接损失，我们不承担任何责任。</text>
            </view>
          </view>

          <view class="section">
            <view class="section-title">六、免责声明</view>
            <view class="section-content">
              <text class="text">（1）本小程序的AI服务基于人工智能技术，生成的内容可能存在错误、不准确或不完整的情况。我们不对AI生成内容的准确性、可靠性、完整性作任何保证。</text>
              <text class="text">（2）因不可抗力（包括但不限于自然灾害、政府行为、网络攻击、系统故障等）导致的服务中断或数据丢失，我们不承担责任，但我们将尽力减少对您的影响。</text>
              <text class="text">（3）对于因用户自身原因（包括但不限于操作不当、设备故障、网络问题等）导致的服务体验问题，我们不承担责任。</text>
              <text class="text">（4）本小程序可能包含指向第三方网站或服务的链接，这些链接仅为方便用户而设置。对于第三方网站或服务的内容、隐私政策、安全性，我们不承担任何责任。</text>
            </view>
          </view>

          <view class="section">
            <view class="section-title">七、服务的变更与终止</view>
            <view class="section-content">
              <text class="text bold">1. 服务变更</text>
              <text class="text">我们保留随时修改、暂停或终止部分或全部服务的权利。对于重大变更，我们将通过小程序内通知的方式提前告知用户。</text>
              <text class="text bold">2. 账号注销</text>
              <text class="text">您可以通过"个人中心"或联系我们的方式申请注销账号。账号注销后，我们将在30日内删除您的个人信息和对话历史，法律法规另有规定的除外。账号注销后不可恢复。</text>
              <text class="text bold">3. 违规处理</text>
              <text class="text">如您违反本协议的任何条款，我们有权在不事先通知的情况下暂停或终止向您提供服务，并有权删除违规内容。</text>
            </view>
          </view>

          <view class="section">
            <view class="section-title">八、争议解决</view>
            <view class="section-content">
              <text class="text">本协议的订立、执行、解释及争议解决均适用中华人民共和国法律。如双方就本协议内容或其执行发生任何争议，双方应首先通过友好协商解决。协商不成的，任何一方均有权向我们所在地有管辖权的人民法院提起诉讼。</text>
            </view>
          </view>

          <view class="section">
            <view class="section-title">九、其他条款</view>
            <view class="section-content">
              <text class="text">（1）本协议构成您与我们之间关于使用本小程序服务的完整协议，取代此前双方就相同事项达成的任何口头或书面协议。</text>
              <text class="text">（2）如本协议中的任何条款被认定为无效或不可执行，该条款应在最小必要范围内被修改或删除，其余条款继续有效。</text>
              <text class="text">（3）我们未行使或延迟行使本协议项下的任何权利，不构成对该权利的放弃。</text>
              <text class="text">（4）本协议的标题仅为方便阅读而设置，不影响本协议条款的解释。</text>
            </view>
          </view>

          <view class="section">
            <view class="section-title">十、联系我们</view>
            <view class="section-content">
              <text class="text">如您对本协议有任何疑问或建议，您可以通过以下方式与我们联系：</text>
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
