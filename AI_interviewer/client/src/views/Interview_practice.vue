<script setup>
import { ref, computed } from "vue";
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()


const jobs = ref([
  {
    id: 1,
    title: "前端开发工程师",
    desc: "负责前端页面开发，熟悉 Vue、TypeScript。",
    interviewers: [
      { name: "李雷", title: "高级前端工程师", avatar: "/avatar1.png" },
      { name: "韩梅梅", title: "前端技术专家", avatar: "/avatar2.png" }
    ]
  },
  {
    id: 2,
    title: "后端开发工程师",
    desc: "负责后端接口开发，熟悉 FastAPI、Node.js。",
    interviewers: [
      { name: "张伟", title: "资深后端工程师", avatar: "/avatar3.png" }
    ]
  }
]);

const selectedJobId = ref(null);

const selectJob = (id) => {
  selectedJobId.value = id;
};

const currentJob = computed(() => {
  if (selectedJobId.value === "all") {
    return {
      title: "全部岗位",
      desc: "查看所有岗位的面试官",
      interviewers: jobs.value.flatMap(j => j.interviewers)
    }
  }
  return jobs.value.find(j => j.id === selectedJobId.value)
})

const goToInterview = (interviewer) => {
  router.push({
    name: 'Interview',  // Interview.vue 对应的路由 name
    query: { 
      name: interviewer.name, 
      title: interviewer.title 
    }
  })
}

</script>

<template>
  <div class="interview-container">
    <!-- 左侧岗位列表 -->
    <div class="job-list">
      <h2>选择岗位</h2>
        <div
      class="job-item"
      :class="{ active: selectedJobId === 'all' }"
      @click="selectJob('all')"
      >
      全部岗位
      </div>
      <div
        v-for="job in jobs"
        :key="job.id"
        class="job-item"
        :class="{ active: job.id === selectedJobId }"
        @click="selectJob(job.id)"
      >
        {{ job.title }}
      </div>
    </div>

    <!-- 右侧岗位详情 -->
    <div class="job-detail">
      <h2 v-if="currentJob">{{ currentJob.title }}</h2>
      <p v-if="currentJob">{{ currentJob.desc }}</p>

      <h3 v-if="currentJob">面试官</h3>

      <div class="interviewer-box">
        <div
          v-for="p in currentJob?.interviewers"
          :key="p.name"
          class="interviewer-card"
          @click="goToInterview(p)" 
        >
          <img :src="p.avatar" class="avatar" />
          <div class="info">
            <div class="name">{{ p.name }}</div>
            <div class="title">{{ p.title }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>


<style scoped>
.interview-container {
  display: flex;
  height: 100vh;
  background: #f4f6fa;
  font-family: "Segoe UI", Helvetica, Arial, sans-serif;
}

/* 左侧岗位列表 */
.job-list {
  width: 260px;
  background: #fff;
  border-right: 1px solid #e6e8eb;
  padding: 24px;
  box-shadow: 2px 0 6px rgba(0, 0, 0, 0.03);
  display: flex;
  flex-direction: column; /* 垂直排列岗位 */
  align-items: center;   
}
.job-item {
  width: 100%;            /* 占满列表宽度 */
  display: flex;
  justify-content: center; /* 水平居中文字 */
  align-items: center;     /* 垂直居中文字 */
  padding: 14px 0;         /* 上下内边距 */
  margin-bottom: 12px;
  background: #f8f9fb;
  cursor: pointer;
  border-radius: 8px;
  transition: all 0.2s ease;
  font-size: 15px;
  color: #1c1c1e;
  border: 1px solid transparent;
}

.job-list h2 {
  margin-bottom: 20px;
  font-size: 20px;
  font-weight: 600;
  color: #1f2937;
}

.job-item {
  padding: 14px 16px;
  margin-bottom: 12px;
  background: #f8f9fb; /* 浅灰背景 */
  cursor: pointer;
  border-radius: 8px;
  transition: all 0.2s ease;
  font-size: 15px;
  color: #1c1c1e; /* 深灰色字体，更清晰 */
  border: 1px solid transparent;
}

/* 悬浮状态 */
.job-item:hover {
  background: rgba(0, 122, 255, 0.08); 
  color: #1c1c1e;
}

/* 选中状态 */
.job-item.active {
  background: rgba(0, 122, 255, 0.2); 
  color: #007aff; 
  font-weight: 600;
  border-color: rgba(0, 122, 255, 0.4);
  box-shadow: 0 1px 4px rgba(0, 122, 255, 0.3); /* 微光效果 */
}

/* 支持平滑动画 */
.job-item,
.job-item.active,
.job-item:hover {
  transition: background 0.2s ease, color 0.2s ease, box-shadow 0.2s ease;
}

/* 右侧内容 */
.job-detail {
  flex: 1;
  padding: 40px;
  overflow-y: auto;
  color: #1f2937;
}

.job-detail h2 {
  font-size: 26px;
  font-weight: 600;
  color: #1f2937;
}

.job-detail h3 {
  margin-top: 30px;
  margin-bottom: 10px;
  color: #1f2937;
}

/* 面试官列表 */
.interviewer-box {
  display: flex;
  flex-wrap: wrap;
  gap: 28px;
  margin-top: 20px;
}

/* 面试官卡片 */
.interviewer-card {
  background: #fff;
  padding: 20px;
  border-radius: 14px;
  width: 220px;
  text-align: center;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.08);
  transition: transform 0.2s;
}

.interviewer-card:hover {
  transform: translateY(-4px);
}

.avatar {
  width: 90px;
  height: 90px;
  border-radius: 50%;
  object-fit: cover;
}

.name {
  font-size: 17px;
  margin-top: 12px;
  font-weight: 600;
}

.title {
  font-size: 14px;
  color: #666;
}

.empty {
  margin-top: 80px;
  font-size: 30px;
  text-align: center;
  color: #2f2e2e;
}
</style>
