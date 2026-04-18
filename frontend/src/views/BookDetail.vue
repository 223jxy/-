<template>
  <div class="book-detail">
    <!-- 图书基本信息 -->
    <div class="book-info">
      <div class="book-cover">
        <img :src="safeBook.cover_image || 'https://via.placeholder.com/200x300'" alt="图书封面">
        <div class="condition-badge" :class="book.condition">{{ getConditionText(book.condition) }}</div>
      </div>
      <div class="book-meta">
        <h1>{{ safeBook.title }}</h1>
        <p class="author">作者：{{ safeBook.author }}</p>
        <p class="isbn">ISBN：{{ safeBook.isbn }}</p>
        <p class="price">价格：¥{{ safeBook.price }}</p>
        <p class="original-price">原价：¥{{ safeBook.original_price }}</p>
        <p class="category">分类：{{ safeBook.category }}</p>
        <p class="campus">校园：{{ safeBook.university }} - {{ safeBook.major }} - {{ safeBook.grade }}</p>
        
        <!-- 订单表单 -->
        <el-form :model="orderForm" :rules="rules" ref="orderForm" label-width="80px" class="order-form">
          <el-form-item label="交易方式" prop="trade_type">
            <el-radio-group v-model="orderForm.trade_type">
              <el-radio label="buy">购买</el-radio>
              <el-radio label="rent">短租</el-radio>
            </el-radio-group>
          </el-form-item>
          <el-form-item label="联系人" prop="contact_name">
            <el-input v-model="orderForm.contact_name" placeholder="请输入联系人姓名" clearable></el-input>
          </el-form-item>
          <el-form-item label="手机号" prop="contact_phone">
            <el-input v-model="orderForm.contact_phone" placeholder="请输入手机号" clearable></el-input>
          </el-form-item>
          <el-form-item label="取货地点" prop="pickup_location">
            <el-select v-model="orderForm.pickup_location" placeholder="请选择取货地点" clearable>
              <el-option label="图书馆门口" value="library"></el-option>
              <el-option label="教学楼大厅" value="teaching_building"></el-option>
              <el-option label="宿舍楼下" value="dormitory"></el-option>
              <el-option label="其他地点" value="other"></el-option>
            </el-select>
          </el-form-item>
          <el-form-item v-if="orderForm.pickup_location === 'other'" label="其他地点" prop="other_location">
            <el-input v-model="orderForm.other_location" placeholder="请输入具体地点" clearable></el-input>
          </el-form-item>
          <el-form-item label="备注" prop="remark">
            <el-input type="textarea" v-model="orderForm.remark" placeholder="请输入备注信息" rows="2"></el-input>
          </el-form-item>
        </el-form>
        
        <!-- 操作按钮 -->
        <div class="action-buttons">
          <el-button type="primary" size="large" @click="submitOrder" :loading="loading">确认下单</el-button>
          <el-button type="info" size="large" @click="contactSeller" style="margin-left: 20px;">联系卖家</el-button>
          <el-button size="large" @click="$router.push('/book-trade')" style="margin-left: 20px;">返回列表</el-button>
        </div>
      </div>
    </div>
    
    <!-- 图书描述 -->
    <div class="book-description">
      <h2>图书描述</h2>
      <p>{{ safeBook.description }}</p>
    </div>
    
    <!-- 卖家信息 -->
    <div class="seller-info">
      <h2>卖家信息</h2>
      <p>用户名：{{ safeSeller.username }}</p>
      <p>学校：{{ safeSeller.university }}</p>
      <p>专业：{{ safeSeller.major }}</p>
      <p>发布时间：{{ formatPublishTime(book.created_at) }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { escapeHtml } from '../utils/xss'
import logger from '../utils/logger'

const router = useRouter()
const route = useRoute()

// 图书信息
const book = reactive({
  id: 1,
  title: '高等数学',
  author: '同济大学数学系',
  isbn: '9787040494435',
  price: 39.9,
  original_price: 59.9,
  condition: 'A1',
  category: '教材',
  university: '北京大学',
  major: '数学',
  grade: '大一',
  description: '本教材是同济大学数学系编写的《高等数学》第七版，内容包括函数与极限、导数与微分、微分中值定理与导数的应用、不定积分、定积分及其应用、微分方程、向量代数与空间解析几何、多元函数微分法及其应用、重积分、曲线积分与曲面积分、无穷级数等。',
  owner_id: 1,
  created_at: new Date().toISOString()
})

// 卖家信息
const seller = reactive({
  username: '张三',
  university: '北京大学',
  major: '数学'
})

// 订单表单
const orderForm = reactive({
  trade_type: 'buy',
  contact_name: '',
  contact_phone: '',
  pickup_location: '',
  other_location: '',
  remark: ''
})

// 其他状态
const loading = ref(false)
const orderFormRef = ref(null)

// 表单验证规则
const rules = {
  trade_type: [
    { required: true, message: '请选择交易方式', trigger: 'change' }
  ],
  contact_name: [
    { required: true, message: '请输入联系人姓名', trigger: 'blur' },
    { min: 2, max: 20, message: '姓名长度在2到20个字符之间', trigger: 'blur' }
  ],
  contact_phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确', trigger: 'blur' }
  ],
  pickup_location: [
    { required: true, message: '请选择取货地点', trigger: 'change' }
  ],
  other_location: [
    { required: true, message: '请输入具体地点', trigger: 'blur' },
    { min: 5, message: '地点描述至少5个字符', trigger: 'blur' }
  ],
  remark: [
    { max: 100, message: '备注信息不能超过100个字符', trigger: 'blur' }
  ]
}

