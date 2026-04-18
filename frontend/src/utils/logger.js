// 前端日志工具
import { Logtail } from '@logtail/browser'

// 配置Logtail
const logtail = import.meta.env.VITE_LOGTAIL_TOKEN 
  ? new Logtail(import.meta.env.VITE_LOGTAIL_TOKEN) 
  : null

// 日志级别
export const LogLevel = {
  DEBUG: 'debug',
  INFO: 'info',
  WARN: 'warn',
  ERROR: 'error',
  FATAL: 'fatal'
}

class Logger {
  constructor() {
    this.userId = null
    this.sessionId = this.generateSessionId()
  }

  // 生成会话ID
  generateSessionId() {
    return Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15)
  }

  // 设置用户ID
  setUserId(userId) {
    this.userId = userId
  }

  // 基础日志方法
  log(level, message, meta = {}) {
    const logData = {
      level,
      message,
      userId: this.userId,
      sessionId: this.sessionId,
      timestamp: new Date().toISOString(),
      ...meta
    }

    // 控制台输出
    console[level](message, meta)

    // 发送到Logtail
    if (logtail) {
      try {
        logtail[level](message, meta)
      } catch (error) {
        console.error('Logtail error:', error)
      }
    }
  }

  // 调试日志
  debug(message, meta = {}) {
    this.log(LogLevel.DEBUG, message, meta)
  }

  // 信息日志
  info(message, meta = {}) {
    this.log(LogLevel.INFO, message, meta)
  }

  // 警告日志
  warn(message, meta = {}) {
    this.log(LogLevel.WARN, message, meta)
  }

  // 错误日志
  error(message, meta = {}) {
    this.log(LogLevel.ERROR, message, meta)
  }

  // 致命错误日志
  fatal(message, meta = {}) {
    this.log(LogLevel.FATAL, message, meta)
  }

  // 操作日志
  operation(operation, meta = {}) {
    this.info(`Operation: ${operation}`, {
      operation,
      ...meta
    })
  }

  // API请求日志
  apiRequest(url, method, params = {}, meta = {}) {
    const startTime = Date.now()
    
    return {
      end: (response, error = null) => {
        const endTime = Date.now()
        const duration = endTime - startTime
        
        if (error) {
          this.error(`API Request Failed: ${method} ${url}`, {
            url,
            method,
            params,
            error: error.message,
            duration,
            ...meta
          })
        } else {
          this.info(`API Request Success: ${method} ${url}`, {
            url,
            method,
            params,
            duration,
            ...meta
          })
        }
      }
    }
  }

  // 页面访问日志
  pageView(page, meta = {}) {
    this.info(`Page View: ${page}`, {
      page,
      ...meta
    })
  }

  // 错误捕获
  captureError(error, meta = {}) {
    this.error('Unhandled Error', {
      error: error.message,
      stack: error.stack,
      ...meta
    })
  }
}

// 导出单例
export default new Logger()