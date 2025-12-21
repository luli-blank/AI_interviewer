<script setup lang="ts">
// 1. 引入必要的核心函数，特别是 toRaw
import { reactive, ref, nextTick, onMounted, watch, toRaw } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus' 
import { 
  RefreshLeft, 
  Check, 
  ArrowRight,
  Loading 
} from '@element-plus/icons-vue'

const router = useRouter()

// === 定义本地存储的 Key ===
const STORAGE_KEY = 'interview_data_step1'

// 定义岗位名称输入框的引用
const jobNameInputRef = ref<HTMLElement | null>(null)

// 表单数据
const formData = reactive({
  jobName: '',
  jobDesc: '',
  companyName: '',
  companyDesc: ''
})

// === 1. 页面加载：回填数据 ===
onMounted(() => {
  try {
    const savedData = localStorage.getItem(STORAGE_KEY)
    if (savedData) {
      const parsedData = JSON.parse(savedData)
      // 使用 Object.assign 保持 formData 的响应性
      Object.assign(formData, parsedData)
    }
  } catch (error) {
    console.error('读取缓存出错，已自动重置:', error)
    // 如果数据损坏，清除旧数据防止持续报错
    localStorage.removeItem(STORAGE_KEY)
  }
})

// === 2. 实时保存：监听数据变化 ===
watch(formData, () => {
  try {
    // 【关键修复】使用 toRaw 将 Vue 的响应式 Proxy 对象转为普通 JS 对象
    // 这一步能防止 JSON.stringify 在处理 Proxy 时可能导致的死循环或报错（即白屏原因）
    const rawData = toRaw(formData)
    localStorage.setItem(STORAGE_KEY, JSON.stringify(rawData))
  } catch (error) {
    console.error('保存缓存失败:', error)
  }
}, { deep: true }) // deep: true 确保监听对象内部属性变化

// 路由跳转：返回上一页
const goBack = () => {
  router.push({ name: 'Home' }) 
}

// 路由跳转：下一步
const nextStep = () => {
  console.log('提交数据:', toRaw(formData))
  
  // 校验逻辑
  if(!formData.jobName) {
    ElMessage.warning('请输入岗位名称')
    
    // 聚焦逻辑
    nextTick(() => {
      window.focus()
      if (jobNameInputRef.value) {
        jobNameInputRef.value.focus()
      }
    })
    return
  }
  
  // 跳转到第二步（注意：这里不清除 Storage，保留数据以便用户返回修改）
  router.push({ name: 'CreateJob_2' }) 
}
</script>

<template>
  <div class="page-container">
    
    <!-- 1. 顶部步骤条 -->
    <div class="steps-wrapper">
      <div class="step-pill">
        <span class="step-item active">填写岗位信息</span>
        <el-icon class="step-arrow"><ArrowRight /></el-icon>
        <span class="step-item">选择简历</span>
        <el-icon class="step-arrow"><ArrowRight /></el-icon>
        <span class="step-item">岗位推荐</span>
      </div>
    </div>

    <!-- 2. 标题区域 -->
    <div class="header-section">
      <h1 class="main-title">准备面试什么岗位呢？</h1>
      <p class="sub-title">了解您的求职岗位，提高AI回答的针对性</p>
    </div>

    <!-- 装饰图标 -->
    <!-- <div class="decor-icon left-loading">
      <el-icon class="is-loading"><Loading /></el-icon>
    </div> -->

    <!-- 3. 表单区域 -->
    <div class="form-section">
      
      <!-- 岗位名称 -->
      <div class="input-group">
        <el-input 
          ref="jobNameInputRef"
          v-model="formData.jobName" 
          placeholder="请输入岗位名称" 
          class="custom-input large-input"
        />
      </div>

      <!-- 岗位描述 -->
      <div class="input-group">
        <el-input 
          v-model="formData.jobDesc" 
          type="textarea"
          :rows="6"
          placeholder="请输入岗位描述，AI 会根据具体的岗位要求，工作职责，生成面试押题、规划模拟面试流程、AI生成面试回答。" 
          class="custom-input custom-textarea"
          maxlength="2000"
          show-word-limit
        />
      </div>

      <!-- 公司名称 -->
      <div class="input-group">
        <el-input 
          v-model="formData.companyName" 
          placeholder="(可选)请输入公司名称" 
          class="custom-input large-input"
        />
      </div>

      <!-- 公司简介 -->
      <div class="input-group">
        <el-input 
          v-model="formData.companyDesc" 
          type="textarea"
          :rows="6"
          placeholder="(可选)请输入公司简介，当面试官提及公司业务情况时，AI会根据描述，生成恰当的回答。" 
          class="custom-input custom-textarea"
          maxlength="2000"
          show-word-limit
        />
      </div>

    </div>

    <!-- 4. 底部按钮 -->
    <div class="footer-actions">
      <button class="action-btn back-btn" @click="goBack">
        <el-icon style="margin-right: 4px"><RefreshLeft /></el-icon>
        返回首页
      </button>
      
      <button class="action-btn next-btn" @click="nextStep">
        <el-icon style="margin-right: 4px"><Check /></el-icon>
        下一步
      </button>
    </div>

  </div>
