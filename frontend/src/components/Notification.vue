<template>
  <div class="notification">
    <!-- 通知图标 -->
    <el-dropdown trigger="click" @command="handleCommand">
      <div class="notification-icon">
        <i class="el-icon-bell"></i>
        <span v-if="unreadCount > 0" class="badge">{{ unreadCount }}</span>
      </div>
      <template #dropdown>
        <el-dropdown-menu>
          <el-dropdown-item divided @click="markAllAsRead">
            全部标记为已读
          </el-dropdown-item>
          <el-dropdown-item divided @click="viewAllNotifications">
            查看全部通知
          </el-dropdown-item>
        </el-dropdown-menu>
      </template>
    </el-dropdown>
    
    <!-- 通知列表 -->
    <el-drawer
      v-model="drawerVisible"
      title="通知中心"
      size="30%"
      :with-header="false"
    >
      <div class="notification-drawer">
        <div class="drawer-header">
          <h3>通知中心</h3>
          <el-button type="text" @click="markAllAsRead">全部标记为已读</el-button>
        </div>
        <div class="notification-list">
          <div 
            v-for="notification in notifications" 
            :key="notification.id"
            class="notification-item"
            :class="{ 'unread': !notification.read }"
            @click="markAsRead(notification.id)"
          >
            <div class="notification-content">
              <h4>{{ notification.title }}</h4>
              <p>{{ notification.content }}</p>
              <span class="notification-time">{{ formatTime(notification.created_at) }}</span>
            </div>
            <div class="notification-status">
              <span v-if="!notification.read" class="unread-dot"></span>
            </div>
          </div>
          <div v-if="notifications.length === 0" class="no-notifications">
            <el-empty description="暂无通知" />
          </div>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage, ElEmpty } from 'element-plus'

// 通知抽屉可见性
const drawerVisible = ref(false)

// 通知列表
const notifications = ref([
  {
    id: 1,
    title: '订单状态更新',
    content: '您的订单 #202603310001 已更新为待发货状态',
    read: false,
    created_at: new Date().toISOString()
  },
  {
    id: 2,
    title: '新消息',
    content: '卖家 张三 给您发送了一条新消息',
    read: false,
    created_at: new Date(Date.now() - 3600000).toISOString()
  },
  {
    id: 3,
    title: '交易完成',
    content: '您的订单 #202603310003 已完成交易',
    read: true,
    created_at: new Date(Date.now() - 86400000).toISOString()
  }
])

/**
 * 未读通知数量
 */
const unreadCount = computed(() => {
  return notifications.value.filter(n => !n.read).length
})

/**
 * 处理下拉菜单命令
 * @param {string} command - 命令类型
 */
const handleCommand = (command) => {
  if (command === 'view') {
    drawerVisible.value = true
  }
}

/**
 * 查看全部通知
 */
const viewAllNotifications = () => {
  drawerVisible.value = true
}

/**
 * 标记通知为已读
 * @param {number} notificationId - 通知ID
 */
const markAsRead = (notificationId) => {
  const notification = notifications.value.find(n => n.id === notificationId)
  if (notification) {
    notification.read = true
  }
}

/**
 * 全部标记为已读
 */
const markAllAsRead = () => {
  notifications.value.forEach(notification => {
    notification.read = true
  })
  ElMessage.success('已全部标记为已读')
}

/**
 * 格式化时间
 * @param {string} time - 时间字符串
 * @returns {string} 格式化后的时间
 */
const formatTime = (time) => {
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
.notification {
  position: relative;
}

.notification-icon {
  position: relative;
  cursor: pointer;
  font-size: 20px;
  color: #666;
  transition: color 0.3s ease;
}

.notification-icon:hover {
  color: #409EFF;
}

.badge {
  position: absolute;
  top: -5px;
  right: -5px;
  background-color: #F56C6C;
  color: white;
  border-radius: 50%;
  width: 18px;
  height: 18px;
  font-size: 12px;
  line-height: 18px;
  text-align: center;
  font-weight: bold;
}

.notification-drawer {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.drawer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #e0e0e0;
  margin-bottom: 20px;
}

.drawer-header h3 {
  margin: 0;
  color: #333;
  font-size: 1.2rem;
  font-weight: bold;
}

.notification-list {
  flex: 1;
  overflow-y: auto;
  padding: 0 20px;
}

.notification-item {
  display: flex;
  align-items: flex-start;
  padding: 15px;
  border-bottom: 1px solid #e0e0e0;
  cursor: pointer;
  transition: all 0.3s ease;
}

.notification-item:hover {
  background-color: #f5f7fa;
}

.notification-item.unread {
  background-color: #ecf5ff;
}

.notification-content {
  flex: 1;
}

.notification-content h4 {
  margin: 0 0 10px 0;
  color: #333;
  font-size: 1rem;
  font-weight: bold;
}

.notification-content p {
  margin: 0 0 10px 0;
  color: #666;
  font-size: 0.9rem;
  line-height: 1.4;
}

.notification-time {
  font-size: 0.8rem;
  color: #999;
}

.notification-status {
  margin-left: 10px;
}

.unread-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #409EFF;
  margin-top: 6px;
}

.no-notifications {
  padding: 60px 0;
  text-align: center;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .notification-drawer {
    padding: 0;
  }
  
  .drawer-header {
    padding: 15px;
  }
  
  .notification-list {
    padding: 0 15px;
  }
  
  .notification-item {
    padding: 12px;
  }
}
</style>