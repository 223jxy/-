import axios from 'axios'
import logger from './logger'
import { setCsrfToken } from './csrf'
import { escapeHtml } from './xss'
import { encrypt, decrypt } from './encryption'

// 创建axios实例
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求缓存
const requestCache = new Map()
const CACHE_DURATION = 5 * 60 * 1000 // 5分钟

// 防抖/节流配置
const debounceMap = new Map()
const throttleMap = new Map()

// 防抖函数
const debounce = (key, func, wait = 300) => {
  if (debounceMap.has(key)) {
    clearTimeout(debounceMap.get(key))
  }
  
  return new Promise((resolve) => {
    const timeout = setTimeout(() => {
      debounceMap.delete(key)
      resolve(func())
    }, wait)
    debounceMap.set(key, timeout)
  })
}

// 节流函数
const throttle = (key, func, limit = 1000) => {
  const now = Date.now()
  const lastCall = throttleMap.get(key) || 0
  
  if (now - lastCall < limit) {
    return Promise.resolve()
  }
  
  throttleMap.set(key, now)
  return func()
}

// 请求合并
const pendingRequests = new Map()

// 生成请求缓存键
const generateCacheKey = (config) => {
  return `${config.method}:${config.url}:${JSON.stringify(config.params || {})}:${JSON.stringify(config.data || {})}`
}

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 设置CSRF token
    config = setCsrfToken(config)
    
    // 敏感数据加密
    if (config.data) {
      // 加密敏感字段
      const sensitiveFields = ['password', 'phone', 'email', 'id_card']
      const encryptedData = { ...config.data }
      
      for (const field of sensitiveFields) {
        if (encryptedData[field]) {
          encryptedData[field] = encrypt(encryptedData[field])
        }
      }
      
      config.data = encryptedData
    }
    
    // 生成缓存键
    const cacheKey = generateCacheKey(config)
    
    // 检查是否有相同的请求正在进行
    if (pendingRequests.has(cacheKey)) {
      return pendingRequests.get(cacheKey)
    }
    
    // 检查缓存
    if (config.method === 'get' && requestCache.has(cacheKey)) {
      const cached = requestCache.get(cacheKey)
      if (Date.now() - cached.timestamp < CACHE_DURATION) {
        logger.info('从缓存获取数据:', cacheKey)
        return Promise.resolve(cached.response)
      } else {
        requestCache.delete(cacheKey)
      }
    }
    
    // 处理防抖/节流
    if (config.debounce) {
      const promise = debounce(cacheKey, () => axios(config))
      pendingRequests.set(cacheKey, promise)
      return promise
    }
    
    if (config.throttle) {
      const promise = throttle(cacheKey, () => axios(config))
      pendingRequests.set(cacheKey, promise)
      return promise
    }
    
    const promise = axios(config)
    pendingRequests.set(cacheKey, promise)
    return promise
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    const config = response.config
    const cacheKey = generateCacheKey(config)
    
    // 移除pending请求
    pendingRequests.delete(cacheKey)
    
    // 缓存GET请求
    if (config.method === 'get') {
      requestCache.set(cacheKey, {
        response,
        timestamp: Date.now()
      })
    }
    
    // 对响应数据进行XSS防护
    if (response.data) {
      response.data = sanitizeResponseData(response.data)
    }
    
    return response
  },
  (error) => {
    const config = error.config
    if (config) {
      const cacheKey = generateCacheKey(config)
      pendingRequests.delete(cacheKey)
    }
    
    logger.error('API请求错误:', error)
    return Promise.reject(error)
  }
)

// 清理响应数据，防止XSS攻击
function sanitizeResponseData(data) {
  if (typeof data === 'string') {
    return escapeHtml(data)
  } else if (Array.isArray(data)) {
    return data.map(item => sanitizeResponseData(item))
  } else if (typeof data === 'object' && data !== null) {
    const sanitized = {}
    for (const key in data) {
      if (Object.prototype.hasOwnProperty.call(data, key)) {
        sanitized[key] = sanitizeResponseData(data[key])
      }
    }
    return sanitized
  }
  return data
}

// 清除缓存
export const clearCache = (url) => {
  for (const [key, value] of requestCache.entries()) {
    if (key.includes(url)) {
      requestCache.delete(key)
    }
  }
}

// 清除所有缓存
export const clearAllCache = () => {
  requestCache.clear()
}

export default api