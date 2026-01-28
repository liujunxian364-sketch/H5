<template>
  <view class="page-container">
    <!-- 内容区域 -->
    <view class="content">
      <!-- 空状态 -->
      <view class="empty-state" v-if="!loading && errorList.length === 0">
        <text class="empty-icon">📝</text>
        <text class="empty-text">还没有错题记录</text>
        <text class="empty-desc">点击底部拍照按钮，开始记录错题吧</text>
      </view>

      <!-- 错题列表 -->
      <view class="error-list" v-else>
        <view
          class="error-card"
          v-for="item in errorList"
          :key="item.id"
          @click="viewDetail(item)"
        >
          <image
            class="card-image"
            :src="getImageUrl(item.image_url)"
            mode="aspectFill"
          />
          <view class="card-content">
            <text class="card-subject">{{ item.subject }}</text>
            <view class="knowledge-tags">
              <text
                class="tag"
                v-for="(kp, index) in item.knowledge_points"
                :key="index"
              >{{ kp }}</text>
            </view>
            <text class="card-time">{{ formatTime(item.createTime) }}</text>
          </view>
        </view>
      </view>

      <!-- 加载状态 -->
      <view class="loading" v-if="loading">
        <text>加载中...</text>
      </view>
    </view>

    <!-- 底部菜单栏 -->
    <view class="bottom-menu">
      <view class="menu-item" @click="showSubjectPicker = true">
        <text class="menu-icon">📚</text>
        <text class="menu-text">{{ currentSubject || '全部科目' }}</text>
      </view>
      <view class="menu-item menu-item-camera" @click="handleTakePhoto">
        <text class="camera-icon">📷</text>
      </view>
      <view class="menu-item" @click="handleViewReport">
        <text class="menu-icon">📊</text>
        <text class="menu-text">错题报告</text>
      </view>
    </view>

    <!-- 科目选择器 -->
    <view class="subject-picker-overlay" v-if="showSubjectPicker" @click.stop="showSubjectPicker = false">
      <view class="subject-picker" @click.stop>
        <view class="picker-header">
          <text class="picker-title">选择科目</text>
          <text class="btn-close" @click="showSubjectPicker = false">×</text>
        </view>
        <scroll-view class="picker-content" scroll-y>
          <view
            class="subject-item"
            :class="{ active: !currentSubject }"
            @click="selectSubject(null)"
          >
            <text>全部科目</text>
          </view>
          <view
            class="subject-item"
            v-for="subject in subjects"
            :key="subject"
            :class="{ active: currentSubject === subject }"
            @click="selectSubject(subject)"
          >
            <text>{{ subject }}</text>
          </view>
        </scroll-view>
      </view>
    </view>

    <!-- 科目选择对话框（拍照后） -->
    <view class="subject-select-overlay" v-if="showSubjectSelect" @click.stop="showSubjectSelect = false">
      <view class="subject-select-dialog" @click.stop>
        <text class="dialog-title">选择科目</text>
        <view class="subject-grid">
          <view
            class="subject-btn"
            v-for="subject in subjects"
            :key="subject"
            @click="handleSubjectSelect(subject)"
          >
            <text>{{ subject }}</text>
          </view>
        </view>
        <view class="btn-cancel-select" @click="showSubjectSelect = false">
          <text>取消</text>
        </view>
      </view>
    </view>

    <!-- 报告展示 -->
    <view class="report-overlay" v-if="showReport" @click.stop="showReport = false">
      <view class="report-dialog" @click.stop>
        <view class="report-header">
          <text class="report-title">{{ currentSubject }} - 错题报告</text>
          <text class="btn-close" @click="showReport = false">×</text>
        </view>
        <scroll-view class="report-content" scroll-y v-if="reportData">
          <view class="report-section">
            <text class="section-title">错题统计</text>
            <text class="section-text">总错题数：{{ reportData.total_count }}道</text>
          </view>
          <view class="report-section">
            <text class="section-title">高频知识点</text>
            <view class="knowledge-stats">
              <view
                class="stat-item"
                v-for="(kp, index) in reportData.knowledge_points.slice(0, 5)"
                :key="index"
              >
                <text class="kp-name">{{ kp.name }}</text>
                <text class="kp-count">{{ kp.count }}次</text>
              </view>
            </view>
          </view>
          <view class="report-section">
            <text class="section-title">学习建议</text>
            <text class="report-analysis">{{ reportData.analysis }}</text>
          </view>
        </scroll-view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { errorMemoryApi } from '@/api'