</template>

<style scoped>
/* 页面整体背景色 - 极淡的青色 */
.page-container {
  width: 100%;
  height: 100%; 
  background-color: #f7fbf9; 
  padding: 40px 20px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
}

/* === 1. 顶部步骤条 === */
.steps-wrapper {
  margin-bottom: 40px;
}

.step-pill {
  background-color: white;
  padding: 12px 60px;
  border-radius: 30px;
  display: flex;
  align-items: center;
  gap: 20px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.03);
}

.step-item {
  color: #999;
  font-size: 14px;
  font-weight: 500;
}

.step-item.active {
  color: #3a856b; /* 激活色：墨绿 */
  font-weight: bold;
}

.step-arrow {
  color: #ccc;
  font-size: 12px;
}

/* === 2. 标题区域 === */
.header-section {
  text-align: center;
  margin-bottom: 40px;
}

.main-title {
  color: #333;
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 10px;
}

.sub-title {
  color: #666;
  font-size: 14px;
}

/* === 装饰图标 === */
.decor-icon {
  position: absolute;
  color: #3a856b;
  font-size: 24px;
}
.left-loading {
  top: 200px;
  left: 15%;
}

/* === 3. 表单区域 === */
.form-section {
  width: 100%;
  max-width: 800px; /* 限制表单最大宽度 */
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.input-group {
  width: 100%;
}

/* --- 深度定制 Element Input 样式 --- */
:deep(.custom-input .el-input__wrapper),
:deep(.custom-input.el-textarea .el-textarea__inner) {
  background-color: white;
  border-radius: 12px; 
  box-shadow: 0 0 0 1px #eef0f2 inset; 
  padding: 15px 20px;
  transition: all 0.3s;
}

/* 输入框悬停/聚焦效果 */
:deep(.custom-input .el-input__wrapper:hover),
:deep(.custom-input.el-textarea .el-textarea__inner:hover) {
  box-shadow: 0 0 0 1px #c0dcd3 inset; 
}

:deep(.custom-input .el-input__wrapper.is-focus),
:deep(.custom-input.el-textarea .el-textarea__inner:focus) {
  box-shadow: 0 0 0 1px #3a856b inset !important; 
}

/* 调整大号输入框的高度 */
:deep(.large-input .el-input__inner) {
  height: 24px;
  font-size: 15px;
  color: #333;
}

/* 调整文本域样式 */
:deep(.custom-textarea .el-textarea__inner) {
  font-family: inherit;
  font-size: 15px;
  resize: none; 
}

/* 调整字数统计的位置 */
:deep(.el-input__count), 
:deep(.el-textarea .el-input__count) {
  background: transparent;
  bottom: 10px;
  right: 20px;
  color: #bbb;
}

/* Placeholder 颜色 */
:deep(input::placeholder),
:deep(textarea::placeholder) {
  color: #a8abb2;
}

/* === 4. 底部按钮 === */
.footer-actions {
  margin-top: 50px;
  display: flex;
  gap: 20px;
}

.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 12px 40px;
  border-radius: 8px;
  font-size: 16px;
  border: none;
  cursor: pointer;
  transition: all 0.3s;
}

/* 返回按钮 */
.back-btn {
  background-color: #dbece5; /* 浅薄荷绿 */
  color: #2c5e4f;
}
.back-btn:hover {
  background-color: #cce3db;
}

/* 下一步按钮 */
.next-btn {
  background-color: #8bb3a6; /* 莫兰迪灰绿 */
  color: white;
  font-weight: 500;
}
.next-btn:hover {
  background-color: #7da598;
}
</style>