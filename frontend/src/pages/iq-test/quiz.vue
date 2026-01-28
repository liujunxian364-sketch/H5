<template>
  <view class="quiz-page">
    <!-- 进度条 -->
    <view class="progress-bar">
      <view class="progress-fill" :style="{ width: progressPercent + '%' }"></view>
      <view class="progress-text">{{ currentIndex + 1 }} / {{ questions.length }}</view>
    </view>

    <!-- 题目卡片 -->
    <view v-if="!loading && questions.length > 0" class="quiz-content">
      <view class="question-card">
        <!-- 题目序号 -->
        <view class="question-number">第 {{ currentIndex + 1 }} 题</view>
        
        <!-- 题目内容 -->
        <view class="question-text">{{ currentQuestion.question }}</view>
        
        <!-- 选项列表 -->
        <view class="options-list">
          <view
            v-for="(option, index) in currentQuestion.options"
            :key="index"
            class="option-item touchable"
            :class="{ selected: selectedAnswer === option.value }"
            @click="selectAnswer(option.value)"
          >
            <view class="option-label">{{ option.label }}</view>
            <view class="option-text">{{ option.text }}</view>
            <view v-if="selectedAnswer === option.value" class="option-check">✓</view>
          </view>
        </view>
      </view>

      <!-- 底部按钮 -->
      <view class="action-buttons">
        <button
          v-if="currentIndex > 0"
          class="prev-btn touchable"
          @click="prevQuestion"
        >
          ← 上一题
        </button>
        <button
          v-if="isLastQuestion && selectedAnswer"
          class="submit-btn touchable"
          @click="submitAnswers"
        >
          提交答案
        </button>
      </view>
    </view>

    <!-- 加载状态 -->
    <view v-if="loading" class="loading-state">
      <view class="loading-icon">⏳</view>
      <text class="loading-text">正在加载题目...</text>
    </view>

    <!-- 空状态 -->
    <view v-if="!loading && questions.length === 0" class="empty-state">
      <view class="empty-icon">📝</view>
      <text class="empty-text">暂无题目</text>
    </view>
  </view>
</template>

<script>
import { ref, computed, onMounted } from 'vue'

export default {
  setup() {
    const loading = ref(true)
    const questions = ref([])
    const currentIndex = ref(0)
    const selectedAnswer = ref('')
    const answers = ref([]) // 存储所有答案
    const birthTime = ref('') // 出生时间段

    // 当前题目
    const currentQuestion = computed(() => {
      return questions.value[currentIndex.value] || {}
    })

    // 进度百分比
    const progressPercent = computed(() => {
      if (questions.value.length === 0) return 0
      return ((currentIndex.value + 1) / questions.value.length) * 100
    })

    // 是否是最后一题
    const isLastQuestion = computed(() => {
      return currentIndex.value === questions.value.length - 1
    })

    // 选择答案
    const selectAnswer = (value) => {
      selectedAnswer.value = value
      
      console.log('[选择答案] 当前题:', currentIndex.value + 1, '/', questions.value.length)
      console.log('[选择答案] 是否最后一题:', isLastQuestion.value)
      console.log('[选择答案] 已选答案:', value)
      
      // 保存当前答案
      answers.value[currentIndex.value] = {
        questionId: currentQuestion.value.id,
        answer: value,
        question: currentQuestion.value.question
      }
      
      // 如果不是最后一题，延迟300ms后自动跳转到下一题
      if (!isLastQuestion.value) {
        console.log('[选择答案] 将在300ms后跳到下一题')
        setTimeout(() => {
          currentIndex.value++
          
          // 如果下一题已经有答案，自动填充
          if (answers.value[currentIndex.value]) {
            selectedAnswer.value = answers.value[currentIndex.value].answer
          } else {
            selectedAnswer.value = ''
          }
        }, 300)
      } else {
        console.log('[选择答案] 这是最后一题，显示提交按钮')
      }
    }

    // 下一题（已废弃，但保留以防万一）
    const nextQuestion = () => {
      // 不再使用，所有逻辑都在 selectAnswer 中处理
    }

    // 上一题
    const prevQuestion = () => {
      if (currentIndex.value > 0) {
        currentIndex.value--
        // 恢复上一题的答案
        if (answers.value[currentIndex.value]) {
          selectedAnswer.value = answers.value[currentIndex.value].answer
        } else {
          selectedAnswer.value = ''
        }
      }
    }

    // 提交答案
    const submitAnswers = () => {
      try {
        // 获取用户信息
        const userInfo = uni.getStorageSync('iq_test_user_info') || {}
        
        // 格式化答案为 Dify 需要的格式: "id,answer|id,answer|..."
        const answerString = answers.value
          .map(a => `${a.questionId},${a.answer}`)
          .join('|')
        
        console.log('[提交答案] 立即跳转到结果页面')
        
        // 准备用户信息（用于结果页面分析）
        const submitData = {
          name: userInfo.name || '未知',
          birthDate: userInfo.birthDate || '',
          academicYear: userInfo.academicYear || '2025',
          birthTime: birthTime.value,
          answer: answerString
        }
        
        // 立即跳转到结果页面（不等待后端）
        uni.navigateTo({
          url: `/pages/iq-test/result?userInfo=${encodeURIComponent(JSON.stringify(submitData))}`
        })
      } catch (error) {
        console.error('[提交答案] 失败:', error)
        uni.showToast({
          title: '跳转失败，请重试',
          icon: 'none'
        })
      }
    }

    // 加载题目
    const loadQuestions = async () => {
      loading.value = true
      try {
        console.log('[题目加载] 开始请求 API...')
        const res = await uni.request({
          url: '/api/iq-test/questions',
          method: 'GET'
        })

        console.log('[题目加载] API 响应:', res)
        console.log('[题目加载] 状态码:', res.statusCode)
        console.log('[题目加载] 数据:', res.data)

        if (res.statusCode === 200 && res.data && res.data.code === 0) {
          questions.value = res.data.data || []
          console.log('[题目加载] 成功加载', questions.value.length, '道题')
        } else {
          console.error('[题目加载] API 返回错误:', res.data)
          throw new Error(res.data?.message || '加载题目失败')
        }
      } catch (error) {
        console.error('[题目加载] 失败:', error)
        console.error('[题目加载] 错误详情:', {
          message: error.message,
          stack: error.stack,
          error: error
        })
        uni.showToast({
          title: `加载失败: ${error.message || '网络错误'}`,
          icon: 'none',
          duration: 3000
        })
        
        // 使用模拟数据
        console.log('[题目加载] 使用模拟数据')
        questions.value = [
          {
            id: 1,
            question: '你更喜欢哪种学习方式？',
            options: [
              { label: 'A', value: 'A', text: '独立思考，自主学习' },
              { label: 'B', value: 'B', text: '小组讨论，合作学习' },
              { label: 'C', value: 'C', text: '听老师讲解，被动接受' },
              { label: 'D', value: 'D', text: '实践操作，动手尝试' }
            ]
          },
          {
            id: 2,
            question: '面对难题时，你通常会？',
            options: [
              { label: 'A', value: 'A', text: '立即寻求帮助' },
              { label: 'B', value: 'B', text: '先自己尝试解决' },
              { label: 'C', value: 'C', text: '暂时放下，休息后再试' },
              { label: 'D', value: 'D', text: '查找资料，系统学习' }
            ]
          }
        ]
      } finally {
        loading.value = false
      }
    }

    onMounted(() => {
      // 获取出生时间段参数
      const pages = getCurrentPages()
      const currentPage = pages[pages.length - 1]
      birthTime.value = currentPage.options.birthTime || ''
      
      console.log('[答题页面] 出生时间段:', birthTime.value)
      
      // 加载题目
      loadQuestions()
    })

    return {
      loading,
      questions,
      currentIndex,
      selectedAnswer,
      currentQuestion,
      progressPercent,
      isLastQuestion,
      selectAnswer,
      nextQuestion,
      prevQuestion,
      submitAnswers  // 添加 submitAnswers
    }
  }
}
</script>

