<template>
  <view class="result-page">
    <!-- 自定义导航栏 -->
    <view class="custom-navbar">
      <view class="navbar-btn" @click="goHome">
        <text class="icon">←</text>
        <text class="text">返回首页</text>
      </view>
      <view class="navbar-title">分析结果</view>
      <view class="navbar-placeholder"></view>
    </view>

    <!-- 消息列表 -->
    <scroll-view
      class="message-list"
      scroll-y
      :scroll-into-view="scrollToId"
      scroll-with-animation
    >
      <!-- 初始分析结果 -->
      <view class="message-item assistant">
        <view class="assistant-message">
          <view class="avatar">🤖</view>
          <view class="message-content">
            <view v-if="isAnalyzing" class="analyzing">
              <view class="loading-spinner">⏳</view>
              <text class="loading-text">AI正在分析你的答案...</text>
            </view>
            <view v-else class="message-text" v-html="formatText(analysis)"></view>
          </view>
        </view>
      </view>

      <!-- 后续对话消息 -->
      <view
        v-for="(msg, index) in messages"
        :key="msg.id"
        :id="`msg-${index}`"
        class="message-item"
        :class="msg.role"
      >
        <!-- 用户消息 -->
        <view v-if="msg.role === 'user'" class="user-message">
          <view class="message-content">
            <view class="message-text">{{ msg.content }}</view>
          </view>
          <view class="avatar user-avatar">👤</view>
        </view>

        <!-- AI消息 -->
        <view v-else-if="msg.role === 'assistant'" class="assistant-message">
          <view class="avatar ai-avatar">🤖</view>
          <view class="message-content">
            <view class="message-text" v-html="formatText(msg.content)"></view>
          </view>
        </view>
      </view>

      <!-- 加载中提示 -->
      <view v-if="isStreaming" class="message-item assistant">
        <view class="assistant-message">
          <view class="avatar ai-avatar">🤖</view>
          <view class="message-content">
            <view class="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </view>
          </view>
        </view>
      </view>
    </scroll-view>

    <!-- 输入栏 -->
    <view class="input-bar" v-if="!isAnalyzing">
      <view class="input-container">
        <textarea
          class="input-text"
          v-model="inputText"
          placeholder="继续提问..."
          :auto-height="true"
          :maxlength="500"
        />
        
        <view
          class="send-btn touchable"
          :class="{ active: canSend }"
          @click="sendMessage"
        >
          <text class="icon">➤</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { marked } from 'marked'

