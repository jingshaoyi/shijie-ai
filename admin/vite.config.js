import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  server: {
    port: 5173,
    // 开发环境使用代理，生产环境直接请求
    proxy: {
      '/api': {
        // ⚠️ 注意：请将此地址替换为您的后端API地址
        target: 'https://YOUR_BACKEND_DOMAIN',
        changeOrigin: true,
        // rewrite: (path) => path.replace(/^\/api/, ''), // 如果后端需要/api前缀则注释掉
      },
    },
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
  },
})
