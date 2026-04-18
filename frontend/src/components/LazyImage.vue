<template>
  <img
    v-if="imageLoaded"
    :src="src"
    :alt="alt"
    :class="classes"
    @load="handleLoad"
    @error="handleError"
  />
  <div
    v-else
    :class="[classes, 'lazy-loading']"
    :style="{ width: width, height: height }"
  >
    <el-skeleton :rows="1" animated />
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'

const props = defineProps({
  src: {
    type: String,
    required: true
  },
  alt: {
    type: String,
    default: ''
  },
  width: {
    type: String,
    default: '100%'
  },
  height: {
    type: String,
    default: 'auto'
  },
  class: {
    type: String,
    default: ''
  }
})

const imageLoaded = ref(false)
const classes = ref(props.class)

const handleLoad = () => {
  imageLoaded.value = true
}

const handleError = () => {
  imageLoaded.value = false
}

// 检查图片是否在视口内
const checkInView = () => {
  const image = document.querySelector(`img[src="${props.src}"]`)
  if (!image) return
  
  const rect = image.getBoundingClientRect()
  const isVisible = (
    rect.top <= (window.innerHeight || document.documentElement.clientHeight) &&
    rect.left <= (window.innerWidth || document.documentElement.clientWidth) &&
    rect.bottom >= 0 &&
    rect.right >= 0
  )
  
  if (isVisible) {
    imageLoaded.value = true
  }
}

onMounted(() => {
  // 初始检查
  checkInView()
  // 监听滚动事件
  window.addEventListener('scroll', checkInView, { passive: true })
  // 监听 resize 事件
  window.addEventListener('resize', checkInView, { passive: true })
})

watch(() => props.src, () => {
  imageLoaded.value = false
  checkInView()
})
</script>

<style scoped>
.lazy-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f5f5;
  border-radius: 4px;
}

img {
  transition: opacity 0.3s ease;
}

img[src] {
  opacity: 1;
}
</style>