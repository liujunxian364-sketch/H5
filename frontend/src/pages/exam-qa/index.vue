<template>
  <view class="conversation-list-page">
    <!-- 头部 -->
    <view class="header">
      <text class="title">考点答疑</text>
      <view class="new-btn touchable" @click="createNewConversation">
        <text class="icon">➕</text>
        <text class="text">新对话</text>
      </view>
    </view>

    <!-- 对话列表 -->
    <view class="conversation-list" v-if="conversations.length > 0">
      <view
        v-for="conv in conversations"
        :key="conv.id"
        class="conversation-item touchable"
        @click="goToChat(conv.id)"
      >
        <view class="conv-icon">💬</view>
        <view class="conv-info">
          <view class="conv-title">{{ conv.title }}</view>
          <view class="conv-last-msg">{{ conv.last_message || '开始新对话...' }}</view>
        </view>
        <view class="conv-meta">
          <text class="conv-time">{{ formatTime(conv.updated_at) }}</text>
          <view class="delete-btn" @click.stop="deleteConversation(conv.id)">
            <text>🗑️</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 空状态 -->
    <view class="empty-state" v-else>
      <text class="empty-icon">💭</text>
      <text class="empty-text">还没有对话记录</text>
      <text class="empty-hint">点击右上角"新对话"开始提问</text>
    </view>

    <!-- 加载状态 -->
    <view class="loading" v-if="loading">
      <text>加载中...</text>
    </view>
  </view>
</template>

<script>
import { ref, onMounted, onActivated } from 'vue'
import { conversationApi } from '@/api'

export default {
  setup() {
    const conversations = ref([])
    const loading = ref(false)

    // 加载对话列表
    const loadConversations = async () => {
      loading.value = true
      try {
        console.log('[对话列表] 开始加载对话列表，请求 URL:', '/api/exam-qa/conversations')
        const res = await conversationApi.getList()
        console.log('[对话列表] API 响应:', res)
        if (res && res.code === 0) {
          conversations.value = res.data || []
          console.log('[对话列表] 加载了', conversations.value.length, '个对话')
        } else {
          console.error('[对话列表] API 返回错误:', res)
          uni.showToast({
            title: res.message || '加载失败',
            icon: 'none'
          })
        }
      } catch (error) {
        console.error('[对话列表] 加载对话列表失败:', error)
        console.error('[对话列表] 错误详情:', {
          message: error.message,
          stack: error.stack,
          error: error
        })
        uni.showToast({
          title: `加载失败: ${error.message || '网络错误'}`,
          icon: 'none',
          duration: 3000
        })
      } finally {
        loading.value = false
      }
    }

    // 创建新对话
    const createNewConversation = async () => {
      try {
        const res = await conversationApi.create({ title: '新对话' })
        if (res && res.code === 0) {
          const newConv = res.data
          // 直接跳转到对话页面
          goToChat(newConv.id)
        }
      } catch (error) {
        console.error('创建对话失败:', error)
        uni.showToast({
          title: '创建失败',
          icon: 'none'
        })
      }
    }

    // 跳转到对话页面
    const goToChat = (conversationId) => {
      uni.navigateTo({
        url: `/pages/exam-qa/chat?id=${conversationId}`
      })
    }

    // 删除对话
    const deleteConversation = (conversationId) => {
      uni.showModal({
        title: '确认删除',
        content: '确定要删除这个对话吗？',
        success: async (res) => {
          if (res.confirm) {
            try {
              await conversationApi.delete(conversationId)
              // 从列表中移除
              conversations.value = conversations.value.filter(
                (c) => c.id !== conversationId
              )
              uni.showToast({
                title: '删除成功',
                icon: 'success'
              })
            } catch (error) {
              console.error('删除对话失败:', error)
              uni.showToast({
                title: '删除失败',
                icon: 'none'
              })
            }
          }
        }
      })
    }

    // 格式化时间
    const formatTime = (timeStr) => {
      const date = new Date(timeStr)
      const now = new Date()
      const diff = now - date

      // 1分钟内
      if (diff < 60000) {
        return '刚刚'
      }
      // 1小时内
      if (diff < 3600000) {
        return `${Math.floor(diff / 60000)}分钟前`
      }
      // 今天
      if (date.toDateString() === now.toDateString()) {
        return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
      }
      // 昨天
      const yesterday = new Date(now)
      yesterday.setDate(yesterday.getDate() - 1)
      if (date.toDateString() === yesterday.toDateString()) {
        return '昨天'
      }
      // 更早
      return date.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' })
    }

    onMounted(() => {
      console.log('[对话列表] onMounted - 首次加载')
      loadConversations()
    })

    // 使用 onActivated 代替 onShow（在 keep-alive 组件中生效）
    // 当从对话页面返回时会触发
    onActivated(() => {
      console.log('[对话列表] onActivated - 页面激活，重新加载')
      loadConversations()
    })

    return {
      conversations,
      loading,
      loadConversations,
      createNewConversation,
      goToChat,
      deleteConversation,
      formatTime
    }
  }
}
</script>

<style scoped>
.conversation-list-page {
  min-height: 100vh;
  background: #f5f6f8;
}

/* 头部 */
.header {
  position: sticky;
  top: 0;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background: #45B7D1;
  color: #fff;
}

.header .title {
  font-size: 20px;
  font-weight: 600;
}

.new-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  font-size: 14px;
}

.new-btn .icon {
  font-size: 16px;
}

/* 对话列表 */
.conversation-list {
  padding: 12px 16px;
}

.conversation-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  margin-bottom: 12px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.conv-icon {
  font-size: 32px;
  flex-shrink: 0;
}

.conv-info {
  flex: 1;
  min-width: 0;
}

.conv-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 6px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.conv-last-msg {
  font-size: 14px;
  color: #999;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.conv-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 8px;
  flex-shrink: 0;
}

.conv-time {
  font-size: 12px;
  color: #999;
}

.delete-btn {
  padding: 4px;
  font-size: 20px;
  opacity: 0.6;
}

.delete-btn:active {
  opacity: 1;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 40px;
  text-align: center;
}

.empty-icon {
  font-size: 80px;
  margin-bottom: 20px;
  opacity: 0.3;
}

.empty-text {
  font-size: 16px;
  color: #666;
  margin-bottom: 12px;
}

.empty-hint {
  font-size: 14px;
  color: #999;
}

/* 加载状态 */
.loading {
  text-align: center;
  padding: 20px;
  color: #999;
  font-size: 14px;
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
