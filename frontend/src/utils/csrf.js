// CSRF防护工具

/**
 * 获取CSRF token
 * @returns {string} - CSRF token
 */
export function getCsrfToken() {
  // 从cookie中获取CSRF token
  const cookieValue = document.cookie
    .split('; ')  
    .find(row => row.startsWith('XSRF-TOKEN='))
    ?.split('=')[1]
  
  return cookieValue ? decodeURIComponent(cookieValue) : ''
}

/**
 * 设置CSRF token到请求头
 * @param {object} config - axios请求配置
 * @returns {object} - 配置后的请求配置
 */
export function setCsrfToken(config) {
  const token = getCsrfToken()
  if (token) {
    config.headers['X-XSRF-TOKEN'] = token
  }
  return config
}

/**
 * 验证CSRF token是否存在
 * @returns {boolean} - 是否存在CSRF token
 */
export function hasCsrfToken() {
  return getCsrfToken() !== ''
}