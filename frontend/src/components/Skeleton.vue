<template>
  <div class="skeleton">
    <div v-if="type === 'card'" class="skeleton-card">
      <div class="skeleton-image"></div>
      <div class="skeleton-content">
        <div class="skeleton-title"></div>
        <div class="skeleton-text"></div>
        <div class="skeleton-text"></div>
      </div>
    </div>
    <div v-else-if="type === 'list'" class="skeleton-list">
      <div v-for="i in count" :key="i" class="skeleton-list-item">
        <div class="skeleton-avatar"></div>
        <div class="skeleton-list-content">
          <div class="skeleton-list-title"></div>
          <div class="skeleton-list-text"></div>
        </div>
      </div>
    </div>
    <div v-else-if="type === 'detail'" class="skeleton-detail">
      <div class="skeleton-detail-header"></div>
      <div class="skeleton-detail-content">
        <div class="skeleton-detail-title"></div>
        <div class="skeleton-detail-text"></div>
        <div class="skeleton-detail-text"></div>
        <div class="skeleton-detail-text"></div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Skeleton',
  props: {
    type: {
      type: String,
      default: 'card',
      validator: (value) => ['card', 'list', 'detail'].includes(value)
    },
    count: {
      type: Number,
      default: 3
    }
  }
}
</script>

<style scoped>
.skeleton {
  width: 100%;
}

/* 卡片骨架屏 */
.skeleton-card {
  display: flex;
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

.skeleton-image {
  width: 120px;
  height: 160px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
  border-radius: 4px;
  margin-right: 20px;
}

.skeleton-content {
  flex: 1;
}

.skeleton-title {
  width: 60%;
  height: 24px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
  border-radius: 4px;
  margin-bottom: 12px;
}

.skeleton-text {
  width: 100%;
  height: 16px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
  border-radius: 4px;
  margin-bottom: 8px;
}

/* 列表骨架屏 */
.skeleton-list {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.skeleton-list-item {
  display: flex;
  padding: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.skeleton-list-item:last-child {
  border-bottom: none;
}

.skeleton-avatar {
  width: 48px;
  height: 48px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
  border-radius: 50%;
  margin-right: 16px;
}

.skeleton-list-content {
  flex: 1;
}

.skeleton-list-title {
  width: 80%;
  height: 20px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
  border-radius: 4px;
  margin-bottom: 8px;
}

.skeleton-list-text {
  width: 60%;
  height: 16px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
  border-radius: 4px;
}

/* 详情页骨架屏 */
.skeleton-detail {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.skeleton-detail-header {
  height: 200px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
}

.skeleton-detail-content {
  padding: 20px;
}

.skeleton-detail-title {
  width: 80%;
  height: 32px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
  border-radius: 4px;
  margin-bottom: 16px;
}

.skeleton-detail-text {
  width: 100%;
  height: 18px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
  border-radius: 4px;
  margin-bottom: 12px;
}

/* 加载动画 */
@keyframes loading {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}
</style>