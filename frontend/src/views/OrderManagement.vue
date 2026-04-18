<template>
  <div class="order-management">
    <h2>订单管理</h2>
    
    <!-- 订单状态筛选 -->
    <div class="order-filter">
      <el-select v-model="selectedStatus" placeholder="选择订单状态" @change="filterOrders">
        <el-option label="全部" value=""></el-option>
        <el-option label="待付款" value="pending_payment"></el-option>
        <el-option label="待发货" value="pending_shipping"></el-option>
        <el-option label="待收货" value="pending_receipt"></el-option>
        <el-option label="已完成" value="completed"></el-option>
        <el-option label="已取消" value="cancelled"></el-option>
      </el-select>
      <el-select v-model="selectedType" placeholder="选择交易类型" @change="filterOrders">
        <el-option label="全部" value=""></el-option>
        <el-option label="购买" value="buy"></el-option>
        <el-option label="短租" value="rent"></el-option>
      </el-select>
    </div>
    
    <!-- 订单列表 -->
    <div class="order-list">
      <Skeleton v-if="loading" type="card" :count="5" />
      <div v-else-if="filteredOrders.length === 0" class="no-orders">
        <el-empty description="暂无订单" />
      </div>
      <div v-else class="order-item" v-for="order in filteredOrders" :key="order.id">
        <div class="order-header">
          <span class="order-id">订单号：{{ order.id }}</span>
          <span class="order-status" :class="order.status">{{ getStatusText(order.status) }}</span>
          <span class="order-time">{{ formatOrderTime(order.created_at) }}</span>
        </div>
        <div class="order-content">
          <div class="book-info">
            <img :src="order.book.cover_image || 'https://via.placeholder.com/80x120'" alt="图书封面">
            <div class="book-details">
              <h3>{{ order.book.title }}</h3>
              <p>作者：{{ order.book.author }}</p>
              <p>ISBN：{{ order.book.isbn }}</p>
            </div>
          </div>
          <div class="order-meta">
            <p>交易方式：{{ order.trade_type === 'buy' ? '购买' : '短租' }}</p>
            <p>价格：¥{{ order.price }}</p>
            <p>联系人：{{ order.contact_name }}</p>
            <p>手机号：{{ order.contact_phone }}</p>
            <p>取货地点：{{ getPickupLocationText(order.pickup_location, order.other_location) }}</p>
          </div>
        </div>
        <div class="order-actions">
          <el-button v-if="order.status === 'pending_payment'" type="primary" @click="payOrder(order.id)">立即付款</el-button>
          <el-button v-if="order.status === 'pending_shipping'" type="success" @click="shipOrder(order.id)">确认发货</el-button>
          <el-button v-if="order.status === 'pending_receipt'" type="info" @click="receiveOrder(order.id)">确认收货</el-button>
          <el-button v-if="order.status === 'pending_payment'" type="danger" @click="cancelOrder(order.id)">取消订单</el-button>
          <el-button type="text" @click="viewOrderDetail(order.id)">查看详情</el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { ElMessage } from 'element-plus'
import Skeleton from '../components/Skeleton.vue'
import logger from '../utils/logger'

// 订单数据
const orders = ref([])
const loading = ref(true)
const selectedStatus = ref('')
const selectedType = ref('')
const pollInterval = ref(null)

// 筛选后的订单
const filteredOrders = computed(() => orders.value.filter(order => {
  const matchesStatus = !selectedStatus.value || order.status === selectedStatus.value
  const matchesType = !selectedType.value || order.trade_type === selectedType.value
  return matchesStatus && matchesType
}))

/**
 * 生命周期：组件挂载后
 */
onMounted(() => {
  fetchOrders()
  // 启动轮询，每30秒更新一次订单状态
  pollInterval.value = setInterval(() => {
    fetchOrders()
  }, 30000)
  logger.pageView('OrderManagement')
})

/**
 * 生命周期：组件卸载前
 */
onBeforeUnmount(() => {
  // 清除轮询
  if (pollInterval.value) {
    clearInterval(pollInterval.value);
  }
});

/**
 * 获取订单列表
 */
const fetchOrders = () => {
  loading.value = true
  // 模拟从API获取订单列表
  setTimeout(() => {
    orders.value = [
      {
        id: '202603310001',
        book: {
          id: 1,
          title: '高等数学',
          author: '同济大学数学系',
          isbn: '9787040494435',
          cover_image: 'https://via.placeholder.com/200x300'
        },
        price: 39.9,
        trade_type: 'buy',
        status: 'pending_payment',
        contact_name: '李四',
        contact_phone: '13800138000',
        pickup_location: 'library',
        other_location: '',
        created_at: new Date().toISOString()
      },
      {
        id: '202603310002',
        book: {
          id: 2,
          title: '大学物理',
          author: '张三',
          isbn: '9787040494436',
          cover_image: 'https://via.placeholder.com/200x300'
        },
        price: 29.9,
        trade_type: 'rent',
        status: 'pending_shipping',
        contact_name: '王五',
        contact_phone: '13900139000',
        pickup_location: 'teaching_building',
        other_location: '',
        created_at: new Date(Date.now() - 3600000).toISOString()
      },
      {
        id: '202603310003',
        book: {
          id: 3,
          title: '计算机导论',
          author: '赵六',
          isbn: '9787040494437',
          cover_image: 'https://via.placeholder.com/200x300'
        },
        price: 49.9,
        trade_type: 'buy',
        status: 'completed',
        contact_name: '钱七',
        contact_phone: '13700137000',
        pickup_location: 'dormitory',
        other_location: '',
        created_at: new Date(Date.now() - 86400000).toISOString()
      }
    ]
    loading.value = false
  }, 1000)
}

