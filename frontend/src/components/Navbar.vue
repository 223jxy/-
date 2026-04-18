<template>
  <nav class="navbar">
    <div class="navbar-container">
      <!-- 品牌Logo -->
      <div class="navbar-brand" @click="navigateToHome">
        <h1>书驿云桥</h1>
      </div>
      
      <!-- 导航链接 -->
      <div class="navbar-links">
        <a href="#" @click.prevent="navigateToHome">首页</a>
        <a href="#" @click.prevent="navigateToTrade">图书交易</a>
        <a href="#" @click.prevent="navigateToPublish">发布图书</a>
        <a href="#" @click.prevent="navigateToCarbonPoints">碳积分</a>
        <a href="#" @click.prevent="navigateToDataAnalysis">数据统计</a>
      </div>
      
      <!-- 用户操作 -->
      <div class="navbar-actions">
        <!-- 通知组件 -->
        <Notification />
        
        <!-- 用户中心 -->
        <el-dropdown trigger="click">
          <div class="user-profile">
            <i class="el-icon-user"></i>
            <span>用户中心</span>
          </div>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="navigateToUserCenter">个人信息</el-dropdown-item>
              <el-dropdown-item @click="navigateToOrderManagement">订单管理</el-dropdown-item>
              <el-dropdown-item divided @click="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import Notification from './Notification.vue'

const router = useRouter()

/**
 * 导航到首页
 */
const navigateToHome = () => {
  router.push('/')
}

/**
 * 导航到图书交易页面
 */
const navigateToTrade = () => {
  router.push('/book-trade')
}

/**
 * 导航到发布图书页面
 */
const navigateToPublish = () => {
  router.push('/publish-book')
}

/**
 * 导航到碳积分页面
 */
const navigateToCarbonPoints = () => {
  router.push('/carbon-points')
}

/**
 * 导航到数据统计页面
 */
const navigateToDataAnalysis = () => {
  router.push('/data-analysis')
}

/**
 * 导航到用户中心页面
 */
const navigateToUserCenter = () => {
  router.push('/user-center')
}

/**
 * 导航到订单管理页面
 */
const navigateToOrderManagement = () => {
  router.push('/order-management')
}

/**
 * 退出登录
 */
const logout = () => {
  // 模拟退出登录
  ElMessage.success('退出登录成功')
  router.push('/login')
}
</script>

<style scoped>
.navbar {
  background-color: white;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.navbar-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 60px;
}

.navbar-brand {
  cursor: pointer;
}

.navbar-brand h1 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: bold;
  color: #667eea;
  transition: color 0.3s ease;
}

.navbar-brand h1:hover {
  color: #764ba2;
}

.navbar-links {
  display: flex;
  gap: 30px;
}

.navbar-links a {
  text-decoration: none;
  color: #333;
  font-size: 1rem;
  font-weight: 500;
  transition: all 0.3s ease;
  position: relative;
}

.navbar-links a:hover {
  color: #667eea;
}

.navbar-links a::after {
  content: '';
  position: absolute;
  bottom: -5px;
  left: 0;
  width: 0;
  height: 2px;
  background-color: #667eea;
  transition: width 0.3s ease;
}

.navbar-links a:hover::after {
  width: 100%;
}

.navbar-actions {
  display: flex;
  align-items: center;
  gap: 20px;
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 5px;
  cursor: pointer;
  padding: 5px 10px;
  border-radius: 20px;
  transition: all 0.3s ease;
}

.user-profile:hover {
  background-color: #f5f5f5;
}

.user-profile i {
  font-size: 18px;
  color: #666;
}

.user-profile span {
  color: #333;
  font-size: 0.9rem;
  font-weight: 500;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .navbar-container {
    padding: 0 10px;
  }
  
  .navbar-brand h1 {
    font-size: 1.3rem;
  }
  
  .navbar-links {
    gap: 20px;
  }
  
  .navbar-links a {
    font-size: 0.9rem;
  }
  
  .user-profile span {
    display: none;
  }
}

@media (max-width: 480px) {
  .navbar-links {
    display: none;
  }
  
  .navbar-actions {
    gap: 10px;
  }
}
</style>