const errorList = ref([])
const subjects = ref([])
const currentSubject = ref(null)
const loading = ref(false)
const showSubjectPicker = ref(false)
const showSubjectSelect = ref(false)
const showReport = ref(false)
const capturedImagePath = ref('')
const cropData = ref(null)
const reportData = ref(null)

// 获取图片完整URL
const getImageUrl = (url) => {
  if (!url) return ''
  if (url.startsWith('http')) return url
  if (url.startsWith('/uploads')) {
    // H5环境使用代理，App环境需要完整URL
    // #ifdef H5
    return url
    // #endif
    // #ifndef H5
    return `http://localhost:8000${url}`
    // #endif
  }
  return url
}

// 格式化时间
const formatTime = (timeStr) => {
  if (!timeStr) return ''
  const date = new Date(timeStr)
  const now = new Date()
  const diff = now - date
  
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  if (diff < 604800000) return `${Math.floor(diff / 86400000)}天前`
  
  return timeStr.split(' ')[0]
}

// 获取科目列表
const fetchSubjects = async () => {
  try {
    const res = await errorMemoryApi.getSubjects()
    if (res.code === 0) {
      subjects.value = res.data || []
    }
  } catch (error) {
    console.error('获取科目列表失败:', error)
  }
}

// 获取错题列表
const fetchErrorList = async () => {
  loading.value = true
  try {
    const params = {
      page: 1,
      pageSize: 50
    }
    if (currentSubject.value) {
      params.subject = currentSubject.value
    }
    
    const res = await errorMemoryApi.getList(params)
    if (res.code === 0) {
      errorList.value = res.data || []
    }
  } catch (error) {
    console.error('获取错题列表失败:', error)
    errorList.value = []
  } finally {
    loading.value = false
  }
}

// 选择科目
const selectSubject = (subject) => {
  currentSubject.value = subject
  showSubjectPicker.value = false
  fetchErrorList()
}

// 拍照 - 使用uni.chooseImage
const handleTakePhoto = () => {
  uni.chooseImage({
    count: 1,
    sourceType: ['camera', 'album'],
    success: (res) => {
      const tempFilePath = res.tempFilePaths[0]
      capturedImagePath.value = tempFilePath
      // 直接选择科目，不进行裁剪（uni-app中图片裁剪可以使用uni.cropImage，但需要插件）
      // 简化流程：拍照后直接选择科目上传
      showSubjectSelect.value = true
    },
    fail: (err) => {
      console.error('选择图片失败:', err)
      uni.showToast({
        title: '选择图片失败',
        icon: 'none'
      })
    }
  })
}

// 选择科目（上传错题）
const handleSubjectSelect = async (subject) => {
  if (!capturedImagePath.value) return
  
  uni.showLoading({
    title: '上传中...'
  })
  
  try {
    const res = await errorMemoryApi.upload(
      capturedImagePath.value,
      subject,
      cropData.value
    )
    
    if (res.code === 0) {
      showSubjectSelect.value = false
      capturedImagePath.value = ''
      cropData.value = null
      
      // 刷新列表
      await fetchErrorList()
      
      uni.showToast({
        title: '错题上传成功！',
        icon: 'success'
      })
    } else {
      uni.showToast({
        title: res.message || '上传失败',
        icon: 'none'
      })
    }
  } catch (error) {
    console.error('上传失败:', error)
    uni.showToast({
      title: '上传失败，请重试',
      icon: 'none'
    })
  } finally {
    uni.hideLoading()
  }
}

