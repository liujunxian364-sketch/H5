<template>
  <view class="iq-test-page">
    <view class="container">
      <view class="icon">🎯</view>
      <view class="title">学商速测</view>
      <view class="subtitle">了解你的学习潜力和风格</view>
      <button class="start-btn touchable" @click="goToTimeSelect">开始测试</button>
    </view>
  </view>
</template>

<script>
export default {
  methods: {
    goToTimeSelect() {
      // 跳转到用户信息页面
      uni.navigateTo({
        url: '/pages/iq-test/user-info'
      })
    }
  }
}
</script>

<style scoped>
.iq-test-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #96CEB4 0%, #76B7A2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

.container {
  text-align: center;
  color: #fff;
}

.icon {
  font-size: 100px;
  margin-bottom: 30px;
  animation: bounce 2s infinite;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-20px); }
}

.title {
  font-size: 32px;
  font-weight: bold;
  margin-bottom: 16px;
}

.subtitle {
  font-size: 16px;
  opacity: 0.9;
  margin-bottom: 40px;
}

.start-btn {
  width: 200px;
  height: 50px;
  background: #fff;
  color: #96CEB4;
  border-radius: 25px;
  font-size: 18px;
  font-weight: bold;
  border: none;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
  margin: 0 auto;
}

.touchable {
  transition: all 0.2s ease;
  cursor: pointer;
}

.touchable:active {
  transform: scale(0.95);
}
</style>
