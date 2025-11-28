<script setup>
import { ref, computed } from "vue";
import { useRouter } from 'vue-router'
import { User, Suitcase, ArrowRight } from '@element-plus/icons-vue' // 假设已安装图标库，如未安装可移除icon属性
import avatar1 from '../img/log.png'

const router = useRouter()

// 模拟数据
const jobs = ref([
  {
    id: 1,
    title: "前端开发工程师",
    desc: "负责前端页面开发，熟悉 Vue、TypeScript。",
    interviewers: [
      { name: "雷雷", title: "高级算法工程师", avatar: avatar1 },
      { name: "韩梅梅", title: "前端技术专家", avatar: avatar1}
    ]
  },
  {
    id: 2,
    title: "后端开发工程师",
    desc: "负责后端接口开发，熟悉 FastAPI、Node.js。",
    interviewers: [
      { name: "张伟", title: "资深后端工程师", avatar: avatar1 }
    ]
  }
]);

// 默认选中 'all'
const selectedJobId = ref("all");

const currentJob = computed(() => {
  if (selectedJobId.value === "all") {
    return {
      title: "全部岗位",
      desc: "请选择下方的面试官开始模拟面试",
      interviewers: jobs.value.flatMap(j => j.interviewers)
    }
  }
  // 确保类型匹配（el-menu index 默认为 string）
  return jobs.value.find(j => String(j.id) === selectedJobId.value)
})

const handleMenuSelect = (index) => {
  selectedJobId.value = index;
}

const goToInterview = (interviewer) => {
  router.push({
    name: 'Interview',
    query: { 
      name: interviewer.name, 
      title: interviewer.title 
    }
  })
}
</script>

<template>
  <el-container class="main-layout">
    <!-- 左侧侧边栏 -->
    <el-aside width="280px" class="custom-aside">
      <div class="logo-area">
        <h2 class="app-title">AI Interviewer</h2>
        <p class="app-subtitle">选择您的目标岗位</p>
      </div>
      
      <el-menu
        :default-active="selectedJobId"
        class="custom-menu"
        @select="handleMenuSelect"
      >
        <el-menu-item index="all">
          <el-icon><Suitcase /></el-icon>
          <span>全部岗位</span>
        </el-menu-item>
        
        <el-menu-item 
          v-for="job in jobs" 
          :key="job.id" 
          :index="String(job.id)"
        >
          <el-icon><User /></el-icon>
          <span>{{ job.title }}</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <!-- 右侧主内容 -->
    <el-main class="content-area">
      <!-- 顶部面包屑/标题区 -->
      <div class="header-section">
        <h1 class="page-title">准备面试什么岗位呢？</h1>
        <p class="page-desc">了解您的求职岗位，提高 AI 回答的针对性</p>
      </div>

      <!-- 核心内容卡片 -->
      <el-card class="detail-card" shadow="never">
        <template #header>
          <div class="card-header">
            <div>
              <span class="job-title-large">{{ currentJob?.title }}</span>
              <p class="job-desc-text">{{ currentJob?.desc }}</p>
            </div>
            <el-tag v-if="selectedJobId !== 'all'" type="success" effect="light" round>
              当前选择
            </el-tag>
          </div>
        </template>

        <div class="interviewers-section">
          <div class="section-label">推荐面试官</div>
          
          <el-row :gutter="20">
            <el-col 
              v-for="p in currentJob?.interviewers" 
              :key="p.name" 
              :xs="24" :sm="12" :md="8" :lg="6"
            >
              <div class="interviewer-card-wrapper" @click="goToInterview(p)">
                <el-card shadow="hover" class="interviewer-card-item">
                  <div class="card-content">
                    <el-avatar :size="64" :src="p.avatar" class="custom-avatar" />
                    <div class="text-info">
                      <div class="p-name">{{ p.name }}</div>
                      <div class="p-title">{{ p.title }}</div>
                    </div>
                    <div class="action-icon">
                      <el-icon><ArrowRight /></el-icon>
                    </div>
                  </div>
                </el-card>
              </div>
            </el-col>
          </el-row>
          
          <el-empty 
            v-if="!currentJob?.interviewers?.length" 
            description="暂无面试官信息" 
          />
        </div>
      </el-card>
    </el-main>
  </el-container>
</template>

<style scoped>
/* 全局布局背景 */
.main-layout {
  height: 100vh;
  background-color: #f7f9fc; /* 极淡的灰蓝色背景 */
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

/* 左侧侧边栏样式 */
.custom-aside {
  background-color: #ffffff;
  border-right: 1px solid #ebEEF5;
  display: flex;
  flex-direction: column;
}

.logo-area {
  padding: 30px 24px;
}

.app-title {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  color: #303133;
}

.app-subtitle {
  margin: 8px 0 0 0;
  font-size: 13px;
  color: #909399;
}

/* 覆盖 Element Menu 样式以匹配图片风格 */
.custom-menu {
  border-right: none;
  padding: 0 12px;
}

:deep(.el-menu-item) {
  border-radius: 8px;
  margin-bottom: 8px;
  height: 50px;
  color: #606266;
}

:deep(.el-menu-item:hover) {
  background-color: #f0fdf9; /* 极淡的绿色 hover */
  color: #303133;
}

/* 选中态：仿照图片的青绿色 */
:deep(.el-menu-item.is-active) {
  background-color: #eaf7f4; 
  color: #4b9e88; /* 图片中的青绿色文字 */
  font-weight: 600;
}

/* 右侧内容区 */
.content-area {
  padding: 40px;
  display: flex;
  flex-direction: column;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

.header-section {
  text-align: center;
  margin-bottom: 30px;
}

.page-title {
  font-size: 28px;
  color: #303133;
  font-weight: 700;
  margin-bottom: 10px;
}

.page-desc {
  font-size: 14px;
  color: #909399;
}

/* 核心大卡片 */
.detail-card {
  border-radius: 16px;
  border: 1px solid #e4e7ed;
  /* 柔和的阴影 */
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04); 
}

:deep(.el-card__header) {
  padding: 24px 30px;
  border-bottom: 1px solid #f2f6fc;
}

:deep(.el-card__body) {
  padding: 30px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.job-title-large {
  font-size: 22px;
  font-weight: 600;
  color: #303133;
  display: block;
  margin-bottom: 8px;
}

.job-desc-text {
  font-size: 14px;
  color: #606266;
  margin: 0;
}

/* 面试官区域 */
.section-label {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 20px;
  padding-left: 10px;
  border-left: 4px solid #4b9e88; /* 青绿色装饰条 */
  line-height: 1;
}

.interviewer-card-wrapper {
  cursor: pointer;
  margin-bottom: 20px;
  transition: transform 0.3s ease;
}

.interviewer-card-wrapper:hover {
  transform: translateY(-5px);
}

.interviewer-card-item {
  border-radius: 12px;
  border: 1px solid #ebeef5;
  background: #fdfdfd;
}

.card-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 10px 0;
  position: relative;
}

.custom-avatar {
  border: 2px solid #fff;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  margin-bottom: 16px;
}

.text-info .p-name {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.text-info .p-title {
  font-size: 12px;
  color: #909399;
  background-color: #f4f4f5;
  padding: 2px 8px;
  border-radius: 10px;
}

.action-icon {
  margin-top: 15px;
  opacity: 0;
  color: #4b9e88;
  transition: opacity 0.3s;
}

.interviewer-card-wrapper:hover .action-icon {
  opacity: 1;
}
</style>