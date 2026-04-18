<template>
  <div class="home">
    <!-- 英雄区 -->
    <div class="hero">
      <h1>书驿云桥</h1>
      <p>高校图书资源共享生态平台</p>
      <button class="btn-primary" @click="navigateToTrade">开始交易</button>
    </div>
    
    <!-- 功能特性 -->
    <div class="features">
      <div class="feature-item">
        <h3>智能图书交易</h3>
        <p>AI自动识别书籍信息，精准匹配供需</p>
      </div>
      <div class="feature-item">
        <h3>标准化运营</h3>
        <p>四级品相分级，统一定价模型</p>
      </div>
      <div class="feature-item">
        <h3>创新激励</h3>
        <p>首卖者收益，碳积分体系</p>
      </div>
      <div class="feature-item">
        <h3>校园配送</h3>
        <p>书驿骑士，当日达服务</p>
      </div>
      <div class="feature-item">
        <h3>公益联动</h3>
        <p>书香驿站，乡村教育支持</p>
      </div>
      <div class="feature-item">
        <h3>知识增值</h3>
        <p>学霸笔记，文创产品</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

/**
 * 导航到图书交易页面
 */
const navigateToTrade = () => {
  router.push('/book-trade')
}
</script>

<style scoped>
.home {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.hero {
  text-align: center;
  padding: 60px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 10px;
  margin-bottom: 40px;
}

.hero h1 {
  font-size: 3rem;
  margin-bottom: 20px;
}

.hero p {
  font-size: 1.2rem;
  margin-bottom: 30px;
}

.btn-primary {
  background-color: #fff;
  color: #667eea;
  border: none;
  padding: 12px 30px;
  font-size: 1.1rem;
  border-radius: 50px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}

.features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 30px;
}

.feature-item {
  background: white;
  padding: 30px;
  border-radius: 10px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.feature-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
}

.feature-item h3 {
  color: #667eea;
  margin-bottom: 15px;
  font-size: 1.3rem;
}

.feature-item p {
  color: #666;
  line-height: 1.6;
}
</style>