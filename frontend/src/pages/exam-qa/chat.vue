<template>
  <view class="chat-page">
    <!-- 消息列表 -->
    <scroll-view
      class="message-list"
      scroll-y
      :scroll-into-view="scrollToId"
      scroll-with-animation
    >
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
            <image v-if="msg.image_url" :src="msg.image_url" class="message-image" mode="widthFix" @click="previewImage(msg.image_url)" />
            <!-- 用户消息也支持 Markdown/LaTeX 渲染 -->
            <view class="message-text markdown-body" v-html="renderMarkdown(msg.content)"></view>
          </view>
          <view class="avatar user-avatar">👤</view>
        </view>

        <!-- AI消息 -->
        <view v-else-if="msg.role === 'assistant'" class="assistant-message">
          <view class="avatar ai-avatar">🤖</view>
          <view class="message-content">
            <!-- 如果有图片，先显示图片 -->
            <image v-if="msg.image_url" :src="msg.image_url" class="message-image" mode="widthFix" @click="previewImage(msg.image_url)" />
            <!-- Markdown 内容 -->
            <view class="message-text markdown-body" v-html="renderMarkdown(msg.content)"></view>
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
    <view class="input-bar" :style="{ paddingBottom: keyboardHeight + 'px' }">
      <!-- 图片预览 -->
      <view v-if="selectedImage" class="image-preview">
        <image :src="selectedImage" mode="aspectFill" class="preview-img" />
        <view class="remove-img" @click="removeImage">✕</view>
      </view>

      <view class="input-container">
        <view class="image-btn touchable" @click="selectImage">
          <text class="icon">📷</text>
        </view>
        
        <textarea
          class="input-text"
          v-model="inputText"
          placeholder="输入你的问题..."
          :auto-height="true"
          :maxlength="2000"
          :adjust-position="false"
          @focus="onInputFocus"
          @blur="onInputBlur"
        />
        
        <view
          class="send-btn touchable"
          :class="{ active: canSend }"
          @click="sendMessage"
        >
          <text class="icon">📤</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { ref, computed, onMounted, nextTick } from 'vue'
import { conversationApi } from '@/api'
import { marked } from 'marked'
import katex from 'katex'

