<script setup lang="ts">
import { useRouter } from 'vue-router'
import { 
  DocumentChecked, 
  ChatDotRound, 
  Right, 
  Timer,
  DataLine
} from '@element-plus/icons-vue'
import { ro } from 'element-plus/es/locales.mjs'

const router = useRouter()

const handleStartForm = () => {
  router.push('/CHaracter_test_write')
}

const handleStartChat = () => {
  router.push('/Interview_character')
}
</script>

<template>
  <div class="page-container">
    
    <!-- 性能优化后的动态背景 -->
    <div class="bg-shape shape-green"></div>
    <div class="bg-shape shape-orange"></div>

    <div class="content-wrapper">
      
      <!-- 1. 标题区 (最先出现) -->
      <div class="header-section animate-in">
        <h2 class="main-title">性格潜能测评</h2>
        <p class="sub-title">请选择一种你喜欢的测试方式，探索你的职场基因</p>
      </div>

      <!-- 双卡片入口 -->
      <div class="cards-container">
        
        <!-- 2. 左侧卡片 (延迟 0.1s 出现) -->
        <div 
          class="glass-card form-theme animate-in" 
          style="animation-delay: 0.1s"
        >
          <div class="card-inner">
            <div class="icon-ring">
              <el-icon><DocumentChecked /></el-icon>
            </div>
            <h3 class="card-title">标准量表测试</h3>
            <p class="card-desc">
              基于 MBTI 与大五人格理论的标准化问卷。<br>
              适合喜欢快速、精准、结构化作答的用户。
            </p>
            
            <div class="tags-group">
              <el-tag type="success" effect="plain" round size="small"><el-icon><Timer /></el-icon> 约 3 分钟</el-tag>
              <el-tag type="success" effect="plain" round size="small"><el-icon><DataLine /></el-icon> 精准分析</el-tag>
            </div>

            <el-button 
              type="primary" 
              class="action-btn" 
              round 
              @click="handleStartForm"
            >
              开始填表 <el-icon class="el-icon--right"><Right /></el-icon>
            </el-button>
          </div>
        </div>

        <!-- 3. 右侧卡片 (延迟 0.1s 出现) -->
        <div 
          class="glass-card chat-theme animate-in" 
          style="animation-delay: 0.2s"
        >
          <div class="card-inner">
            <div class="icon-ring">
              <el-icon><ChatDotRound /></el-icon>
            </div>
            <h3 class="card-title">AI 深度对话</h3>
            <p class="card-desc">
              由 AI 面试官引导的沉浸式聊天测试。<br>
              在轻松自然的对话中发掘你的潜在特质。
            </p>

            <div class="tags-group">
              <el-tag type="warning" effect="plain" round size="small"><el-icon><Timer /></el-icon> 约 5 分钟</el-tag>
              <el-tag type="warning" effect="plain" round size="small"><el-icon><DataLine /></el-icon> 深度挖掘</el-tag>
            </div>

            <el-button 
              type="primary" 
              class="action-btn chat-btn" 
              round 
              @click="handleStartChat"
            >
              进入对话 <el-icon class="el-icon--right"><Right /></el-icon>
            </el-button>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<style scoped>
/* === 基础布局 === */
.page-container {
  position: relative;
  width: 100%;
  min-height: 100%; 
  display: flex;
  justify-content: center;
  align-items: center; 
  background: linear-gradient(135deg, #f5fcf9 0%, #ffffff 100%);
  overflow: hidden; 
}

/* === 背景球 (高性能版) === */
.bg-shape {
  position: absolute;
  border-radius: 50%;
  z-index: 0;
  opacity: 0.6;
  will-change: transform; 
  animation: floatAnimation 10s infinite ease-in-out alternate;
}

.shape-green {
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, rgba(58,133,107,0.8) 0%, rgba(58,133,107,0) 70%);
  top: -150px;
  left: -150px;
}

