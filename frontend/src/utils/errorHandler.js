// 前端错误捕获工具
import logger from './logger'
import * as Sentry from '@sentry/browser'

// 初始化Sentry
if (import.meta.env.VITE_SENTRY_DSN) {
  Sentry.init({
    dsn: import.meta.env.VITE_SENTRY_DSN,
    environment: import.meta.env.MODE,
    release: import.meta.env.VITE_APP_VERSION || '1.0.0'
  })
}

class ErrorHandler {
  constructor() {
    this.init()
  }

  // 初始化错误捕获
  init() {
    // 捕获全局错误
    this.captureGlobalErrors()
    // 捕获未处理的Promise拒绝
    this.captureUnhandledRejections()
    // 捕获Vue错误
    this.captureVueErrors()
    // 捕获资源加载错误
    this.captureResourceErrors()
  }

  // 捕获全局错误
  captureGlobalErrors() {
    window.addEventListener('error', (event) => {
      // 过滤掉资源加载错误，由专门的资源错误捕获处理
      if (event.target instanceof Element) {
        if (event.target.tagName === 'SCRIPT' || event.target.tagName === 'LINK' || event.target.tagName === 'IMG') {
          return
        }
      }

      logger.captureError(event.error, {
        type: 'global',
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno,
        timestamp: Date.now()
      })

      // 发送到Sentry
      if (import.meta.env.VITE_SENTRY_DSN) {
        Sentry.captureException(event.error, {
          tags: {
            error_type: 'global',
            filename: event.filename
          }
        })
      }
    })
  }

  // 捕获未处理的Promise拒绝
  captureUnhandledRejections() {
    window.addEventListener('unhandledrejection', (event) => {
      logger.captureError(event.reason, {
        type: 'unhandled_rejection',
        promise: event.promise,
        timestamp: Date.now()
      })

      // 发送到Sentry
      if (import.meta.env.VITE_SENTRY_DSN) {
        Sentry.captureException(event.reason, {
          tags: {
            error_type: 'unhandled_rejection'
          }
        })
      }
    })
  }

  // 捕获Vue错误
  captureVueErrors() {
    // 在main.js中使用
  }

  // 捕获资源加载错误
  captureResourceErrors() {
    window.addEventListener('error', (event) => {
      if (event.target instanceof Element) {
        if (event.target.tagName === 'SCRIPT' || event.target.tagName === 'LINK' || event.target.tagName === 'IMG') {
          logger.error('Resource load error', {
            type: 'resource',
            url: event.target.src || event.target.href,
            tagName: event.target.tagName,
            timestamp: Date.now()
          })

          // 发送到Sentry
          if (import.meta.env.VITE_SENTRY_DSN) {
            Sentry.captureMessage('Resource load error', {
              tags: {
                error_type: 'resource',
                url: event.target.src || event.target.href,
                tagName: event.target.tagName
              }
            })
          }
        }
      }
    }, true)
  }

  // 手动捕获错误
  captureError(error, context = {}) {
    logger.captureError(error, {
      ...context,
      timestamp: Date.now()
    })

    // 发送到Sentry
    if (import.meta.env.VITE_SENTRY_DSN) {
      Sentry.captureException(error, {
        tags: {
          error_type: 'manual',
          ...context
        }
      })
    }
  }

  // 捕获API错误
  captureApiError(error, url, method, config = {}) {
    logger.captureError(error, {
      type: 'api',
      url,
      method,
      data: config.data,
      params: config.params,
      timestamp: Date.now()
    })

    // 发送到Sentry
    if (import.meta.env.VITE_SENTRY_DSN) {
      Sentry.captureException(error, {
        tags: {
          error_type: 'api',
          url,
          method
        }
      })
    }
  }

  // 捕获路由错误
  captureRouteError(error, to, from) {
    logger.captureError(error, {
      type: 'router',
      to: to.path,
      from: from.path,
      timestamp: Date.now()
    })

    // 发送到Sentry
    if (import.meta.env.VITE_SENTRY_DSN) {
      Sentry.captureException(error, {
        tags: {
          error_type: 'router',
          to: to.path,
          from: from.path
        }
      })
    }
  }

  // 处理错误并返回友好消息
  handleError(error) {
    let message = '操作失败，请稍后重试'
    
    if (error.response) {
      // 服务器返回错误
      const status = error.response.status
      switch (status) {
        case 400:
          message = error.response.data.detail || '请求参数错误'
          break
        case 401:
          message = '登录已过期，请重新登录'
          // 可以在这里处理登出逻辑
          break
        case 403:
          message = '无权限执行此操作'
          break
        case 404:
          message = '请求的资源不存在'
          break
        case 429:
          message = '请求过于频繁，请稍后再试'
          break
        case 500:
          message = '服务器内部错误'
          break
        case 502:
          message = '网关错误'
          break
        case 503:
          message = '服务暂时不可用'
          break
        case 504:
          message = '请求超时'
          break
        default:
          message = `服务器错误 (${status})`
      }
    } else if (error.request) {
      // 请求已发送但没有收到响应
      message = '网络连接失败，请检查网络'
    } else {
      // 请求配置错误
      message = error.message || '请求失败'
    }
    
    logger.error(message, { error, timestamp: Date.now() })
    return message
  }

  // 记录错误并显示提示
  logAndShowError(error, showNotification = true) {
    const message = this.handleError(error)
    if (showNotification) {
      // 这里可以集成通知组件，如Element Plus的Message
      if (window.$message) {
        window.$message.error(message)
      }
    }
    return message
  }
}

// 导出单例
export default new ErrorHandler()