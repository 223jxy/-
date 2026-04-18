<template>
  <div class="data-analysis">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>数据统计与分析</h2>
      <div class="header-actions">
        <el-button-group>
          <el-button :type="dimension === 'personal' ? 'primary' : ''" @click="switchDimension('personal')">
            个人数据
          </el-button>
          <el-button :type="dimension === 'campus' ? 'primary' : ''" @click="switchDimension('campus')">
            校园数据
          </el-button>
        </el-button-group>
      </div>
    </div>

    <!-- 时间筛选 -->
    <div class="filter-section">
      <el-card shadow="hover">
        <div class="filter-content">
          <div class="time-filter">
            <el-radio-group v-model="timeRange" @change="handleTimeRangeChange">
              <el-radio-button label="today">今日</el-radio-button>
              <el-radio-button label="week">本周</el-radio-button>
              <el-radio-button label="month">本月</el-radio-button>
              <el-radio-button label="custom">自定义</el-radio-button>
            </el-radio-group>
            <el-date-picker
              v-if="timeRange === 'custom'"
              v-model="customDateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              @change="handleCustomDateChange"
            />
          </div>
          <div class="export-actions">
            <el-dropdown @command="handleExport">
              <el-button type="success">
                导出数据 <el-icon class="el-icon--right"><arrow-down /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="excel">导出Excel</el-dropdown-item>
                  <el-dropdown-item command="image">导出图片</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="5" animated />
      <el-skeleton :rows="5" animated style="margin-top: 20px;" />
    </div>

    <!-- 错误状态 -->
    <el-alert
      v-else-if="error"
      :title="error"
      type="error"
      show-icon
      :closable="false"
      class="error-alert"
    />

    <!-- 空数据状态 -->
    <el-empty
      v-else-if="isEmpty"
      description="暂无数据"
      :image-size="200"
    />

    <!-- 数据内容 -->
    <div v-else class="data-content">
      <!-- 统计卡片 -->
      <div class="stat-cards">
        <el-row :gutter="20">
          <el-col :xs="12" :sm="12" :md="6" :lg="6">
            <el-card shadow="hover" class="stat-card">
              <div class="stat-content">
                <div class="stat-icon" style="background: linear-gradient(135deg, #409EFF 0%, #66B1FF 100%);">
                  <el-icon><document /></el-icon>
                </div>
                <div class="stat-info">
                  <div class="stat-label">图书总数</div>
                  <div class="stat-value">
                    <animated-number :value="stats.books.total" />
                  </div>
                  <div class="stat-trend up">
                    <el-icon><top /></el-icon>
                    <span>较昨日 +{{ stats.books.trend }}%</span>
                  </div>
                </div>
              </div>
            </el-card>
          </el-col>
          <el-col :xs="12" :sm="12" :md="6" :lg="6">
            <el-card shadow="hover" class="stat-card">
              <div class="stat-content">
                <div class="stat-icon" style="background: linear-gradient(135deg, #67C23A 0%, #85CE61 100%);">
                  <el-icon><shopping-cart /></el-icon>
                </div>
                <div class="stat-info">
                  <div class="stat-label">已售出</div>
                  <div class="stat-value">
                    <animated-number :value="stats.books.sold" />
                  </div>
                  <div class="stat-trend up">
                    <el-icon><top /></el-icon>
                    <span>较上周 +{{ stats.books.soldTrend }}%</span>
                  </div>
                </div>
              </div>
            </el-card>
          </el-col>
          <el-col :xs="12" :sm="12" :md="6" :lg="6">
            <el-card shadow="hover" class="stat-card">
              <div class="stat-content">
                <div class="stat-icon" style="background: linear-gradient(135deg, #E6A23C 0%, #F7BA2A 100%);">
                  <el-icon><tickets /></el-icon>
                </div>
                <div class="stat-info">
                  <div class="stat-label">订单总数</div>
                  <div class="stat-value">
                    <animated-number :value="stats.orders.total" />
                  </div>
                  <div class="stat-trend down">
                    <el-icon><bottom /></el-icon>
                    <span>较上月 -{{ stats.orders.trend }}%</span>
                  </div>
                </div>
              </div>
            </el-card>
          </el-col>
          <el-col :xs="12" :sm="12" :md="6" :lg="6">
            <el-card shadow="hover" class="stat-card">
              <div class="stat-content">
                <div class="stat-icon" style="background: linear-gradient(135deg, #409EFF 0%, #67C23A 100%);">
                  <el-icon><coin /></el-icon>
                </div>
                <div class="stat-info">
                  <div class="stat-label">碳积分</div>
                  <div class="stat-value">
                    <animated-number :value="stats.carbonPoints.total" />
                  </div>
                  <div class="stat-trend up">
                    <el-icon><top /></el-icon>
                    <span>累计 {{ stats.carbonPoints.total }} 积分</span>
                  </div>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- 图表区域 -->
      <div class="charts-section">
        <el-row :gutter="20">
          <!-- 图书流通趋势 -->
          <el-col :xs="24" :sm="24" :md="12" :lg="12">
            <el-card shadow="hover" class="chart-card">
              <template #header>
                <div class="chart-header">
                  <span class="chart-title">图书流通趋势</span>
                  <el-radio-group v-model="chartTypes.books" size="small">
                    <el-radio-button label="line">折线图</el-radio-button>
                    <el-radio-button label="bar">柱状图</el-radio-button>
                  </el-radio-group>
                </div>
              </template>
              <div ref="booksChartRef" class="chart-container" v-loading="chartsLoading.books"></div>
            </el-card>
          </el-col>

          <!-- 碳积分增长趋势 -->
          <el-col :xs="24" :sm="24" :md="12" :lg="12">
            <el-card shadow="hover" class="chart-card">
              <template #header>
                <div class="chart-header">
                  <span class="chart-title">碳积分增长趋势</span>
                  <el-radio-group v-model="chartTypes.carbon" size="small">
                    <el-radio-button label="line">折线图</el-radio-button>
                    <el-radio-button label="bar">柱状图</el-radio-button>
                  </el-radio-group>
                </div>
              </template>
              <div ref="carbonChartRef" class="chart-container" v-loading="chartsLoading.carbon"></div>
            </el-card>
          </el-col>

          <!-- 图书分类占比 -->
          <el-col :xs="24" :sm="24" :md="12" :lg="12">
            <el-card shadow="hover" class="chart-card">
              <template #header>
                <div class="chart-header">
                  <span class="chart-title">图书分类占比</span>
                  <el-radio-group v-model="chartTypes.category" size="small">
                    <el-radio-button label="pie">饼图</el-radio-button>
                    <el-radio-button label="bar">柱状图</el-radio-button>
                  </el-radio-group>
                </div>
              </template>
              <div ref="categoryChartRef" class="chart-container" v-loading="chartsLoading.category"></div>
            </el-card>
          </el-col>

          <!-- 订单状态分布 -->
          <el-col :xs="24" :sm="24" :md="12" :lg="12">
            <el-card shadow="hover" class="chart-card">
              <template #header>
                <div class="chart-header">
                  <span class="chart-title">订单状态分布</span>
                  <el-radio-group v-model="chartTypes.order" size="small">
                    <el-radio-button label="pie">饼图</el-radio-button>
                    <el-radio-button label="bar">柱状图</el-radio-button>
                  </el-radio-group>
                </div>
              </template>
              <div ref="orderChartRef" class="chart-container" v-loading="chartsLoading.order"></div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- 数据表格 -->
      <div class="data-table-section">
        <el-card shadow="hover">
          <template #header>
            <div class="table-header">
              <span class="table-title">详细数据</span>
              <el-input
                v-model="tableSearch"
                placeholder="搜索"
                style="width: 200px;"
                clearable
              >
                <template #prefix>
                  <el-icon><search /></el-icon>
                </template>
              </el-input>
            </div>
          </template>
          <el-table
            :data="paginatedTableData"
            style="width: 100%"
            v-loading="tableLoading"
            :header-cell-style="{ background: '#f5f7fa', color: '#606266' }"
          >
            <el-table-column prop="date" label="日期" width="120" sortable />
            <el-table-column prop="books" label="图书数量" width="100" sortable />
            <el-table-column prop="sold" label="已售出" width="100" sortable />
            <el-table-column prop="rented" label="已出租" width="100" sortable />
            <el-table-column prop="orders" label="订单数" width="100" sortable />
            <el-table-column prop="carbonPoints" label="碳积分" width="100" sortable />
            <el-table-column prop="trend" label="趋势">
              <template #default="scope">
                <el-tag :type="scope.row.trend > 0 ? 'success' : 'danger'" size="small">
                  {{ scope.row.trend > 0 ? '+' : '' }}{{ scope.row.trend }}%
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="filteredTableData.length"
            layout="total, sizes, prev, pager, next, jumper"
            class="pagination"
          />
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Document,
  ShoppingCart,
  Tickets,
  Coin,
  Top,
  Bottom,
  ArrowDown,
  Search
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { saveAs } from 'file-saver'
import logger from '../utils/logger'