export default {
  setup() {
    const conversationId = ref('')
    const messages = ref([])
    const inputText = ref('')
    const selectedImage = ref('')
    const selectedImageUrl = ref('')
    const isStreaming = ref(false)
    const scrollToId = ref('')
    const keyboardHeight = ref(0)

    // 配置 marked 渲染器
    const renderer = new marked.Renderer()
    
    // 自定义图片渲染
    renderer.image = function(href, title, text) {
      const imageSrc = href
      const titleAttr = title ? ` title="${title}"` : ''
      const altAttr = text ? ` alt="${text}"` : ''
      return `<img src="${imageSrc}"${titleAttr}${altAttr} style="max-width: 100%; border-radius: 8px; margin: 8px 0; cursor: pointer;" />`
    }
    
    // 自定义段落渲染（去除多余的空段落）
    renderer.paragraph = function(text) {
      if (!text || !text.trim()) {
        return ''
      }
      return `<p style="margin: 2px 0;">${text}</p>`
    }
    
    // 配置 marked（不再使用 marked-katex-extension，改为手动处理）
    marked.setOptions({
      renderer: renderer,
      breaks: true,
      gfm: true,
      pedantic: false
    })

    // 是否可以发送
    const canSend = computed(() => {
      return (inputText.value.trim() || selectedImage.value) && !isStreaming.value
    })

    // 加载消息历史
    const loadMessages = async () => {
      // 如果正在流式接收，不要重新加载
      if (isStreaming.value) {
        console.log('正在流式接收，跳过加载历史消息')
        return
      }
      
      try {
        const res = await conversationApi.getMessages(conversationId.value)
        if (res && res.code === 0) {
          messages.value = res.data || []
          await nextTick()
          scrollToBottom()
        }
      } catch (error) {
        console.error('加载消息失败:', error)
      }
    }

    // 选择图片
    const selectImage = () => {
      uni.chooseImage({
        count: 1,
        sizeType: ['compressed'],
        sourceType: ['album', 'camera'],
        success: (res) => {
          selectedImage.value = res.tempFilePaths[0]
        }
      })
    }

    // 移除图片
    const removeImage = () => {
      selectedImage.value = ''
      selectedImageUrl.value = ''
    }

    // 预览图片
    const previewImage = (url) => {
      uni.previewImage({
        urls: [url],
        current: url
      })
    }

    // 发送消息
    const sendMessage = async () => {
      if (!canSend.value) return

      const content = inputText.value.trim()
      let imageUrl = selectedImageUrl.value

      // 如果有图片，先上传
      if (selectedImage.value && !imageUrl) {
        try {
          uni.showLoading({ title: '上传图片中...' })
          const uploadRes = await conversationApi.uploadImage(selectedImage.value)
          uni.hideLoading()
          
          if (uploadRes && uploadRes.code === 0) {
            imageUrl = uploadRes.data.url
            selectedImageUrl.value = imageUrl
          } else {
            throw new Error('上传失败')
          }
        } catch (error) {
          uni.hideLoading()
          console.error('上传图片失败:', error)
          uni.showToast({
            title: '图片上传失败',
            icon: 'none'
          })
          return
        }
      }

      if (!content && !imageUrl) {
        uni.showToast({
          title: '请输入内容',
          icon: 'none'
        })
        return
      }

      // 添加用户消息到列表
      const userMsg = {
        id: `temp_${Date.now()}`,
        role: 'user',
        content: content,
        image_url: imageUrl,
        created_at: new Date().toISOString()
      }
      messages.value.push(userMsg)

      // 清空输入
      inputText.value = ''
      selectedImage.value = ''
      selectedImageUrl.value = ''

      // 滚动到底部
      await nextTick()
      scrollToBottom()

      // 开始流式接收
      isStreaming.value = true
      
      // 创建临时 AI 消息（注意：不要立即添加到列表，等收到第一个chunk再添加）
      const tempAiMsg = {
        id: `temp_ai_${Date.now()}`,
        role: 'assistant',
        content: '',
        created_at: new Date().toISOString()
      }
      
      let hasAddedAiMsg = false  // 标记是否已添加AI消息到列表

      try {
        await streamMessage(content, imageUrl, tempAiMsg, () => {
          // 收到第一个chunk时的回调
          if (!hasAddedAiMsg) {
            messages.value.push(tempAiMsg)
            hasAddedAiMsg = true
          }
        })
      } catch (error) {
        console.error('发送消息失败:', error)
        // 只有已添加的消息才需要移除
        if (hasAddedAiMsg) {
          messages.value = messages.value.filter(m => m.id !== tempAiMsg.id)
        }
        uni.showToast({
          title: '发送失败',
          icon: 'none'
        })
      } finally {
        isStreaming.value = false
      }
    }

    // 流式接收消息
    const streamMessage = (content, imageUrl, tempAiMsg, onFirstChunk) => {
      return new Promise((resolve, reject) => {
        // #ifdef H5
        const baseURL = '/api'
        // #endif
        // #ifndef H5
        const baseURL = 'http://localhost:8000/api'
        // #endif

        const url = `${baseURL}/exam-qa/conversations/${conversationId.value}/messages`
        
        // 使用 fetch API 处理流式响应（仅 H5）
        // #ifdef H5
        let isDone = false  // 标记是否已完成
        let isFirstChunk = true  // 标记是否是第一个chunk
        
        fetch(url, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            content: content,
            image_url: imageUrl
          })
        })
          .then(response => {
            if (!response.ok) {
              throw new Error(`HTTP error! status: ${response.status}`)
            }
            
            const reader = response.body.getReader()
            const decoder = new TextDecoder()
            let buffer = '' // 缓冲区，存储未完成的行
            
            // 读取流式数据
            function processText(text) {
              // 将新数据添加到缓冲区
              buffer += text
              
              // 按行分割
              const lines = buffer.split('\n')
              
              // 最后一行可能不完整，保留在缓冲区
              buffer = lines.pop() || ''
              
              // 处理每一行
              for (const line of lines) {
                if (line.startsWith('data:')) {
                  const dataStr = line.substring(5).trim()
                      if (dataStr) {
                        try {
                          const data = JSON.parse(dataStr)
                          console.log('收到数据:', data)
                          
                          if (data.type === 'chunk') {
                            // 旧的逐块流式方式（兼容）
                            if (isFirstChunk && onFirstChunk) {
                              onFirstChunk()
                              isFirstChunk = false
                            }
                            
                            // 合并内容
                            tempAiMsg.content += data.content
                            
                            // 强制更新视图
                            messages.value = [...messages.value]
                            // 滚动到底部
                            nextTick(() => scrollToBottom())
                          } else if (data.type === 'content') {
                            // 新的一次性完整内容方式
                            if (isFirstChunk && onFirstChunk) {
                              onFirstChunk()
                              isFirstChunk = false
                            }
                            
                            // 直接替换整个内容
                            tempAiMsg.content = data.content
                            
                            // 强制更新视图
                            messages.value = [...messages.value]
                            // 滚动到底部
                            nextTick(() => scrollToBottom())
                          } else if (data.type === 'done') {
                        tempAiMsg.id = data.message_id
                        console.log('对话完成，message_id:', data.message_id)
                        isDone = true
                        // 关闭 reader 并 resolve
                        reader.cancel()
                        resolve()
                      } else if (data.type === 'error') {
                        console.error('服务器错误:', data.message)
                        isDone = true
                        reader.cancel()
                        reject(new Error(data.message))
                      }
                    } catch (e) {
                      console.error('解析SSE数据失败:', e, dataStr)
                    }
                  }
                }
              }
            }
            
            function readStream() {
              if (isDone) {
                return
              }
              
              reader.read().then(({ done, value }) => {
                if (done) {
                  console.log('流式响应结束')
                  // 处理缓冲区中剩余的数据
                  if (buffer.trim()) {
                    processText('\n')
                  }
                  if (!isDone) {
                    resolve()
                  }
                  return
                }
                
                // 解码数据并处理
                const text = decoder.decode(value, { stream: true })
                processText(text)
                
                // 继续读取下一块
                if (!isDone) {
                  readStream()
                }
              }).catch(err => {
                if (!isDone) {
                  console.error('读取流失败:', err)
                  reject(err)
                }
              })
            }
            
            readStream()
          })
          .catch(err => {
            console.error('Fetch 失败:', err)
            reject(err)
          })
        // #endif
        
        // #ifndef H5
        // 非 H5 平台使用 uni.request（需要后续优化）
        uni.request({
          url: url,
          method: 'POST',
          data: {
            content: content,
            image_url: imageUrl
          },
          header: {
            'Content-Type': 'application/json'
          },
          timeout: 60000,
          success: (res) => {
            if (res.statusCode === 200) {
              // 简单处理：直接显示最终结果
              tempAiMsg.content = res.data.answer || '回复失败'
              resolve()
            } else {
              reject(new Error(`请求失败: ${res.statusCode}`))
            }
          },
          fail: (err) => {
            reject(err)
          }
        })
        // #endif
      })
    }

    // 渲染 Markdown
    const renderMarkdown = (content) => {
      try {
        // 预处理：减少过多的连续换行（将3个及以上的换行符压缩为2个）
        let processedContent = content || ''
        processedContent = processedContent.replace(/\n{3,}/g, '\n\n')
        
        // 手动处理 LaTeX 公式，避免 marked-katex-extension 的匹配问题
        // 1. 先提取所有公式，用占位符替换
        const formulas = []
        let formulaIndex = 0
        
        // 处理块级公式 $$...$$
        processedContent = processedContent.replace(/\$\$([^$]+?)\$\$/g, (match, formula) => {
          const placeholder = `BLOCKFORMULA${formulaIndex}BLOCKFORMULA`
          formulas.push({ type: 'block', formula: formula.trim(), placeholder })
          console.log('[KaTeX] 提取块级公式:', formula.trim(), '→', placeholder)
          formulaIndex++
          return placeholder
        })
        
        // 处理行内公式 $...$（使用非贪婪匹配，且不能跨行）
        processedContent = processedContent.replace(/\$([^\n$]+?)\$/g, (match, formula) => {
          const placeholder = `INLINEFORMULA${formulaIndex}INLINEFORMULA`
          formulas.push({ type: 'inline', formula: formula.trim(), placeholder })
          console.log('[KaTeX] 提取行内公式:', formula.trim(), '→', placeholder)
          formulaIndex++
          return placeholder
        })
        
        console.log('[KaTeX] 共提取', formulas.length, '个公式')
        console.log('[KaTeX] 替换后的内容:', processedContent.substring(0, 200))
        
        // 2. 用 marked 渲染 Markdown（不包含公式）
        let html = marked.parse(processedContent)
        
        console.log('[KaTeX] Markdown 渲染后:', html.substring(0, 300))
        
        // 3. 将占位符替换为渲染后的 KaTeX HTML
        formulas.forEach(item => {
          try {
            const rendered = katex.renderToString(item.formula, {
              throwOnError: false,
              displayMode: item.type === 'block',
              strict: false,
              output: 'html'
            })
            console.log('[KaTeX] 渲染公式:', item.formula, '→ 成功 (长度:', rendered.length, ')')
            
            // 检查占位符是否存在
            if (html.includes(item.placeholder)) {
              html = html.replace(new RegExp(item.placeholder, 'g'), rendered)
              console.log('[KaTeX] 替换占位符成功:', item.placeholder)
            } else {
              console.warn('[KaTeX] 占位符未找到:', item.placeholder)
              console.warn('[KaTeX] HTML 中的内容:', html.substring(0, 500))
            }
          } catch (e) {
            console.error('[KaTeX] 渲染公式失败:', item.formula, e)
            // 如果渲染失败，保留原始公式
            const original = item.type === 'block' ? `$$${item.formula}$$` : `$${item.formula}$`
            html = html.replace(new RegExp(item.placeholder, 'g'), original)
          }
        })
        
        console.log('[KaTeX] 最终 HTML:', html.substring(0, 300))
        
        return html
      } catch (error) {
        console.error('Markdown 渲染失败:', error)
        return content
      }
    }

    // 滚动到底部
    const scrollToBottom = () => {
      if (messages.value.length > 0) {
        scrollToId.value = `msg-${messages.value.length - 1}`
      }
    }

    // 输入框聚焦
    const onInputFocus = (e) => {
      keyboardHeight.value = e.detail.height || 0
      setTimeout(() => scrollToBottom(), 300)
    }

    // 输入框失焦
    const onInputBlur = () => {
      keyboardHeight.value = 0
    }

    onMounted(() => {
      // 获取对话 ID
      const pages = getCurrentPages()
      const currentPage = pages[pages.length - 1]
      conversationId.value = currentPage.options.id || ''

      if (conversationId.value) {
        loadMessages()
      }
    })

    return {
      messages,
      inputText,
      selectedImage,
      isStreaming,
      scrollToId,
      keyboardHeight,
      canSend,
      selectImage,
      removeImage,
      previewImage,
      sendMessage,
      renderMarkdown,
      onInputFocus,
      onInputBlur
    }
  }
}
</script>