/**
 * 筛选订单
 */
const filterOrders = () => {
  // 筛选订单
}

/**
 * 获取订单状态文本
 * @param {string} status 状态代码
 * @returns {string} 状态文本
 */
const getStatusText = (status) => {
  const statusMap = {
    'pending_payment': '待付款',
    'pending_shipping': '待发货',
    'pending_receipt': '待收货',
    'completed': '已完成',
    'cancelled': '已取消'
  }
  return statusMap[status] || status
}

/**
 * 获取取货地点文本
 * @param {string} location 地点代码
 * @param {string} other 其他地点
 * @returns {string} 地点文本
 */
const getPickupLocationText = (location, other) => {
  const locationMap = {
    'library': '图书馆门口',
    'teaching_building': '教学楼大厅',
    'dormitory': '宿舍楼下',
    'other': other || '其他地点'
  }
  return locationMap[location] || location
}

/**
 * 格式化订单时间
 * @param {string} time 时间字符串
 * @returns {string} 格式化后的时间
 */
const formatOrderTime = (time) => {
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

/**
 * 付款
 * @param {string} orderId 订单ID
 */
const payOrder = (orderId) => {
  // 模拟付款
  updateOrderStatus(orderId, 'pending_shipping')
}

/**
 * 发货
 * @param {string} orderId 订单ID
 */
const shipOrder = (orderId) => {
  // 模拟发货
  updateOrderStatus(orderId, 'pending_receipt')
}

/**
 * 收货
 * @param {string} orderId 订单ID
 */
const receiveOrder = (orderId) => {
  // 模拟收货
  updateOrderStatus(orderId, 'completed')
}

/**
 * 取消订单
 * @param {string} orderId 订单ID
 */
const cancelOrder = (orderId) => {
  // 模拟取消订单
  updateOrderStatus(orderId, 'cancelled')
}

/**
 * 更新订单状态
 * @param {string} orderId 订单ID
 * @param {string} newStatus 新状态
 */
const updateOrderStatus = (orderId, newStatus) => {
  const order = orders.value.find(o => o.id === orderId)
  if (order) {
    order.status = newStatus
    ElMessage.success('订单状态已更新')
  }
}

/**
 * 查看订单详情
 * @param {string} orderId 订单ID
 */
const viewOrderDetail = (orderId) => {
  // 跳转到订单详情页
  ElMessage.info(`查看订单详情功能开发中，订单ID: ${orderId}`)
}
</script>

<style scoped>
.order-management {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.order-management h2 {
  margin-bottom: 30px;
  color: #333;
  text-align: center;
  font-size: 1.8rem;
  font-weight: bold;
}

.order-filter {
  display: flex;
  gap: 20px;
  margin-bottom: 30px;
  padding: 20px;
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.order-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.no-orders {
  padding: 60px 0;
  text-align: center;
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.order-item {
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 20px;
  transition: all 0.3s ease;
}

.order-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.15);
}

.order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #e0e0e0;
}

.order-id {
  font-weight: bold;
  color: #333;
}

.order-status {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: bold;
  color: white;
}

.order-status.pending_payment {
  background-color: #FF9800;
}

.order-status.pending_shipping {
  background-color: #2196F3;
}

.order-status.pending_receipt {
  background-color: #4CAF50;
}

.order-status.completed {
  background-color: #9E9E9E;
}

.order-status.cancelled {
  background-color: #F44336;
}

.order-time {
  font-size: 0.8rem;
  color: #999;
}

.order-content {
  display: flex;
  margin-bottom: 20px;
  gap: 30px;
}

.book-info {
  display: flex;
  gap: 20px;
  flex: 2;
}

.book-info img {
  width: 80px;
  height: 120px;
  object-fit: cover;
  border-radius: 5px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.book-details {
  flex: 1;
}

.book-details h3 {
  margin-bottom: 10px;
  color: #333;
  font-size: 1.1rem;
  font-weight: bold;
}

.book-details p {
  margin-bottom: 5px;
  color: #666;
  font-size: 0.9rem;
}

.order-meta {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.order-meta p {
  color: #666;
  font-size: 0.9rem;
}

.order-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding-top: 20px;
  border-top: 1px solid #e0e0e0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .order-management {
    padding: 10px;
  }
  
  .order-filter {
    flex-direction: column;
    gap: 10px;
  }
  
  .order-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .order-content {
    flex-direction: column;
    gap: 20px;
  }
  
  .book-info {
    flex: 1;
  }
  
  .order-actions {
    flex-direction: column;
  }
  
  .order-actions .el-button {
    width: 100%;
  }
}
</style>