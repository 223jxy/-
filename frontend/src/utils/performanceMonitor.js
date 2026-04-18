// 前端性能埋点工具
import logger from './logger'
import { onCLS, onFID, onFCP, onLCP, onTTFB } from 'web-vitals'

class PerformanceMonitor {
  constructor() {
    this.init()
  }

  // 初始化性能监控
  init() {
    // 监控核心Web指标
    this.monitorCoreWebVitals()
    // 监控页面加载性能
    this.monitorPageLoad()
    // 监控用户交互
    this.monitorUserInteraction()
  }

  // 监控核心Web指标
  monitorCoreWebVitals() {
    // 累积布局偏移
    onCLS((metric) => {
      this.logPerformanceMetric('CLS', metric)
    })

    // 首次输入延迟
    onFID((metric) => {
      this.logPerformanceMetric('FID', metric)
    })

    // 首次内容绘制
    onFCP((metric) => {
      this.logPerformanceMetric('FCP', metric)
    })

    // 最大内容绘制
    onLCP((metric) => {
      this.logPerformanceMetric('LCP', metric)
    })

    // 首字节时间
    onTTFB((metric) => {
      this.logPerformanceMetric('TTFB', metric)
    })
  }

  // 监控页面加载性能
  monitorPageLoad() {
    window.addEventListener('load', () => {
      const performanceData = window.performance.getEntriesByType('navigation')[0]
      if (performanceData) {
        logger.info('Page Load Performance', {
          type: 'page_load',
          metrics: {
            loadTime: performanceData.loadEventEnd - performanceData.startTime,
            domContentLoaded: performanceData.domContentLoadedEventEnd - performanceData.startTime,
            firstPaint: performanceData.fetchStart,
            redirectTime: performanceData.redirectEnd - performanceData.redirectStart,
            dnsTime: performanceData.domainLookupEnd - performanceData.domainLookupStart,
            tcpTime: performanceData.connectEnd - performanceData.connectStart,
            sslTime: performanceData.secureConnectionStart ? (performanceData.connectEnd - performanceData.secureConnectionStart) : 0,
            requestTime: performanceData.responseEnd - performanceData.requestStart,
            responseTime: performanceData.responseEnd - performanceData.responseStart
          }
        })
      }
    })
  }

  // 监控用户交互
  monitorUserInteraction() {
    // 点击事件监控
    document.addEventListener('click', (event) => {
      const target = event.target
      const selector = this.getElementSelector(target)
      
      logger.info('User Interaction', {
        type: 'click',
        selector,
        timestamp: Date.now()
      })
    }, true)

    // 页面滚动监控
    window.addEventListener('scroll', () => {
      const scrollTop = window.pageYOffset || document.documentElement.scrollTop
      const scrollHeight = document.documentElement.scrollHeight
      const clientHeight = document.documentElement.clientHeight
      const scrollPercentage = (scrollTop / (scrollHeight - clientHeight)) * 100

      logger.info('User Interaction', {
        type: 'scroll',
        scrollTop,
        scrollPercentage,
        timestamp: Date.now()
      })
    }, { passive: true })
  }

  // 日志性能指标
  logPerformanceMetric(name, metric) {
    logger.info(`Performance Metric: ${name}`, {
      type: 'performance',
      metric: name,
      value: metric.value,
      id: metric.id,
      entries: metric.entries,
      rating: this.getPerformanceRating(name, metric.value)
    })
  }

  // 获取性能评级
  getPerformanceRating(metric, value) {
    switch (metric) {
      case 'CLS':
        return value < 0.1 ? 'good' : value < 0.25 ? 'needs-improvement' : 'poor'
      case 'FID':
        return value < 100 ? 'good' : value < 300 ? 'needs-improvement' : 'poor'
      case 'LCP':
        return value < 2500 ? 'good' : value < 4000 ? 'needs-improvement' : 'poor'
      case 'TTFB':
        return value < 800 ? 'good' : value < 1800 ? 'needs-improvement' : 'poor'
      default:
        return 'unknown'
    }
  }

  // 获取元素选择器
  getElementSelector(element) {
    if (!element) return ''
    if (element.id) return `#${element.id}`
    if (element.className) return `.${element.className.split(' ').filter(Boolean).join('.')}`
    return element.tagName.toLowerCase()
  }

  // 监控API性能
  monitorApiPerformance(url, method, startTime, endTime, success) {
    const duration = endTime - startTime
    logger.info('API Performance', {
      type: 'api',
      url,
      method,
      duration,
      success,
      timestamp: Date.now()
    })
  }

  // 监控组件性能
  monitorComponentPerformance(componentName, startTime, endTime) {
    const duration = endTime - startTime
    logger.info('Component Performance', {
      type: 'component',
      component: componentName,
      duration,
      timestamp: Date.now()
    })
  }
}

// 导出单例
export default new PerformanceMonitor()