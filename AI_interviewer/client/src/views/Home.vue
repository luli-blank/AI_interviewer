<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
// 引入 Element Plus 图标
import { 
  CircleCheck, 
  User, 
  Trophy, 
  ArrowDown, 
  Microphone 
} from '@element-plus/icons-vue'
import homeBackImg from '../img/homeBackground.jpg'
const router = useRouter()

// 当前选中的岗位
const currentRole = ref('后端工程师')

// 模拟开始面试的跳转
const startInterview = () => {
  router.push({ name: 'Going' }) // 假设跳转到“面试进行中”页面
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
      <!-- 胶囊标语 -->
      <div class="hero-badge">
        已帮助10,000+求职者成功拿下理想offer
      </div>

      <!-- 主标题 -->
      <h1 class="main-title">
        你的<span class="highlight">专属AI面试教练</span>
      </h1>

      <!-- 副标题 -->
      <p class="sub-title">
        面试过程中实时提供<strong>专业建议</strong>，帮助构建<strong>清晰有逻辑</strong>的回答框架，<span class="green-text">面试成功率提升3倍</span>
      </p>

      <!-- 岗位选择 -->
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

      <!-- 开始面试按钮 -->
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
</template>

<style scoped>
/* 定义颜色变量，方便统一修改 */
:root {
  --primary-green: #3a856b; /* 图片中的深墨绿色 */
  --light-green-bg: #e6f4ef;
  --text-main: #333333;
  --text-sub: #666666;
}

.home-container {
  width: 100%;
  height: 100%; /* 继承 MainLayout 的内容区高度 */
  /* 设置背景图：你可以换成 assets 里的本地图片 */
  background-repeat: no-repeat;
  background-position: center;
  background-size: cover;
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

/* 增加一层白色蒙版，让背景淡一点，凸显文字 */
.home-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.85); /* 85% 透明度的白 */
  z-index: 1;
}

/* 所有的内容都必须在蒙版之上 */
.top-toggle-container, .hero-section, .stats-card {
  z-index: 2;
  position: relative;
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
}

.toggle-pill {
  padding: 10px 30px;
  border-radius: 24px;
  font-size: 15px;
  cursor: pointer;
  transition: all 0.3s;
  position: relative;
  color: #666;
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
  max-width: 800px;
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
}

.main-title {
  font-size: 48px;
  color: #333;
  margin: 0 0 20px 0;
  font-weight: bold;
  letter-spacing: 1px;
}

.highlight {
  color: #3a856b; /* 墨绿色高亮 */
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

/* 岗位选择 */
.role-selector {
  margin-bottom: 30px;
  color: #555;
  font-size: 15px;
  display: flex;
  align-items: center;
  gap: 5px;
}

.dropdown-link {
  cursor: pointer;
  color: #3a856b;
  font-weight: 500;
  display: flex;
  align-items: center;
  font-size: 16px;
}

/* CTA 按钮区域 */
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
  margin-top: 80px; /* 距离上方内容的间距 */
  background-color: white;
  border-radius: 12px;
  padding: 25px 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
  min-width: 800px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 15px;
  text-align: left;
}

.stat-icon {
  color: #3a856b;
  background-color: #eef7f4; /* 浅绿色圆形背景 */
  padding: 8px;
  border-radius: 50%;
  box-sizing: content-box;
}

.stat-info .number {
  font-size: 20px;
  font-weight: bold;
  color: #3a856b;
}

.stat-info .desc {
  font-size: 12px;
  color: #888;
  margin-top: 2px;
}

.divider {
  width: 1px;
  height: 40px;
  background-color: #eee;
  margin: 0 30px;
}
</style>