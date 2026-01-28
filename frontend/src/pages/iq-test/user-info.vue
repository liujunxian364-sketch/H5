<template>
  <view class="user-info-page">
    <!-- 标题 -->
    <view class="header">
      <text class="title">个人信息</text>
      <text class="subtitle">帮助我们更好地为你分析</text>
    </view>

    <!-- 表单 -->
    <view class="form-container">
      <!-- 姓名 -->
      <view class="form-item">
        <view class="label">
          <text class="label-text">姓名</text>
          <text class="required">*</text>
        </view>
        <input
          class="input"
          v-model="name"
          placeholder="请输入你的姓名"
          maxlength="20"
        />
      </view>

      <!-- 出生日期 -->
      <view class="form-item">
        <view class="label">
          <text class="label-text">出生日期</text>
          <text class="required">*</text>
        </view>
        <picker
          mode="date"
          :value="birthDate"
          @change="onDateChange"
          :end="today"
        >
          <view class="picker-input">
            <text :class="{ placeholder: !birthDate }">
              {{ birthDate || '请选择出生日期' }}
            </text>
            <text class="arrow">📅</text>
          </view>
        </picker>
      </view>

      <!-- 学年 -->
      <view class="form-item">
        <view class="label">
          <text class="label-text">学年</text>
        </view>
        <picker
          mode="selector"
          :range="academicYears"
          :value="academicYearIndex"
          @change="onAcademicYearChange"
        >
          <view class="picker-input">
            <text>{{ academicYears[academicYearIndex] }}</text>
            <text class="arrow">▼</text>
          </view>
        </picker>
      </view>
    </view>

    <!-- 底部按钮 -->
    <view class="footer">
      <button
        class="next-btn touchable"
        :class="{ active: canNext }"
        :disabled="!canNext"
        @click="nextStep"
      >
        下一步
      </button>
    </view>
  </view>
</template>

<script>
import { ref, computed } from 'vue'

export default {
  setup() {
    const name = ref('')
    const birthDate = ref('')
    const academicYearIndex = ref(0)
    const academicYears = ref(['2025', '2024', '2023', '2022', '2021'])
    
    // 今天日期（限制不能选未来日期）
    const today = new Date().toISOString().split('T')[0]

    // 是否可以进入下一步
    const canNext = computed(() => {
      return name.value.trim() && birthDate.value
    })

    // 选择日期
    const onDateChange = (e) => {
      birthDate.value = e.detail.value
    }

    // 选择学年
    const onAcademicYearChange = (e) => {
      academicYearIndex.value = e.detail.value
    }

    // 下一步
    const nextStep = () => {
      if (!canNext.value) {
        uni.showToast({
          title: '请填写完整信息',
          icon: 'none'
        })
        return
      }

      // 保存用户信息到全局或本地存储
      const userInfo = {
        name: name.value.trim(),
        birthDate: birthDate.value,
        academicYear: academicYears.value[academicYearIndex.value]
      }
      
      console.log('[用户信息] 保存:', userInfo)
      
      // 使用 uni.setStorageSync 保存
      uni.setStorageSync('iq_test_user_info', userInfo)

      // 跳转到时间段选择页面
      uni.navigateTo({
        url: '/pages/iq-test/time-select'
      })
    }

    return {
      name,
      birthDate,
      today,
      academicYearIndex,
      academicYears,
      canNext,
      onDateChange,
      onAcademicYearChange,
      nextStep
    }
  }
}
</script>

<style scoped>
.user-info-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

/* 头部 */
.header {
  text-align: center;
  padding: 40px 20px 30px;
  color: #fff;
}

.title {
  font-size: 28px;
  font-weight: bold;
  display: block;
  margin-bottom: 12px;
}

.subtitle {
  font-size: 14px;
  opacity: 0.9;
  display: block;
}

/* 表单 */
.form-container {
  background: #fff;
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 20px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.form-item {
  margin-bottom: 24px;
}

.form-item:last-child {
  margin-bottom: 0;
}

.label {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}

.label-text {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.required {
  color: #ff4d4f;
  margin-left: 4px;
  font-size: 16px;
}

.input {
  width: 100%;
  height: 48px;
  padding: 0 16px;
  background: #f5f6f8;
  border: 2px solid #e8e8e8;
  border-radius: 12px;
  font-size: 15px;
  transition: all 0.3s;
}

.input:focus {
  background: #fff;
  border-color: #667eea;
}

.picker-input {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 48px;
  padding: 0 16px;
  background: #f5f6f8;
  border: 2px solid #e8e8e8;
  border-radius: 12px;
  font-size: 15px;
  color: #333;
}

.picker-input .placeholder {
  color: #999;
}

.arrow {
  font-size: 14px;
  color: #999;
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

.next-btn {
  width: 100%;
  height: 50px;
  background: #ccc;
  color: #999;
  border-radius: 25px;
  font-size: 18px;
  font-weight: bold;
  border: none;
  transition: all 0.3s ease;
}

.next-btn.active {
  background: #fff;
  color: #667eea;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
}

.next-btn:disabled {
  opacity: 0.6;
}

.next-btn.active:active {
  transform: scale(0.98);
}

/* 触摸反馈 */
.touchable {
  transition: all 0.2s ease;
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
  user-select: none;
}
</style>

