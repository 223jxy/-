// 前端性能监控工具
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals'
import * as Sentry from '@sentry/browser'
import logger from './logger'

// 配置Sentry
Sentry.init({
  dsn: 'YOUR_SENTRY_DSN', // 实际项目中应该从环境变量获取
  integrations: [
    new Sentry.BrowserTracing({
      tracingOrigins: ['localhost', 'your-production-domain.com'],
    }),
  ],
  tracesSampleRate: 1.0,
})

class PerformanceMonitor {
  constructor() {
    this.metrics = {}
  }

  // 初始化性能监控
  init() {
    // 收集核心Web性能指标
    this.collectWebVitals()
    
    // 监控路由变化
    this.monitorRouteChanges()
    
    // 监控API请求性能
    this.monitorApiRequests()
  }

  // 收集核心Web性能指标
  collectWebVitals() {
    getCLS(metric => {
      this.metrics.cls = metric.value
      logger.info('CLS metric collected', { metric: 'CLS', value: metric.value })
      Sentry.captureMetric('cls', metric.value)
    })

    getFID(metric => {
      this.metrics.fid = metric.value
      logger.info('FID metric collected', { metric: 'FID', value: metric.value })
      Sentry.captureMetric('fid', metric.value)
    })

    getFCP(metric => {
      this.metrics.fcp = metric.value
      logger.info('FCP metric collected', { metric: 'FCP', value: metric.value })
      Sentry.captureMetric('fcp', metric.value)
    })

    getLCP(metric => {
      this.metrics.lcp = metric.value
      logger.info('LCP metric collected', { metric: 'LCP', value: metric.value })
      Sentry.captureMetric('lcp', metric.value)
    })

    getTTFB(metric => {
      this.metrics.ttfb = metric.value
      logger.info('TTFB metric collected', { metric: 'TTFB', value: metric.value })
      Sentry.captureMetric('ttfb', metric.value)
    })
  }

  // 监控路由变化
  monitorRouteChanges() {
    // 监听路由变化
    if (window.router) {
      window.router.beforeEach((to, from, next) => {
        const startTime = Date.now()
        
        // 路由导航完成后记录耗时
        window.router.afterEach((to, from) => {
          const endTime = Date.now()
          const duration = endTime - startTime
          
          logger.info(`Route navigation duration: ${duration}ms`, {
            from: from.path,
            to: to.path,
            duration
          })
          
          Sentry.captureMetric('route_navigation_duration', duration, {
            tags: {
              from: from.path,
              to: to.path
            }
          })
        })
        
        next()
      })
    }
  }

  // 监控API请求性能
  monitorApiRequests() {
    // 拦截XMLHttpRequest
    const originalXhrOpen = XMLHttpRequest.prototype.open
    const originalXhrSend = XMLHttpRequest.prototype.send
    
    XMLHttpRequest.prototype.open = function(method, url) {
      this._startTime = Date.now()
      this._method = method
      this._url = url
      return originalXhrOpen.apply(this, arguments)
    }
    
    XMLHttpRequest.prototype.send = function() {
      const xhr = this
      
      const originalOnLoad = this.onload
      this.onload = function() {
        const endTime = Date.now()
        const duration = endTime - xhr._startTime
        
        logger.info(`XHR Request: ${xhr._method} ${xhr._url} ${xhr.status} ${duration}ms`, {
          method: xhr._method,
          url: xhr._url,
          status: xhr.status,
          duration
        })
        
        Sentry.captureMetric('api_request_duration', duration, {
          tags: {
            method: xhr._method,
            url: xhr._url,
            status: xhr.status
          }
        })
        
        if (originalOnLoad) {
          originalOnLoad.apply(this, arguments)
        }
      }
      
      const originalOnError = this.onerror
      this.onerror = function() {
        const endTime = Date.now()
        const duration = endTime - xhr._startTime
        
        logger.error(`XHR Request Failed: ${xhr._method} ${xhr._url} ${duration}ms`, {
          method: xhr._method,
          url: xhr._url,
          duration
        })
        
        if (originalOnError) {
          originalOnError.apply(this, arguments)
        }
      }
      
      return originalXhrSend.apply(this, arguments)
    }
  }

  // 捕获异常
  captureException(error, context = {}) {
    logger.error('Exception captured', { error: error.message, stack: error.stack, ...context })
    Sentry.captureException(error, { extra: context })
  }

  // 捕获消息
  captureMessage(message, level = 'info', context = {}) {
    logger.info(`Message captured: ${message}`, context)
    Sentry.captureMessage(message, {
      level,
      extra: context
    })
  }

  // 设置用户信息
  setUser(user) {
    if (user) {
      Sentry.setUser({
        id: user.id,
        username: user.username,
        email: user.email
      })
      logger.setUserId(user.id)
    }
  }

  // 获取性能指标
  getMetrics() {
    return this.metrics
  }
}

// 导出单例
export default new PerformanceMonitor()