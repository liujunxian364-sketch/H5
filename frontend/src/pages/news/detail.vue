<template>
  <view class="news-detail">
    <view class="article" v-if="newsDetail">
      <text class="article-title">{{ newsDetail.title }}</text>
      <view class="article-meta">
        <text class="meta-time">{{ newsDetail.createTime }}</text>
        <text class="meta-views">阅读 {{ newsDetail.views || 0 }}</text>
      </view>
      <image
        v-if="newsDetail.image"
        class="article-cover"
        :src="newsDetail.image"
        mode="widthFix"
      />
      <rich-text class="article-content" :nodes="newsDetail.content"></rich-text>
    </view>
    <view class="loading" v-else>
      <text>加载中...</text>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { newsApi } from '@/api'

const newsDetail = ref(null)

const fetchNewsDetail = async () => {
  const pages = getCurrentPages()
  const currentPage = pages[pages.length - 1]
  const id = currentPage.options?.id
  if (!id) return
  
  try {
    const res = await newsApi.getDetail(id)
    newsDetail.value = res.data
  } catch (error) {
    console.error('获取资讯详情失败:', error)
  }
}

onMounted(() => {
  fetchNewsDetail()
})
</script>

<style scoped>
.news-detail {
  min-height: 100vh;
  background: #fff;
}

.article {
  padding: 16px;
}

.article-title {
  font-size: 20px;
  font-weight: 600;
  color: #333;
  line-height: 1.4;
  margin-bottom: 12px;
  display: block;
}

.article-meta {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: #999;
  margin-bottom: 16px;
}

.article-cover {
  width: 100%;
  margin-bottom: 16px;
  border-radius: 8px;
}

.article-content {
  font-size: 15px;
  line-height: 1.8;
  color: #333;
}

.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: #999;
}
</style>
