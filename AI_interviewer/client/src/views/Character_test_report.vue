<template>
  <div class="page-background">
    <div class="main-container">
      <!-- 导出PDF范围（不包含底部操作按钮） -->
      <div ref="pdfRef">
        <div class="header-section">
          <h1 class="page-title">职业性格测试报告</h1>
          <p class="page-subtitle">基于 MBTI 与大五人格的标准化分析</p>
        </div>

        <!-- 报告内容 -->
        <div v-if="!loading">
          <div class="survey-card">
            <el-card class="mb-4" shadow="never" style="border-radius: 24px; padding: 20px;">
              <h3 class="question-label">总体信息</h3>
              <el-descriptions border :column="2">
                <el-descriptions-item label="问题总数">{{ report.total }}</el-descriptions-item>
                <el-descriptions-item label="MBTI 类型">{{ report.personality_type }}</el-descriptions-item>
              </el-descriptions>
            </el-card>

            <el-card class="mb-4" shadow="never" style="border-radius: 24px; padding: 20px;">
              <h3 class="question-label">职业竞争力雷达图（核心能力量化）</h3>
              <div class="radar-wrap">
                <svg
                  class="radar-svg"
                  :width="radarSize"
                  :height="radarSize"
                  viewBox="0 0 320 320"
                  role="img"
                  aria-label="competency radar chart"
                >
                  <!-- 背景网格 -->
                  <g>
                    <polygon v-for="lvl in 5" :key="lvl" :points="gridPoints(lvl / 5)" class="radar-grid" />
                    <line v-for="(a, idx) in axes" :key="idx" :x1="center" :y1="center" :x2="a.x" :y2="a.y" class="radar-axis" />
                  </g>

                  <!-- 数据多边形 -->
                  <polygon :points="dataPolygonPoints" class="radar-area" />
                  <polyline :points="dataPolygonPoints" class="radar-line" />

                  <!-- 维度标签 -->
                  <g>
                    <text
                      v-for="(a, idx) in axes"
                      :key="'t' + idx"
                      :x="labelPos(a).x"
                      :y="labelPos(a).y"
                      class="radar-label"
                      text-anchor="middle"
                    >
                      {{ radarItems[idx]?.name || '' }}
                    </text>
                  </g>
                </svg>

                <div class="radar-legend">
                  <div v-for="(item, idx) in radarItems" :key="'l' + idx" class="radar-legend-item">
                    <div class="radar-legend-title">
                      <span class="radar-dot"></span>
                      <span>{{ item.name }}</span>
                      <span class="radar-score">{{ item.score }}</span>
                    </div>
                    <el-progress :percentage="item.score" :stroke-width="10" :show-text="false" />
                  </div>
                </div>
              </div>
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
              <h3 class="question-label">职业动机与价值观适配（深度分析）</h3>
              <div class="mv-block">
                <div class="mv-row">
                  <div class="mv-title">动机侧重点（马斯洛）</div>
                  <div>
                    <el-tag
                      v-for="(item, index) in report.motivation_values.maslow_focus"
                      :key="'m' + index"
                      type="info"
                      effect="plain"
                      round
                      class="mr-2 mb-2"
                    >
                      {{ item }}
                    </el-tag>
                  </div>
                </div>

                <div class="mv-row">
                  <div class="mv-title">动机总结</div>
                  <p class="mv-text">{{ report.motivation_values.motivation_summary }}</p>
                </div>

                <div class="mv-row">
                  <div class="mv-title">理想环境</div>
                  <ul>
                    <li v-for="(item, index) in report.motivation_values.ideal_environment" :key="'ie' + index">{{ item }}</li>
                  </ul>
                </div>

                <div class="mv-row">
                  <div class="mv-title">风险预警</div>
                  <ul>
                    <li v-for="(item, index) in report.motivation_values.risk_warnings" :key="'rw' + index">{{ item }}</li>
                  </ul>
                </div>
              </div>
            </el-card>

            <el-card class="mt-4" shadow="never" style="border-radius: 24px; padding: 20px;">
              <h3 class="question-label">总结与建议</h3>
              <p style="line-height: 1.6; color: #2c3e50;">{{ report.summary }}</p>
            </el-card>
          </div>
        </div>
      </div>

      <!-- 操作按钮（不导出到PDF） -->
      <div v-if="!loading" class="form-actions">
        <el-button
          class="export-btn"
          type="success"
          round
          :loading="exporting"
          @click="exportPdf"
        >
          导出 PDF
        </el-button>
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
</template>


<script setup lang="ts">
import { computed, nextTick, ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getReport } from "../api/Character_test_report"
import { ElLoading } from 'element-plus'
import html2canvas from 'html2canvas'
import { jsPDF } from 'jspdf'