// 安全的图书信息（防止XSS）
const safeBook = computed(() => ({
  ...book,
  title: escapeHtml(book.title),
  author: escapeHtml(book.author),
  description: escapeHtml(book.description),
  university: escapeHtml(book.university),
  major: escapeHtml(book.major),
  grade: escapeHtml(book.grade)
}))

// 安全的卖家信息（防止XSS）
const safeSeller = computed(() => ({
  ...seller,
  username: escapeHtml(seller.username),
  university: escapeHtml(seller.university),
  major: escapeHtml(seller.major)
}))

/**
 * 生命周期：组件挂载后
 */
onMounted(() => {
  // 模拟从API获取图书详情
  const bookId = route.params.id
  logger.pageView('BookDetail', { bookId })
  // 实际项目中，这里应该调用API获取图书详情
})

/**
 * 获取品相文本
 * @param {string} condition 品相代码
 * @returns {string} 品相文本
 */
const getConditionText = (condition) => {
  const conditionMap = {
    'A1': '九成新',
    'A2': '八五新',
    'B': '八成新',
    'C': '五成新以上'
  }
  return conditionMap[condition] || condition
}

/**
 * 提交订单
 */
const submitOrder = () => {
  // 表单验证
  orderFormRef.value.validate((valid) => {
    if (valid) {
      loading.value = true
      // 模拟下单
      setTimeout(() => {
        ElMessage.success('订单提交成功')
        loading.value = false
        // 跳转到订单详情或用户中心
        router.push('/user-center')
      }, 1000)
    } else {
      ElMessage.error('请检查表单填写是否完整')
      return false
    }
  })
}

/**
 * 联系卖家
 */
const contactSeller = () => {
  ElMessage.info('联系卖家功能开发中')
}

/**
 * 格式化发布时间
 * @param {string} time 时间字符串
 * @returns {string} 格式化后的时间
 */
const formatPublishTime = (time) => {
  if (!time) return '未知'
  const date = new Date(time)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style scoped>
.book-detail {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.book-info {
  display: flex;
  background: white;
  padding: 30px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  margin-bottom: 30px;
  position: relative;
}

.book-cover {
  margin-right: 40px;
  position: relative;
}

.book-cover img {
  width: 200px;
  height: 300px;
  object-fit: cover;
  border-radius: 10px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
}

.book-cover img:hover {
  transform: scale(1.02);
}

.condition-badge {
  position: absolute;
  top: 10px;
  right: 10px;
  padding: 5px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: bold;
  color: white;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
}

.condition-badge.A1 {
  background-color: #4CAF50;
}

.condition-badge.A2 {
  background-color: #8BC34A;
}

.condition-badge.B {
  background-color: #FFC107;
}

.condition-badge.C {
  background-color: #FF9800;
}

.book-meta {
  flex: 1;
}

.book-meta h1 {
  margin-bottom: 20px;
  color: #333;
  font-size: 1.8rem;
  font-weight: bold;
  line-height: 1.2;
}

.book-meta p {
  margin-bottom: 10px;
  color: #666;
  font-size: 1.1rem;
}

.book-meta .price {
  color: #ff6b6b;
  font-weight: bold;
  font-size: 1.8rem;
  margin: 20px 0;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.book-meta .original-price {
  text-decoration: line-through;
  color: #999;
  font-size: 1rem;
}

.book-meta .category {
  color: #4ecdc4;
  font-weight: bold;
}

.order-form {
  margin: 30px 0;
  padding: 20px;
  background: #f9f9f9;
  border-radius: 10px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.action-buttons {
  margin-top: 30px;
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
}

.book-description {
  background: white;
  padding: 30px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  margin-bottom: 30px;
}

.book-description h2 {
  margin-bottom: 20px;
  color: #333;
  font-size: 1.5rem;
  font-weight: bold;
  border-bottom: 2px solid #409EFF;
  padding-bottom: 10px;
}

.book-description p {
  color: #666;
  line-height: 1.8;
  font-size: 1.1rem;
  text-align: justify;
}

.seller-info {
  background: white;
  padding: 30px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.seller-info h2 {
  margin-bottom: 20px;
  color: #333;
  font-size: 1.5rem;
  font-weight: bold;
  border-bottom: 2px solid #409EFF;
  padding-bottom: 10px;
}

.seller-info p {
  margin-bottom: 10px;
  color: #666;
  font-size: 1.1rem;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .book-detail {
    padding: 10px;
  }
  
  .book-info {
    flex-direction: column;
    align-items: center;
    text-align: center;
    padding: 20px;
  }
  
  .book-cover {
    margin-right: 0;
    margin-bottom: 30px;
  }
  
  .book-cover img {
    width: 180px;
    height: 270px;
  }
  
  .book-meta h1 {
    font-size: 1.5rem;
  }
  
  .book-meta .price {
    font-size: 1.5rem;
  }
  
  .order-form {
    padding: 15px;
  }
  
  .action-buttons {
    justify-content: center;
  }
  
  .book-description,
  .seller-info {
    padding: 20px;
  }
  
  .book-description h2,
  .seller-info h2 {
    font-size: 1.3rem;
  }
}

@media (max-width: 480px) {
  .book-cover img {
    width: 150px;
    height: 225px;
  }
  
  .book-meta h1 {
    font-size: 1.3rem;
  }
  
  .book-meta p {
    font-size: 1rem;
  }
  
  .order-form .el-form-item {
    margin-bottom: 15px;
  }
  
  .action-buttons {
    flex-direction: column;
  }
  
  .action-buttons .el-button {
    margin-left: 0 !important;
  }
}
</style>