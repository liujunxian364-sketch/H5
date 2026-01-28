<template>
  <view class="page-container">
    <view class="placeholder touchable">
      <text class="placeholder-icon">📚</text>
      <text class="placeholder-text">单词速记功能</text>
      <text class="placeholder-desc">功能开发中，敬请期待...</text>
      <view class="coming-soon">
        <text class="tag">即将推出</text>
      </view>
    </view>
  </view>
</template>

<script setup>
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #4ECDC4 0%, #44bdb5 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 30px;
  background: #fff;
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
  position: relative;
  overflow: hidden;
}

.placeholder::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(78, 205, 196, 0.05) 0%, transparent 70%);
}

.placeholder-icon {
  font-size: 80px;
  margin-bottom: 24px;
  animation: float 3s ease-in-out infinite;
  filter: drop-shadow(0 4px 12px rgba(0, 0, 0, 0.1));
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-10px);
  }
}

.placeholder-text {
  font-size: 22px;
  font-weight: 600;
  color: #333;
  margin-bottom: 12px;
  display: block;
  position: relative;
  z-index: 1;
}

.placeholder-desc {
  font-size: 15px;
  color: #999;
  display: block;
  position: relative;
  z-index: 1;
  margin-bottom: 20px;
}

.coming-soon {
  margin-top: 8px;
}

.tag {
  display: inline-block;
  padding: 8px 20px;
  background: linear-gradient(135deg, #4ECDC4 0%, #44bdb5 100%);
  color: #fff;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
  box-shadow: 0 4px 12px rgba(78, 205, 196, 0.3);
}
</style>
