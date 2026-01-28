import { defineConfig } from 'vite'
import uniModule from '@dcloudio/vite-plugin-uni'
import { resolve } from 'path'

// 获取 uni 插件函数（处理不同的导出方式）
const getUniPlugin = () => {
  const uni = uniModule.default || uniModule
  // 如果 uni 是对象且有 default 属性，使用 default
  if (uni && typeof uni === 'object' && typeof uni.default === 'function') {
    return uni.default
  }
  // 如果 uni 本身就是函数，直接使用
  if (typeof uni === 'function') {
    return uni
  }
  // 否则抛出错误
  throw new Error('无法加载 @dcloudio/vite-plugin-uni')
}

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    getUniPlugin()()
  ],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  server: {
    port: 3000,
    open: true,
    host: '0.0.0.0',
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path
      },
      '/uploads': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path
      }
    }
  },
  build: {
    target: 'es6',
    cssTarget: 'chrome61'
  }
})