<style scoped>
.quiz-page {
  min-height: 100vh;
  background: #f5f6f8;
  padding-bottom: 100px;
}

/* 进度条 */
.progress-bar {
  position: sticky;
  top: 0;
  z-index: 10;
  height: 8px;
  background: #e0e0e0;
  position: relative;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea, #764ba2);
  transition: width 0.3s ease;
}

.progress-text {
  position: absolute;
  top: 12px;
  right: 20px;
  font-size: 14px;
  color: #666;
  font-weight: bold;
}

/* 题目内容 */
.quiz-content {
  padding: 20px;
}

.question-card {
  background: #fff;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  margin-bottom: 20px;
}

.question-number {
  font-size: 14px;
  color: #667eea;
  font-weight: bold;
  margin-bottom: 16px;
}

.question-text {
  font-size: 18px;
  font-weight: bold;
  color: #333;
  line-height: 1.6;
  margin-bottom: 24px;
}

/* 选项列表 */
.options-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.option-item {
  position: relative;
  background: #f8f9fa;
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  padding: 16px;
  transition: all 0.3s ease;
}

.option-item.selected {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-color: #667eea;
  color: #fff;
  transform: scale(1.02);
}

.option-label {
  display: inline-block;
  width: 32px;
  height: 32px;
  background: #fff;
  color: #667eea;
  border-radius: 50%;
  text-align: center;
  line-height: 32px;
  font-weight: bold;
  margin-bottom: 8px;
}

.option-item.selected .option-label {
  background: #fff;
  color: #667eea;
}

.option-text {
  font-size: 15px;
  line-height: 1.5;
}

.option-check {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 28px;
  height: 28px;
  background: #fff;
  color: #667eea;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: bold;
}

/* 底部按钮 */
.action-buttons {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 16px 20px;
  background: #fff;
  box-shadow: 0 -2px 12px rgba(0, 0, 0, 0.08);
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.prev-btn,
.submit-btn {
  height: 48px;
  border-radius: 24px;
  font-size: 16px;
  font-weight: bold;
  border: none;
  transition: all 0.3s ease;
  padding: 0 32px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
}

.submit-btn {
  flex: 1;
}

/* 加载和空状态 */
.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 100px 40px;
}

.loading-icon,
.empty-icon {
  font-size: 80px;
  margin-bottom: 20px;
}

.loading-text,
.empty-text {
  font-size: 16px;
  color: #999;
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
  opacity: 0.9;
}
</style>

