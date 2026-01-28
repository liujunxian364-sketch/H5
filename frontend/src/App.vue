<script>
export default {
  onLaunch: function() {
    console.log('App Launch')
    // 设置状态栏样式
    // #ifdef APP-PLUS
    plus.navigator.setStatusBarStyle('dark')
    // #endif
  },
  onShow: function() {
    console.log('App Show')
  },
  onHide: function() {
    console.log('App Hide')
  }
}
</script>

<style>
/* 引入全局样式 - @import 必须在最前面 */
@import './assets/style.css';
/* 引入 KaTeX 全局样式 */
@import 'katex/dist/katex.min.css';

/* 全局样式 */
page {
  width: 100%;
  min-height: 100vh;
  background-color: #f5f6f8;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
  /* 优化移动端字体渲染 */
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  /* 防止文本自动调整大小 */
  -webkit-text-size-adjust: 100%;
  text-size-adjust: 100%;
}

/* 滚动容器优化 */
::-webkit-scrollbar {
  width: 0;
  height: 0;
  background: transparent;
}

/* 全局动画 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideIn {
  from {
    transform: translateX(-100%);
  }
  to {
    transform: translateX(0);
  }
}

@keyframes scaleIn {
  from {
    transform: scale(0.9);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}

/* uni-app页面头部样式 - 天蓝色背景 */
uni-page-head {
  background-color: #87CEEB !important;
  position: relative !important; /* 取消固定定位 */
}

/* 兼容不同的导航栏元素 */
.uni-page-head,
uni-page-head .uni-page-head__wrapper {
  background-color: #87CEEB !important;
  position: relative !important; /* 取消固定定位 */
}

/* 隐藏导航栏占位符 */
.uni-placeholder {
  display: none !important;
  height: 0 !important;
}
</style>
