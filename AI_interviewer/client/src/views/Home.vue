<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { 
  CircleCheck, 
  User, 
  Trophy, 
  ArrowDown, 
} from '@element-plus/icons-vue'
import homeBackImg from '../img/homeBackground.jpg'

const router = useRouter()

// 当前选中的岗位
const currentRole = ref('后端工程师')

// 模拟开始面试的跳转
const startInterview = () => {
  router.push({ name: 'Going' }) 
}

// 模拟岗位选项
const roleOptions = [
  '后端工程师',
  '前端工程师',
  '产品经理',
  '算法工程师'
]
</script>

<template>
  <div class="home-container"
  :style="{ backgroundImage: `url(${homeBackImg})` }"
  >
    <!-- 内容包装器 -->
    <div class="content-wrapper">
      
      <!-- 1. 顶部切换栏 -->
      <div class="top-toggle-container">
        <div class="toggle-pill active">
          AI面试教练
        </div>
        <div class="toggle-pill inactive">
          AI简历优化
          <span class="new-badge">新</span>
        </div>
      </div>

      <!-- 2. 核心标语区 -->
      <div class="hero-section">
        <div class="hero-badge">
          已帮助10,000+求职者成功拿下理想offer
        </div>

        <h1 class="main-title">
          你的<span class="highlight">专属AI面试教练</span>
        </h1>

        <p class="sub-title">
          面试过程中实时提供<strong>专业建议</strong>，帮助构建<strong>清晰有逻辑</strong>的回答框架，<span class="green-text">面试成功率提升3倍</span>
        </p>

        <div class="role-selector">
          <span class="label">当前岗位：</span>
          <el-dropdown trigger="click" @command="(c: string) => currentRole = c">
            <span class="dropdown-link">
              {{ currentRole }}-
              <el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item v-for="role in roleOptions" :key="role" :command="role">
                  {{ role }}
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>

        <div class="cta-area">
          <button class="start-btn" @click="startInterview">
            开始面试
          </button>
          <p class="cta-subtext">AI面试练习</p>
        </div>
      </div>

      <!-- 3. 底部数据统计卡片 -->
      <div class="stats-card">
        <div class="stat-item">
          <el-icon class="stat-icon" :size="28"><CircleCheck /></el-icon>
          <div class="stat-info">
            <div class="number">320,000+</div>
            <div class="desc">收到的 Offer 数量</div>
          </div>
        </div>
        
        <div class="divider"></div>

        <div class="stat-item">
          <el-icon class="stat-icon" :size="28"><User /></el-icon>
          <div class="stat-info">
            <div class="number">1,600,000+</div>
            <div class="desc">通过的面试次数</div>
          </div>
        </div>

        <div class="divider"></div>

        <div class="stat-item">
          <el-icon class="stat-icon" :size="28"><Trophy /></el-icon>
          <div class="stat-info">
            <div class="number">12,000+</div>
            <div class="desc">用户成功入职的公司数量</div>
          </div>
        </div>
      </div>
    
    </div>
  </div>
</template>

<style scoped>
:root {
  --primary-green: #3a856b;
  --light-green-bg: #e6f4ef;
  --text-main: #333333;
  --text-sub: #666666;
}

.home-container {
  width: 100%;
  
  /* === 修改点 1: 关键！=== */
  /* 改为 min-height，让内容撑开高度 */
  min-height: 100%; 
  /* 移除 height: 100% 和 overflow-y: auto */
  /* 这样滚动条就会由 MainLayout 统一管理，样式自然也就一致了 */
  
  background-repeat: no-repeat;
  background-position: center;
  background-size: cover;
  /* 固定背景图，防止页面滚动时背景图截断 */
  background-attachment: fixed; 
  
  position: relative;
  display: flex;
  justify-content: center;
}

.home-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.85);
  z-index: 1;
}

/* 内容包装层 */
.content-wrapper {
  z-index: 2;
  position: relative;
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px 20px; 
  box-sizing: border-box;
  /* 确保内容少的时候也能居中 */
  min-height: 100%; 
  justify-content: center;
}