// 图表主题色配置
const THEME_COLORS = {
  primary: '#409EFF',
  success: '#67C23A',
  warning: '#E6A23C',
  danger: '#F56C6C',
  info: '#909399',
  gradient: [
    '#409EFF',
    '#67C23A',
    '#E6A23C',
    '#409EFF',
    '#67C23A',
    '#E6A23C',
    '#409EFF',
    '#67C23A'
  ]
}

// 状态管理
const dimension = ref('personal')
const timeRange = ref('week')
const customDateRange = ref([])
const loading = ref(false)
const error = ref('')
const tableSearch = ref('')
const currentPage = ref(1)
const pageSize = ref(10)

// 图表类型
const chartTypes = ref({
  books: 'line',
  carbon: 'line',
  category: 'pie',
  order: 'pie'
})

// 图表加载状态
const chartsLoading = ref({
  books: false,
  carbon: false,
  category: false,
  order: false
})

// 统计数据
const stats = ref({
  books: {
    total: 1256,
    sold: 324,
    rented: 189,
    trend: 12.5,
    soldTrend: 8.3
  },
  orders: {
    total: 892,
    completed: 756,
    trend: 5.2
  },
  carbonPoints: {
    total: 15680
  }
})

// 图表数据
const chartData = ref({
  books: {
    dates: ['03-01', '03-02', '03-03', '03-04', '03-05', '03-06', '03-07'],
    sold: [12, 15, 18, 14, 20, 16, 22],
    rented: [5, 8, 6, 10, 7, 9, 11]
  },
  carbon: {
    dates: ['03-01', '03-02', '03-03', '03-04', '03-05', '03-06', '03-07'],
    values: [120, 180, 240, 200, 280, 320, 380]
  },
  category: [
    { name: '教材', value: 450 },
    { name: '备考资料', value: 280 },
    { name: '课外读物', value: 320 },
    { name: '其他', value: 206 }
  ],
  order: [
    { name: '已完成', value: 756 },
    { name: '待付款', value: 45 },
    { name: '待发货', value: 38 },
    { name: '待收货', value: 53 }
  ]
})

