<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
// 保持原来的 API 引用路径
import { loginApi, registerApi } from '../api/user'

// === 新增：引入 Element Plus 图标 ===
import { User, Lock, Message, ArrowRight } from '@element-plus/icons-vue'
// === 新增：引入类型定义，防止 TS 报错 ===
import type { InputInstance } from 'element-plus'

const router = useRouter()

// === 状态定义 (保持不变) ===
const username = ref('')
const password = ref('')
const email = ref('') 
const errorMessage = ref('')

// 【修改点】类型改为 InputInstance 以匹配 Element Plus 组件
const usernameInputRef = ref<InputInstance | null>(null)

const isRegisterMode = ref(false)

const buttonText = computed(() => isRegisterMode.value ? '立即注册' : '登录系统')

// === 页面加载时的焦点修复逻辑 (保持不变) ===
onMounted(() => {
  nextTick(() => {
    window.focus()
    if (document.activeElement instanceof HTMLElement) {
      document.activeElement.blur()
    }
    // Element Plus 的 focus 方法调用方式是一样的
    if (usernameInputRef.value) {
      usernameInputRef.value.focus()
    }
  })
})

// === 切换模式逻辑 (保持不变) ===
const toggleMode = () => {
  isRegisterMode.value = !isRegisterMode.value
  errorMessage.value = '' 
  
  nextTick(() => {
    if (usernameInputRef.value) {
      usernameInputRef.value.focus()
    }
  })
}

// === 核心提交逻辑 (保持不变) ===
const handleSubmit = async () => {
  errorMessage.value = ''

  if (!username.value || !password.value) {
    errorMessage.value = '用户名和密码不能为空'
    return
  }
  if (isRegisterMode.value && !email.value) {
    errorMessage.value = '注册需要填写邮箱'
    return
  }

  try {
    if (isRegisterMode.value) {
      // 注册逻辑
      const res: any = await registerApi({
        username: username.value,
        password: password.value,
        email: email.value
      })

      if (res && (res.code === 200 || res.id)) {
        isRegisterMode.value = false 
        password.value = '' 
        errorMessage.value = '注册成功！请直接登录'
        
        nextTick(() => {
          if (usernameInputRef.value) {
            usernameInputRef.value.focus()
          }
        })
      } else {
        errorMessage.value = res.message || '注册失败，用户名或邮箱可能已存在'
      }

    } else {
      // 登录逻辑
      const res = await loginApi({
        username: username.value,
        password: password.value
      })

      if (res.code === 200) {
        console.log('登录成功:', res)
        const token = (res as any).token || (res.data && res.data.token)

        if (token) {
          localStorage.removeItem('token')
          localStorage.setItem('token', token)
        } 
        router.push({ name: 'Home' })
      } else {
        errorMessage.value = res.message || '用户名或密码错误'
      }
    }

  } catch (error: any) {
    console.error('请求出错:', error)
    const actionName = isRegisterMode.value ? '注册' : '登录'
    if (error.response && error.response.data && error.response.data.detail) {
        errorMessage.value = error.response.data.detail
    } else {
        errorMessage.value = `${actionName}失败，请检查网络或联系管理员`
    }
  }
}
</script>

<template>
  <div class="login-bg">
    <div class="login-container">
      <el-card class="login-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <!-- 动态标题 -->
            <h2>{{ isRegisterMode ? '创建新账户' : 'AI 面试官系统' }}</h2>
            <p class="subtitle">{{ isRegisterMode ? '请填写信息完成注册' : '欢迎回来，请登录' }}</p>
          </div>
        </template>

        <div class="form-content">
          <!-- 用户名 -->
          <el-input
            ref="usernameInputRef"
            v-model="username"
            placeholder="请输入用户名"
            size="large"
            :prefix-icon="User"
            clearable
          />

          <!-- 邮箱 (带折叠动画) -->
          <transition name="el-zoom-in-top">
            <div v-if="isRegisterMode" class="input-wrapper">
              <el-input
                v-model="email"
                type="email"
                placeholder="请输入邮箱"
                size="large"
                :prefix-icon="Message"
                clearable
              />
            </div>
          </transition>

          <!-- 密码 -->
          <el-input
            v-model="password"
            type="password"
            placeholder="请输入密码"
            size="large"
            :prefix-icon="Lock"
            show-password
            @keyup.enter="handleSubmit"
          />

          <!-- 错误提示 -->
          <div class="error-area">
             <el-alert
                v-if="errorMessage"
                :title="errorMessage"
                type="error"
                show-icon
                :closable="false"
              />
          </div>

          <!-- 提交按钮 -->
          <el-button 
            type="primary" 
            size="large" 
            class="submit-btn" 
            @click="handleSubmit" 
            round
          >
            {{ buttonText }}
            <el-icon class="el-icon--right"><ArrowRight /></el-icon>
          </el-button>

          <!-- 切换模式 -->
          <div class="toggle-box">
            <span class="toggle-text" @click="toggleMode">
              {{ isRegisterMode ? '已有账号？去登录' : '没有账号？立即注册' }}
            </span>
          </div>
        </div>
      </el-card>
      
      <div class="footer-copyright">
        &copy; 2024 AI Interviewer. All rights reserved.
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 全屏背景：蓝紫渐变 */
.login-bg {
  width: 100vw;
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: hidden;
  margin: 0;
  padding: 0;
}

.login-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
}

/* 登录卡片 */
.login-card {
  width: 400px;
  border-radius: 16px;
  background-color: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border: none;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15) !important;
}

.card-header {
  text-align: center;
  padding: 10px 0 0 0;
}

.card-header h2 {
  margin: 0;
  color: #303133;
  font-size: 24px;
  font-weight: 600;
}

.subtitle {
  margin-top: 10px;
  margin-bottom: 0;
  color: #909399;
  font-size: 14px;
}

.form-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 10px 20px 20px;
}

.input-wrapper {
  width: 100%;
}

.error-area {
  min-height: 40px; /* 预留高度防止跳动 */
  display: flex;
  align-items: center;
}

.submit-btn {
  width: 100%;
  font-weight: bold;
  letter-spacing: 2px;
  background: linear-gradient(to right, #667eea, #764ba2); /* 按钮也用渐变色 */
  border: none;
  transition: transform 0.1s, opacity 0.3s;
}

.submit-btn:hover {
  opacity: 0.9;
  background: linear-gradient(to right, #667eea, #764ba2);
}

.submit-btn:active {
  transform: scale(0.98);
}

.toggle-box {
  text-align: center; /* 居中更好看 */
  margin-top: 5px;
}

.toggle-text {
  color: #606266;
  font-size: 14px;
  cursor: pointer;
  transition: color 0.3s;
}

.toggle-text:hover {
  color: #764ba2;
  text-decoration: underline;
}

.footer-copyright {
  margin-top: 25px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 12px;
}

/* 移动端适配 */
@media (max-width: 480px) {
  .login-card {
    width: 90%;
  }
}
</style>