<template>
  <div class="page-background">
    <div class="main-container">
      
      <div class="header-section">
        <h1 class="page-title">动态问卷测评</h1>
        <!-- 数据加载完成后，才显示真实的题目数量 -->
        <p class="page-subtitle" v-if="!pageLoading">
          共 {{ questions.length }} 道题目，系统将自动生成分析报告。
        </p>
        <p class="page-subtitle" v-else>正在从服务器获取题目...</p>
      </div>

      <!-- 增加 v-loading 指令，数据请求期间显示加载动画 -->
      <el-card 
        class="survey-card" 
        shadow="hover"
        v-loading="pageLoading"
        element-loading-text="正在加载问卷内容..."
      >
        <!-- 只有当数据加载完毕且有题目时，才渲染表单 -->
        <el-form
          v-if="!pageLoading && questions.length > 0"
          ref="ruleFormRef"
          :model="form"
          :rules="rules"
          label-position="top"
          class="survey-form"
          size="large"
        >
          
          <div 
            v-for="(item, index) in questions" 
            :key="item.id" 
            class="question-block"
          >
            <el-form-item :prop="item.id" class="dynamic-form-item">
              <template #label>
                <span class="question-label">
                  <span class="question-index">{{ formatIndex(index) }}.</span>
                  {{ item.title }}
                </span>
              </template>

              <el-radio-group v-model="form[item.id]" class="custom-radio-group">
                <el-radio 
                  v-for="opt in item.options" 
                  :key="opt.value" 
                  :label="opt.value" 
                  border
                >
                  {{ opt.label }}
                </el-radio>
              </el-radio-group>
            </el-form-item>
            
            <el-divider v-if="index < questions.length - 1" class="custom-divider" />
          </div>

          <!-- 底部按钮 -->
          <div class="form-actions">
            <el-button @click="resetForm(ruleFormRef)">重置</el-button>
            <el-button 
              type="primary" 
              class="submit-btn" 
              :loading="submitting"
              @click="submitForm(ruleFormRef)"
            >
              提交问卷
            </el-button>
          </div>

        </el-form>

        <!-- 如果加载完发现没有题目，或者加载失败 -->
        <div v-else-if="!pageLoading && questions.length === 0" class="empty-state">
          <p>暂无问卷数据，请稍后重试</p>
          <el-button type="primary" link @click="fetchQuestions">重新加载</el-button>
        </div>
      </el-card>
      
      <div class="footer-spacer"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
// 如果你安装了 axios，建议使用 import axios from 'axios'

// --- 1. 定义接口 ---
interface SurveyOption {
  label: string;
  value: string;
}

interface SurveyQuestion {
  id: string;
  title: string;
  required?: boolean;
  options: SurveyOption[];
}

// --- 2. 状态变量 ---
const ruleFormRef = ref<FormInstance>()
const pageLoading = ref(true) // 控制页面加载状态
const submitting = ref(false) // 控制提交按钮状态
const questions = ref<SurveyQuestion[]>([]) // 存储从后端拿到的题目

// 动态表单数据和规则
const form = reactive<Record<string, any>>({})
const rules = reactive<FormRules>({})

// --- 3. 核心：从后端获取数据 ---
const fetchQuestions = async () => {
  pageLoading.value = true
  try {
    // ==========================================
    // 模拟后端请求 (实际开发中请替换为真实 API)
    // ==========================================
    
    // const response = await axios.get('/api/survey/questions')
    // const data = response.data
    
    // 这里我用 Promise 模拟一个 1秒 的网络延迟
    const mockData: SurveyQuestion[] = await new Promise((resolve) => {
      setTimeout(() => {
        resolve([
          {
            id: 'q_backend_1',
            title: '（来自后端）您的首选开发语言是？',
            required: true,
            options: [
              { label: 'JavaScript / TypeScript', value: 'js' },
              { label: 'Java', value: 'java' },
              { label: 'Python', value: 'python' },
              { label: 'Go / Rust', value: 'go_rust' }
            ]
          },
          {
            id: 'q_backend_2',
            title: '（来自后端）您通常在哪个平台部署应用？',
            required: true,
            options: [
              { label: 'AWS / Azure / GCP', value: 'cloud' },
              { label: 'Vercel / Netlify', value: 'serverless' },
              { label: '自建服务器 (Linux)', value: 'self_host' }
            ]
          }
        ])
      }, 800)
    })

    questions.value = mockData
    
    // 获取数据后，初始化表单
    initForm() 

  } catch (error) {
    console.error('获取问卷失败:', error)
    ElMessage.error('无法加载问卷数据，请检查网络连接')
  } finally {
    pageLoading.value = false
  }
}

