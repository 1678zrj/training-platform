import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  //新增server配置
  server:{
    host:true,
    proxy:{
      '/api':{
        target:'http://localhost:8000',
        changeOrigin:true
      },
      '/media':{
        target:'http://localhost:8000',
        changeOrigin:true
      },
      '/jupyter-proxy': {
        target: 'http://127.0.0.1:80',
        changeOrigin: true,
        ws: true
      },
      '/lab': { // 匹配新的路径前缀
        target: 'http://localhost:80', // 指向 Docker 运行的 Nginx
        changeOrigin: true,
        ws: true
      },

    }
  }
})