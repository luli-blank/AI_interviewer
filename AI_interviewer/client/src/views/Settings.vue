<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  Bell, 
  Monitor 
} from '@element-plus/icons-vue'

// 当前激活的 Tab
const activeTab = ref('preference')

// 模拟表单数据
const form = reactive({
  notifications: {
    email: true,
    browser: false,
    marketing: false
  },
  theme: 'light',
  language: 'zh-CN'
})

// 保存设置
const handleSave = () => {
  ElMessage.success({
    message: '设置已保存成功！',
    type: 'success',
  })
}
</script>

<template>
  <div class="page-container">
    
    <!-- 1. 动态背景 -->
    <div class="bg-shape shape-green"></div>
    <div class="bg-shape shape-orange"></div>

    <!-- 2. 主内容区 -->
    <div class="settings-wrapper animate-in">

      <!-- 设置卡片容器 -->
      <div class="settings-card glass-panel animate-in" style="animation-delay: 0.1s">
        
        <el-tabs 
          v-model="activeTab" 
          tab-position="left" 
          class="custom-tabs"
        >
          
          <!-- === Tab 1: 偏好设置 === -->
          <el-tab-pane name="preference">
            <template #label>
              <div class="tab-label">
                <el-icon><Monitor /></el-icon> <span>偏好设置</span>
              </div>
            </template>

            <div class="pane-content">
              <h3 class="pane-title">外观与语言</h3>
              
              <div class="setting-item">
                <div class="info">
                  <div class="label">界面主题</div>
                  <div class="desc">选择你喜欢的界面风格</div>
                </div>
                <el-radio-group v-model="form.theme" class="theme-radio">
                  <el-radio-button label="light">浅色模式</el-radio-button>
                  <el-radio-button label="dark">深色模式</el-radio-button>
                  <el-radio-button label="auto">跟随系统</el-radio-button>
                </el-radio-group>
              </div>

              <div class="divider"></div>

              <div class="setting-item">
                <div class="info">
                  <div class="label">系统语言</div>
                  <div class="desc">切换平台的显示语言</div>
                </div>
                <el-select v-model="form.language" style="width: 140px;">
                  <el-option label="简体中文" value="zh-CN" />
                  <el-option label="English" value="en-US" />
                </el-select>
              </div>

              <div class="form-footer" style="margin-top: 40px;">
                <el-button type="primary" class="save-btn" round @click="handleSave">应用设置</el-button>
              </div>
            </div>
          </el-tab-pane>

          <!-- === Tab 2: 通知管理 === -->
          <el-tab-pane name="notification">
            <template #label>
              <div class="tab-label">
                <el-icon><Bell /></el-icon> <span>通知管理</span>
              </div>
            </template>

            <div class="pane-content">
              <h3 class="pane-title">消息推送</h3>
              
              <div class="switch-row">
                <div class="switch-info">
                  <div class="s-title">邮件通知</div>
                  <div class="s-desc">当有新的面试邀请或报告生成时发送邮件</div>
                </div>
                <el-switch v-model="form.notifications.email" active-color="#3a856b" />
              </div>

              <div class="switch-row">
                <div class="switch-info">
                  <div class="s-title">浏览器推送</div>
                  <div class="s-desc">在浏览器右下角显示实时消息提醒</div>
                </div>
                <el-switch v-model="form.notifications.browser" active-color="#3a856b" />
              </div>

              <div class="switch-row">
                <div class="switch-info">
                  <div class="s-title">营销与活动</div>
                  <div class="s-desc">接收产品更新、优惠活动等相关信息</div>
                </div>
                <el-switch v-model="form.notifications.marketing" active-color="#3a856b" />
              </div>

              <div class="form-footer" style="margin-top: 40px;">
                <el-button type="primary" class="save-btn" round @click="handleSave">保存偏好</el-button>
              </div>
            </div>
          </el-tab-pane>

        </el-tabs>
      </div>
    </div>

  </div>
</template>