export default {
  setup() {
    const analysis = ref('') // 初始分析结果
    const conversationId = ref('')
    const userInfo = ref({})
    const messages = ref([]) // 后续对话消息
    const inputText = ref('')
    const isStreaming = ref(false)
    const isAnalyzing = ref(true) // 是否正在分析
    const scrollToId = ref('')

    // 配置 marked
    marked.setOptions({
      breaks: true, // 支持换行
      gfm: true // 支持 GitHub Flavored Markdown
    })

    // 返回首页
    const goHome = () => {
      uni.reLaunch({
        url: '/pages/home/index'
      })
    }

    // 是否可以发送
    const canSend = computed(() => {
      return inputText.value.trim() && !isStreaming.value
    })

    // 格式化文本（markdown渲染）
    const formatText = (text) => {
      if (!text) return ''
      try {
        return marked.parse(text)
      } catch (e) {
        console.error('[Markdown渲染] 失败:', e)
        return text.replace(/\n/g, '<br>')
      }
    }

    // 请求后端分析
    const requestAnalysis = async () => {
      try {
        console.log('[结果页面] 开始请求分析', userInfo.value)
        
        const res = await uni.request({
          url: '/api/iq-test/submit',
          method: 'POST',
          timeout: 180000, // 3分钟超时
          data: userInfo.value
        })

        console.log('[结果页面] 分析响应:', res)

        if (res.statusCode === 200 && res.data && res.data.code === 0) {
          const result = res.data.data
          analysis.value = result.analysis || '分析完成'
          conversationId.value = result.conversation_id || ''
          
          console.log('[结果页面] 分析成功, conversation_id:', conversationId.value)
        } else {
          throw new Error(res.data?.message || '分析失败')
        }
      } catch (error) {
        console.error('[结果页面] 分析失败:', error)
        analysis.value = '抱歉，分析失败了，请重试。\n错误信息: ' + (error.message || '网络错误')
      } finally {
        isAnalyzing.value = false
      }
    }

    // 发送消息
    const sendMessage = async () => {
      if (!canSend.value) return

      const content = inputText.value.trim()
      
      // 添加用户消息
      const userMsg = {
        id: `user_${Date.now()}`,
        role: 'user',
        content: content
      }
      messages.value.push(userMsg)
      inputText.value = ''

      // 显示加载状态（不添加空白消息）
      isStreaming.value = true

      try {
        console.log('[对话] 发送请求:', {
          conversation_id: conversationId.value,
          query: content,
          user_info: userInfo.value
        })

        // 调用继续对话接口（传递完整的用户信息，包括 answer）
        const res = await uni.request({
          url: '/api/iq-test/continue-chat',
          method: 'POST',
          timeout: 60000,
          data: {
            conversation_id: conversationId.value,
            query: content,
            user_info: userInfo.value  // 包含 name, birthDate, academicYear, birthTime, answer
          }
        })

        console.log('[对话] 响应:', res)

        if (res.statusCode === 200 && res.data && res.data.code === 0) {
          // 请求成功后，添加 AI 回复消息
          const aiMsg = {
            id: `ai_${Date.now()}`,
            role: 'assistant',
            content: res.data.data.answer || '回答生成中...'
          }
          messages.value.push(aiMsg)
        } else {
          throw new Error(res.data?.message || '请求失败')
        }
      } catch (error) {
        console.error('[对话] 发送失败:', error)
        // 请求失败后，添加错误消息
        const errorMsg = {
          id: `ai_${Date.now()}`,
          role: 'assistant',
          content: '抱歉，回复失败了。错误: ' + (error.message || '网络错误')
        }
        messages.value.push(errorMsg)
      } finally {
        isStreaming.value = false
      }
    }

    onMounted(() => {
      // 获取 URL 参数
      const pages = getCurrentPages()
      const currentPage = pages[pages.length - 1]
      const options = currentPage.options

      if (options.userInfo) {
        try {
          userInfo.value = JSON.parse(decodeURIComponent(options.userInfo))
          console.log('[结果页面] 用户信息:', userInfo.value)
          
          // 开始请求分析
          requestAnalysis()
        } catch (e) {
          console.error('[结果页面] 解析用户信息失败:', e)
          analysis.value = '参数错误，请返回重试'
          isAnalyzing.value = false
        }
      } else {
        analysis.value = '缺少用户信息，请返回重试'
        isAnalyzing.value = false
      }
    })

    return {
      analysis,
      messages,
      inputText,
      isStreaming,
      isAnalyzing,
      scrollToId,
      canSend,
      sendMessage,
      formatText,
      goHome
    }
  }
}
</script>

<style scoped>
.result-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f6f8;
}

/* 自定义导航栏 */
.custom-navbar {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 44px;
  background: #667eea;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  z-index: 999;
}

.navbar-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  color: #fff;
  font-size: 15px;
  cursor: pointer;
  transition: opacity 0.2s;
}

.navbar-btn:active {
  opacity: 0.7;
}

.navbar-btn .icon {
  font-size: 20px;
  font-weight: bold;
}

.navbar-title {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  color: #fff;
  font-size: 17px;
  font-weight: bold;
}

.navbar-placeholder {
  width: 80px;
}

/* 消息列表 */
.message-list {
  flex: 1;
  padding: 60px 16px 16px 16px; /* 上方留出导航栏空间 */
  overflow-y: auto;
}

.message-item {
  margin-bottom: 20px;
}

