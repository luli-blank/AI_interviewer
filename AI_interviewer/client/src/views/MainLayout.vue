<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
// 引入 Element Plus 的图标
import { 
  House, 
  VideoPlay, 
  Setting, 
  Document, 
  DataAnalysis, 
  ArrowDown,
  Female
} from '@element-plus/icons-vue'

// 引入本地图片
import logoImg from '../img/log.png' 

const router = useRouter()
const route = useRoute()

// 计算当前激活的菜单项
const activeMenu = computed(() => route.name as string)

// 菜单点击跳转
const handleSelect = (key: string) => {
  if (key) {
    router.push({ name: key })
  }
}
</script>

<template>
  <el-container class="layout-container">
    
    <!-- === 顶部导航栏 === -->
    <el-header class="top-header">
      <div class="header-inner">
        
        <!-- 1. 左侧 Logo Area -->
         <div class="logo-area" @click="router.push({name: 'Home'})">
          <img :src="logoImg" alt="Logo" class="custom-logo" />
          <span class="logo-text hide-on-mobile">AI_interviewer</span>
        </div>

        <!-- 2. 中间导航菜单 -->
        <div class="nav-center">
          <el-menu
            :default-active="activeMenu"
            mode="horizontal"
            class="top-menu"
            :ellipsis="false" 
            @select="handleSelect"
          >
            <!-- 首页 -->
            <el-menu-item index="Home">
              <el-icon><House /></el-icon>
              <span class="menu-text">主页</span>
            </el-menu-item>

            <!-- 岗位推荐 -->
            <el-menu-item index="CreateJob_1" >
              <el-icon><Document /></el-icon>
              <span class="menu-text">岗位推荐</span>
            </el-menu-item>

            <!-- 性格测试 -->
            <el-menu-item index="Character_test" >
              <el-icon><Female /></el-icon>
              <span class="menu-text">性格测试</span>
            </el-menu-item>

            <!-- 面试演练 -->
            <el-menu-item index="Interview_practice">
              <el-icon><VideoPlay /></el-icon>
              <span class="menu-text">面试演练</span>
            </el-menu-item>

            <!-- 面试复盘 -->
            <el-menu-item index="Interview_Review" >
              <el-icon><DataAnalysis /></el-icon>
              <span class="menu-text">面试复盘</span>
            </el-menu-item>

            <!-- 系统设置 -->
            <el-menu-item index="Settings">
              <el-icon><Setting /></el-icon>
              <span class="menu-text">系统设置</span>
            </el-menu-item>
          </el-menu>
        </div>

        <!-- 3. 右侧功能区 -->
        <div class="right-actions">
          <el-dropdown trigger="click">
            <div class="user-avatar-box">
              <el-avatar :size="32" :src="logoImg" />
              <el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="router.push({name:'Profile'})">个人中心</el-dropdown-item>
                <el-dropdown-item divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>

      </div>
    </el-header>

    <!-- === 内容区域 === -->
    <el-main class="layout-main">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </el-main>

  </el-container>
</template>

<style scoped>
.layout-container {
  height: 100vh;
  width: 100vw;
  background-color: #f7f8fa;
  display: flex;
  flex-direction: column;
}

/* === 顶部栏样式 === */
.top-header {
  height: 64px;
  background-color: #ffffff;
  border-bottom: 1px solid #e4e7ed;
  padding: 0; 
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 2px 6px rgba(0,0,0,0.02);
}

.header-inner {
  width: 100%; 
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px; 
  box-sizing: border-box; 
}

/* 左侧 Logo */
.logo-area {
  display: flex;
  align-items: center;
  cursor: pointer;
  flex-shrink: 0; 
  margin-right: 20px;
}

.custom-logo {
  height: 32px;
  width: auto;
  margin-right: 10px;
  border-radius: 4px;
}

.logo-text {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  letter-spacing: 0.5px;
  font-family: 'PingFang SC', sans-serif;
  white-space: nowrap; 
}

/* 中间导航 - 核心布局 */
.nav-center {
  flex: 1;
  display: flex;
  justify-content: center;
  min-width: 0; 
  overflow: hidden; 
}

.top-menu {
  border-bottom: none !important;
  background-color: transparent;
  height: 64px;
  align-items: center;
  width: 100%;
  justify-content: center;
  display: flex;
}

/* 覆盖 Element Menu Item 样式 */
:deep(.el-menu-item) {
  font-size: 14px;
  color: #606266;
  font-weight: 500;
  padding: 0 20px !important; 
  height: 64px;
  line-height: 64px;
  border-bottom: 2px solid transparent !important;
  transition: all 0.3s;
}

:deep(.el-menu-item:hover) {
  color: #000000 !important;
  background-color: transparent !important;
}

:deep(.el-menu-item.is-active) {
  color: #1f2329 !important;
  font-weight: 600;
}

/* 右侧功能区 */
.right-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  flex-shrink: 0; 
  margin-left: 20px;
}

.user-avatar-box {
  display: flex;
  align-items: center;
  cursor: pointer;
  gap: 4px;
}

/* === 内容区域 === */
.layout-main {
  padding: 0;
  
  /* 关键点：设置为 auto，内容不足时不显示，溢出时显示 */
  overflow-y: auto; 
  height: 100%; 
}

/* === 全局滚动条美化 (应用在 .layout-main 上) === */
/* 1. 滚动条整体 */
.layout-main::-webkit-scrollbar {
  width: 8px; /* 竖向滚动条宽度 */
  height: 8px; /* 横向滚动条高度 */
}

/* 2. 滚动条轨道 (透明) */
.layout-main::-webkit-scrollbar-track {
  background: transparent; 
}

/* 3. 滚动条滑块 (默认半透明黑) */
.layout-main::-webkit-scrollbar-thumb {
  background-color: rgba(0, 0, 0, 0.2); 
  border-radius: 4px;
}

/* 4. 鼠标悬停 (墨绿色高亮 - 与 Home.vue 保持一致) */
.layout-main::-webkit-scrollbar-thumb:hover {
  background-color: rgba(58, 133, 107, 0.8); 
}

/* 路由切换动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* === 媒体查询 (响应式适配) === */

@media (max-width: 1000px) {
  :deep(.el-menu-item) {
    padding: 0 10px !important;
  }
}

@media (max-width: 768px) {
  .logo-text {
    display: none;
  }
  
  .custom-logo {
    margin-right: 0;
  }
  
  .header-inner {
    padding: 0 12px;
  }

}
</style>