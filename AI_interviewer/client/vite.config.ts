import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path' 

// https://vite.dev/config/
export default defineConfig({
  base: './',
  plugins: [vue()],

   resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src') // 这里定义了 @ 等于 src 目录
    }
  }

})
