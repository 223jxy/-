// axios配置
import axios from 'axios'
import { setCsrfToken } from './csrf'
import logger from './logger'

// 创建axios实例
const axiosInstance = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 生成随机nonce
function generateNonce() {
  return Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15)
}

// 请求拦截器，添加CSRF token和防重放攻击头部
axiosInstance.interceptors.request.use(
  config => {
    // 添加CSRF token
    config = setCsrfToken(config)
    
    // 添加时间戳和nonce，防止重放攻击
    const timestamp = Date.now()
    const nonce = generateNonce()
    config.headers['X-Timestamp'] = timestamp
    config.headers['X-Nonce'] = nonce
    
    return config
  },
  error => {
    return Promise.reject(error)
  }
)



// 响应拦截器
axiosInstance.interceptors.response.use(
  response => {
    // 记录API请求成功
    const config = response.config
    const url = config.url
    const method = config.method
    const params = config.params || config.data || {}
    
    logger.info(`API Request Success: ${method.toUpperCase()} ${url}`, {
      url,
      method: method.toUpperCase(),
      params,
      status: response.status,
      statusText: response.statusText
    })
    
    return response
  },
  error => {
    // 记录API请求失败
    const config = error.config || {}
    const url = config.url || 'unknown'
    const method = config.method || 'unknown'
    const params = config.params || config.data || {}
    
    logger.error(`API Request Failed: ${method.toUpperCase()} ${url}`, {
      url,
      method: method.toUpperCase(),
      params,
      error: error.message,
      status: error.response?.status,
      statusText: error.response?.statusText
    })
    
    // 处理错误
    if (error.response) {
      switch (error.response.status) {
        case 401:
          // 未授权，跳转到登录页
          break
        case 403:
          // 禁止访问
          break
        case 404:
          // 资源不存在
          break
        case 500:
          // 服务器错误
          break
        default:
          // 其他错误
          break
      }
    }
    return Promise.reject(error)
  }
)

export default axiosInstance