<style scoped>
/* === 全局基础配置 === */
.page-container {
  position: relative;
  width: 100%;
  min-height: 100%;
  display: flex;
  justify-content: center;
  padding: 40px 20px;
  background: linear-gradient(135deg, #f5fcf9 0%, #ffffff 100%);
  overflow: hidden;
  box-sizing: border-box;
  align-items: center; /* 垂直居中 */
}

/* === 背景动画 === */
.bg-shape {
  position: absolute;
  border-radius: 50%;
  z-index: 0;
  opacity: 0.5;
  will-change: transform;
  animation: floatAnimation 12s infinite ease-in-out alternate;
}
.shape-green {
  width: 600px; height: 600px;
  background: radial-gradient(circle, rgba(58,133,107,0.15) 0%, rgba(58,133,107,0) 70%);
  top: -200px; left: -100px;
}
.shape-orange {
  width: 500px; height: 500px;
  background: radial-gradient(circle, rgba(243,209,158,0.15) 0%, rgba(243,209,158,0) 70%);
  bottom: -150px; right: -100px;
  animation-delay: -5s;
}
@keyframes floatAnimation {
  0% { transform: translate3d(0, 0, 0); }
  100% { transform: translate3d(20px, 40px, 0); }
}

/* === 主容器 === */
.settings-wrapper {
  z-index: 1;
  width: 100%;
  max-width: 1200px; /* 较宽的布局 */
  display: flex;
  flex-direction: column;
}

/* === 玻璃卡片容器 === */
.settings-card {
  background: rgba(255, 255, 255, 0.92);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.9);
  box-shadow: 0 10px 40px rgba(58, 133, 107, 0.05);
  overflow: hidden;
  min-height: 800px; /* 较高的卡片 */

  transform: translateZ(0);
  will-change: transform; 
}

/* === Element Tabs 定制 === */
.custom-tabs {
  height: 100%;
  min-height: 800px;
}

/* 侧边栏样式覆盖 */
:deep(.el-tabs__header) {
  margin-right: 0 !important;
  background-color: rgba(249, 250, 251, 0.6);
  border-right: 1px solid #eee;
  padding-top: 20px;
  width: 220px;
}

:deep(.el-tabs__item) {
  height: 56px;
  line-height: 56px;
  font-size: 15px;
  color: #606266;
  text-align: left;
  padding-left: 30px !important;
  justify-content: flex-start;
  transition: all 0.3s;
}

:deep(.el-tabs__item.is-active) {
  color: #3a856b;
  background-color: #e6f2ee;
  font-weight: 600;
  border-right: 3px solid #3a856b;
}

:deep(.el-tabs__item:hover) {
  color: #3a856b;
}

.tab-label {
  display: flex;
  align-items: center;
  gap: 10px;
}

/* === 右侧内容区 === */
:deep(.el-tabs__content) {
  padding: 40px 60px;
  color: #2c3e50;
}

.pane-title {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 30px;
  color: #2c3e50;
  border-left: 4px solid #3a856b;
  padding-left: 12px;
}

/* 保存按钮 */
.save-btn {
  width: 140px;
  height: 40px;
  background-color: #3a856b;
  border-color: #3a856b;
  font-weight: 500;
  letter-spacing: 1px;
}
.save-btn:hover {
  background-color: #2c6652;
  border-color: #2c6652;
}

/* 设置项通用样式 */
.setting-item, .switch-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}
.info .label, .s-title {
  font-size: 15px;
  font-weight: 500;
  color: #333;
  margin-bottom: 4px;
}
.info .desc, .s-desc {
  font-size: 13px;
  color: #909399;
}

/* 分割线 */
.divider {
  height: 1px;
  background: #f0f2f5;
  margin: 30px 0;
}

/* 主题切换 Radio */
:deep(.el-radio-button__inner) {
  border-radius: 0;
  padding: 10px 20px;
}
:deep(.el-radio-button:first-child .el-radio-button__inner) {
  border-radius: 8px 0 0 8px;
}
:deep(.el-radio-button:last-child .el-radio-button__inner) {
  border-radius: 0 8px 8px 0;
}
:deep(.el-radio-button__original-radio:checked + .el-radio-button__inner) {
  background-color: #3a856b;
  border-color: #3a856b;
  box-shadow: -1px 0 0 0 #3a856b;
}

/* 动画类 */
.animate-in {
  opacity: 0;
  animation: fadeSlideUp 0.8s cubic-bezier(0.22, 1, 0.36, 1) forwards;
}
@keyframes fadeSlideUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 响应式 */
@media (max-width: 768px) {
  :deep(.el-tabs__header) {
    width: 60px;
  }
  :deep(.el-tabs__item span) {
    display: none;
  }
  :deep(.el-tabs__content) {
    padding: 20px;
    transform: none !important;
  }
  :deep(.el-tab-pane) {
    /* 确保切换时没有淡入淡出的重叠计算 */
    animation: none !important;
    transition: none !important;
  }
}
</style>