import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import lazyload from './directives/lazyload'
import axiosInstance from './utils/axios'
import logger from './utils/logger'
import errorHandler from './utils/errorHandler'
import performanceMonitor from './utils/performanceMonitor'

const app = createApp(App)
app.use(router)
app.use(store)
app.use(ElementPlus)
app.directive('lazyload', lazyload)
app.config.globalProperties.$axios = axiosInstance
app.config.globalProperties.$logger = logger

// 配置Vue错误捕获
app.config.errorHandler = (err, instance, info) => {
  errorHandler.captureError(err, {
    type: 'vue',
    info,
    component: instance?.$options?.name
  })
}

// 路由导航日志
router.beforeEach((to, from, next) => {
  logger.pageView(to.name || to.path, {
    from: from.name || from.path,
    to: to.name || to.path
  })
  next()
})

// 将工具挂载到全局
app.config.globalProperties.$logger = logger
app.config.globalProperties.$errorHandler = errorHandler
app.config.globalProperties.$performance = performanceMonitor

app.mount('#app')