<style scoped>
/* KaTeX 样式已在 App.vue 全局引入 */

.chat-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f6f8;
}

/* 消息列表 */
.message-list {
  flex: 1;
  padding: 16px;
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
  max-width: 80%;
  padding: 12px 16px;
  background: #fff;
  color: #333;
  border-radius: 16px 16px 16px 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

/* 头像 */
.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  flex-shrink: 0;
}

.user-avatar {
  background: #667eea;
}

.ai-avatar {
  background: #f0f0f0;
}

/* 消息内容 */
.message-text {
  word-wrap: break-word;
  white-space: pre-wrap;
  line-height: 1.6;
}

.message-image {
  width: 100%;
  max-width: 200px;
  border-radius: 8px;
  margin-bottom: 8px;
}

/* Markdown 样式 */
.markdown-body {
  font-size: 15px;
  line-height: 1.5;  /* 减小行高 */
}

.markdown-body :deep(p) {
  margin: 2px 0;  /* 进一步减小段落间距 */
}

.markdown-body :deep(p:empty) {
  display: none;  /* 隐藏空段落 */
  margin: 0;
  padding: 0;
  height: 0;
}

.markdown-body :deep(br:last-child) {
  display: none;  /* 隐藏末尾的换行 */
}

.markdown-body :deep(img) {
  max-width: 100%;
  border-radius: 8px;
  margin: 8px 0;
  display: block;
}