// --- 4. 初始化表单逻辑 ---
const initForm = () => {
  // 清空之前的规则（防止重新加载时叠加）
  for (const key in rules) delete rules[key]
  
  questions.value.forEach(q => {
    // 建立响应式属性
    // 注意：如果这题已经有值（比如回显），则不覆盖；否则设为空
    if (form[q.id] === undefined) {
      form[q.id] = ''
    }

    // 动态生成规则
    if (q.required) {
      rules[q.id] = [
        { required: true, message: '该项为必选项', trigger: 'change' }
      ]
    }
  })
}

// 辅助函数：格式化序号 (1 -> 01)
const formatIndex = (index: number) => {
  const num = index + 1
  return num < 10 ? `0${num}` : num
}

// --- 5. 生命周期 ---
onMounted(() => {
  fetchQuestions()
})

// --- 6. 提交与重置 ---
const submitForm = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  
  await formEl.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      
      try {
        // 构建要发给后端的数据 Payload
        const payload = {
          answers: form,
          timestamp: new Date().toISOString()
        }
        
        console.log('准备提交给后端的数据:', payload)

        // 模拟提交请求
        // await axios.post('/api/survey/submit', payload)
        await new Promise(resolve => setTimeout(resolve, 1000))

        ElMessageBox.alert('问卷提交成功！感谢您的参与。', '完成', {
          confirmButtonText: '关闭',
          type: 'success',
          callback: () => {
            // 这里可以重置表单或者跳转页面
            // router.push('/')
          }
        })
      } catch (e) {
        ElMessage.error('提交失败，请稍后重试')
      } finally {
        submitting.value = false
      }

    } else {
      ElMessage.warning('请完成所有必填项')
      // 自动滚动到错误位置
      const isError = document.querySelector('.is-error')
      isError?.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }
  })
}

const resetForm = (formEl: FormInstance | undefined) => {
  if (!formEl) return
  formEl.resetFields()
}
</script>

<style scoped>
/* 保持原有样式，增加 Empty State 样式 */
.page-background {
  background: radial-gradient(circle at 10% 20%, #e6f7f2 0%, #f7f9fa 60%, #fff7ec 100%);
  min-height: 100vh;
  padding: 40px 20px;
  box-sizing: border-box;
  overflow-y: auto;
}

.main-container {
  max-width: 800px;
  margin: 0 auto;
}

.header-section {
  text-align: center;
  margin-bottom: 30px;
}

.page-title {
  color: #2c3e50;
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 10px;
}

.page-subtitle {
  color: #606266;
}

.survey-card {
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.95);
  padding: 10px 20px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.03);
  min-height: 300px; /* 给 Loading 留点高度 */
}

.question-block {
  margin-bottom: 10px;
}

.question-label {
  font-size: 1.1rem;
  font-weight: 600;
  color: #2c3e50;
  line-height: 1.5;
  display: block;
  margin-bottom: 10px;
}

.question-index {
  color: #42b983;
  margin-right: 8px;
}

.custom-radio-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
  width: 100%;
}

:deep(.el-radio) {
  margin-right: 0;
  width: 100%;
  padding: 12px 15px;
  height: auto;
  border-radius: 12px;
  border: 1px solid #dcdfe6;
  background: #fff;
}

:deep(.el-radio.is-bordered.is-checked) {
  background-color: #f0f9eb;
  border-color: #42b983;
}

:deep(.el-radio__input.is-checked .el-radio__inner) {
  background-color: #42b983;
  border-color: #42b983;
}

.custom-divider {
  margin: 30px 0;
  border-top: 1px dashed #e0e0e0;
}

.form-actions {
  margin-top: 40px;
  display: flex;
  justify-content: center;
  gap: 20px;
  padding-bottom: 20px;
}

.submit-btn {
  background: linear-gradient(135deg, #42b983 0%, #2f7c6e 100%);
  border: none;
  min-width: 160px;
  border-radius: 50px;
}

.submit-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(66, 185, 131, 0.3);
}

.footer-spacer {
  height: 60px;
}

.empty-state {
  text-align: center;
  padding: 60px 0;
  color: #909399;
}
</style>