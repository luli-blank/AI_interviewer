<script setup lang="ts">
// 这里不需要写逻辑
</script>

<template>
  <div class="app-container">
    <!-- 左侧侧边栏 -->
    <nav class="sidebar">
      <div class="title">我的应用</div>
      <router-link :to="{name:'Home'}" class="nav-item">首页</router-link>
      <router-link :to="{name:'Settings'}" class="nav-item">设置</router-link>
      <router-link :to="{name:'Going'}" class="nav-item">转向</router-link>
    </nav>

    <!-- 右侧内容区：子路由（Home, Settings等）会渲染在这里 -->
    <main class="content-area">
      <router-view></router-view>
    </main>
  </div>
</template>

<!-- 注意：这里之前多余的 <script setup> 已经被删除 -->

<style>
/* 简单的左右布局样式 */
html, body, #app { height: 100%; margin: 0; }

.app-container {
  display: flex; /* 左右布局 */
  height: 100vh; /* 占满屏幕高度 */
}

.sidebar {
  width: 200px;
  background-color: #2c3e50;
  color: white;
  display: flex;
  flex-direction: column;
  padding: 20px;
}

.nav-item {
  color: #b0c4de;
  text-decoration: none;
  padding: 10px;
  margin: 5px 0;
  border-radius: 4px;
}

.nav-item:hover, .router-link-active {
  background-color: #42b983;
  color: white;
}

.content-area {
  flex: 1; /* 占满剩余空间 */
  overflow: auto; /* 内容多了可以滚动 */
}
</style>