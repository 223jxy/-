// XSS防护工具

/**
 * 转义HTML特殊字符，防止XSS攻击
 * @param {string} str - 需要转义的字符串
 * @returns {string} - 转义后的字符串
 */
export function escapeHtml(str) {
  if (!str) return ''
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;')
}

/**
 * 验证用户输入，防止XSS攻击
 * @param {string} input - 用户输入
 * @returns {boolean} - 是否安全
 */
export function validateInput(input) {
  if (!input) return true
  
  // 检测常见的XSS攻击模式
  const xssPatterns = [
    /<script[\s\S]*?<\/script>/gi,
    /<iframe[\s\S]*?<\/iframe>/gi,
    /on\w+\s*=\s*["'][^"']*["']/gi,
    /javascript:\s*[^"']*/gi
  ]
  
  for (const pattern of xssPatterns) {
    if (pattern.test(input)) {
      return false
    }
  }
  
  return true
}

/**
 * 清理用户输入，移除潜在的XSS攻击代码
 * @param {string} input - 用户输入
 * @returns {string} - 清理后的输入
 */
export function sanitizeInput(input) {
  if (!input) return ''
  
  // 移除script标签
  input = input.replace(/<script[\s\S]*?<\/script>/gi, '')
  
  // 移除iframe标签
  input = input.replace(/<iframe[\s\S]*?<\/iframe>/gi, '')
  
  // 移除事件属性
  input = input.replace(/on\w+\s*=\s*["'][^"']*["']/gi, '')
  
  // 移除javascript:伪协议
  input = input.replace(/javascript:\s*[^"']*/gi, '')
  
  return input
}