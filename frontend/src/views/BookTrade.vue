<template>
  <div class="book-trade">
    <!-- 搜索和筛选区域 -->
    <div class="search-bar">
      <el-form :inline="true" class="search-form">
        <el-form-item label="搜索">
          <el-input v-model="searchQuery" placeholder="搜索图书名称、作者或ISBN" clearable @keyup.enter="searchBooks"></el-input>
        </el-form-item>
        <el-form-item label="学校">
          <el-select v-model="selectedUniversity" placeholder="选择学校" clearable>
            <el-option label="北京大学" value="北京大学"></el-option>
            <el-option label="清华大学" value="清华大学"></el-option>
            <el-option label="复旦大学" value="复旦大学"></el-option>
            <el-option label="上海交通大学" value="上海交通大学"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="专业">
          <el-select v-model="selectedMajor" placeholder="选择专业" clearable>
            <el-option label="数学" value="数学"></el-option>
            <el-option label="物理" value="物理"></el-option>
            <el-option label="计算机" value="计算机"></el-option>
            <el-option label="化学" value="化学"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="年级">
          <el-select v-model="selectedGrade" placeholder="选择年级" clearable>
            <el-option label="大一" value="大一"></el-option>
            <el-option label="大二" value="大二"></el-option>
            <el-option label="大三" value="大三"></el-option>
            <el-option label="大四" value="大四"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="selectedCategory" placeholder="选择分类" clearable>
            <el-option label="教材" value="教材"></el-option>
            <el-option label="备考资料" value="备考资料"></el-option>
            <el-option label="课外读物" value="课外读物"></el-option>
            <el-option label="其他" value="其他"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="品相">
          <el-select v-model="selectedCondition" placeholder="选择品相" clearable>
            <el-option label="A1（九成新）" value="A1"></el-option>
            <el-option label="A2（八五新）" value="A2"></el-option>
            <el-option label="B（八成新）" value="B"></el-option>
            <el-option label="C（五成新以上）" value="C"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="searchBooks" :loading="loading">搜索</el-button>
          <el-button @click="resetSearch" style="margin-left: 10px;">重置</el-button>
        </el-form-item>
      </el-form>
      
      <!-- 排序和发布按钮 -->
      <div class="sort-and-publish">
        <el-select v-model="sortBy" placeholder="排序方式" @change="sortBooks" clearable>
          <el-option label="价格从低到高" value="price_asc"></el-option>
          <el-option label="价格从高到低" value="price_desc"></el-option>
          <el-option label="最新发布" value="latest"></el-option>
          <el-option label="品相近到远" value="condition_asc"></el-option>
        </el-select>
        <el-button type="success" @click="navigateToPublish" style="margin-left: 20px;">发布图书</el-button>
      </div>
    </div>
    
    <!-- 搜索结果统计 -->
    <div class="search-result">
      <span v-if="!loading">共找到 {{ books.length }} 本图书</span>
      <span v-else>搜索中...</span>
    </div>
    
    <!-- 图书列表 -->
    <div class="book-list">
      <Skeleton v-if="loading" type="card" :count="6" />
      <div v-else-if="books.length === 0" class="no-result">
        <el-empty description="没有找到相关图书" />
      </div>
      <div v-else class="book-item" v-for="book in books" :key="book.id" @click="navigateToDetail(book.id)">
        <div class="book-cover">
          <img v-lazyload="book.cover_image || 'https://via.placeholder.com/100x150'" alt="图书封面">
          <div class="condition-badge" :class="book.condition">{{ getConditionText(book.condition) }}</div>
        </div>
        <div class="book-info">
          <h3>{{ book.title }}</h3>
          <p class="author">作者：{{ book.author }}</p>
          <p class="isbn">ISBN：{{ book.isbn }}</p>
          <p class="price">价格：¥{{ book.price }}</p>
          <p class="category">分类：{{ book.category }}</p>
          <p class="campus">校园：{{ book.university }} - {{ book.major }} - {{ book.grade }}</p>
          <p class="publish-time">发布时间：{{ formatPublishTime(book.created_at) }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useStore } from 'vuex'
import Skeleton from '../components/Skeleton.vue'
import logger from '../utils/logger'

// 状态管理
const store = useStore()
const router = useRouter()
const route = useRoute()

// 搜索和筛选条件
const searchQuery = ref('')
const selectedUniversity = ref('')
const selectedMajor = ref('')
const selectedGrade = ref('')
const selectedCategory = ref('')
const selectedCondition = ref('')
const sortBy = ref('')

// 数据状态
const books = ref([])
const loading = ref(true)
const allBooks = ref([]) // 用于存储所有图书，方便筛选

/**
 * 生命周期：组件挂载后
 */
onMounted(() => {
  fetchBooks()
  logger.pageView('BookTrade')
})

/**
 * 获取图书列表
 */
const fetchBooks = async () => {
  loading.value = true
  try {
    // 调用Vuex action获取图书列表
    await store.dispatch('fetchBooks')
    allBooks.value = store.getters.getBooks
    books.value = [...allBooks.value]
  } catch (error) {
    logger.error('Failed to fetch books', { error: error.message })
  } finally {
    loading.value = false
  }
}

/**
 * 搜索图书
 */