let loadingInstance: any = null

interface ReportSchema {
  total: number
  personality_type: string
  career_preferences: string[]
  strengths: string[]
  weaknesses: string[]
  summary: string

  competency_radar: { name: string; score: number }[]
  motivation_values: {
    maslow_focus: string[]
    motivation_summary: string
    ideal_environment: string[]
    risk_warnings: string[]
  }
}

const loading = ref(true)
const exporting = ref(false)
const pdfRef = ref<HTMLElement | null>(null)
const report = ref<ReportSchema>({
  total: 0,
  personality_type: '',
  career_preferences: [],
  strengths: [],
  weaknesses: [],
  summary: '',
  competency_radar: [],
  motivation_values: {
    maslow_focus: [],
    motivation_summary: '',
    ideal_environment: [],
    risk_warnings: []
  }
})

// ===== 雷达图（SVG） =====
const radarSize = 320
const center = 160
const radius = 115

const radarItems = computed(() => {
  const items = report.value.competency_radar || []
  // 保证长度为5
  const padded = [...items]
  while (padded.length < 5) padded.push({ name: '', score: 0 })
  return padded.slice(0, 5).map((x) => ({ ...x, score: Math.max(0, Math.min(100, Number(x.score) || 0)) }))
})

const axes = computed(() => {
  // 5个维度，起始角 -90°（正上方）
  const pts: { x: number; y: number }[] = []
  for (let i = 0; i < 5; i++) {
    const angle = (-90 + (360 / 5) * i) * (Math.PI / 180)
    pts.push({
      x: center + radius * Math.cos(angle),
      y: center + radius * Math.sin(angle),
    })
  }
  return pts
})

function gridPoints(scale: number) {
  const pts: string[] = []
  for (let i = 0; i < 5; i++) {
    const angle = (-90 + (360 / 5) * i) * (Math.PI / 180)
    const r = radius * scale
    const x = center + r * Math.cos(angle)
    const y = center + r * Math.sin(angle)
    pts.push(`${x},${y}`)
  }
  return pts.join(' ')
}

const dataPolygonPoints = computed(() => {
  const pts: string[] = []
  for (let i = 0; i < 5; i++) {
    const score = radarItems.value[i]?.score ?? 0
    const scale = score / 100
    const angle = (-90 + (360 / 5) * i) * (Math.PI / 180)
    const r = radius * scale
    const x = center + r * Math.cos(angle)
    const y = center + r * Math.sin(angle)
    pts.push(`${x},${y}`)
  }
  return pts.join(' ')
})

function labelPos(a: { x: number; y: number }) {
  // 在轴末端外侧一点点
  const dx = a.x - center
  const dy = a.y - center
  const len = Math.sqrt(dx * dx + dy * dy) || 1
  const pad = 18
  return { x: a.x + (dx / len) * pad, y: a.y + (dy / len) * pad }
}

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
      duration: 10000
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

