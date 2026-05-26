import { createSSRApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'

export function createApp() {
  const app = createSSRApp(App)
  const pinia = createPinia()
  
  app.use(pinia)
  
  // uview-plus 需要安装后取消注释
  // import uviewPlus from 'uview-plus'
  // app.use(uviewPlus)
  
  return {
    app
  }
}
