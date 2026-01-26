<script setup lang="ts">
import { ref } from 'vue' 
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus' 
import { 
  RefreshLeft, 
  VideoPlay, 
  ArrowRight,
  CircleCheckFilled,
  Trophy
} from '@element-plus/icons-vue'
import { getResumeFile, clearResumeFile } from '../utils/localStorage'
import { createInterviewSession } from '../api/Resume_upload'

const router = useRouter()

// === 定义 LocalStorage Key ===
const STEP1_KEY = 'interview_data_step1'
const STEP2_KEY = 'interview_data_step2'

// === 定义状态 ===
const isSubmitting = ref(false) 
const btnText = ref('数据同步') 

// === 修改点 1：移除返回按钮的锁定拦截 ===
const goBack = () => {
  // 原来的拦截逻辑已删除：if (isSubmitting.value) return 
  router.go(-1) 
}

const startInterview = async () => {
  // === 1. 冷却拦截逻辑 (15秒锁) - 依然对当前按钮生效 ===
  if (isSubmitting.value) return
  
  isSubmitting.value = true
  
  // 这里你设置的是3秒倒计时演示，如果是15秒请改为15
  let countdown = 3
  btnText.value = `请等待 ${countdown} 秒`
  
  const timer = setInterval(() => {
    countdown--
    if (countdown <= 0) {
      clearInterval(timer)
      isSubmitting.value = false
      btnText.value = '数据同步'
    } else {
      btnText.value = `请等待 ${countdown} 秒`
    }
  }, 1000)

  // === 2. 业务逻辑 ===
  try {
    const step1Data = localStorage.getItem(STEP1_KEY)
    const step2Data = localStorage.getItem(STEP2_KEY)
    
    if (!step1Data || !step2Data) {
      ElMessage.warning('数据不完整，请重新填写')
      return
    }
    
    const step1 = JSON.parse(step1Data)
    const step2 = JSON.parse(step2Data)
    
    const resumeFile = await getResumeFile()
    
    // 组装 FormData
    const formData = new FormData()
    formData.append('job_name', step1.jobName)
    formData.append('job_desc', step1.jobDesc || '')
    formData.append('company_name', step1.companyName || '')
    formData.append('company_desc', step1.companyDesc || '')
    formData.append('resume_text', step2.resumeText || '')
    
    if (resumeFile) {
      formData.append('resume_file', resumeFile)
    }
    
    // === 3. 调用后端 API ===
    console.log('正在向后端发送数据...')
    const response = await createInterviewSession(formData)
    
    // 获取后端生成的 SessionID
    const sessionId = response.data?.sessionId || response.sessionId
    console.log('后端返回的 SessionID:', sessionId)

    // 清空本地缓存
    localStorage.removeItem(STEP1_KEY)
    localStorage.removeItem(STEP2_KEY)
    await clearResumeFile()
    
    // === 4. 成功提示 ===
    ElMessage.success({
      message: '数据已成功同步至服务器！',
      duration: 3000, 
    })
    
  } catch (error: any) {
    console.error('上传失败:', error)
    let msg = '请求失败'
    if (error.response?.data?.message) {
      msg = error.response.data.message
    } else if (error.message) {
      msg = error.message
    }
    ElMessage.error(msg)
  }
}
</script>

<template>
  <div class="page-container">
    
    <!-- 步骤条 -->
    <div class="steps-wrapper">
      <div class="step-pill">
        <span class="step-item finished">填写岗位信息</span>
        <el-icon class="step-arrow"><ArrowRight /></el-icon>
        <span class="step-item finished">选择简历</span>
        <el-icon class="step-arrow"><ArrowRight /></el-icon>
        <span class="step-item active">数据同步</span>
      </div>
    </div>

    <!-- 内容区 -->
    <div class="content-wrapper">
      <div class="success-illustration">
        <div class="icon-bg-layer"></div>
        <el-icon class="success-icon"><CircleCheckFilled /></el-icon>
        <div class="deco-dot dot-1"></div>
        <div class="deco-dot dot-2"></div>
        <div class="deco-dot dot-3"></div>
        <el-icon class="deco-icon trophy"><Trophy /></el-icon>
      </div>

      <h1 class="main-title">准备工作已完成！</h1>
      <p class="sub-title">
        点击下方按钮将您的简历和岗位信息同步至服务器。<br>
        (本次操作仅用于数据传输测试，不会开启面试)
      </p>
    </div>

    <!-- 按钮区 -->
    <div class="footer-actions">
      <!-- 
        修改点 2：移除了 :disabled="isSubmitting" 
        现在无论右侧按钮是否在倒计时，上一步按钮永远可点
      -->
      <button class="action-btn back-btn" @click="goBack">
        <el-icon style="margin-right: 4px"><RefreshLeft /></el-icon>
        上一步
      </button>
      
      <!-- 数据同步按钮保持原样，受 isSubmitting 控制 -->
      <button 
        class="action-btn start-btn" 
        :class="{ 'is-disabled': isSubmitting }"
        @click="startInterview"
        :disabled="isSubmitting"
      >
        <el-icon style="margin-right: 6px" v-if="!isSubmitting"><VideoPlay /></el-icon>
        {{ btnText }}
      </button>
    </div>

  </div>
</template>

<style scoped>
/* 样式保持不变 */
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
.step-item.finished { color: #3a856b; } 
.step-arrow { color: #ccc; font-size: 12px; }

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

.success-illustration {
  position: relative;
  width: 120px;
  height: 120px;
  margin-bottom: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
}

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

.success-icon {
  font-size: 80px;
  color: #3a856b;
  z-index: 2;
  filter: drop-shadow(0 10px 15px rgba(58, 133, 107, 0.3));
}

.deco-dot {
  position: absolute;
  border-radius: 50%;
  background-color: #fca5a5; 
}
.dot-1 { width: 10px; height: 10px; top: 0; right: 10px; animation: float 3s infinite ease-in-out; }
.dot-2 { width: 8px; height: 8px; bottom: 10px; left: 0; background-color: #fcd34d; animation: float 4s infinite ease-in-out reverse; }
.dot-3 { width: 6px; height: 6px; top: 20px; left: -10px; background-color: #60a5fa; animation: float 2.5s infinite ease-in-out; }

.deco-icon.trophy {
  position: absolute;
  font-size: 24px;
  color: #f59e0b; 
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

.action-btn:disabled,
.action-btn.is-disabled {
  background-color: #e0e0e0;
  color: #999;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.back-btn { background-color: #dbece5; color: #2c5e4f; }
.back-btn:hover { background-color: #cce3db; }

.start-btn { 
  background-color: #3a856b; 
  color: white; 
  font-weight: 600; 
  box-shadow: 0 4px 14px rgba(58, 133, 107, 0.4);
}
.start-btn:not(:disabled):hover { 
  background-color: #2e6b56; 
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(58, 133, 107, 0.5);
}
.start-btn:not(:disabled):active { transform: scale(0.98); }
</style>