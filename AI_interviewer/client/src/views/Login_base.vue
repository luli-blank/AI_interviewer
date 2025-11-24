<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const handleLogin = () => {
  // 这里写登录逻辑（比如请求后端接口）
  // 登录成功后，跳转到带有侧边栏的首页
  router.push('/MainLayout/home')
}
</script>

<template>
  <div class="login-container">
    <h1>欢迎登录</h1>
    <button @click="handleLogin">点击登录进入系统</button>
  </div>
</template>

<style scoped>
.login-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100vh;
  width: 100vw;  /* 视口宽度的 100% */
  background-color: #f0f2f5;
  margin: 0;
  padding: 0;
  box-sizing: border-box; 
}

button {
  margin-top: 20px;
  padding: 10px 20px;
  font-size: 16px;
  cursor: pointer;
}
</style>