// 表格数据
const tableData = ref([
  { date: '2026-03-07', books: 45, sold: 12, rented: 5, orders: 18, carbonPoints: 380, trend: 12.5 },
  { date: '2026-03-06', books: 42, sold: 16, rented: 9, orders: 22, carbonPoints: 320, trend: 8.3 },
  { date: '2026-03-05', books: 38, sold: 20, rented: 7, orders: 15, carbonPoints: 280, trend: -3.2 },
  { date: '2026-03-04', books: 35, sold: 14, rented: 10, orders: 20, carbonPoints: 200, trend: 5.6 },
  { date: '2026-03-03', books: 40, sold: 18, rented: 6, orders: 25, carbonPoints: 240, trend: 10.2 },
  { date: '2026-03-02', books: 36, sold: 15, rented: 8, orders: 19, carbonPoints: 180, trend: 7.8 },
  { date: '2026-03-01', books: 32, sold: 12, rented: 5, orders: 16, carbonPoints: 120, trend: 6.5 }
])

// 图表实例
let booksChart = null
let carbonChart = null
let categoryChart = null
let orderChart = null

// 图表DOM引用
const booksChartRef = ref(null)
const carbonChartRef = ref(null)
const categoryChartRef = ref(null)
const orderChartRef = ref(null)

