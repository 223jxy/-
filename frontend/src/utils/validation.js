// 表单验证工具

/**
 * 验证规则配置
 */
export const VALIDATION_RULES = {
  // 用户名验证
  username: {
    required: true,
    minLength: 3,
    maxLength: 20,
    pattern: /^[a-zA-Z0-9_]+$/,
    message: '用户名只能包含字母、数字和下划线，长度3-20位'
  },
  
  // 密码验证
  password: {
    required: true,
    minLength: 6,
    maxLength: 20,
    pattern: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$/, // 至少包含一个小写字母、一个大写字母和一个数字
    message: '密码长度6-20位，必须包含大小写字母和数字'
  },
  
  // 邮箱验证
  email: {
    required: true,
    pattern: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/,
    message: '请输入有效的邮箱地址'
  },
  
  // 手机号验证
  phone: {
    required: true,
    pattern: /^1[3-9]\d{9}$/,
    message: '请输入有效的手机号码'
  },
  
  // 身份证号验证
  idCard: {
    required: true,
    pattern: /^[1-9]\d{5}(18|19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dXx]$/,
    message: '请输入有效的身份证号码'
  },
  
  // 书名验证
  bookTitle: {
    required: true,
    minLength: 1,
    maxLength: 200,
    message: '书名长度1-200位'
  },
  
  // 作者验证
  author: {
    required: true,
    minLength: 1,
    maxLength: 100,
    message: '作者名称长度1-100位'
  },
  
  // 价格验证
  price: {
    required: true,
    min: 0,
    max: 99999,
    message: '价格必须在0-99999之间'
  }
}

/**
 * 验证输入是否符合规则
 * @param {string} value - 输入值
 * @param {object} rules - 验证规则
 * @returns {string|null} - 错误信息，null表示验证通过
 */
export function validateInput(value, rules) {
  // 检查是否必填
  if (rules.required && (!value || value.trim() === '')) {
    return rules.message || '此项为必填项'
  }
  
  // 检查最小长度
  if (rules.minLength && value && value.length < rules.minLength) {
    return rules.message || `长度不能小于${rules.minLength}位`
  }
  
  // 检查最大长度
  if (rules.maxLength && value && value.length > rules.maxLength) {
    return rules.message || `长度不能大于${rules.maxLength}位`
  }
  
  // 检查最小值
  if (rules.min !== undefined && value && parseFloat(value) < rules.min) {
    return rules.message || `值不能小于${rules.min}`
  }
  
  // 检查最大值
  if (rules.max !== undefined && value && parseFloat(value) > rules.max) {
    return rules.message || `值不能大于${rules.max}`
  }
  
  // 检查正则表达式
  if (rules.pattern && value && !rules.pattern.test(value)) {
    return rules.message || '输入格式不正确'
  }
  
  return null
}

/**
 * 验证表单数据
 * @param {object} data - 表单数据
 * @param {object} ruleConfig - 验证规则配置
 * @returns {object} - 验证结果，{ isValid: boolean, errors: object }
 */
export function validateForm(data, ruleConfig) {
  const errors = {}
  let isValid = true
  
  for (const field in ruleConfig) {
    if (Object.prototype.hasOwnProperty.call(ruleConfig, field)) {
      const value = data[field]
      const rules = ruleConfig[field]
      const error = validateInput(value, rules)
      
      if (error) {
        errors[field] = error
        isValid = false
      }
    }
  }
  
  return { isValid, errors }
}

/**
 * 防注入处理
 * @param {string} input - 用户输入
 * @returns {string} - 处理后的输入
 */
export function sanitizeInput(input) {
  if (!input || typeof input !== 'string') {
    return input
  }
  
  // 移除SQL注入风险字符
  const sqlInjectionPatterns = [
    /'\s*OR\s*1=1/gi,
    /'\s*AND\s*1=1/gi,
    /\bUNION\b\s+SELECT/gi,
    /\bINSERT\b\s+INTO/gi,
    /\bUPDATE\b\s+.*\bSET\b/gi,
    /\bDELETE\b\s+FROM/gi,
    /\bDROP\b\s+TABLE/gi,
    /\bTRUNCATE\b\s+TABLE/gi
  ]
  
  let sanitized = input
  for (const pattern of sqlInjectionPatterns) {
    sanitized = sanitized.replace(pattern, '')
  }
  
  // 移除XSS风险字符
  const xssPatterns = [
    /<script[\s\S]*?<\/script>/gi,
    /<iframe[\s\S]*?<\/iframe>/gi,
    /on\w+\s*=\s*["'][^"']*["']/gi,
    /javascript:\s*[^"']*/gi
  ]
  
  for (const pattern of xssPatterns) {
    sanitized = sanitized.replace(pattern, '')
  }
  
  return sanitized
}

/**
 * 清理表单数据，防止注入攻击
 * @param {object} data - 表单数据
 * @returns {object} - 清理后的数据
 */
export function sanitizeFormData(data) {
  if (!data || typeof data !== 'object') {
    return data
  }
  
  const sanitized = {}
  for (const key in data) {
    if (Object.prototype.hasOwnProperty.call(data, key)) {
      const value = data[key]
      if (typeof value === 'string') {
        sanitized[key] = sanitizeInput(value)
      } else if (Array.isArray(value)) {
        sanitized[key] = value.map(item => 
          typeof item === 'string' ? sanitizeInput(item) : item
        )
      } else if (typeof value === 'object' && value !== null) {
        sanitized[key] = sanitizeFormData(value)
      } else {
        sanitized[key] = value
      }
    }
  }
  
  return sanitized
}