<template>
  <view class="page flex-col">
    <!-- 主要内容 -->
    <view class="group_2 flex-col">
      <view class="box_1 flex-col">
        <!-- 顶部装饰条 -->
        <view class="section_1 flex-row"></view>
        
        <!-- 用户信息 -->
        <view class="section_2 flex-row justify-between">
          <view class="image-wrapper_2 flex-col">
            <text class="avatar-text">👤</text>
          </view>
          <view class="text-group_1 flex-col justify-between">
            <text class="text_1">移动学习平台</text>
            <text class="text_2">智能学习，高效提升</text>
          </view>
        </view>

        <!-- 第一行：错题记忆 + 单词速记 -->
        <view class="section_3 flex-row justify-between">
          <view 
            class="block_2 flex-row justify-end touchable"
            @click="goToModule('/pages/error-memory/index')"
          >
            <view class="text-wrapper_1 flex-col justify-between">
              <text class="text_3">错题记忆</text>
              <text class="text_4">错题归类/个性报告</text>
            </view>
            <text class="module-icon">📝</text>
          </view>

          <view 
            class="block_3 flex-row touchable"
            @click="goToModule('/pages/word-memory/index')"
          >
            <view class="text-group_2 flex-col justify-between">
              <text class="text_5">单词速记</text>
              <text class="text_6">智能标错/加深记忆</text>
            </view>
            <text class="module-icon">📚</text>
          </view>
        </view>

        <!-- 第二行：考点答疑 + 学商速测 -->
        <view class="section_4 flex-row justify-between">
          <view 
            class="box_3 flex-row touchable"
            @click="goToModule('/pages/exam-qa/index')"
          >
            <view class="text-group_3 flex-col justify-between">
              <text class="text_7">考点答疑</text>
              <text class="text_8">引导解析/伴随成长</text>
            </view>
            <text class="module-icon">💡</text>
          </view>

          <view 
            class="box_4 flex-row touchable"
            @click="goToModule('/pages/iq-test/index')"
          >
            <view class="text-group_4 flex-col justify-between">
              <text class="text_9">学商速测</text>
              <text class="text_10">性格测试/规划</text>
            </view>
            <text class="module-icon">🎯</text>
          </view>
        </view>
      </view>

      <!-- 资讯列表 -->
      <view class="news-title">最新资讯</view>
      <view class="box_5 flex-col touchable" v-for="item in newsList" :key="item.id" @click="goToNews(item.id)">
        <view class="text-group_5 flex-col justify-between">
          <text class="text_11">{{ item.title }}</text>
          <text class="text_12">#教育资讯#</text>
        </view>
        <image class="image_8" :src="item.image" mode="aspectFill" lazy-load />
      </view>
    </view>
  </view>
</template>

<script>
import { ref, onMounted } from 'vue'
import { newsApi } from '@/api'

export default {
  setup() {
    const modules = [
      { 
        name: '错题记忆', 
        path: '/pages/error-memory/index', 
        icon: '📝', 
        color: '#FF6B6B',
        desc: '拍照记录'
      },
      { 
        name: '单词速记', 
        path: '/pages/word-memory/index', 
        icon: '📚', 
        color: '#4ECDC4',
        desc: '高效背词'
      },
      { 
        name: '考点答疑', 
        path: '/pages/exam-qa/index', 
        icon: '💡', 
        color: '#45B7D1',
        desc: 'AI助手'
      },
      { 
        name: '学商速测', 
        path: '/pages/iq-test/index', 
        icon: '🎯', 
        color: '#96CEB4',
        desc: '能力评估'
      }
    ]

    const newsList = ref([])

    const goToModule = (path) => {
      uni.navigateTo({
        url: path
      })
    }

    const goToNews = (id) => {
      uni.navigateTo({
        url: `/pages/news/detail?id=${id}`
      })
    }

    const fetchNews = async () => {
      try {
        const res = await newsApi.getList({ page: 1, pageSize: 10 })
        if (res && res.code === 0) {
          newsList.value = res.data || []
        } else {
          throw new Error('API返回数据格式错误')
        }
      } catch (error) {
        console.error('获取资讯失败:', error)
        // 使用模拟数据
        newsList.value = [
          {
            id: 1,
            title: '2024年考研英语备考攻略',
            summary: '考研英语是很多同学的难点，本文将从词汇、阅读、写作三个方面为大家详细讲解备考技巧...',
            image: 'https://picsum.photos/200/120?random=1',
            createTime: '2024-01-15',
            views: 1523
          },
          {
            id: 2,
            title: '高效记忆法：艾宾浩斯遗忘曲线的应用',
            summary: '艾宾浩斯遗忘曲线告诉我们，记忆会随时间逐渐衰退，但通过科学的复习方法可以有效巩固记忆...',
            image: 'https://picsum.photos/200/120?random=2',
            createTime: '2024-01-14',
            views: 892
          },
          {
            id: 3,
            title: '如何提高学习效率？这5个方法值得一试',
            summary: '学习效率的高低直接影响学习成果，掌握正确的学习方法能让你事半功倍...',
            image: 'https://picsum.photos/200/120?random=3',
            createTime: '2024-01-13',
            views: 2341
          }
        ]
      }
    }

    onMounted(() => {
      console.log('首页组件已挂载', new Date().toISOString())
      fetchNews()
    })

    return {
      modules,
      newsList,
      goToModule,
      goToNews
    }
  }
}
</script>