// 防抖定时器
let resizeTimer = null

// 缓存数据
const cache = new Map()
const CACHE_DURATION = 5 * 60 * 1000 // 5分钟

// 计算属性
const isEmpty = computed(() => {
  return !stats.value.books.total && !stats.value.orders.total
})

const filteredTableData = computed(() => {
  if (!tableSearch.value) {
    return tableData.value
  }
  return tableData.value.filter(item =>
    item.date.includes(tableSearch.value) ||
    item.books.toString().includes(tableSearch.value)
  )
})

const paginatedTableData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredTableData.value.slice(start, end)
})

// 数字滚动动画组件
const AnimatedNumber = {
  props: {
    value: { type: Number, required: true }
  },
  setup(props) {
    const displayValue = ref(0)
    
    const animateValue = (start, end, duration) => {
      const startTime = performance.now()
      const animate = (currentTime) => {
        const elapsed = currentTime - startTime
        const progress = Math.min(elapsed / duration, 1)
        const easeProgress = 1 - Math.pow(1 - progress, 3)
        displayValue.value = Math.floor(start + (end - start) * easeProgress)
        if (progress < 1) {
          requestAnimationFrame(animate)
        }
      }
      requestAnimationFrame(animate)
    }
    
    watch(() => props.value, (newVal, oldVal) => {
      animateValue(oldVal || 0, newVal, 1000)
    }, { immediate: true })
    
    return () => displayValue.value.toLocaleString()
  }
}

// 生命周期
onMounted(() => {
  // 延迟加载数据，提高首屏加载速度
  setTimeout(() => {
    fetchData()
  }, 100)
  logger.pageView('DataAnalysis')
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  disposeCharts()
  if (resizeTimer) {
    clearTimeout(resizeTimer)
  }
  if (fetchTimer) {
    clearTimeout(fetchTimer)
  }
})

// 防抖定时器
let fetchTimer = null

// 监听图表类型变化
watch(chartTypes, () => {
  nextTick(() => {
    // 防抖处理，避免频繁重绘
    if (resizeTimer) {
      clearTimeout(resizeTimer)
    }
    resizeTimer = setTimeout(() => {
      initCharts()
    }, 100)
  })
}, { deep: true })

// 方法
const switchDimension = (newDimension) => {
  dimension.value = newDimension
  // 防抖处理，避免频繁请求
  if (fetchTimer) {
    clearTimeout(fetchTimer)
  }
  fetchTimer = setTimeout(() => {
    fetchData()
  }, 300)
}

const handleTimeRangeChange = (value) => {
  if (value !== 'custom') {
    // 防抖处理，避免频繁请求
    if (fetchTimer) {
      clearTimeout(fetchTimer)
    }
    fetchTimer = setTimeout(() => {
      fetchData()
    }, 300)
  }
}

const handleCustomDateChange = () => {
  if (customDateRange.value && customDateRange.value.length === 2) {
    // 防抖处理，避免频繁请求
    if (fetchTimer) {
      clearTimeout(fetchTimer)
    }
    fetchTimer = setTimeout(() => {
      fetchData()
    }, 300)
  }
}