/* 用户消息 */
.user-message {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.user-message .message-content {
  max-width: 70%;
  padding: 12px 16px;
  background: #667eea;
  color: #fff;
  border-radius: 16px 16px 4px 16px;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

/* AI消息 */
.assistant-message {
  display: flex;
  gap: 10px;
}

.assistant-message .message-content {
  max-width: 85%;
  padding: 12px 16px;
  background: #fff;
  color: #333;
  border-radius: 16px 16px 16px 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
}

.user-avatar {
  background: #667eea;
  color: #fff;
}

.ai-avatar {
  background: #45B7D1;
  color: #fff;
}

.message-text {
  font-size: 15px;
  line-height: 1.6;
  word-break: break-word;
}

/* Markdown 样式 */
.message-text :deep(h1),
.message-text :deep(h2),
.message-text :deep(h3) {
  margin: 16px 0 8px 0;
  font-weight: bold;
  line-height: 1.4;
}

.message-text :deep(h1) { font-size: 20px; }
.message-text :deep(h2) { font-size: 18px; }
.message-text :deep(h3) { font-size: 16px; }

.message-text :deep(p) {
  margin: 8px 0;
}

.message-text :deep(ul),
.message-text :deep(ol) {
  margin: 8px 0;
  padding-left: 20px;
}

.message-text :deep(li) {
  margin: 4px 0;
}

.message-text :deep(code) {
  background: #f5f5f5;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 14px;
}

.message-text :deep(pre) {
  background: #f5f5f5;
  padding: 12px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 8px 0;
}

.message-text :deep(pre code) {
  background: none;
  padding: 0;
}

.message-text :deep(blockquote) {
  border-left: 4px solid #667eea;
  padding-left: 12px;
  margin: 8px 0;
  color: #666;
}

.message-text :deep(strong) {
  font-weight: bold;
  color: #333;
}

.message-text :deep(em) {
  font-style: italic;
}

.message-text :deep(a) {
  color: #667eea;
  text-decoration: underline;
}

.message-text :deep(hr) {
  border: none;
  border-top: 1px solid #e0e0e0;
  margin: 16px 0;
}

.message-text :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 8px 0;
}

.message-text :deep(th),
.message-text :deep(td) {
  border: 1px solid #e0e0e0;
  padding: 8px;
  text-align: left;
}

.message-text :deep(th) {
  background: #f5f5f5;
  font-weight: bold;
}

.message-text :deep(br) {
  display: block;
  content: "";
  margin: 4px 0;
}

/* 分析中状态 */
.analyzing {
  display: flex;
  align-items: center;
  gap: 10px;
}

.loading-spinner {
  font-size: 24px;
  animation: spin 2s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.loading-text {
  font-size: 15px;
  color: #666;
}

/* 输入栏 */
.input-bar {
  position: sticky;
  bottom: 0;
  left: 0;
  width: 100%;
  background: #fff;
  padding: 12px 16px;
  box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.05);
}

.input-container {
  display: flex;
  align-items: flex-end;
  gap: 10px;
}

.input-text {
  flex: 1;
  min-height: 40px;
  max-height: 120px;
  background: #f0f0f0;
  border-radius: 20px;
  padding: 10px 15px;
  font-size: 15px;
  line-height: 1.5;
}

.send-btn {
  width: 40px;
  height: 40px;
  border-radius: 20px;
  background: #e5e5e5;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 20px;
  transition: all 0.3s;
}

.send-btn.active {
  background: #667eea;
}

.send-btn.active .icon {
  color: #fff;
}

.typing-indicator {
  display: flex;
  align-items: center;
  height: 20px;
}

.typing-indicator span {
  width: 6px;
  height: 6px;
  background-color: #ccc;
  border-radius: 50%;
  margin: 0 2px;
  animation: bounce 1.4s infinite ease-in-out both;
}

.typing-indicator span:nth-child(1) {
  animation-delay: -0.32s;
}
.typing-indicator span:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes bounce {
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
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
