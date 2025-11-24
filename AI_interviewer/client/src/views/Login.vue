<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
// 1. 引入我们在 api 文件夹定义的接口函数
import { loginApi } from '../api/user'

const router = useRouter()

const username = ref('')
const password = ref('')
const errorMessage = ref('')

const handleLogin = async () => {
  // 清空错误并校验
  errorMessage.value = ''
  if (!username.value || !password.value) {
    errorMessage.value = '用户名和密码不能为空'
    return
  }

  try {
    // 2. 调用封装好的接口
    // 注意：因为响应拦截器已经解构了 response.data，这里拿到的 res 直接就是后端返回的 JSON 对象
    const res = await loginApi({
      username: username.value,
      password: password.value
    })

    // 3. 判断业务状态码 (根据你提供的逻辑是 code === 200)
    if (res.code === 200) {
      console.log('登录成功:', res)

      // =========== 关键步骤：保存 Token ===========
      // 假设后端返回结构是 { code: 200, data: { token: "..." } }
      // 请务必确认 res.data.token 是否存在，这取决于你后端的实际返回结构
      if (res.data && res.data.token) {
        localStorage.setItem('token', res.data.token)
      } else {
        // 如果后端没返回 token，这里可能需要根据实际情况调整
        console.warn('注意：后端未返回 token 字段')
      }
      // ==========================================

      router.push({ name: 'Home' })
    } else {
      // 业务错误（如密码不对）
      errorMessage.value = res.message || '用户名或密码错误'
    }

  } catch (error: any) {
    console.error('请求逻辑出错:', error)
    // 这里的 error 可能是网络超时，或者后端返回 4xx/5xx 状态码
    errorMessage.value = '登录失败，请检查网络或联系管理员'
  }
}
</script>

<template>
  <div class="login-container">
    <h1>欢迎登录</h1>

    <div class="input-group">
      <!-- 添加 .trim 修饰符，防止用户不小心输入空格 -->
      <input 
        v-model.trim="username" 
        type="text" 
        placeholder="请输入用户名 (admin)" 
        @keyup.enter="handleLogin"
      />
      <input 
        v-model.trim="password" 
        type="password" 
        placeholder="请输入密码 (123456)" 
        @keyup.enter="handleLogin"
      />
    </div>

    <p v-if="errorMessage" class="error-msg">{{ errorMessage }}</p>

    <button @click="handleLogin">登录系统</button>
  </div>
</template>

<style scoped>
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
</style>