const handleResize = () => {
  if (resizeTimer) {
    clearTimeout(resizeTimer)
  }
  resizeTimer = setTimeout(() => {
    booksChart?.resize()
    carbonChart?.resize()
    categoryChart?.resize()
    orderChart?.resize()
  }, 300)
}

const fetchData = async () => {
  loading.value = true
  error.value = ''
  
  try {
    const cacheKey = `${dimension.value}-${timeRange.value}`
    const cached = cache.get(cacheKey)
    
    if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
      stats.value = cached.data.stats
      chartData.value = cached.data.chartData
      tableData.value = cached.data.tableData
    } else {
      await new Promise(resolve => setTimeout(resolve, 800))
      
      cache.set(cacheKey, {
        data: {
          stats: stats.value,
          chartData: chartData.value,
          tableData: tableData.value
        },
        timestamp: Date.now()
      })
    }
    
    await nextTick()
    initCharts()
  } catch (err) {
    error.value = '数据加载失败，请稍后重试'
    logger.error('Failed to fetch data', { error: err.message })
  } finally {
    loading.value = false
  }
}

const initCharts = () => {
  initBooksChart()
  initCarbonChart()
  initCategoryChart()
  initOrderChart()
}

const initBooksChart = () => {
  if (!booksChartRef.value) return
  
  chartsLoading.value.books = true
  
  if (booksChart) {
    booksChart.dispose()
  }
  
  booksChart = echarts.init(booksChartRef.value)
  
  const option = {
    animation: true,
    animationDuration: 1500,
    animationEasing: 'cubicOut',
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: chartTypes.value.books === 'line' ? 'line' : 'shadow'
      },
      backgroundColor: 'rgba(255, 255, 255, 0.9)',
      borderColor: '#eee',
      borderWidth: 1,
      textStyle: {
        color: '#333'
      }
    },
    legend: {
      data: ['已售出', '已出租'],
      bottom: 10,
      textStyle: {
        color: '#666'
      },
      selectedMode: 'multiple'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      top: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: chartData.value.books.dates,
      axisLabel: {
        color: '#666'
      },
      axisLine: {
        lineStyle: {
          color: '#ddd'
        }
      }
    },
    yAxis: {
      type: 'value',
      name: '数量',
      axisLabel: {
        color: '#666'
      },
      axisLine: {
        lineStyle: {
          color: '#ddd'
        }
      },
      splitLine: {
        lineStyle: {
          color: '#f0f0f0'
        }
      }
    },
    series: [
      {
        name: '已售出',
        type: chartTypes.value.books,
        data: chartData.value.books.sold,
        smooth: true,
        itemStyle: {
          color: THEME_COLORS.primary
        },
        areaStyle: chartTypes.value.books === 'line' ? {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(64, 158, 255, 0.3)' },
            { offset: 1, color: 'rgba(64, 158, 255, 0.05)' }
          ])
        } : undefined,
        label: {
          show: true,
          position: 'top',
          color: '#666'
        },
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowColor: 'rgba(64, 158, 255, 0.5)'
          }
        }
      },
      {
        name: '已出租',
        type: chartTypes.value.books,
        data: chartData.value.books.rented,
        smooth: true,
        itemStyle: {
          color: THEME_COLORS.success
        },
        areaStyle: chartTypes.value.books === 'line' ? {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(103, 194, 58, 0.3)' },
            { offset: 1, color: 'rgba(103, 194, 58, 0.05)' }
          ])
        } : undefined,
        label: {
          show: true,
          position: 'top',
          color: '#666'
        },
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowColor: 'rgba(103, 194, 58, 0.5)'
          }
        }
      }
    ]
  }
  
  booksChart.setOption(option)
  chartsLoading.value.books = false
}