/* === 1. 顶部切换栏 === */
.top-toggle-container {
  display: flex;
  background-color: #eee;
  border-radius: 30px;
  padding: 4px;
  margin-bottom: 40px;
  background: rgba(230, 230, 230, 0.6);
  backdrop-filter: blur(4px);
  flex-wrap: wrap; 
  justify-content: center;
}

.toggle-pill {
  padding: 10px 30px;
  border-radius: 24px;
  font-size: 15px;
  cursor: pointer;
  transition: all 0.3s;
  position: relative;
  color: #666;
  white-space: nowrap; 
}

.toggle-pill.active {
  background-color: #3a856b;
  color: white;
  font-weight: 500;
  box-shadow: 0 4px 10px rgba(58, 133, 107, 0.3);
}

.toggle-pill.inactive:hover {
  color: #3a856b;
}

.new-badge {
  position: absolute;
  top: -5px;
  right: -10px;
  background-color: #ff4d4f;
  color: white;
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 10px;
  transform: scale(0.8);
}

/* === 2. 核心标语区 === */
.hero-section {
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  max-width: 800px;
  padding: 0 10px; 
  box-sizing: border-box;
}

.hero-badge {
  border: 1px solid #3a856b;
  color: #3a856b;
  background-color: #f0fdf9;
  padding: 6px 20px;
  border-radius: 20px;
  font-size: 14px;
  margin-bottom: 20px;
  display: inline-block;
  max-width: 100%; 
  white-space: normal;
}

.main-title {
  font-size: 48px;
  color: #333;
  margin: 0 0 20px 0;
  font-weight: bold;
  letter-spacing: 1px;
  line-height: 1.2; 
}

.highlight {
  color: #3a856b;
}

.sub-title {
  font-size: 16px;
  color: #666;
  line-height: 1.6;
  margin-bottom: 30px;
  max-width: 700px;
}

.green-text {
  color: #3a856b;
  font-weight: bold;
}

.role-selector {
  margin-bottom: 30px;
  color: #555;
  font-size: 15px;
  display: flex;
  align-items: center;
  gap: 5px;
  flex-wrap: wrap; 
  justify-content: center;
}

.dropdown-link {
  cursor: pointer;
  color: #3a856b;
  font-weight: 500;
  display: flex;
  align-items: center;
  font-size: 16px;
}

.cta-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.start-btn {
  background-color: #3a856b;
  color: white;
  border: none;
  padding: 12px 60px;
  font-size: 18px;
  border-radius: 6px;
  cursor: pointer;
  transition: transform 0.2s, background-color 0.2s;
  box-shadow: 0 4px 12px rgba(58, 133, 107, 0.3);
}

.start-btn:hover {
  background-color: #2e6b56;
  transform: translateY(-2px);
}

.start-btn:active {
  transform: scale(0.98);
}

.cta-subtext {
  font-size: 13px;
  color: #888;
  margin: 0;
}

/* === 3. 底部数据统计卡片 === */
.stats-card {
  margin-top: 60px;
  background-color: white;
  border-radius: 12px;
  padding: 25px 40px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
  width: 90%; 
  max-width: 1000px; 
  box-sizing: border-box;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 15px;
  text-align: left;
  flex: 1; 
  justify-content: center; 
}

.stat-icon {
  color: #3a856b;
  background-color: #eef7f4;
  padding: 8px;
  border-radius: 50%;
  box-sizing: content-box;
  flex-shrink: 0; 
}

.stat-info .number {
  font-size: 20px;
  font-weight: bold;
  color: #3a856b;
  white-space: nowrap;
}

.stat-info .desc {
  font-size: 12px;
  color: #888;
  margin-top: 2px;
  white-space: nowrap;
}

.divider {
  width: 1px;
  height: 40px;
  background-color: #eee;
  margin: 0 20px;
}

/* === 媒体查询 (响应式适配) === */
@media (max-width: 768px) {
  .main-title {
    font-size: 32px;
  }
  
  .stats-card {
    flex-direction: column;
    padding: 20px;
    gap: 20px;
    width: 95%; 
  }

  .divider {
    display: none;
  }

  .stat-item {
    width: 100%;
    justify-content: flex-start; 
    padding-left: 20px; 
  }

  .stat-info .number {
    font-size: 18px;
  }
}
</style>