<script setup lang="ts">
import { ref, onMounted, watch, toRaw } from 'vue' // 引入必要的 Hook
import { useRouter } from 'vue-router'
import { 
  RefreshLeft, 
  Check, 
  ArrowRight,
  Plus
} from '@element-plus/icons-vue'
import type { UploadProps, UploadUserFile } from 'element-plus'
import { ElMessage } from 'element-plus'

const router = useRouter()

// === 1. 定义存储 Key ===
const STORAGE_KEY = 'interview_data_step2'

// === 2. 定义响应式数据 ===
const resumeText = ref('')
// 专门用于管理上传组件的文件列表，实现回显
const fileList = ref<UploadUserFile[]>([])

// === 3. 页面加载：回填数据 ===
onMounted(() => {
  try {
    const savedData = localStorage.getItem(STORAGE_KEY)
    if (savedData) {
      const parsedData = JSON.parse(savedData)
      
      // 3.1 回填文本
      if (parsedData.resumeText) {
        resumeText.value = parsedData.resumeText
      }

      // 3.2 回填文件列表 (视觉回显)
      // 注意：LocalStorage 存不了真正的 File 对象，这里只回显文件名
      if (parsedData.fileName) {
        fileList.value = [{
          name: parsedData.fileName,
          url: '', // 本地并没有真实 URL
          status: 'success'
        }]
      }
    }
  } catch (error) {
    console.error('读取缓存失败:', error)
    localStorage.removeItem(STORAGE_KEY)
  }
})

// === 4. 统一保存逻辑 ===
// 将当前状态保存到 localStorage
const saveState = () => {
  try {
    // 获取当前选中的第一个文件名（如果是单文件上传）
    const currentFileName = fileList.value.length > 0 ? fileList.value[0].name : ''
    
    const data = {
      resumeText: resumeText.value,
      fileName: currentFileName
    }
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data))
  } catch (error) {
    console.error('保存状态失败', error)
  }
}

// === 5. 监听数据变化 ===

// 5.1 监听文本输入，实时保存
watch(resumeText, () => {
  saveState()
})

// 5.2 监听文件变化 (添加文件)
const handleUpload: UploadProps['onChange'] = (uploadFile, uploadFiles) => {
  fileList.value = uploadFiles // 更新列表
  saveState() // 保存状态
  
  if (uploadFile.status === 'ready') {
    ElMessage.success(`已选择文件: ${uploadFile.name}`)
  }
}

// 5.3 监听文件移除
const handleRemove: UploadProps['onRemove'] = (uploadFile, uploadFiles) => {
  fileList.value = uploadFiles // 更新列表
  saveState() // 保存状态（此时 fileName 会变为空）
}

// === 路由跳转逻辑 ===
const goBack = () => {
  router.go(-1) 
}

const nextStep = () => {
  // 简单校验：文本和文件至少有一个
  if (!resumeText.value && fileList.value.length === 0) {
     ElMessage.warning('请上传简历文件或粘贴简历文本')
     return
  }
  
  // 打印最终数据（实际开发中这里可能需要构建 FormData 发给后端）
  console.log('Step 2 提交数据:', {
    text: resumeText.value,
    file: fileList.value.length > 0 ? toRaw(fileList.value[0]) : null
  })

  ElMessage.success('进入下一步')
  router.push({ name: 'CreateJob_3' })
}
</script>

<template>
  <div class="page-container">
    
    <!-- 1. 顶部步骤条 -->
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
        <!-- 
          修改点：
          1. 绑定 v-model:file-list="fileList" 用于回显
          2. 添加 :on-remove="handleRemove" 处理删除
          3. :limit="1" 限制只能传一个简历
        -->
        <el-upload
          v-model:file-list="fileList"
          class="custom-uploader"
          drag
          action="#" 
          :auto-upload="false"
          :on-change="handleUpload"
          :on-remove="handleRemove"
          :limit="1" 
          :show-file-list="true"
        >
          <div class="upload-content">
            <!-- 模拟图中那个带框的十字图标 -->
            <div class="icon-box">
              <el-icon class="plus-icon"><Plus /></el-icon>
              <!-- 四个角的装饰 -->
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
/* 页面容器 */
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
.step-item.active { color: #3a856b; font-weight: bold; } 
.step-item.finished { color: #666; }
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
  background-color: #f6fbf9; 
  border: 1px dashed #c0dcd3; 
  border-radius: 12px;
  height: 200px; 
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

/* --- 文本框样式 --- */
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