const searchBooks = () => {
  loading.value = true
  setTimeout(() => {
    const filteredBooks = allBooks.value.filter(book => {
      // 搜索关键词匹配
      const searchLower = searchQuery.value.toLowerCase()
      const matchesSearch = !searchLower || 
                         book.title.toLowerCase().includes(searchLower) || 
                         book.author.toLowerCase().includes(searchLower) || 
                         book.isbn.includes(searchLower)
      
      // 其他筛选条件
      const matchesUniversity = !selectedUniversity.value || book.university === selectedUniversity.value
      const matchesMajor = !selectedMajor.value || book.major === selectedMajor.value
      const matchesGrade = !selectedGrade.value || book.grade === selectedGrade.value
      const matchesCategory = !selectedCategory.value || book.category === selectedCategory.value
      const matchesCondition = !selectedCondition.value || book.condition === selectedCondition.value
      
      return matchesSearch && matchesUniversity && matchesMajor && matchesGrade && matchesCategory && matchesCondition
    })
    
    books.value = filteredBooks
    sortBooks()
    loading.value = false
  }, 300)
}

/**
 * 排序图书
 */
const sortBooks = () => {
  if (!sortBy.value) return
  
  switch (sortBy.value) {
    case 'price_asc':
      books.value.sort((a, b) => a.price - b.price)
      break
    case 'price_desc':
      books.value.sort((a, b) => b.price - a.price)
      break
    case 'latest':
      books.value.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
      break
    case 'condition_asc':
      const conditionOrder = { 'A1': 0, 'A2': 1, 'B': 2, 'C': 3 }
      books.value.sort((a, b) => conditionOrder[a.condition] - conditionOrder[b.condition])
      break
  }
}

/**
 * 重置搜索条件
 */
const resetSearch = () => {
  searchQuery.value = ''
  selectedUniversity.value = ''
  selectedMajor.value = ''
  selectedGrade.value = ''
  selectedCategory.value = ''
  selectedCondition.value = ''
  sortBy.value = ''
  books.value = [...allBooks.value]
}

/**
 * 导航到发布图书页面
 */
const navigateToPublish = () => {
  router.push('/publish-book')
}

/**
 * 导航到图书详情页面
 * @param {number} bookId 图书ID
 */
const navigateToDetail = (bookId) => {
  router.push(`/book-detail/${bookId}`)
}

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
.book-trade {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.search-bar {
  margin-bottom: 30px;
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 20px;
}

.search-form {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  margin-bottom: 20px;
  gap: 10px;
}

.search-form .el-form-item {
  margin-right: 10px;
  margin-bottom: 10px;
}

.sort-and-publish {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  flex-wrap: wrap;
  gap: 10px;
}

.search-result {
  margin-bottom: 20px;
  font-size: 0.9rem;
  color: #666;
  font-weight: bold;
}

.no-result {
  grid-column: 1 / -1;
  padding: 60px 0;
  text-align: center;
}

.book-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.book-item {
  display: flex;
  background: white;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  cursor: pointer;
  position: relative;
  overflow: hidden;
}

.book-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.15);
}

.book-cover {
  margin-right: 20px;
  position: relative;
}

.book-cover img {
  width: 100px;
  height: 150px;
  object-fit: cover;
  border-radius: 5px;
  transition: transform 0.3s ease;
}

.book-item:hover .book-cover img {
  transform: scale(1.05);
}

.condition-badge {
  position: absolute;
  top: 0;
  right: 0;
  padding: 2px 8px;
  border-radius: 0 5px 0 5px;
  font-size: 0.7rem;
  font-weight: bold;
  color: white;
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

.book-info {
  flex: 1;
  min-width: 0;
}

.book-info h3 {
  margin-bottom: 10px;
  color: #333;
  font-size: 1.1rem;
  font-weight: bold;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.book-info p {
  margin-bottom: 5px;
  color: #666;
  font-size: 0.9rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.book-info .price {
  color: #ff6b6b;
  font-weight: bold;
  font-size: 1.2rem;
  margin: 10px 0;
}

.book-info .category {
  color: #4ecdc4;
  font-weight: bold;
}

.book-info .campus {
  margin-top: 5px;
  font-size: 0.8rem;
  color: #999;
}

.book-info .publish-time {
  margin-top: 5px;
  font-size: 0.75rem;
  color: #999;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .search-form {
    justify-content: center;
  }
  
  .sort-and-publish {
    justify-content: center;
  }
}

@media (max-width: 768px) {
  .book-trade {
    padding: 10px;
  }
  
  .search-bar {
    padding: 15px;
  }
  
  .search-form .el-form-item {
    margin-right: 5px;
  }
  
  .book-list {
    grid-template-columns: 1fr;
    gap: 15px;
  }
  
  .book-item {
    flex-direction: column;
    align-items: center;
    text-align: center;
    padding: 15px;
  }
  
  .book-cover {
    margin-right: 0;
    margin-bottom: 15px;
  }
  
  .book-cover img {
    width: 120px;
    height: 180px;
  }
  
  .book-info h3 {
    white-space: normal;
    overflow: visible;
  }
  
  .book-info p {
    white-space: normal;
    overflow: visible;
  }
}

@media (max-width: 480px) {
  .search-form {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-form .el-form-item {
    margin-right: 0;
  }
  
  .sort-and-publish {
    flex-direction: column;
    align-items: stretch;
  }
  
  .sort-and-publish .el-button {
    margin-left: 0;
    margin-top: 10px;
  }
}
</style>