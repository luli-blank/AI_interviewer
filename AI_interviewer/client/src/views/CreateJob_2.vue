<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { 
  RefreshLeft, 
  Check, 
  ArrowRight,
  Plus,
  UploadFilled
} from '@element-plus/icons-vue'
import type { UploadProps } from 'element-plus'
import { ElMessage } from 'element-plus'

const router = useRouter()
const resumeText = ref('')

// === 路由跳转逻辑 ===
const goBack = () => {
  router.go(-1) // 返回上一页 (JobInfo)
}

const nextStep = () => {
  // 这里可以添加校验逻辑，比如检查是否上传了文件或输入了文本
  if (!resumeText.value) {
     // 仅作演示，实际逻辑根据需求
     console.log('未输入文本，但可能上传了文件')
  }
  // router.push({ name: 'PrepareDone' }) // 假设下一步是完成页
  ElMessage.success('进入下一步')
  router.push({ name: 'CreateJob_3' })
}

// === 文件上传逻辑 ===
const handleUpload: UploadProps['onChange'] = (uploadFile) => {
  ElMessage.success(`已选择文件: ${uploadFile.name}`)
}
</script>

<template>
  <div class="page-container">
    
    <!-- 1. 顶部步骤条 (状态改变：第二步高亮) -->
    <div class="steps-wrapper">
      <div class="step-pill">
        <span class="step-item finished">填写岗位信息</span>
        <el-icon class="step-arrow"><ArrowRight /></el-icon>
        <span class="step-item active">选择简历</span>
        <el-icon class="step-arrow"><ArrowRight /></el-icon>
        <span class="step-item">岗位推荐</span>
      </div>
    </div>

    <!-- 2. 标题区域 -->
    <div class="header-section">
      <h1 class="main-title">想用哪份简历？</h1>
      <p class="sub-title">了解您的求职岗位，提高AI回答的针对性</p>
    </div>

    <!-- 3. 核心内容区域 -->
    <div class="form-section">
      
      <!-- 文件上传卡片 -->
      <div class="upload-wrapper">
        <el-upload
          class="custom-uploader"
          drag
          action="#" 
          :auto-upload="false"
          :on-change="handleUpload"
          :show-file-list="true"
        >
          <div class="upload-content">
            <!-- 模拟图中那个带框的十字图标 -->
            <div class="icon-box">
              <el-icon class="plus-icon"><Plus /></el-icon>
              <!-- 四个角的装饰 (CSS实现) -->
              <div class="corner top-left"></div>
              <div class="corner top-right"></div>
              <div class="corner bottom-left"></div>
              <div class="corner bottom-right"></div>
            </div>
            
            <div class="upload-text-main">拖拽简历到此处上传</div>
            <div class="upload-text-sub">或点击选择文件上传</div>
          </div>
        </el-upload>
      </div>

      <!-- 文本粘贴区域 -->
      <div class="input-group">
        <el-input 
          v-model="resumeText" 
          type="textarea"
          :rows="10"
          placeholder="你还可以直接粘贴你的简历文本到这里，特别是遇到解析失败的时候。" 
          class="custom-input custom-textarea"
          maxlength="3000"
          show-word-limit
        />
      </div>

    </div>

    <!-- 4. 底部按钮 -->
    <div class="footer-actions">
      <!-- 上一步 -->
      <button class="action-btn back-btn" @click="goBack">
        <el-icon style="margin-right: 4px"><RefreshLeft /></el-icon>
        上一步
      </button>
      
      <!-- 下一步 -->
      <button class="action-btn next-btn" @click="nextStep">
        <el-icon style="margin-right: 4px"><Check /></el-icon>
        下一步
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
.steps-wrapper { margin-bottom: 40px; }
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
.step-item.active { color: #3a856b; font-weight: bold; } /* 当前激活：绿色 */
.step-item.finished { color: #666; } /* 已完成：深灰 */
.step-arrow { color: #ccc; font-size: 12px; }

/* === 标题 === */
.header-section { text-align: center; margin-bottom: 30px; }
.main-title { color: #333; font-size: 32px; font-weight: 700; margin-bottom: 10px; }
.sub-title { color: #666; font-size: 14px; }

/* === 表单区域 === */
.form-section {
  width: 100%;
  max-width: 800px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* --- 上传控件深度定制 --- */
.upload-wrapper {
  width: 100%;
}

:deep(.custom-uploader .el-upload-dragger) {
  background-color: #f6fbf9; /* 极淡的绿色背景 */
  border: 1px dashed #c0dcd3; /* 虚线边框 */
  border-radius: 12px;
  height: 200px; /* 增加高度 */
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
}

:deep(.custom-uploader .el-upload-dragger:hover) {
  border-color: #3a856b;
  background-color: #f0f7f5;
}

.upload-content {
  display: flex;
  flex-direction: column;
  align-items: center;
}

/* 模拟十字图标和边角 */
.icon-box {
  width: 40px;
  height: 40px;
  position: relative;
  margin-bottom: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.plus-icon {
  font-size: 24px;
  color: #3a856b;
}

/* 四个角落的小折线 (装饰) */
.corner {
  position: absolute;
  width: 8px;
  height: 8px;
  border-color: #3a856b;
  border-style: solid;
  border-width: 0;
}
.top-left { top: 0; left: 0; border-top-width: 2px; border-left-width: 2px; }
.top-right { top: 0; right: 0; border-top-width: 2px; border-right-width: 2px; }
.bottom-left { bottom: 0; left: 0; border-bottom-width: 2px; border-left-width: 2px; }
.bottom-right { bottom: 0; right: 0; border-bottom-width: 2px; border-right-width: 2px; }

.upload-text-main { color: #333; font-size: 15px; margin-bottom: 5px; }
.upload-text-sub { color: #3a856b; font-size: 14px; cursor: pointer; }

/* --- 文本框样式 (复用之前的逻辑) --- */
:deep(.custom-input.el-textarea .el-textarea__inner) {
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 0 0 1px #eef0f2 inset;
  padding: 20px;
  font-size: 15px;
  color: #555;
  transition: all 0.3s;
  font-family: inherit;
  resize: none;
}

:deep(.custom-input.el-textarea .el-textarea__inner:focus) {
  box-shadow: 0 0 0 1px #3a856b inset !important;
}

:deep(.el-textarea .el-input__count) {
  background: transparent;
  bottom: 15px;
  right: 20px;
  color: #bbb;
}

:deep(textarea::placeholder) { color: #b1b3b8; }

/* === 底部按钮 === */
.footer-actions {
  margin-top: 40px;
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

.back-btn { background-color: #dbece5; color: #2c5e4f; }
.back-btn:hover { background-color: #cce3db; }

.next-btn { background-color: #8bb3a6; color: white; font-weight: 500; }
.next-btn:hover { background-color: #7da598; }
</style>