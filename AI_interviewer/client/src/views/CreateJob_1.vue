<script setup lang="ts">
import { reactive, ref, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus' 
import { 
  RefreshLeft, 
  Check, 
  ArrowRight,
  Loading 
} from '@element-plus/icons-vue'

const router = useRouter()

// === 新增：定义岗位名称输入框的引用 ===
// 用于在校验失败时获取该组件实例并调用 focus 方法
const jobNameInputRef = ref<HTMLElement | null>(null)

// 表单数据
const formData = reactive({
  jobName: '',
  jobDesc: '',
  companyName: '',
  companyDesc: ''
})

// 路由跳转
const goBack = () => {
  router.push({ name: 'Home' }) // 返回上一页
}

const nextStep = () => {
  console.log('提交数据:', formData)
  
  // === 修改：校验逻辑 ===
  if(!formData.jobName) {
    // 1. 使用 ElMessage 替代 alert，避免系统弹窗抢夺焦点
    ElMessage.warning('请输入岗位名称')
    
    // 2. 强制聚焦逻辑
    nextTick(() => {
      // 兼容 Electron/浏览器：先强制让窗口获取焦点
      window.focus()
      
      // 再让具体的输入框获取焦点
      if (jobNameInputRef.value) {
        jobNameInputRef.value.focus()
      }
    })
    return
  }
  
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
    <div class="decor-icon left-loading">
      <el-icon class="is-loading"><Loading /></el-icon>
    </div>

    <!-- 3. 表单区域 -->
    <div class="form-section">
      
      <!-- 岗位名称 -->
      <div class="input-group">
        <!-- === 修改点：绑定 ref="jobNameInputRef" === -->
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
  height: 100%; /* 将 min-height 改为固定 height，占满屏幕 */
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
/* 这里使用了 :deep() 来穿透 Element Plus 的原生样式 */

:deep(.custom-input .el-input__wrapper),
:deep(.custom-input.el-textarea .el-textarea__inner) {
  background-color: white;
  border-radius: 12px; /* 大圆角 */
  box-shadow: 0 0 0 1px #eef0f2 inset; /* 极细的内边框 */
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
  box-shadow: 0 0 0 1px #3a856b inset !important; /* 聚焦变成墨绿色 */
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
  resize: none; /* 禁止拖拽改变大小 */
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