<style scoped>
/* ==================== 全局 flex 类 ==================== */
.flex-col {
  display: flex;
  flex-direction: column;
}

.flex-row {
  display: flex;
  flex-direction: row;
}

.justify-between {
  justify-content: space-between;
}

.justify-end {
  justify-content: flex-end;
}

/* ==================== 主容器 - 天蓝色拼接色块 ==================== */
.page {
  width: 100%;
  min-height: 100vh;
  background: #87CEEB; /* 天蓝色 Sky Blue */
  padding-bottom: calc(20px + constant(safe-area-inset-bottom));
  padding-bottom: calc(20px + env(safe-area-inset-bottom));
  position: relative;
  overflow: hidden;
}

/* 拼接色块 - 左上角深蓝 */
.page::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 45%;
  height: 280px;
  background: #5DADE2; /* 深一点的天蓝 */
  clip-path: polygon(0 0, 100% 0, 0 100%);
  z-index: 0;
}

/* 拼接色块 - 右上角浅蓝 */
.page::after {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 40%;
  height: 220px;
  background: #AED6F1; /* 浅一点的天蓝 */
  clip-path: polygon(100% 0, 100% 100%, 40% 100%);
  z-index: 0;
}

/* 底部拼接色块 */
.group_2::before {
  content: '';
  position: absolute;
  bottom: -100px;
  left: -50px;
  width: 200px;
  height: 200px;
  background: #5DADE2;
  border-radius: 50%;
  opacity: 0.3;
  z-index: 0;
}

.group_2::after {
  content: '';
  position: absolute;
  bottom: -80px;
  right: -30px;
  width: 150px;
  height: 150px;
  background: #AED6F1;
  clip-path: polygon(50% 0%, 100% 50%, 50% 100%, 0% 50%);
  opacity: 0.4;
  z-index: 0;
}

/* 主内容区 */
.group_2 {
  padding: 0 16px 20px;
  position: relative;
  z-index: 1;
}

