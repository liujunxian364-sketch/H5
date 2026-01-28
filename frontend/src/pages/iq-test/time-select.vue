<template>
  <view class="time-select-page">
    <!-- 标题 -->
    <view class="header">
      <text class="title">选择你的出生时间段</text>
      <text class="subtitle">更精准的时间信息，更准确的分析结果</text>
    </view>

    <!-- 时间段选项 -->
    <view class="time-options">
      <view
        v-for="(option, index) in timeOptions"
        :key="index"
        class="time-card touchable"
        :class="{ selected: selectedTime === option.value }"
        @click="selectTime(option.value)"
      >
        <!-- 图标/插图 -->
        <view class="card-icon">{{ option.emoji }}</view>
        
        <!-- 标题 -->
        <view class="card-title">{{ option.title }}</view>
        
        <!-- 时间范围 -->
        <view class="card-time">{{ option.time }}</view>
        
        <!-- 描述 -->
        <view class="card-desc">{{ option.description }}</view>
        
        <!-- 选中标记 -->
        <view v-if="selectedTime === option.value" class="check-mark">✓</view>
      </view>
    </view>

    <!-- 底部按钮 -->
    <view class="footer">
      <button class="start-btn touchable" :disabled="!selectedTime" @click="startTest">
        开始潜力测试
      </button>
    </view>
  </view>
</template>

<script>
import { ref } from 'vue'

export default {
  setup() {
    const selectedTime = ref('')
    
    const timeOptions = [
      {
        value: '04:00-10:00',
        emoji: '🌅',
        title: '风拂轻纱的早晨',
        time: '4:00 - 10:00',
        description: '晨曦初露，万物复苏的时刻'
      },
      {
        value: '10:00-16:00',
        emoji: '🌞',
        title: '树影婆娑的中午',
        time: '10:00 - 16:00',
        description: '阳光正好，生机勃勃的午后'
      },
      {
        value: '16:00-22:00',
        emoji: '🌆',
        title: '流萤点点的晚上',
        time: '16:00 - 22:00',
        description: '夕阳西下，星光渐现的傍晚'
      },
      {
        value: '22:00-04:00',
        emoji: '🌙',
        title: '万籁俱寂的凌晨',
        time: '22:00 - 04:00',
        description: '夜深人静，群星闪耀的深夜'
      },
      {
        value: '00:00-23:59',
        emoji: '❓',
        title: '不太清楚',
        time: '00:00 - 23:59',
        description: '记不清具体的出生时间'
      }
    ]
    
    const selectTime = (value) => {
      selectedTime.value = value
    }
    
    const startTest = () => {
      if (!selectedTime.value) {
        uni.showToast({
          title: '请选择出生时间段',
          icon: 'none'
        })
        return
      }
      
      // 保存出生时间段并跳转到答题页面
      uni.navigateTo({
        url: `/pages/iq-test/quiz?birthTime=${selectedTime.value}`
      })
    }
    
    return {
      selectedTime,
      timeOptions,
      selectTime,
      startTest
    }
  }
}
</script>

<style scoped>
.time-select-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  padding-bottom: 100px;
}

/* 头部 */
.header {
  text-align: center;
  padding: 40px 20px 30px;
  color: #fff;
}

.title {
  font-size: 26px;
  font-weight: bold;
  display: block;
  margin-bottom: 12px;
}

.subtitle {
  font-size: 14px;
  opacity: 0.9;
  display: block;
}

/* 时间选项 */
.time-options {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.time-card {
  position: relative;
  background: #fff;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.time-card.selected {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  transform: scale(1.02);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
}

.card-icon {
  font-size: 48px;
  text-align: center;
  margin-bottom: 12px;
}

.card-title {
  font-size: 20px;
  font-weight: bold;
  text-align: center;
  margin-bottom: 8px;
}

.card-time {
  font-size: 14px;
  text-align: center;
  margin-bottom: 12px;
  opacity: 0.8;
}

.card-desc {
  font-size: 13px;
  text-align: center;
  opacity: 0.7;
  line-height: 1.5;
}

.time-card.selected .card-time,
.time-card.selected .card-desc {
  opacity: 0.9;
}

.check-mark {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 32px;
  height: 32px;
  background: #fff;
  color: #667eea;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: bold;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

/* 底部按钮 */
.footer {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 20px;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.3), transparent);
}

.start-btn {
  width: 100%;
  height: 50px;
  background: #fff;
  color: #667eea;
  border-radius: 25px;
  font-size: 18px;
  font-weight: bold;
  border: none;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
}

.start-btn:disabled {
  opacity: 0.5;
  background: #ccc;
  color: #666;
}

.start-btn:not(:disabled):active {
  transform: scale(0.98);
}

/* 触摸反馈 */
.touchable {
  transition: all 0.2s ease;
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
  user-select: none;
}

.touchable:active {
  transform: scale(0.98);
  opacity: 0.95;
}
</style>