const initCarbonChart = () => {
  if (!carbonChartRef.value) return
  
  chartsLoading.value.carbon = true
  
  if (carbonChart) {
    carbonChart.dispose()
  }
  
  carbonChart = echarts.init(carbonChartRef.value)
  
  const option = {
    animation: true,
    animationDuration: 1500,
    animationEasing: 'cubicOut',
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: chartTypes.value.carbon === 'line' ? 'line' : 'shadow'
      },
      backgroundColor: 'rgba(255, 255, 255, 0.9)',
      borderColor: '#eee',
      borderWidth: 1,
      textStyle: {
        color: '#333'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '10%',
      top: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: chartData.value.carbon.dates,
      axisLabel: {
        color: '#666'
      },
      axisLine: {
        lineStyle: {
          color: '#ddd'
        }
      }
    },
    yAxis: {
      type: 'value',
      name: '积分',
      axisLabel: {
        color: '#666'
      },
      axisLine: {
        lineStyle: {
          color: '#ddd'
        }
      },
      splitLine: {
        lineStyle: {
          color: '#f0f0f0'
        }
      }
    },
    series: [
      {
        name: '碳积分',
        type: chartTypes.value.carbon,
        data: chartData.value.carbon.values,
        smooth: true,
        itemStyle: {
          color: THEME_COLORS.warning
        },
        areaStyle: chartTypes.value.carbon === 'line' ? {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(230, 162, 60, 0.3)' },
            { offset: 1, color: 'rgba(230, 162, 60, 0.05)' }
          ])
        } : undefined,
        label: {
          show: true,
          position: 'top',
          color: '#666'
        },
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowColor: 'rgba(230, 162, 60, 0.5)'
          }
        }
      }
    ]
  }
  
  carbonChart.setOption(option)
  chartsLoading.value.carbon = false
}

const initCategoryChart = () => {
  if (!categoryChartRef.value) return
  
  chartsLoading.value.category = true
  
  if (categoryChart) {
    categoryChart.dispose()
  }
  
  categoryChart = echarts.init(categoryChartRef.value)
  
  let option
  
  if (chartTypes.value.category === 'pie') {
    option = {
      animation: true,
      animationDuration: 1500,
      animationEasing: 'cubicOut',
      tooltip: {
        trigger: 'item',
        formatter: '{b}: {c} ({d}%)',
        backgroundColor: 'rgba(255, 255, 255, 0.9)',
        borderColor: '#eee',
        borderWidth: 1,
        textStyle: {
          color: '#333'
        }
      },
      legend: {
        orient: 'vertical',
        right: '5%',
        top: 'center',
        textStyle: {
          color: '#666'
        },
        selectedMode: 'multiple'
      },
      series: [
        {
          name: '图书分类',
          type: 'pie',
          radius: ['40%', '70%'],
          center: ['40%', '50%'],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 10,
            borderColor: '#fff',
            borderWidth: 2
          },
          label: {
            show: true,
            formatter: '{b}: {d}%',
            color: '#666'
          },
          emphasis: {
            label: {
              show: true,
              fontSize: 16,
              fontWeight: 'bold'
            },
            itemStyle: {
              shadowBlur: 10,
              shadowColor: 'rgba(0, 0, 0, 0.3)'
            }
          },
          data: chartData.value.category.map((item, index) => ({
            ...item,
            itemStyle: {
              color: THEME_COLORS.gradient[index % THEME_COLORS.gradient.length]
            }
          }))
        }
      ]
    }
  } else {
    option = {
      animation: true,
      animationDuration: 1500,
      animationEasing: 'cubicOut',
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        },
        backgroundColor: 'rgba(255, 255, 255, 0.9)',
        borderColor: '#eee',
        borderWidth: 1,
        textStyle: {
          color: '#333'
        }
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '10%',
        top: '10%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: chartData.value.category.map(item => item.name),
        axisLabel: {
          color: '#666'
        },
        axisLine: {
          lineStyle: {
            color: '#ddd'
          }
        }
      },
      yAxis: {
        type: 'value',
        name: '数量',
        axisLabel: {
          color: '#666'
        },
        axisLine: {
          lineStyle: {
            color: '#ddd'
          }
        },
        splitLine: {
          lineStyle: {
            color: '#f0f0f0'
          }
        }
      },
      series: [
        {
          name: '图书数量',
          type: 'bar',
          data: chartData.value.category.map((item, index) => ({
            value: item.value,
            itemStyle: {
              color: THEME_COLORS.gradient[index % THEME_COLORS.gradient.length]
            }
          })),
          barWidth: '50%',
          label: {
            show: true,
            position: 'top',
            color: '#666'
          },
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowColor: 'rgba(0, 0, 0, 0.3)'
            }
          }
        }
      ]
    }
  }
  
  categoryChart.setOption(option)
  chartsLoading.value.category = false
}

