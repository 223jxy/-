<template>
  <div class="user-center">
    <h2>用户中心</h2>
    <div class="user-info">
      <div class="info-item">
        <span class="label">用户名：</span>
        <span class="value">{{ user.username }}</span>
      </div>
      <div class="info-item">
        <span class="label">邮箱：</span>
        <span class="value">{{ user.email }}</span>
      </div>
      <div class="info-item">
        <span class="label">学校：</span>
        <span class="value">{{ user.university }}</span>
      </div>
      <div class="info-item">
        <span class="label">专业：</span>
        <span class="value">{{ user.major }}</span>
      </div>
      <div class="info-item">
        <span class="label">年级：</span>
        <span class="value">{{ user.grade }}</span>
      </div>
      <div class="info-item">
        <span class="label">碳积分：</span>
        <span class="value">{{ user.carbon_points }}</span>
      </div>
    </div>
    
    <!-- 功能导航 -->
    <div class="user-nav">
      <h3>我的功能</h3>
      <div class="nav-items">
        <el-button type="primary" @click="navigateToOrderManagement">订单管理</el-button>
        <el-button type="success" @click="navigateToPublishBook">发布图书</el-button>
        <el-button type="info" @click="navigateToBookTrade">图书交易</el-button>
        <el-button type="warning" @click="navigateToCarbonPoints">碳积分</el-button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'UserCenter',
  data() {
    return {
      user: {
        username: '张三',
        email: 'zhangsan@example.com',
        university: '北京大学',
        major: '计算机科学与技术',
        grade: '大三',
        carbon_points: 120
      }
    }
  },
  methods: {
    navigateToOrderManagement() {
      this.$router.push('/order-management')
    },
    navigateToPublishBook() {
      this.$router.push('/publish-book')
    },
    navigateToBookTrade() {
      this.$router.push('/book-trade')
    },
    navigateToCarbonPoints() {
      this.$router.push('/carbon-points')
    }
  }
}
</script>

<style scoped>
.user-center {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.user-center h2 {
  margin-bottom: 30px;
  color: #333;
  text-align: center;
}

.user-info {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-bottom: 40px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  padding: 15px;
  border-bottom: 1px solid #e0e0e0;
}

.info-item:last-child {
  border-bottom: none;
}

.label {
  font-weight: bold;
  color: #666;
}

.value {
  color: #333;
}

.user-nav {
  background: #f9f9f9;
  padding: 30px;
  border-radius: 10px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.user-nav h3 {
  margin-bottom: 20px;
  color: #333;
  font-size: 1.2rem;
  font-weight: bold;
  border-bottom: 2px solid #409EFF;
  padding-bottom: 10px;
}

.nav-items {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .user-nav {
    padding: 20px;
  }
  
  .nav-items {
    grid-template-columns: 1fr;
  }
  
  .nav-items .el-button {
    width: 100%;
  }
}
</style>