<template>
  <div class="page-background">
    <div class="main-container">
      <div class="header-section">
        <h1 class="page-title">职业性格测试报告</h1>
        <p class="page-subtitle">基于 MBTI 与大五人格的标准化分析</p>
      </div>

      <!-- 报告内容 -->
      <div v-if="!loading">
        <div class="survey-card">
          <el-card class="mb-4" shadow="never" style="border-radius: 24px; padding: 20px;">
            <h3 class="question-label">总体信息</h3>
            <el-descriptions border column="2">
              <el-descriptions-item label="问题总数">{{ report.total }}</el-descriptions-item>
              <el-descriptions-item label="MBTI 类型">{{ report.personality_type }}</el-descriptions-item>
            </el-descriptions>
          </el-card>

          <el-card class="mb-4" shadow="never" style="border-radius: 24px; padding: 20px;">
            <h3 class="question-label">职业偏好</h3>
            <el-tag
              v-for="(item, index) in report.career_preferences"
              :key="index"
              type="success"
              effect="plain"
              round
              class="mr-2 mb-2"
            >
              {{ item }}
            </el-tag>
          </el-card>

          <div class="grid" style="display: flex; gap: 20px; flex-wrap: wrap;">
            <el-card style="flex:1; min-width: 250px; border-radius: 24px; padding: 20px;">
              <h3 class="question-label">职场优势</h3>
              <ul style="padding-left: 20px;">
                <li v-for="(item, index) in report.strengths" :key="index">{{ item }}</li>
              </ul>
            </el-card>

            <el-card style="flex:1; min-width: 250px; border-radius: 24px; padding: 20px;">
              <h3 class="question-label">潜在劣势</h3>
              <ul style="padding-left: 20px;">
                <li v-for="(item, index) in report.weaknesses" :key="index">{{ item }}</li>
              </ul>
            </el-card>
          </div>

          <el-card class="mt-4" shadow="never" style="border-radius: 24px; padding: 20px;">
            <h3 class="question-label">总结与建议</h3>
            <p style="line-height: 1.6; color: #2c3e50;">{{ report.summary }}</p>
          </el-card>

          <div class="form-actions">
            <el-button 
              class="submit-btn"
              type="primary"
              round
              @click="goBack"
            >
              返回首页
            </el-button>
          </div>
        </div>
      </div>

      <!-- 全屏居中 Loading -->
      <el-loading 
        v-if="loading"
        :fullscreen="true"
        text="报告生成中，请稍候..."
        background="rgba(255, 255, 255, 0.6)">
      </el-loading>

    </div>
  </div>
</template>


<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getReport } from "../api/Character_test_report"
import { ElLoading } from 'element-plus'

let loadingInstance: any = null

interface ReportSchema {
  total: number
  personality_type: string
  career_preferences: string[]
  strengths: string[]
  weaknesses: string[]
  summary: string
}

const loading = ref(true)
const report = ref<ReportSchema>({
  total: 0,
  personality_type: '',
  career_preferences: [],
  strengths: [],
  weaknesses: [],
  summary: ''
})

const fetchReport = async () => {
  try {
    loadingInstance = ElLoading.service({ 
      lock: true, 
      text: '正在生成报告，请稍候...', 
      background: 'rgba(0, 0, 0, 0.1)' 
    })
    const res = await getReport()
    report.value = res
  } catch (err) {
    ElMessage.error({
      message: '报告获取失败',
      duration: 1000
    })
  } finally {
    loading.value = false
    loadingInstance?.close()
  }
}

const goBack = () => {
  // 返回首页或问卷列表
  window.history.back()
}

onMounted(() => {
  fetchReport()
})
</script>

<style scoped>
/* 页面背景 */
.page-background {
  background: radial-gradient(circle at 10% 20%, #e6f7f2 0%, #f7f9fa 60%, #fff7ec 100%);
  min-height: 100vh;
  padding: 40px 20px;
  box-sizing: border-box;
  overflow-y: auto;
}

/* 主容器 */
.main-container {
  max-width: 800px;
  margin: 0 auto;
}

/* 头部标题 */
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

/* 卡片 */
.survey-card, .el-card {
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.95);
  padding: 20px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.03);
  margin-bottom: 20px;
}

/* 小标题 */
.question-label {
  font-size: 1.2rem;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 15px;
  display: block;
}

/* 标签组 */
.el-tag {
  margin-right: 8px;
  margin-bottom: 8px;
  font-size: 0.875rem;
}

/* 优势/劣势列表 */
ul {
  padding-left: 20px;
  list-style-type: disc;
  color: #2c3e50;
  line-height: 1.6;
}

/* 按钮容器 */
.form-actions {
  margin-top: 40px;
  display: flex;
  justify-content: center;
  gap: 20px;
  padding-bottom: 20px;
}

/* 按钮样式 */
.submit-btn {
  background: linear-gradient(135deg, #42b983 0%, #2f7c6e 100%);
  border: none;
  min-width: 160px;
  border-radius: 50px;
  color: #fff;
  font-weight: 600;
}

.submit-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(66, 185, 131, 0.3);
}

/* 空状态 / Loading */
.empty-state {
  text-align: center;
  padding: 60px 0;
  color: #909399;
}

/* 响应式布局：优势/劣势卡片 */
@media (max-width: 768px) {
  .grid {
    flex-direction: column;
  }
}
</style>