const initOrderChart = () => {
  if (!orderChartRef.value) return
  
  chartsLoading.value.order = true
  
  if (orderChart) {
    orderChart.dispose()
  }
  
  orderChart = echarts.init(orderChartRef.value)
  
  let option
  
  if (chartTypes.value.order === 'pie') {
    option = {
      animation: true,
      animationDuration: 1500,
      animationEasing: 'cubicOut',
      tooltip: {
        trigger: 'item',
        formatter: '{b}: {c} ({d}%)',
        backgroundColor: 'rgba(255, 255, 255, 0.9)',
        borderColor: '#eee',
        borderWidth: 1,
        textStyle: {
          color: '#333'
        }
      },
      legend: {
        orient: 'vertical',
        right: '5%',
        top: 'center',
        textStyle: {
          color: '#666'
        },
        selectedMode: 'multiple'
      },
      series: [
        {
          name: '订单状态',
          type: 'pie',
          radius: ['40%', '70%'],
          center: ['40%', '50%'],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 10,
            borderColor: '#fff',
            borderWidth: 2
          },
          label: {
            show: true,
            formatter: '{b}: {d}%',
            color: '#666'
          },
          emphasis: {
            label: {
              show: true,
              fontSize: 16,
              fontWeight: 'bold'
            },
            itemStyle: {
              shadowBlur: 10,
              shadowColor: 'rgba(0, 0, 0, 0.3)'
            }
          },
          data: chartData.value.order.map((item, index) => ({
            ...item,
            itemStyle: {
              color: [THEME_COLORS.success, THEME_COLORS.warning, THEME_COLORS.primary, THEME_COLORS.info][index]
            }
          }))
        }
      ]
    }
  } else {
    option = {
      animation: true,
      animationDuration: 1500,
      animationEasing: 'cubicOut',
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        },
        backgroundColor: 'rgba(255, 255, 255, 0.9)',
        borderColor: '#eee',
        borderWidth: 1,
        textStyle: {
          color: '#333'
        }
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '10%',
        top: '10%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: chartData.value.order.map(item => item.name),
        axisLabel: {
          color: '#666'
        },
        axisLine: {
          lineStyle: {
            color: '#ddd'
          }
        }
      },
      yAxis: {
        type: 'value',
        name: '数量',
        axisLabel: {
          color: '#666'
        },
        axisLine: {
          lineStyle: {
            color: '#ddd'
          }
        },
        splitLine: {
          lineStyle: {
            color: '#f0f0f0'
          }
        }
      },
      series: [
        {
          name: '订单数量',
          type: 'bar',
          data: chartData.value.order.map((item, index) => ({
            value: item.value,
            itemStyle: {
              color: [THEME_COLORS.success, THEME_COLORS.warning, THEME_COLORS.primary, THEME_COLORS.info][index]
            }
          })),
          barWidth: '50%',
          label: {
            show: true,
            position: 'top',
            color: '#666'
          },
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowColor: 'rgba(0, 0, 0, 0.3)'
            }
          }
        }
      ]
    }
  }
  
  orderChart.setOption(option)
  chartsLoading.value.order = false
}

