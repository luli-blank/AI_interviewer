<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { 
  ArrowLeft, 
  ArrowRight,
  DCaret
} from '@element-plus/icons-vue'

// 假设这是你的 Logo 图片路径，如果没有可以先用文字代替
// import logoImg from '@/assets/logo.png' 

const router = useRouter()

// 模拟数据
const historyList = ref([
  {
    id: 1,
    date: '2025-10-23',
    time: '18:27',
    title: '后端工程师 - 模拟面试',
    status: 'completed'
  },
  {
    id: 2,
    date: '2025-10-20',
    time: '14:30',
    title: '产品经理 - 压力面试',
    status: 'completed'
  },
  {
    id: 3,
    date: '2025-10-15',
    time: '09:00',
    title: '前端开发 - 基础技术面',
    status: 'completed'
  }
])

const goBack = () => {
  router.push({ name: 'Home' }) // 或者 router.back()
}

const viewDetail = (id: number) => {
  console.log('查看详情', id)
  // router.push({ name: 'InterviewDetail', params: { id } })
}
</script>

<template>
  <div class="history-page">
    <!-- 2. 主体内容区 -->
    <main class="main-container">
      
      <!-- 顶部状态栏 -->
      <div class="status-bar animate-in">
        <div class="left-info">
          <span class="label">面试时间轴</span>
          <span class="count-badge">{{ historyList.length }}</span>
        </div>
        
        <div class="legend-info">
          <div class="legend-item">
            <span class="dot green"></span>
            <span>建议</span>
          </div>
          <div class="legend-item">
            <span class="dot red"></span>
            <span>弱点</span>
          </div>
        </div>
      </div>

      <!-- 时间轴列表 -->
      <div class="timeline-wrapper">
        <div 
          v-for="(item, index) in historyList" 
          :key="item.id" 
          class="timeline-row animate-in"
          :style="{ animationDelay: `${index * 0.1}s` }"
        >
          
          <!-- 左侧：时间 -->
          <div class="time-col">
            <div class="date-text">{{ item.date }}</div>
            <div class="time-text">{{ item.time }}</div>
          </div>

          <!-- 中间：轴线与节点 -->
          <div class="line-col">
            <div class="node-dot"></div>
            <!-- 最后一项不显示连接线 -->
            <div class="vertical-line" v-if="index !== historyList.length - 1"></div>
          </div>

          <!-- 右侧：卡片 -->
          <div class="card-col">
            <div class="history-card" @click="viewDetail(item.id)">
              <div class="card-title">{{ item.title }}</div>
              <div class="card-action">
                <span>查看详情</span>
                <el-icon><ArrowRight /></el-icon>
              </div>
            </div>
          </div>

        </div>
      </div>

    </main>
  </div>
</template>

<style scoped>
/* === 全局变量 === */
:root {
  --primary-color: #3a856b;
  --bg-color: #f2f8f5; /* 极淡的薄荷绿背景 */
  --text-main: #333;
  --text-light: #999;
}

.history-page {
  min-height: 100vh;
  background-color: #f2f8f5;
  font-family: 'PingFang SC', sans-serif;
  color: #333;
}

/* === 1. 顶部导航栏 === */
.top-nav {
  height: 60px;
  background: #ffffff;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: center;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 2px 8px rgba(0,0,0,0.02);
}

.nav-content {
  width: 100%;
  max-width: 1200px;
  padding: 0 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.brand {
  display: flex;
  align-items: center;
  cursor: pointer;
  font-size: 18px;
}

.logo-icon {
  font-size: 24px;
  margin-right: 8px;
}

.brand-name {
  font-weight: 300;
  color: #333;
}

.divider {
  margin: 0 12px;
  color: #ddd;
}

.page-title {
  font-weight: 600;
  color: #000;
}

.back-btn {
  color: #666;
  font-weight: 400;
}
.back-btn:hover {
  color: #3a856b;
}

/* === 2. 主体容器 === */
.main-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}

/* 顶部状态栏 */
.status-bar {
  background: #fff;
  border-radius: 12px;
  padding: 20px 30px;
  display: flex;
  align-items: center;
  margin-bottom: 40px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.01);
}

.left-info {
  display: flex;
  align-items: center;
  margin-right: 40px;
}

.label {
  font-size: 16px;
  font-weight: 500;
  margin-right: 10px;
}

.count-badge {
  background-color: #e6f2ee;
  color: #3a856b;
  padding: 2px 10px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 600;
}

.legend-info {
  display: flex;
  gap: 20px;
}

.legend-item {
  display: flex;
  align-items: center;
  font-size: 13px;
  color: #666;
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  margin-right: 6px;
}
.dot.green { background-color: #3a856b; }
.dot.red { background-color: #f56c6c; }

/* === 时间轴布局 === */
.timeline-wrapper {
  padding-left: 20px; /* 整体微调 */
}

.timeline-row {
  display: flex;
  min-height: 100px; /* 每一行的最小高度 */
}

/* 左侧时间 */
.time-col {
  width: 100px;
  text-align: right;
  padding-right: 20px;
  padding-top: 20px; /* 与卡片顶部对齐 */
}

.date-text {
  font-size: 14px;
  color: #666;
  font-weight: 500;
  line-height: 1.4;
}

.time-text {
  font-size: 13px;
  color: #999;
}

/* 中间线条 */
.line-col {
  position: relative;
  width: 40px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.node-dot {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background-color: #3a856b;
  margin-top: 24px; /* 调整圆点位置，使其对齐卡片中心或顶部 */
  z-index: 2;
  box-shadow: 0 0 0 4px #e6f2ee; /* 外层光晕 */
}

.vertical-line {
  position: absolute;
  top: 38px; /* 从圆点下方开始 */
  bottom: -24px; /* 连接到下一行 */
  width: 2px;
  background-color: #dcdfe6; /* 浅灰色线条 */
  z-index: 1;
}

/* 右侧卡片 */
.card-col {
  flex: 1;
  padding-bottom: 30px; /* 卡片间距 */
}

.history-card {
  background: #fff;
  border-radius: 8px;
  padding: 24px 30px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid transparent;
  box-shadow: 0 2px 6px rgba(0,0,0,0.02);
}

.history-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(58, 133, 107, 0.1);
  border-color: #e6f2ee;
}

.card-title {
  font-size: 16px;
  font-weight: 500;
  color: #333;
}

.card-action {
  display: flex;
  align-items: center;
  font-size: 14px;
  color: #3a856b;
  font-weight: 500;
  gap: 4px;
  opacity: 0.8;
  transition: opacity 0.2s;
}

.history-card:hover .card-action {
  opacity: 1;
}

/* === 入场动画 === */
.animate-in {
  opacity: 0;
  animation: fadeSlideUp 0.6s ease forwards;
}

@keyframes fadeSlideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 响应式适配 */
@media (max-width: 768px) {
  .timeline-row {
    flex-direction: column;
    position: relative;
    padding-left: 20px;
    margin-bottom: 20px;
  }
  
  .line-col {
    position: absolute;
    left: 0;
    top: 0;
    height: 100%;
  }
  
  .node-dot {
    margin-top: 5px;
  }
  
  .vertical-line {
    top: 15px;
    bottom: 0;
  }

  .time-col {
    width: auto;
    text-align: left;
    padding-left: 30px;
    margin-bottom: 8px;
    padding-top: 0;
    display: flex;
    gap: 10px;
  }

  .card-col {
    padding-left: 30px;
  }
}
</style>