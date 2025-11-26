<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const goBack = () => {
    router.go(-1) // 返回上一页Home
}
</script>

<template>
    <header class="top-bar">
    <div class="back-wrapper" @click="goBack">
      <i class="arrow"></i>
      返回上一页
    </div>
    <div class="title">个人中心</div>
  </header>
  <div class="account-page">
    <!-- 左侧导航 -->
    <aside class="sidebar">
      <div class="menu-item active">账号信息</div>
      <!-- <div class="menu-item">软件设置</div> -->
      <div class="menu-item">帮助中心</div>
      <div class="menu-item">关于我们</div>
    </aside>

    <!-- 右侧主体 -->
    <main class="content">
      <div class="user-section">
        <div class="user-header">
            <img src="../img/log.png" alt = 'logo'class="avatar" >
            <span class="username">Username</span>
        </div>
        <!-- <img class="avatar" src="/duck.png" alt="avatar" /> -->
      </div>

      <!-- 账号信息 -->
      <div class="info-card">
        <div class="info-row">
          <div class="label">手机号</div>
          <div class="value">18355012816</div>
        </div>

        <div class="info-row">
          <div class="label">邮箱</div>
          <div class="value gray">暂不支持</div>
        </div>

        <el-button type="danger" class="logout-btn">退出登录</el-button>
      </div>
    </main>
  </div>
</template>


<style scoped>

/* 顶栏 */
.top-bar {
  position: relative;
  height: 52px;
  display: flex;
  align-items: center;
  background: rgba(245, 246, 247, 0.85); 
  backdrop-filter: saturate(180%) blur(20px);
  padding: 0 20px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.08); 
}

.back-wrapper {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 15px;
  color: #3a3a3c;
  cursor: pointer;
  padding: 6px 12px;
  border-radius: 8px;
  transition: 0.2s;
}

.back-wrapper:hover {
  background: rgba(0,0,0,0.06); /* mac 的浅 hover 效果 */
}

.title {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  font-size: 17px;
  font-weight: 600;
  color: #1c1c1e; 
}

.arrow {
  width: 10px;
  height: 10px;
  border-left: 2px solid #555;
  border-bottom: 2px solid #555;
  transform: rotate(45deg);
  margin-top: -1px;
}

/* 整体布局背景 */
.account-page {
  display: flex;
  height: 100vh;
  background: #F5F5F7; /* macOS 系统偏白浅灰 */
  font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", sans-serif;
}

/* 左侧导航栏 */
.sidebar {
  width: 200px;
  padding-top: 40px;
  border-right: 1px solid rgba(0,0,0,0.06);
  background: #F9F9FB;
}

.menu-item {
  padding: 15px 25px;
  font-size: 15px;
  color: #444;
  cursor: pointer;
  border-radius: 12px;
  margin: 6px 10px;
  transition: 0.2s;
}

.menu-item:hover {
  background: rgba(0,0,0,0.05);
}

.menu-item.active {
  background: white;
  box-shadow: 0 2px 6px rgba(0,0,0,0.05);
  font-weight: 500;
  color: #111;
}

/* 右侧内容区 */
.content {
  flex: 1;
  padding: 40px;
}

.user-section {
  text-align: center;
  margin-bottom: 40px;
}

.user-header {
  display: flex;
  align-items: center;
  flex-direction: column;
  justify-content: center;
  margin-top: 10px;
}

.avatar {
  width: 70px;
  height: 70px;
  border-radius: 50%;
  object-fit: cover;
  border: 1px solid rgba(0,0,0,0.08);
  box-shadow: 0 4px 10px rgba(0,0,0,0.08); /* mac 风格阴影 */
  background: white;
}

.username {
  margin-top: 12px;
  font-size: 18px;
  font-weight: 500;
  color: #1c1c1e;
}

/* 信息卡片整体风格 */
.info-card {
  background: white;
  padding: 32px;
  border-radius: 18px;  /* mac 风格偏大圆角 */
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.06);
  max-width: 520px;
  margin: 0 auto;
}

.info-row {
  display: flex;
  justify-content: space-between;
  padding: 16px 0;
  border-bottom: 1px solid rgba(0,0,0,0.06);
}

.info-row:last-child {
  border-bottom: none;
}

.label {
  font-size: 15px;
  color: #3a3a3c;
}

.value {
  font-size: 15px;
  color: #1c1c1e;
}

.value.gray {
  color: #8e8e93;
}

/* 按钮样式（更 mac） */
.logout-btn {
  margin-top: 30px;
  width: 100%;
  border-radius: 10px !important;
  font-size: 15px;
  padding: 12px 0;
}
</style>