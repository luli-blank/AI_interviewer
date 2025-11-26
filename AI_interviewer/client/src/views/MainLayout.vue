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
  ArrowDown 
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
      <!-- 去掉了 max-width 限制，使其铺满全屏 -->
      <div class="header-inner">
        
        <!-- 1. 左侧 Logo Area -->
         <div class="logo-area" @click="router.push({name: 'Home'})">
          <img :src="logoImg" alt="Logo" class="custom-logo" />
          <!-- 增加 hide-on-mobile 类，小屏幕时隐藏文字 -->
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

            <!-- 新建岗位 -->
            <el-menu-item index="Home_Create" disabled>
              <el-icon><Document /></el-icon>
              <span class="menu-text">新建岗位</span>
            </el-menu-item>

            <!-- 面试演练 -->
            <el-menu-item index="Going">
              <el-icon><VideoPlay /></el-icon>
              <span class="menu-text">面试演练</span>
            </el-menu-item>

            <!-- 面试复盘 -->
            <el-menu-item index="Dashboard" disabled>
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
          <!-- 用户头像下拉 -->
          <el-dropdown trigger="click">
            <div class="user-avatar-box">
              <el-avatar :size="32" src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png" />
              <el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item>个人中心</el-dropdown-item>
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
  /* 修改点 1: 移除左右 padding，交给内部元素控制，防止宽度溢出 */
  padding: 0; 
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 2px 6px rgba(0,0,0,0.02);
}

.header-inner {
  /* 修改点 2: 移除 max-width: 1400px，改为 width: 100% */
  width: 100%; 
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  /* 增加左右内边距，确保内容不贴边 */
  padding: 0 24px; 
  box-sizing: border-box; /* 确保 padding 不会撑大 width */
}

/* 左侧 Logo */
.logo-area {
  display: flex;
  align-items: center;
  cursor: pointer;
  /* 修改点 3: 移除 min-width，防止小屏挤压 */
  flex-shrink: 0; /* 防止 Logo 被压缩 */
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
  white-space: nowrap; /* 防止文字换行 */
}

/* 中间导航 - 核心布局 */
.nav-center {
  flex: 1;
  display: flex;
  justify-content: center;
  /* 允许导航区域在空间不足时压缩 */
  min-width: 0; 
  overflow: hidden; /* 防止溢出 */
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
  padding: 0 20px !important; /* 默认间距 */
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
  flex-shrink: 0; /* 防止被压缩 */
  margin-left: 20px;
}

.user-avatar-box {
  display: flex;
  align-items: center;
  cursor: pointer;
  gap: 4px;
}

/* === 内容区 === */
.layout-main {
  padding: 0;
  overflow-y: auto;
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

/* === 修改点 4: 媒体查询 (响应式适配) === */

/* 当屏幕宽度小于 1000px 时 */
@media (max-width: 1000px) {
  /* 减小菜单项的左右间距 */
  :deep(.el-menu-item) {
    padding: 0 10px !important;
  }
}

/* 当屏幕宽度小于 768px (平板/小窗口) 时 */
@media (max-width: 768px) {
  /* 隐藏 Logo 文字，只保留图片 */
  .logo-text {
    display: none;
  }
  
  /* 进一步减小 Logo 图片大小 */
  .custom-logo {
    margin-right: 0;
  }

  /* 隐藏菜单的文字，只保留图标 (可选，如果你想更极致) */
  /* 
  .menu-text {
    display: none;
  } 
  */
  
  /* 减小 header 左右 padding */
  .header-inner {
    padding: 0 12px;
  }
}
</style>