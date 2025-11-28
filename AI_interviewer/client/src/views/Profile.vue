<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { 
  ArrowLeft, 
  User, 
  Setting, 
  Help, 
  InfoFilled, 
  Iphone, 
  Message, 
  Location,
  OfficeBuilding,
  Edit
} from '@element-plus/icons-vue'
import localAvatar from "../img/log.png"

const router = useRouter()

// 模拟用户信息数据
const userInfo = reactive({
  username: 'Admin User',
  avatar: localAvatar,
  phone: '183-5501-2816',
  email: 'frontend@example.com',
  department: '产品研发部 / 前端组',
  location: '北京市朝阳区',
  role: '高级开发工程师'
})

// 当前选中的菜单
const activeMenu = ref('1')

const goBack = () => {
    router.go(-1) 
}

const handleLogout = () => {
  // 模拟退出逻辑
  console.log('User logged out')
}
</script>

<template>
  <el-container class="layout-container">
    <!-- 左侧导航栏 -->
    <el-aside width="240px" class="custom-aside">
      <div class="aside-header">
        <div class="logo-text">个人中心</div>
      </div>
      
      <el-menu
        :default-active="activeMenu"
        class="custom-menu"
      >
        <el-menu-item index="1">
          <el-icon><User /></el-icon>
          <span>账号信息</span>
        </el-menu-item>
        <el-menu-item index="2">
          <el-icon><Setting /></el-icon>
          <span>系统设置</span>
        </el-menu-item>
        <el-menu-item index="3">
          <el-icon><Help /></el-icon>
          <span>帮助中心</span>
        </el-menu-item>
        <el-menu-item index="4">
          <el-icon><InfoFilled /></el-icon>
          <span>关于我们</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <!-- 右侧主体内容 -->
    <el-container>
      <!-- 顶部返回栏 -->
      <el-header class="custom-header">
        <el-page-header @back="goBack" title="返回">
          <template #content>
            <span class="header-title"> 账号详情 </span>
          </template>
        </el-page-header>
      </el-header>

      <el-main class="main-content">
        <div class="content-wrapper">
          <!-- 用户概览卡片 -->
          <el-card class="profile-card" shadow="never">
            <div class="profile-header">
              <el-avatar :size="80" :src="userInfo.avatar" class="user-avatar" />
              <div class="profile-meta">
                <h2 class="user-name">{{ userInfo.username }}</h2>
                <el-tag type="success" effect="plain" round size="small">{{ userInfo.role }}</el-tag>
              </div>
              <el-button type="primary" :icon="Edit" plain round class="edit-btn">编辑资料</el-button>
            </div>

            <el-divider border-style="dashed" />

            <!-- 详细信息列表 -->
            <el-descriptions
              class="custom-descriptions"
              :column="1"
              size="large"
              border
            >
              <el-descriptions-item>
                <template #label>
                  <div class="cell-item">
                    <el-icon><Iphone /></el-icon>
                    手机号码
                  </div>
                </template>
                {{ userInfo.phone }}
              </el-descriptions-item>

              <el-descriptions-item>
                <template #label>
                  <div class="cell-item">
                    <el-icon><Message /></el-icon>
                    电子邮箱
                  </div>
                </template>
                {{ userInfo.email }}
              </el-descriptions-item>

              <el-descriptions-item>
                <template #label>
                  <div class="cell-item">
                    <el-icon><OfficeBuilding /></el-icon>
                    所属部门
                  </div>
                </template>
                {{ userInfo.department }}
              </el-descriptions-item>

              <el-descriptions-item>
                <template #label>
                  <div class="cell-item">
                    <el-icon><Location /></el-icon>
                    办公地点
                  </div>
                </template>
                {{ userInfo.location }}
              </el-descriptions-item>
            </el-descriptions>

            <!-- 退出按钮区域 -->
            <div class="action-area">
              <el-button type="danger" plain class="logout-btn" @click="handleLogout">
                退出登录
              </el-button>
            </div>
          </el-card>
        </div>
      </el-main>
    </el-container>
  </el-container>
</template>

<style scoped>
/* 布局容器 */
.layout-container {
  height: 100vh;
  background-color: #f7f9fc; /* 统一的灰蓝背景 */
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

/* 左侧侧边栏 */
.custom-aside {
  background: #ffffff;
  border-right: 1px solid #e4e7ed;
  display: flex;
  flex-direction: column;
}

.aside-header {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid #f2f6fc;
}

.logo-text {
  font-size: 18px;
  font-weight: 700;
  color: #303133;
}

/* 菜单样式定制 - 保持青绿色风格 */
.custom-menu {
  border-right: none;
  padding: 10px;
}

:deep(.el-menu-item) {
  border-radius: 8px;
  margin-bottom: 4px;
  color: #606266;
}

:deep(.el-menu-item:hover) {
  background-color: #f0fdf9;
}

:deep(.el-menu-item.is-active) {
  background-color: #eaf7f4;
  color: #4b9e88; /* 青绿色 */
  font-weight: 600;
}

/* 顶部 Header */
.custom-header {
  background: #ffffff;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  padding: 0 24px;
  height: 60px;
}

.header-title {
  font-weight: 600;
  color: #303133;
}

/* 主内容区 */
.main-content {
  padding: 30px;
  display: flex;
  justify-content: center;
}

.content-wrapper {
  width: 100%;
  max-width: 800px;
}

/* 资料卡片 */
.profile-card {
  border-radius: 16px;
  border: 1px solid #ebeef5;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03); /* 柔和阴影 */
  overflow: visible; /* 防止阴影被切 */
}

.profile-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 10px 0 20px;
  position: relative;
}

.user-avatar {
  border: 4px solid #fff;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.profile-meta {
  text-align: center;
  margin-top: 15px;
}

.user-name {
  margin: 0 0 8px 0;
  font-size: 22px;
  font-weight: 600;
  color: #303133;
}

.edit-btn {
  position: absolute;
  top: 0;
  right: 0;
  --el-button-text-color: #4b9e88;
  --el-button-border-color: #bcebdc;
  --el-button-hover-bg-color: #eaf7f4;
}

/* 描述列表定制 */
.custom-descriptions {
  margin-top: 20px;
}

:deep(.el-descriptions__cell) {
  padding: 16px 20px !important;
}

:deep(.el-descriptions__label) {
  width: 140px;
  color: #909399;
  background-color: #fafafa; /* 标签背景微灰 */
}

:deep(.el-descriptions__content) {
  color: #303133;
  font-weight: 500;
}

.cell-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 底部按钮 */
.action-area {
  margin-top: 40px;
  display: flex;
  justify-content: center;
}

.logout-btn {
  width: 200px;
  height: 40px;
  border-radius: 8px;
  font-weight: 500;
}
</style>