// 查看详情
const viewDetail = (item) => {
  console.log('查看错题详情:', item)
  // 可以跳转到详情页
}

// 查看报告
const handleViewReport = async () => {
  if (!currentSubject.value) {
    uni.showToast({
      title: '请先选择科目',
      icon: 'none'
    })
    return
  }
  
  uni.showLoading({
    title: '加载中...'
  })
  
  try {
    const res = await errorMemoryApi.getReport(currentSubject.value)
    if (res.code === 0) {
      reportData.value = res.data
      showReport.value = true
    } else {
      uni.showToast({
        title: res.message || '获取报告失败',
        icon: 'none'
      })
    }
  } catch (error) {
    console.error('获取报告失败:', error)
    uni.showToast({
      title: '获取报告失败，请重试',
      icon: 'none'
    })
  } finally {
    uni.hideLoading()
  }
}

onMounted(() => {
  fetchSubjects()
  fetchErrorList()
})
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  background: #f5f6f8;
  padding-bottom: calc(70px + constant(safe-area-inset-bottom));
  padding-bottom: calc(70px + env(safe-area-inset-bottom));
}

.content {
  padding: 16px;
  padding-top: 20px;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 100px 20px 80px;
  text-align: center;
  background: #fff;
  border-radius: 16px;
  margin: 20px 0;
}

.empty-icon {
  font-size: 72px;
  margin-bottom: 20px;
  opacity: 0.8;
}

.empty-text {
  font-size: 17px;
  font-weight: 600;
  color: #333;
  margin-bottom: 10px;
  display: block;
}

.empty-desc {
  font-size: 14px;
  color: #999;
  display: block;
  line-height: 1.6;
}

/* 错题列表 */
.error-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.error-card {
  background: #fff;
  border-radius: 12px;
  padding: 14px;
  display: flex;
  gap: 14px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: all 0.2s ease;
}

.error-card:active {
  transform: scale(0.98);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.card-image {
  width: 110px;
  height: 110px;
  border-radius: 10px;
  flex-shrink: 0;
  background: #f5f5f5;
  object-fit: cover;
}

.card-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.card-subject {
  font-size: 14px;
  font-weight: 500;
  color: #667eea;
  margin-bottom: 8px;
  display: block;
}

.knowledge-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 8px;
}

.tag {
  padding: 4px 8px;
  background: #f0f0f0;
  border-radius: 4px;
  font-size: 12px;
  color: #666;
  display: inline-block;
}

.card-time {
  font-size: 12px;
  color: #999;
  display: block;
}

.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: #999;
}

/* 底部菜单栏 */
.bottom-menu {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: #fff;
  border-top: 1px solid #eee;
  display: flex;
  align-items: center;
  justify-content: space-around;
  padding: 10px 0;
  padding-bottom: calc(10px + constant(safe-area-inset-bottom));
  padding-bottom: calc(10px + env(safe-area-inset-bottom));
  z-index: 100;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.05);
}

.menu-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 8px 20px;
  transition: all 0.2s ease;
  user-select: none;
  -webkit-tap-highlight-color: transparent;
}

.menu-item:active {
  transform: scale(0.95);
}

.menu-item-camera {
  background: linear-gradient(135deg, #FF6B6B 0%, #ee5a5a 100%);
  border-radius: 50%;
  width: 60px;
  height: 60px;
  padding: 0;
  margin: -24px 0;
  justify-content: center;
  box-shadow: 0 4px 16px rgba(255, 107, 107, 0.4);
}

.menu-item-camera:active {
  transform: scale(0.92);
  box-shadow: 0 2px 12px rgba(255, 107, 107, 0.5);
}

.camera-icon {
  font-size: 26px;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
}

.menu-icon {
  font-size: 22px;
}

.menu-text {
  font-size: 12px;
  color: #666;
  font-weight: 500;
}

.menu-item-camera .menu-text {
  display: none;
}

/* 科目选择器 */
.subject-picker-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  z-index: 200;
  display: flex;
  align-items: flex-end;
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
}

