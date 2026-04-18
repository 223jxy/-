// 图片处理工具

/**
 * 压缩图片
 * @param {File} file - 图片文件
 * @param {number} maxWidth - 最大宽度
 * @param {number} quality - 压缩质量 (0-1)
 * @returns {Promise<Blob>} 压缩后的图片
 */
export const compressImage = (file, maxWidth = 800, quality = 0.7) => {
  return new Promise((resolve, reject) => {
    const canvas = document.createElement('canvas')
    const ctx = canvas.getContext('2d')
    const img = new Image()
    
    img.onload = () => {
      const ratio = Math.min(maxWidth / img.width, maxWidth / img.height)
      const width = img.width * ratio
      const height = img.height * ratio
      
      canvas.width = width
      canvas.height = height
      
      ctx.drawImage(img, 0, 0, width, height)
      
      canvas.toBlob(resolve, 'image/webp', quality)
    }
    
    img.onerror = reject
    img.src = URL.createObjectURL(file)
  })
}

/**
 * 检查浏览器是否支持WebP
 * @returns {Promise<boolean>} 是否支持WebP
 */
export const checkWebPSupport = () => {
  return new Promise((resolve) => {
    const img = new Image()
    img.onload = () => resolve(true)
    img.onerror = () => resolve(false)
    img.src = 'data:image/webp;base64,UklGRiQAAABXRUJQVlA4IBgAAAAwAQCdASoBAAEAAwA0JaQAA3AA/vuUAAA='
  })
}

/**
 * 获取优化后的图片URL
 * @param {string} url - 原始图片URL
 * @returns {string} 优化后的图片URL
 */
export const getOptimizedImageUrl = (url) => {
  // 这里可以根据实际情况返回优化后的图片URL
  // 例如：添加CDN处理参数、转换为WebP格式等
  return url
}

/**
 * 批量处理图片
 * @param {File[]} files - 图片文件数组
 * @returns {Promise<Blob[]>} 处理后的图片数组
 */
export const processImages = async (files) => {
  const processedFiles = []
  
  for (const file of files) {
    try {
      const compressed = await compressImage(file)
      processedFiles.push(compressed)
    } catch (error) {
      console.error('图片处理失败:', error)
      processedFiles.push(file)
    }
  }
  
  return processedFiles
}