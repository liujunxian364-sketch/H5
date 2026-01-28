import { createSSRApp } from 'vue'
import App from './App.vue'

// 开发环境启用 vConsole 移动端调试工具
// #ifdef H5
if (import.meta.env.DEV) {
  import('vconsole').then(module => {
    const VConsole = module.default
    new VConsole()
    console.log('🎉 vConsole 已启动 - 移动端调试工具已就绪')
  })
}
// #endif

export function createApp() {
  const app = createSSRApp(App)
  return {
    app
  }
}