const disposeCharts = () => {
  booksChart?.dispose()
  carbonChart?.dispose()
  categoryChart?.dispose()
  orderChart?.dispose()
}

const handleExport = (command) => {
  if (command === 'excel') {
    exportToExcel()
  } else if (command === 'image') {
    exportToImage()
  }
}

const exportToExcel = () => {
  const csvContent = [
    ['日期', '图书数量', '已售出', '已出租', '订单数', '碳积分', '趋势(%)'],
    ...tableData.value.map(item => [
      item.date,
      item.books,
      item.sold,
      item.rented,
      item.orders,
      item.carbonPoints,
      item.trend
    ])
  ].map(row => row.join(',')).join('\n')
  
  const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' })
  saveAs(blob, `数据统计_${new Date().toISOString().split('T')[0]}.csv`)
  ElMessage.success('Excel导出成功')
}

const exportToImage = () => {
  // 导出所有图表为图片
  const charts = [
    { chart: booksChart, name: '图书流通趋势' },
    { chart: carbonChart, name: '碳积分增长趋势' },
    { chart: categoryChart, name: '图书分类占比' },
    { chart: orderChart, name: '订单状态分布' }
  ]
  
  charts.forEach(({ chart, name }) => {
    if (chart) {
      const url = chart.getDataURL({
        type: 'png',
        pixelRatio: 2,
        backgroundColor: '#fff'
      })
      const link = document.createElement('a')
      link.download = `${name}_${new Date().toISOString().split('T')[0]}.png`
      link.href = url
      link.click()
    }
  })
  
  ElMessage.success('图片导出成功')
}
</script>

<style scoped>
.data-analysis {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  font-size: 1.8rem;
  font-weight: bold;
  color: #333;
}

.filter-section {
  margin-bottom: 20px;
}

.filter-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 15px;
}

.time-filter {
  display: flex;
  align-items: center;
  gap: 15px;
  flex-wrap: wrap;
}

.loading-container {
  padding: 40px;
}

.error-alert {
  margin-bottom: 20px;
}

.stat-cards {
  margin-bottom: 20px;
}

.stat-card {
  height: 100%;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 15px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  color: white;
  flex-shrink: 0;
}

.stat-info {
  flex: 1;
}

.stat-label {
  font-size: 0.9rem;
  color: #999;
  margin-bottom: 5px;
}

.stat-value {
  font-size: 1.8rem;
  font-weight: bold;
  color: #333;
  margin-bottom: 5px;
}

.stat-trend {
  font-size: 0.8rem;
  display: flex;
  align-items: center;
  gap: 3px;
}

.stat-trend.up {
  color: #67C23A;
}

.stat-trend.down {
  color: #F56C6C;
}

.charts-section {
  margin-bottom: 20px;
}

.chart-card {
  margin-bottom: 20px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-title {
  font-size: 1rem;
  font-weight: bold;
  color: #333;
}

.chart-container {
  height: 350px;
  width: 100%;
}

.data-table-section {
  margin-bottom: 20px;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.table-title {
  font-size: 1rem;
  font-weight: bold;
  color: #333;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .data-analysis {
    padding: 10px;
  }
  
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .page-header h2 {
    font-size: 1.5rem;
  }
  
  .filter-content {
    flex-direction: column;
    align-items: stretch;
  }
  
  .time-filter {
    flex-direction: column;
    align-items: stretch;
  }
  
  .stat-value {
    font-size: 1.5rem;
  }
  
  .chart-container {
    height: 280px;
  }
  
  .table-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
}

@media (max-width: 480px) {
  .stat-icon {
    width: 50px;
    height: 50px;
    font-size: 24px;
  }
  
  .stat-value {
    font-size: 1.3rem;
  }
  
  .chart-container {
    height: 250px;
  }
}
</style>