<template>
  <div id="app">
    <!-- 全局导航栏 -->
    <Navbar />
    <!-- 路由视图（使用keep-alive缓存高频页面） -->
    <keep-alive :include="['Home', 'BookTrade', 'UserCenter', 'OrderManagement', 'DataAnalysis']">
      <router-view />
    </keep-alive>
  </div>
</template>

<script setup>
import Navbar from './components/Navbar.vue'
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'PingFang SC', 'Helvetica Neue', Arial, sans-serif;
  color: #333;
  background-color: #f5f5f5;
}

#app {
  min-height: 100vh;
}
</style>