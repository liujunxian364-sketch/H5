<template>
  <div class="news-card" @click="$emit('click')">
    <div class="news-content">
      <h3 class="news-title">{{ news.title }}</h3>
      <p class="news-summary">{{ news.summary }}</p>
      <span class="news-time">{{ news.createTime }}</span>
    </div>
    <div class="news-image" v-if="news.image">
      <img :src="news.image" :alt="news.title" />
    </div>
  </div>
</template>

<script setup>
defineProps({
  news: {
    type: Object,
    required: true
  }
})

defineEmits(['click'])
</script>

<style scoped>
.news-card {
  display: flex;
  background: #fff;
  border-radius: 8px;
  padding: 12px;
  cursor: pointer;
  border: 1px solid #eee;
  transition: box-shadow 0.2s;
}

.news-card:active {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.news-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  margin-right: 12px;
}

.news-title {
  font-size: 15px;
  font-weight: 500;
  color: #333;
  line-height: 1.4;
  margin-bottom: 6px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.news-summary {
  font-size: 13px;
  color: #666;
  line-height: 1.5;
  flex: 1;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.news-time {
  font-size: 12px;
  color: #999;
  margin-top: 6px;
}

.news-image {
  width: 100px;
  height: 75px;
  border-radius: 6px;
  overflow: hidden;
  flex-shrink: 0;
}

.news-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
</style>