.markdown-body :deep(h1),
.markdown-body :deep(h2),
.markdown-body :deep(h3),
.markdown-body :deep(h4) {
  margin: 10px 0 4px 0;  /* 标题上下间距 */
  font-weight: bold;
}

.markdown-body :deep(hr) {
  margin: 6px 0;  /* 进一步减小分隔线间距 */
  border: none;
  border-top: 1px solid #e0e0e0;
}

.markdown-body :deep(ul),
.markdown-body :deep(ol) {
  margin: 2px 0;
  padding-left: 20px;
}

.markdown-body :deep(li) {
  margin: 1px 0;
}

.markdown-body :deep(code) {
  background: #f4f4f4;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 14px;
}

.markdown-body :deep(pre) {
  background: #2d2d2d;
  color: #f8f8f2;
  padding: 12px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 6px 0;  /* 进一步减小代码块间距 */
}

.markdown-body :deep(pre code) {
  background: transparent;
  color: inherit;
  padding: 0;
}

.markdown-body :deep(strong) {
  font-weight: bold;
  color: #333;
}

.markdown-body :deep(em) {
  font-style: italic;
}

.markdown-body :deep(blockquote) {
  margin: 4px 0;
  padding-left: 10px;
  border-left: 3px solid #ddd;
  color: #666;
}