.subject-picker {
  width: 100%;
  background: #fff;
  border-radius: 20px 20px 0 0;
  max-height: 60vh;
  display: flex;
  flex-direction: column;
  padding-bottom: constant(safe-area-inset-bottom);
  padding-bottom: env(safe-area-inset-bottom);
}

.picker-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 20px;
  border-bottom: 1px solid #eee;
}

.picker-title {
  font-size: 17px;
  font-weight: 600;
  color: #333;
}

.btn-close {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  color: #999;
  background: #f5f5f5;
  border-radius: 50%;
  transition: all 0.2s ease;
}

.btn-close:active {
  background: #e8e8e8;
  transform: scale(0.95);
}

.picker-content {
  max-height: 50vh;
  padding: 8px 0;
}

.subject-item {
  padding: 18px 20px;
  font-size: 16px;
  color: #333;
  transition: all 0.2s ease;
}

.subject-item:active {
  background: #f5f5f5;
}

.subject-item.active {
  color: #667eea;
  font-weight: 600;
  background: #f0f4ff;
}

/* 科目选择对话框 */
.subject-select-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  z-index: 300;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
}

.subject-select-dialog {
  width: 100%;
  max-width: 400px;
  background: #fff;
  border-radius: 16px;
  padding: 28px 24px 24px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
}

.dialog-title {
  font-size: 19px;
  font-weight: 600;
  display: block;
  text-align: center;
  margin-bottom: 24px;
  color: #333;
}

.subject-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14px;
  margin-bottom: 24px;
}

.subject-btn {
  padding: 16px 12px;
  background: linear-gradient(135deg, #f8f9ff 0%, #fff 100%);
  border-radius: 12px;
  text-align: center;
  font-size: 15px;
  font-weight: 500;
  color: #333;
  border: 2px solid #f0f0f0;
  transition: all 0.2s ease;
}

.subject-btn:active {
  transform: scale(0.95);
  background: #667eea;
  color: #fff;
  border-color: #667eea;
}

.btn-cancel-select {
  width: 100%;
  padding: 14px;
  background: #f5f5f5;
  border-radius: 12px;
  text-align: center;
  font-size: 15px;
  font-weight: 500;
  color: #666;
  transition: all 0.2s ease;
}

.btn-cancel-select:active {
  background: #e8e8e8;
}

/* 报告对话框 */
.report-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  z-index: 400;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
}

.report-dialog {
  width: 100%;
  max-width: 500px;
  max-height: 80vh;
  background: #fff;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
}

.report-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 20px;
  border-bottom: 1px solid #eee;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.report-title {
  font-size: 17px;
  font-weight: 600;
  color: #fff;
}

.report-header .btn-close {
  color: #fff;
  background: rgba(255, 255, 255, 0.2);
}

.report-header .btn-close:active {
  background: rgba(255, 255, 255, 0.3);
}

.report-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.report-section {
  margin-bottom: 24px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 14px;
  display: block;
  position: relative;
  padding-left: 12px;
}

.section-title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 16px;
  background: #667eea;
  border-radius: 2px;
}

.section-text {
  font-size: 15px;
  color: #666;
  line-height: 1.6;
  display: block;
}

.knowledge-stats {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 14px;
  background: linear-gradient(135deg, #f8f9ff 0%, #fff 100%);
  border-radius: 10px;
  border: 1px solid #f0f0f0;
}

.kp-name {
  font-size: 15px;
  color: #333;
  font-weight: 500;
}

.kp-count {
  font-size: 14px;
  color: #667eea;
  font-weight: 600;
  padding: 4px 12px;
  background: rgba(102, 126, 234, 0.1);
  border-radius: 12px;
}

.report-analysis {
  font-size: 14px;
  color: #666;
  line-height: 1.8;
  white-space: pre-wrap;
  word-wrap: break-word;
  background: #f9f9f9;
  padding: 14px;
  border-radius: 10px;
  display: block;
  border: 1px solid #f0f0f0;
}
</style>
