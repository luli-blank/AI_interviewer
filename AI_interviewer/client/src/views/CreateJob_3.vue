<script setup lang="ts">
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  RefreshLeft, 
  VideoPlay, 
  ArrowRight,
  CircleCheckFilled,
  Trophy
} from '@element-plus/icons-vue'

const router = useRouter()

// === 路由跳转逻辑 ===
const goBack = () => {
  router.go(-1) // 返回上一页 (SelectResume)
}

const startInterview = () => {
  // 这里是整个流程的最后一步，点击提交
  ElMessage.success('配置完成，正在进入面试房间...')
  
  // 模拟跳转到正式面试页面
  setTimeout(() => {
    // 假设你的面试页面路由叫 'InterviewRoom' 或者回到首页 'Home'
    router.push({ name: 'Going' }) 
  }, 1000)
}
</script>

<template>
  <div class="page-container">
    
    <!-- 1. 顶部步骤条 (状态改变：全亮) -->
    <div class="steps-wrapper">
      <div class="step-pill">
        <span class="step-item finished">填写岗位信息</span>
        <el-icon class="step-arrow"><ArrowRight /></el-icon>
        <span class="step-item finished">选择简历</span>
        <el-icon class="step-arrow"><ArrowRight /></el-icon>
        <span class="step-item active">准备完成</span>
      </div>
    </div>

    <!-- 2. 核心内容区域 (垂直居中布局) -->
    <div class="content-wrapper">
      
      <!-- 成功插画/图标区域 -->
      <div class="success-illustration">
        <div class="icon-bg-layer"></div>
        <el-icon class="success-icon"><CircleCheckFilled /></el-icon>
        
        <!-- 装饰性的小图标 (模拟撒花效果) -->
        <div class="deco-dot dot-1"></div>
        <div class="deco-dot dot-2"></div>
        <div class="deco-dot dot-3"></div>
        <el-icon class="deco-icon trophy"><Trophy /></el-icon>
      </div>

      <!-- 文本提示 -->
      <h1 class="main-title">准备工作已完成！</h1>
      <p class="sub-title">
        AI 面试官已根据您的岗位和简历生成了专属题库。<br>
        请调整好心态，保持环境安静，随时开始模拟面试。
      </p>

    </div>

    <!-- 3. 底部按钮 -->
    <div class="footer-actions">
      <!-- 上一步 -->
      <button class="action-btn back-btn" @click="goBack">
        <el-icon style="margin-right: 4px"><RefreshLeft /></el-icon>
        上一步
      </button>
      
      <!-- 提交/开始按钮 -->
      <button class="action-btn start-btn" @click="startInterview">
        <el-icon style="margin-right: 6px"><VideoPlay /></el-icon>
        开始模拟面试
      </button>
    </div>

  </div>
</template>

<style scoped>
/* 页面容器 - 保持背景一致 */
.page-container {
  width: 100%;
  height: 100%;
  background-color: #f7fbf9; 
  padding: 40px 20px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  align-items: center;
}

/* === 步骤条 === */
.steps-wrapper { margin-bottom: 60px; }
.step-pill {
  background-color: white;
  padding: 12px 60px;
  border-radius: 30px;
  display: flex;
  align-items: center;
  gap: 20px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.03);
}
.step-item { color: #999; font-size: 14px; font-weight: 500; }
.step-item.active { color: #3a856b; font-weight: bold; } 
.step-item.finished { color: #3a856b; } /* 完成也是绿色，或者可以用深灰 */
.step-arrow { color: #ccc; font-size: 12px; }

/* === 核心内容区 === */
.content-wrapper {
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 60px;
  animation: fadeInUp 0.6s ease-out;
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

/* === 成功插画样式 (CSS绘制) === */
.success-illustration {
  position: relative;
  width: 120px;
  height: 120px;
  margin-bottom: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 绿色光晕背景 */
.icon-bg-layer {
  position: absolute;
  width: 100%;
  height: 100%;
  background-color: #dbece5;
  border-radius: 50%;
  opacity: 0.5;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { transform: scale(0.95); opacity: 0.5; }
  50% { transform: scale(1.1); opacity: 0.3; }
  100% { transform: scale(0.95); opacity: 0.5; }
}

/* 核心对勾图标 */
.success-icon {
  font-size: 80px;
  color: #3a856b;
  z-index: 2;
  /* 阴影让它浮起来 */
  filter: drop-shadow(0 10px 15px rgba(58, 133, 107, 0.3));
}

/* 装饰元素 */
.deco-dot {
  position: absolute;
  border-radius: 50%;
  background-color: #fca5a5; /* 珊瑚红点缀 */
}
.dot-1 { width: 10px; height: 10px; top: 0; right: 10px; animation: float 3s infinite ease-in-out; }
.dot-2 { width: 8px; height: 8px; bottom: 10px; left: 0; background-color: #fcd34d; animation: float 4s infinite ease-in-out reverse; }
.dot-3 { width: 6px; height: 6px; top: 20px; left: -10px; background-color: #60a5fa; animation: float 2.5s infinite ease-in-out; }

.deco-icon.trophy {
  position: absolute;
  font-size: 24px;
  color: #f59e0b; /* 金色奖杯 */
  bottom: -5px;
  right: -10px;
  z-index: 3;
  transform: rotate(15deg);
  animation: float 3s infinite ease-in-out 1s;
}

@keyframes float {
  0%, 100% { transform: translateY(0) rotate(15deg); }
  50% { transform: translateY(-10px) rotate(15deg); }
}

/* === 文本样式 === */
.main-title {
  color: #333;
  font-size: 36px;
  font-weight: 700;
  margin: 0 0 15px 0;
}

.sub-title {
  color: #666;
  font-size: 16px;
  line-height: 1.6;
  max-width: 600px;
}

/* === 底部按钮 === */
.footer-actions {
  display: flex;
  gap: 20px;
}

.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 14px 45px;
  border-radius: 10px;
  font-size: 16px;
  border: none;
  cursor: pointer;
  transition: all 0.3s;
  letter-spacing: 0.5px;
}

.back-btn { background-color: #dbece5; color: #2c5e4f; }
.back-btn:hover { background-color: #cce3db; }

/* 开始面试按钮 - 更加显眼 */
.start-btn { 
  background-color: #3a856b; 
  color: white; 
  font-weight: 600; 
  box-shadow: 0 4px 14px rgba(58, 133, 107, 0.4);
}
.start-btn:hover { 
  background-color: #2e6b56; 
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(58, 133, 107, 0.5);
}
.start-btn:active { transform: scale(0.98); }

</style>