const exportPdf = async () => {
  if (!pdfRef.value) return
  if (exporting.value) return

  exporting.value = true
  try {
    // 导出时应用更适合PDF的样式
    pdfRef.value.classList.add('pdf-export')
    await nextTick()

    // 让截图更清晰（整页截图，保持“上一版”的整体观感）
    const canvas = await html2canvas(pdfRef.value, {
      scale: 2,
      useCORS: true,
      backgroundColor: '#ffffff',
      logging: false,
      // 避免页面滚动导致的偏移问题
      scrollX: 0,
      scrollY: -window.scrollY,
    })

    const pdf = new jsPDF({ orientation: 'p', unit: 'mm', format: 'a4' })
    const pageWidth = pdf.internal.pageSize.getWidth()
    const pageHeight = pdf.internal.pageSize.getHeight()
    const margin = 10
    const contentWidth = pageWidth - margin * 2
    const contentHeight = pageHeight - margin * 2

    // 分页：整页长图按 A4 内容高度切片，分页稳定
    const pageHeightPx = Math.floor((canvas.width * contentHeight) / contentWidth)
    let yPx = 0
    let pageIndex = 0
    while (yPx < canvas.height) {
      const sliceHeightPx = Math.min(pageHeightPx, canvas.height - yPx)
      const pageCanvas = document.createElement('canvas')
      pageCanvas.width = canvas.width
      pageCanvas.height = sliceHeightPx
      const ctx = pageCanvas.getContext('2d')
      if (!ctx) break

      ctx.drawImage(canvas, 0, yPx, canvas.width, sliceHeightPx, 0, 0, canvas.width, sliceHeightPx)
      const imgData = pageCanvas.toDataURL('image/png', 1.0)
      const sliceHeightMm = (sliceHeightPx * contentWidth) / canvas.width

      if (pageIndex > 0) pdf.addPage()
      pdf.addImage(imgData, 'PNG', margin, margin, contentWidth, sliceHeightMm, undefined, 'FAST')

      yPx += sliceHeightPx
      pageIndex += 1
    }

    const pt = (report.value.personality_type || 'report').replace(/[^a-zA-Z0-9_-]+/g, '_')
    const date = new Date()
    const dateStr = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
    pdf.save(`职业性格测试报告_${pt}_${dateStr}.pdf`)
  } catch (e) {
    ElMessage.error({ message: '导出 PDF 失败，请重试', duration: 6000 })
  } finally {
    pdfRef.value?.classList.remove('pdf-export')
    exporting.value = false
  }
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

/* 雷达图布局 */
.radar-wrap {
  display: flex;
  gap: 20px;
  align-items: stretch;
  flex-wrap: wrap;
}

.radar-svg {
  flex: 0 0 auto;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 18px;
  padding: 10px;
}

.radar-grid {
  fill: none;
  stroke: rgba(47, 124, 110, 0.18);
  stroke-width: 1;
}

.radar-axis {
  stroke: rgba(47, 124, 110, 0.18);
  stroke-width: 1;
}

.radar-area {
  fill: rgba(66, 185, 131, 0.20);
  stroke: none;
}

.radar-line {
  fill: none;
  stroke: rgba(66, 185, 131, 0.9);
  stroke-width: 2;
}

.radar-label {
  font-size: 12px;
  fill: #2c3e50;
}

.radar-legend {
  flex: 1 1 260px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  min-width: 240px;
}

.radar-legend-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.radar-legend-title {
  display: flex;
  align-items: center;
  gap: 8px;
  justify-content: space-between;
  color: #2c3e50;
  font-weight: 600;
}

.radar-dot {
  width: 10px;
  height: 10px;
  border-radius: 999px;
  background: rgba(66, 185, 131, 0.9);
  display: inline-block;
}

.radar-score {
  color: #2f7c6e;
  font-weight: 700;
}

/* 动机模块 */
.mv-block {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.mv-row {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.mv-title {
  font-weight: 700;
  color: #2c3e50;
}

.mv-text {
  line-height: 1.7;
  color: #2c3e50;
  margin: 0;
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

.export-btn {
  border: none;
  min-width: 160px;
  border-radius: 50px;
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

/* =========================
   PDF 导出优化样式（仅导出时生效）
   通过给导出区域容器加 .pdf-export 类触发
   ========================= */
.pdf-export {
  font-family: "Microsoft YaHei", "PingFang SC", "Noto Sans SC", Arial, sans-serif;
  color: #1f2d3d;
}

.pdf-export .survey-card,
.pdf-export .el-card {
  background: #ffffff !important;
  box-shadow: none !important;
  border: 1px solid rgba(47, 124, 110, 0.12) !important;
  border-radius: 16px !important;
  padding: 16px !important;
  margin-bottom: 14px !important;
}

.pdf-export .page-title {
  font-size: 26px !important;
  margin-bottom: 8px !important;
}

.pdf-export .page-subtitle {
  margin-top: 0 !important;
}

.pdf-export .radar-wrap {
  /* PDF 内避免横向挤压导致截断：改为纵向排列 */
  flex-direction: column !important;
  flex-wrap: nowrap !important;
}

.pdf-export .radar-svg {
  background: #ffffff !important;
  padding: 8px !important;
  border: 1px solid rgba(47, 124, 110, 0.12) !important;
}

.pdf-export .radar-legend {
  min-width: 100% !important;
}

.pdf-export .el-tag {
  border-radius: 999px !important;
  font-weight: 600 !important;
  /* 强制在截图中可见：给足对比度 */
  background: rgba(66, 185, 131, 0.12) !important;
  border-color: rgba(66, 185, 131, 0.45) !important;
  color: #2f7c6e !important;
}

/* info 标签（马斯洛动机）在 plain 模式下常常太淡，这里再加深一点 */
.pdf-export .el-tag.el-tag--info {
  background: rgba(96, 98, 102, 0.10) !important;
  border-color: rgba(96, 98, 102, 0.35) !important;
  color: #303133 !important;
}

.pdf-export .el-tag.el-tag--success {
  background: rgba(66, 185, 131, 0.12) !important;
  border-color: rgba(66, 185, 131, 0.45) !important;
  color: #2f7c6e !important;
}

.pdf-export ul {
  margin: 6px 0 0 0 !important;
}

/* PDF 导出时把“双列卡片”改成单列，减少被分页切开的概率 */
.pdf-export .grid {
  flex-direction: column !important;
}
</style>