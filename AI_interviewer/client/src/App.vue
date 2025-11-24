<script setup lang="ts">
</script>

<template>
  <!-- 
    如果不匹配任何子路由，显示Login；
    如果匹配 /home 等，会先渲染 MainLayout，再在 MainLayout 里渲染具体的 Home
  -->
  <router-view></router-view>
</template>

<style>
/* 全局重置样式放在这里 */
html, body, #app {
  height: 100%;
  margin: 0;
  padding: 0;
}
</style>