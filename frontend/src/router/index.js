import { createRouter, createWebHistory } from 'vue-router'

// 路由配置
const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/book-trade',
    name: 'BookTrade',
    component: () => import('../views/BookTrade.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/book-detail/:id',
    name: 'BookDetail',
    component: () => import('../views/BookDetail.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/publish-book',
    name: 'PublishBook',
    component: () => import('../views/PublishBook.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/carbon-points',
    name: 'CarbonPoints',
    component: () => import('../views/CarbonPoints.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/delivery',
    name: 'Delivery',
    component: () => import('../views/Delivery.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/charity',
    name: 'Charity',
    component: () => import('../views/Charity.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/study-notes',
    name: 'StudyNotes',
    component: () => import('../views/StudyNotes.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/data-analysis',
    name: 'DataAnalysis',
    component: () => import('../views/DataAnalysis.vue'),
    meta: { requiresAuth: true, roles: ['admin', 'manager'] }
  },
  {
    path: '/user-center',
    name: 'UserCenter',
    component: () => import('../views/UserCenter.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/order-management',
    name: 'OrderManagement',
    component: () => import('../views/OrderManagement.vue'),
    meta: { requiresAuth: true }
  },
  // 404页面
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 检查是否需要登录
  if (to.meta.requiresAuth) {
    const token = localStorage.getItem('token')
    if (!token) {
      // 未登录，跳转到登录页
      next({ name: 'Login' })
      return
    }
    
    // 检查权限角色
    if (to.meta.roles) {
      const userRole = localStorage.getItem('userRole')
      if (!userRole || !to.meta.roles.includes(userRole)) {
        // 权限不足，跳转到首页
        next({ name: 'Home' })
        return
      }
    }
  }
  next()
})

export default router