.shape-orange {
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, rgba(243,209,158,0.8) 0%, rgba(243,209,158,0) 70%);
  bottom: -100px;
  right: -100px;
  animation-delay: -5s;
}

@keyframes floatAnimation {
  0% { transform: translate3d(0, 0, 0) scale(1); } 
  100% { transform: translate3d(30px, 50px, 0) scale(1.1); }
}

/* === 内容区 === */
.content-wrapper {
  z-index: 1;
  text-align: center;
  width: 100%;
  max-width: 1200px;
  padding: 0 20px;
  margin-top: -100px; /* 调整垂直位置 */
}

/* === 核心动画类 (移植自面试历史记录) === */
.animate-in {
  opacity: 0; /* 初始隐藏 */
  animation: fadeSlideUp 0.8s cubic-bezier(0.22, 1, 0.36, 1) forwards;
}

@keyframes fadeSlideUp {
  from {
    opacity: 0;
    transform: translateY(40px); /* 从下方 40px 处升起 */
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.header-section { margin-bottom: 60px; }
.main-title { font-size: 36px; font-weight: 700; color: #2c3e50; margin-bottom: 16px; letter-spacing: 2px; }
.sub-title { font-size: 16px; color: #7f8c8d; font-weight: 400; letter-spacing: 0.5px; }

.cards-container { display: flex; justify-content: center; gap: 40px; flex-wrap: wrap; }

/* === 玻璃卡片 === */
.glass-card {
  flex: 1;
  min-width: 300px;
  max-width: 420px;
  background: rgba(255, 255, 255, 0.65);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.8);
  border-radius: 24px;
  box-shadow: 0 8px 32px rgba(31, 38, 135, 0.05);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  will-change: transform;
  overflow: hidden;
  cursor: default;
}

.glass-card:hover {
  transform: translateY(-10px); /* 悬浮时的位移 */
  box-shadow: 0 15px 40px rgba(58, 133, 107, 0.15);
  background: rgba(255, 255, 255, 0.85);
  border-color: #fff;
}

.card-inner { padding: 50px 30px; display: flex; flex-direction: column; align-items: center; height: 100%; }

.icon-ring {
  width: 80px; height: 80px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 32px; margin-bottom: 24px;
  transition: transform 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}
.glass-card:hover .icon-ring { transform: scale(1.1) rotate(5deg); }

.card-title { font-size: 22px; font-weight: 600; color: #2c3e50; margin-bottom: 12px; }
.card-desc { font-size: 14px; color: #606266; line-height: 1.6; margin-bottom: 30px; min-height: 44px; }
.tags-group { display: flex; gap: 12px; margin-bottom: 40px; }

.action-btn {
  width: 180px; height: 44px; font-size: 15px; font-weight: 500; letter-spacing: 1px;
  box-shadow: 0 4px 14px rgba(58, 133, 107, 0.2);
  transition: transform 0.3s, box-shadow 0.3s, background-color 0.3s;
}
.action-btn:hover { transform: scale(1.03); box-shadow: 0 6px 20px rgba(58, 133, 107, 0.3); }

/* 主题色配置 */
.form-theme .icon-ring { background: linear-gradient(135deg, #e0f2ec 0%, #cbf0e3 100%); color: #3a856b; }
.form-theme .action-btn { background-color: #3a856b; border-color: #3a856b; }

.chat-theme .icon-ring { background: linear-gradient(135deg, #fff7e6 0%, #ffe8cc 100%); color: #e6a23c; }
.chat-theme .action-btn { background-color: #e6a23c; border-color: #e6a23c; box-shadow: 0 4px 14px rgba(230, 162, 60, 0.2); }
.chat-theme .action-btn:hover { background-color: #cf9236; border-color: #cf9236; box-shadow: 0 6px 20px rgba(230, 162, 60, 0.3); }

@media (max-width: 768px) {
  .page-container { height: auto; padding: 60px 20px; }
  .cards-container { flex-direction: column; align-items: center; }
  .glass-card { width: 100%; max-width: 100%; }
}
</style>