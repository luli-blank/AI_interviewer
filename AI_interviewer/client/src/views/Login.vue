<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
// 1. 引入 loginApi 和 新增的 registerApi
import { loginApi, registerApi } from '../api/user'

const router = useRouter()

// === 状态定义 ===
const username = ref('')
const password = ref('')
const email = ref('') // 新增：注册需要的邮箱
const errorMessage = ref('')

// 【修改点 1】定义输入框的引用，用于代码强制聚焦
const usernameInputRef = ref<HTMLInputElement | null>(null)

// 新增：控制当前是“登录模式”还是“注册模式”
const isRegisterMode = ref(false)

// 计算属性：动态显示按钮文字
const buttonText = computed(() => isRegisterMode.value ? '立即注册' : '登录系统')

// 【修改点 2】页面加载时的焦点修复逻辑 (解决 Electron 输入框卡顿)
onMounted(() => {
  nextTick(() => {
    // 1. 强制当前窗口获取焦点
    window.focus()
    // 2. 清除可能残留的焦点
    if (document.activeElement instanceof HTMLElement) {
      document.activeElement.blur()
    }
    // 3. 聚焦到用户名输入框
    if (usernameInputRef.value) {
      usernameInputRef.value.focus()
    }
  })
})

// === 切换模式逻辑 ===
const toggleMode = () => {
  isRegisterMode.value = !isRegisterMode.value
  errorMessage.value = '' // 切换时清空错误提示
  
  // 切换模式后，也自动聚焦输入框，提升体验
  nextTick(() => {
    if (usernameInputRef.value) {
      usernameInputRef.value.focus()
    }
  })
}

// === 核心提交逻辑 ===
const handleSubmit = async () => {
  // 1. 清空错误
  errorMessage.value = ''

  // 2. 基础非空校验
  if (!username.value || !password.value) {
    errorMessage.value = '用户名和密码不能为空'
    return
  }
  // 如果是注册模式，额外校验邮箱
  if (isRegisterMode.value && !email.value) {
    errorMessage.value = '注册需要填写邮箱'
    return
  }

  try {
    if (isRegisterMode.value) {
      // ================= 注册逻辑 =================
      const res: any = await registerApi({
        username: username.value,
        password: password.value,
        email: email.value
      })

      // 假设后端成功返回了用户对象或 code=200
      if (res && (res.code === 200 || res.id)) {
        // 【修改点 3】删除了 alert('注册成功...')
        // 原生 alert 会导致 Electron 窗口焦点丢失，导致输入框无法选中
        
        // 这里的策略是：直接切回登录模式，用户自然知道成功了
        // 如果需要提示，建议使用 ElMessage 或 errorMessage.value = '注册成功，请登录'
        
        isRegisterMode.value = false 
        password.value = '' 

        errorMessage.value = '注册成功！请直接登录'
        
        // 注册成功切回登录页后，强制聚焦输入框
        nextTick(() => {
          if (usernameInputRef.value) {
            usernameInputRef.value.focus()
          }
        })
      } else {
        errorMessage.value = res.message || '注册失败，用户名或邮箱可能已存在'
      }

    } else {
      // ================= 登录逻辑 (保持原样) =================
      const res = await loginApi({
        username: username.value,
        password: password.value
      })

      if (res.code === 200) {
        console.log('登录成功:', res)
        
        // 适配后端结构
        const token = (res as any).token || (res.data && res.data.token)

        if (token) {
          localStorage.removeItem('token')
          localStorage.setItem('token', token)
        } else {
          console.warn('注意：后端虽然返回200，但没有携带Token')
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
  <div class="login-container">
    <!-- 标题根据模式变化 -->
    <h1>{{ isRegisterMode ? '用户注册' : '欢迎登录' }}</h1>

    <div class="input-group">
      <input 
        v-model.trim="username" 
        type="text" 
        placeholder="请输入用户名" 
        autocomplete="off" 
      />

      <!-- 只有在注册模式下才显示邮箱输入框 -->
      <input 
        v-if="isRegisterMode"
        v-model.trim="email" 
        type="email" 
        placeholder="请输入邮箱 (example@qq.com)" 
        autocomplete="off" 
      />

      <input 
        v-model.trim="password" 
        type="password" 
        placeholder="请输入密码" 
        @keyup.enter="handleSubmit"
        autocomplete="off" 
      />
    </div>

    <p v-if="errorMessage" class="error-msg">{{ errorMessage }}</p>

    <!-- 按钮点击触发 handleSubmit -->
    <button @click="handleSubmit">{{ buttonText }}</button>

    <!-- 切换模式的文字链接 -->
    <div class="toggle-box">
      <span class="toggle-text" @click="toggleMode">
        {{ isRegisterMode ? '已有账号？去登录' : '没有账号？去注册' }}
      </span>
    </div>
  </div>
</template>

<style scoped>
/* 保持原有样式不变，只新增了 .toggle-box 相关样式 */
.login-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  width: 100vw;
  height: 100vh;
  background-color: #f0f2f5;
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

h1 {
  margin-bottom: 30px;
  color: #333;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-bottom: 20px;
  /* 增加高度过渡效果，让邮箱框出来时更丝滑 */
  transition: all 0.3s;
}

input {
  width: 250px;
  padding: 12px;
  border: 1px solid #ccc;
  border-radius: 4px;
  outline: none;
  font-size: 14px;
}

input:focus {
  border-color: #409eff;
}

.error-msg {
  color: red;
  font-size: 14px;
  margin-bottom: 15px;
  height: 20px;
}

button {
  width: 276px;
  padding: 12px;
  font-size: 16px;
  background-color: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.3s;
}

button:hover {
  background-color: #66b1ff;
}

/* === 新增样式 === */
.toggle-box {
  margin-top: 15px;
  text-align: right;
  width: 276px; /* 和按钮宽度一致 */
}

.toggle-text {
  color: #666;
  font-size: 14px;
  cursor: pointer;
  user-select: none; /* 防止双击选中文字 */
}

.toggle-text:hover {
  color: #409eff;
  text-decoration: underline;
}
</style>