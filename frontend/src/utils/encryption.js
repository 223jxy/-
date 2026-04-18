// 加密工具
import CryptoJS from 'crypto-js'

// 加密密钥（实际项目中应该从环境变量中获取）
const SECRET_KEY = 'book_bridge_secret_key_2024'

/**
 * 加密数据
 * @param {any} data - 需要加密的数据
 * @returns {string} - 加密后的字符串
 */
export function encrypt(data) {
  try {
    const jsonString = JSON.stringify(data)
    const encrypted = CryptoJS.AES.encrypt(jsonString, SECRET_KEY).toString()
    return encrypted
  } catch (error) {
    console.error('加密失败:', error)
    return null
  }
}

/**
 * 解密数据
 * @param {string} encryptedData - 加密的数据
 * @returns {any} - 解密后的数据
 */
export function decrypt(encryptedData) {
  try {
    const decrypted = CryptoJS.AES.decrypt(encryptedData, SECRET_KEY)
    const jsonString = decrypted.toString(CryptoJS.enc.Utf8)
    return JSON.parse(jsonString)
  } catch (error) {
    console.error('解密失败:', error)
    return null
  }
}

/**
 * 加密字符串
 * @param {string} text - 需要加密的字符串
 * @returns {string} - 加密后的字符串
 */
export function encryptText(text) {
  try {
    const encrypted = CryptoJS.AES.encrypt(text, SECRET_KEY).toString()
    return encrypted
  } catch (error) {
    console.error('加密失败:', error)
    return null
  }
}

/**
 * 解密字符串
 * @param {string} encryptedText - 加密的字符串
 * @returns {string} - 解密后的字符串
 */
export function decryptText(encryptedText) {
  try {
    const decrypted = CryptoJS.AES.decrypt(encryptedText, SECRET_KEY)
    return decrypted.toString(CryptoJS.enc.Utf8)
  } catch (error) {
    console.error('解密失败:', error)
    return null
  }
}