.box_1 {
  background: #ffffff;
  border-radius: 16px;
  padding: 16px;
  margin-top: 20px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

/* 顶部装饰条 */
.section_1 {
  width: 100%;
  height: 4px;
  background: #87CEEB;
  border-radius: 2px;
  margin-bottom: 16px;
}

/* 用户信息区域 */
.section_2 {
  margin-bottom: 20px;
  padding: 12px;
  background: #F0F8FF; /* 淡蓝色 Alice Blue */
  border-radius: 12px;
  align-items: center;
}

.image-wrapper_2 {
  margin-right: 12px;
  width: 60px;
  height: 60px;
  border-radius: 30px;
  background: #87CEEB;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-text {
  font-size: 32px;
}

.text-group_1 {
  flex: 1;
}

.text_1 {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin-bottom: 6px;
  display: block;
}

.text_2 {
  font-size: 14px;
  color: #999;
  display: block;
}

/* ==================== 功能按钮区域 ==================== */

/* 第一行：错题记忆 + 单词速记 */
.section_3 {
  gap: 12px;
  margin-bottom: 12px;
}

.block_2 {
  flex: 1;
  background: linear-gradient(135deg, #ffebee 0%, #fff5f5 100%);
  border-radius: 12px;
  padding: 16px 12px;
  border: 2px solid #ffcdd2;
  position: relative;
  overflow: hidden;
  min-height: 110px;
  align-items: flex-start;
}

.block_2::before {
  content: '';
  position: absolute;
  right: -30px;
  bottom: -30px;
  width: 100px;
  height: 100px;
  background: radial-gradient(circle, rgba(255, 107, 107, 0.15) 0%, transparent 70%);
  border-radius: 50%;
}

.block_3 {
  flex: 1;
  background: linear-gradient(135deg, #e0f7fa 0%, #f1f8fb 100%);
  border-radius: 12px;
  padding: 16px 12px;
  border: 2px solid #b2ebf2;
  position: relative;
  overflow: hidden;
  min-height: 110px;
  align-items: flex-start;
}

.block_3::before {
  content: '';
  position: absolute;
  right: -30px;
  bottom: -30px;
  width: 100px;
  height: 100px;
  background: radial-gradient(circle, rgba(78, 205, 196, 0.15) 0%, transparent 70%);
  border-radius: 50%;
}

/* 第二行：考点答疑 + 学商速测 */
.section_4 {
  gap: 12px;
  margin-bottom: 16px;
}

.box_3 {
  flex: 1;
  background: linear-gradient(135deg, #e3f2fd 0%, #f1f8fe 100%);
  border-radius: 12px;
  padding: 16px 12px;
  border: 2px solid #bbdefb;
  position: relative;
  overflow: hidden;
  min-height: 110px;
  align-items: flex-start;
}

.box_3::before {
  content: '';
  position: absolute;
  right: -30px;
  bottom: -30px;
  width: 100px;
  height: 100px;
  background: radial-gradient(circle, rgba(69, 183, 209, 0.15) 0%, transparent 70%);
  border-radius: 50%;
}

.box_4 {
  flex: 1;
  background: linear-gradient(135deg, #e8f5e9 0%, #f1f8f4 100%);
  border-radius: 12px;
  padding: 16px 12px;
  border: 2px solid #c8e6c9;
  position: relative;
  overflow: hidden;
  min-height: 110px;
  align-items: flex-start;
}

.box_4::before {
  content: '';
  position: absolute;
  right: -30px;
  bottom: -30px;
  width: 100px;
  height: 100px;
  background: radial-gradient(circle, rgba(150, 206, 180, 0.15) 0%, transparent 70%);
  border-radius: 50%;
}

/* 触摸反馈 */
.touchable {
  transition: all 0.2s ease;
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
  user-select: none;
}

.touchable:active {
  transform: scale(0.96);
  opacity: 0.9;
}

/* 文字样式 */
.text-wrapper_1,
.text-group_2,
.text-group_3,
.text-group_4 {
  flex: 1;
  z-index: 1;
}

.text_3,
.text_5,
.text_7,
.text_9 {
  font-size: 17px;
  font-weight: 600;
  color: #333;
  margin-bottom: 6px;
  display: block;
}

.text_4,
.text_6,
.text_8,
.text_10 {
  font-size: 12px;
  color: #666;
  display: block;
  line-height: 1.5;
}

/* 模块图标 */
.module-icon {
  font-size: 48px;
  z-index: 1;
  display: block;
  filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.1));
}

/* ==================== 资讯卡片 ==================== */
.news-title {
  font-size: 20px;
  font-weight: 600;
  color: #333;
  margin: 24px 0 16px;
  padding-left: 12px;
  position: relative;
}

.news-title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 18px;
  background: #87CEEB;
  border-radius: 2px;
}

.box_5 {
  background: #ffffff;
  border-radius: 16px;
  padding: 16px;
  margin-bottom: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: row;
  gap: 12px;
}

.text-group_5 {
  flex: 1;
}

.text_11 {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  line-height: 1.5;
  margin-bottom: 10px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.text_12 {
  font-size: 13px;
  color: #87CEEB;
  display: inline-block;
  padding: 4px 12px;
  background: rgba(135, 206, 235, 0.15);
  border-radius: 12px;
  align-self: flex-start;
}

.image_8 {
  width: 120px;
  height: 90px;
  border-radius: 8px;
  object-fit: cover;
  flex-shrink: 0;
  background: #f0f0f0;
}

/* ==================== 响应式适配 ==================== */
@media screen and (min-width: 375px) {
  .text_3,
  .text_5,
  .text_7,
  .text_9 {
    font-size: 18px;
  }
  
  .module-icon {
    font-size: 52px;
  }
}

@media screen and (min-width: 414px) {
  .block_2,
  .block_3,
  .box_3,
  .box_4 {
    min-height: 120px;
    padding: 18px 14px;
  }
  
  .image_8 {
    width: 130px;
    height: 100px;
  }
}
</style>