/* KaTeX 数学公式样式 */
.markdown-body :deep(.katex) {
  font-size: 1.1em;
}

.markdown-body :deep(.katex-display) {
  margin: 8px 0;
  overflow-x: auto;
  overflow-y: hidden;
}

.markdown-body :deep(.katex-html) {
  white-space: nowrap;
}

/* 打字指示器 */
.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 8px 0;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background: #999;
  border-radius: 50%;
  animation: typing 1.4s infinite;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    opacity: 0.3;
    transform: translateY(0);
  }
  30% {
    opacity: 1;
    transform: translateY(-8px);
  }
}

/* 输入栏 */
.input-bar {
  background: #fff;
  border-top: 1px solid #e5e5e5;
  padding: 12px 16px;
  transition: padding-bottom 0.3s;
}

.image-preview {
  position: relative;
  width: 80px;
  height: 80px;
  margin-bottom: 12px;
}

.preview-img {
  width: 100%;
  height: 100%;
  border-radius: 8px;
  object-fit: cover;
}

.remove-img {
  position: absolute;
  top: -8px;
  right: -8px;
  width: 24px;
  height: 24px;
  background: #ff4d4f;
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: bold;
}

.input-container {
  display: flex;
  align-items: flex-end;
  gap: 12px;
}

.image-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 24px;
}

.input-text {
  flex: 1;
  min-height: 40px;
  max-height: 120px;
  padding: 10px 16px;
  background: #f5f6f8;
  border-radius: 20px;
  font-size: 15px;
  line-height: 1.5;
}

.send-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
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

/* 触摸反馈 */
.touchable {
  transition: all 0.2s ease;
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
  user-select: none;
}

.touchable:active {
  transform: scale(0.95);
  opacity: 0.8;
}
</style>

