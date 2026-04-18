import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  // 加载环境变量
  const env = loadEnv(mode, process.cwd(), '')
  
  return {
    plugins: [vue()],
    resolve: {
      alias: {
        '@': resolve(__dirname, 'src')
      }
    },
    build: {
      // 代码分割
      rollupOptions: {
        output: {
          manualChunks: {
            // 第三方库
            vendor: ['vue', 'vue-router', 'vuex', 'axios'],
            // UI库
            element: ['element-plus'],
            // 图表库
            echarts: ['echarts', 'vue-echarts'],
            // 工具库
            utils: ['crypto-js', 'file-saver']
          }
        }
      },
      // 启用gzip压缩
      cssCodeSplit: true,
      sourcemap: false,
      minify: 'terser',
      terserOptions: {
        compress: {
          drop_console: mode === 'production',
          drop_debugger: mode === 'production'
        }
      }
    },
    // 开发服务器配置
    server: {
      port: 3000,
      open: true,
      proxy: {
        '/api': {
          target: env.VITE_API_BASE_URL || 'http://localhost:8000',
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, '')
        }
      }
    }
  }
})