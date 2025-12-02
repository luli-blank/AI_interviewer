<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { useRouter, useRoute } from 'vue-router'

const route = useRoute() 

// 面试累计时长
const totalTimer = ref('00:12:45');
let timerInterval = null;

const interviewerName = route.query.name
const interviewerTitle = route.query.title

// 自身控制
const isSelfMuted = ref(false); // 自身麦克风状态
const isSelfVideoOff = ref(false); // 自身摄像头状态

// 面试笔记
const interviewNotes = ref('');

// 页面加载启动累计计时
onMounted(() => {
  startTotalTimer();
});

// 页面卸载清除计时器
onUnmounted(() => {
  clearInterval(timerInterval);
});

// 累计计时逻辑（时:分:秒）
const startTotalTimer = () => {
  let time = 0;
  timerInterval = setInterval(() => {
    time++;
    const hours = Math.floor(time / 3600).toString().padStart(2, '0');
    const minutes = Math.floor((time % 3600) / 60).toString().padStart(2, '0');
    const seconds = (time % 60).toString().padStart(2, '0');
    totalTimer.value = `${hours}:${minutes}:${seconds}`;
  }, 1000);

  const isSubtitleOn = ref(true); // 字幕开关
const speed = ref(1); // 字幕滚动速度
const subtitleLines = ref([
  '你好，很高兴今天能和你进行这次面试。',
  '首先想了解一下，你为什么想要应聘产品经理这个岗位？',
  '可以具体说说你在校期间做过的相关产品项目吗？'
]); // 历史字幕
const currentSubtitle = ref(''); // 实时字幕
const subtitleContent = ref(null); // 字幕容器ref
let subtitleInterval = null; // 字幕生成定时器

// 页面加载时新增：启动字幕模拟
onMounted(() => {
  // ... 原有代码保留，新增以下
  if (isSubtitleOn.value) {
    startSubtitleSimulation();
  }
});

// 页面卸载时新增：清除字幕定时器
onUnmounted(() => {
  // ... 原有代码保留，新增以下
  clearInterval(subtitleInterval);
});

// 新增：字幕开关切换
const toggleSubtitle = () => {
  if (isSubtitleOn.value) {
    startSubtitleSimulation();
  } else {
    clearInterval(subtitleInterval);
    currentSubtitle.value = '';
  }
};

// 新增：模拟字幕实时生成
const startSubtitleSimulation = () => {
  clearInterval(subtitleInterval);
  // 根据速度计算间隔（默认1倍速=3秒/句，速度越快间隔越短）
  const interval = 3000 / speed.value;
  let scriptIndex = 0;
  
  subtitleInterval = setInterval(() => {
    // 将当前字幕加入历史，生成新的实时字幕
    if (currentSubtitle.value) {
      subtitleLines.value.push(currentSubtitle.value);
      // 只保留最近10条历史字幕，避免过长
      if (subtitleLines.value.length > 10) {
        subtitleLines.value.shift();
      }
    }
    // 循环取话术库内容
    currentSubtitle.value = interviewScript[scriptIndex % interviewScript.length];
    scriptIndex++;
    
    // 自动滚动到最新字幕
    if (subtitleContent.value) {
      subtitleContent.value.scrollTop = subtitleContent.value.scrollHeight;
    }
  }, interval);
};

};

// 自身麦克风切换
const toggleSelfMute = () => {
  isSelfMuted.value = !isSelfMuted.value;
};

// 自身摄像头切换
const toggleSelfVideo = () => {
  isSelfVideoOff.value = !isSelfVideoOff.value;
};


</script>

<template>
  <div class="interview-practice">
    <!-- 面试演练主区域 -->
    <div class="practice-container">
      <!-- 面试基础信息 -->
      <div class="practice-header">
        <div class="job-info">
          <h2>性格测试</h2>
          <p>面试状态: <span class="status-text">正在进行</span> · 累计时长: <span class="timer">{{ totalTimer }}</span></p>
        </div>
        <div class="status-tag">进行中</div>
      </div>

      <!-- 核心面试区域：面试官+实时交互 -->
      <div class="interview-main">
       
        <!-- 实时面试交互区 -->
        <div class="interview-interactive">
          <!-- 视频/语音交互区 -->
          <div class="video-area">
            <div class="interviewer-video">
              <img 
                src="https://via.placeholder.com/600x400?text=面试官视频画面" 
                alt="面试官视频" 
                v-if="!isVideoOff"
                class="video-frame"
              />
              <div class="video-off" v-else>
                <span class="video-off-text">面试官视频已关闭</span>
              </div>
            </div>
            <div class="self-video">
              <img 
                src="https://via.placeholder.com/200x150?text=你的视频画面" 
                alt="我的视频" 
                class="self-video-frame"
              />
            </div>
          </div>

          <!-- 面试交互控制 -->
          <div class="interactive-controls">
            <button class="interactive-btn" @click="toggleSelfMute">
              {{ isSelfMuted ? '取消麦克风' : '关闭麦克风' }}
            </button>
            <button class="interactive-btn" @click="toggleSelfVideo">
              {{ isSelfVideoOff ? '开启摄像头' : '关闭摄像头' }}
            </button>
            <button class="interactive-btn emergency">举手提问</button>
            <button class="interactive-btn emergency">结束面试</button>
          </div>
        </div>

         <!-- 面试官信息展示区 -->
        <div class="interviewer-panel">
          <div class="interviewer-avatar">
            <img src="../img/log.png" alt="面试官头像" />
          </div>
          <div class="interviewer-info">
            <h3>{{interviewerName}}</h3>
            <p class="position">{{interviewerTitle}}</p>
            <p class="specialty">擅长领域：校招面试、产品思维考察</p>
            <div class="interviewer-tags">
              <span class="tag">沟通能力</span>
              <span class="tag">逻辑思维</span>
              <span class="tag">产品认知</span>
            </div>
          </div>
          <!-- 面试官实时字幕 -->
          <div class="interviewer-subtitle">
            <div class="subtitle-header">
              <h4>面试官实时字幕</h4>
            </div>
            <div class="subtitle-content" ref="subtitleContent">
              <!-- 字幕滚动展示 -->
            <p v-for="(line, index) in subtitleLines" :key="index" class="subtitle-line">
                {{ line }}
              </p>
              <!-- 实时新增字幕的占位 -->
              <p class="subtitle-line current">{{ currentSubtitle }}</p>
            </div>
            <div class="subtitle-toggle">
              <label class="switch">
                <input type="checkbox" v-model="isSubtitleOn" @change="toggleSubtitle" />
                <span class="slider round"></span>
              </label>
              <span class="toggle-text">{{ isSubtitleOn ? '字幕已开启' : '字幕已关闭' }}</span>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>


<style scoped>
.interview-practice {
  min-height: 100vh;
  background-color: #f8fafc;
}

/* 演练容器 */
.practice-container {
  max-width: 1200px;
  margin: 40px auto;
  padding: 0 20px;
}

/* 面试基础信息 */
.practice-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
  padding: 16px 24px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}
.job-info h2 {
  font-size: 20px;
  color: #1f2937;
  margin: 0;
}
.job-info p {
  font-size: 14px;
  color: #6b7280;
  margin-top: 4px;
}
.status-text {
  color: #10b981;
  font-weight: 500;
}
.status-tag {
  background-color: #eff6ff;
  color: #2563eb;
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 13px;
  font-weight: 500;
}

/* 核心面试区域 */
.interview-main {
  display: flex;
  gap: 24px;
  margin-bottom: 32px;
}

/* 面试官信息面板 */
.interviewer-panel {
  width: 300px;
  background-color: #fff;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/*面试官头像*/
.interviewer-avatar {
  text-align: center;
}

.interviewer-avatar img {
  border-radius: 50%;
  width: 64px;
  height: 64px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #eee;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}
.interviewer-info {
  text-align: center;
}
.interviewer-info h3 {
  font-size: 18px;
  color: #1f2937;
  margin: 0;
}
.position {
  font-size: 14px;
  color: #6b7280;
  margin: 4px 0;
}
.specialty {
  font-size: 13px;
  color: #9ca3af;
  margin: 8px 0;
}
.interviewer-tags {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 8px;
  margin-top: 12px;
}
.tag {
  font-size: 12px;
  color: #2563eb;
  background-color: #eff6ff;
  padding: 2px 8px;
  border-radius: 4px;
}
.interviewer-controls {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.control-btn {
  padding: 8px 0;
  border-radius: 6px;
  border: 1px solid #ddd;
  background-color: #fff;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}
.control-btn:hover {
  background-color: #f3f4f6;
}

/* 实时面试交互区 */
.interview-interactive {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 视频区域 */
.video-area {
  background-color: #000;
  border-radius: 8px;
  position: relative;
  height: 550px;
  overflow: hidden;
}
.interviewer-video {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}
.video-frame {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.video-off {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #111827;
}
.video-off-text {
  color: #9ca3af;
  font-size: 16px;
}
.self-video {
  position: absolute;
  bottom: 20px;
  right: 20px;
  width: 200px;
  height: 150px;
  border-radius: 6px;
  overflow: hidden;
  border: 2px solid #fff;
}
.self-video-frame {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* 交互控制按钮 */
.interactive-controls {
  display: flex;
  gap: 12px;
  justify-content: center;
  padding: 16px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}
.interactive-btn {
  padding: 10px 20px;
  border-radius: 6px;
  border: 1px solid #ddd;
  background-color: #fff;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.interactive-btn.emergency {
  background-color: #ef4444;
  color: #fff;
  border-color: #ef4444;
}

/* 面试笔记区 */
.interview-notes {
  background-color: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}
.notes-title {
  font-size: 16px;
  color: #1f2937;
  margin: 0 0 12px 0;
}
.notes-input {
  width: 100%;
  min-height: 120px;
  padding: 12px 16px;
  border: 1px solid #ddd;
  border-radius: 6px;
  resize: vertical;
  font-size: 14px;
  line-height: 1.6;
  margin-bottom: 12px;
}
.save-notes {
  padding: 8px 16px;
  background-color: #2563eb;
  color: #fff;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

/* 面试辅助工具 */
.interview-tools {
  display: flex;
  gap: 16px;
  justify-content: center;
  padding: 16px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}
.tool-btn {
  padding: 10px 20px;
  border-radius: 6px;
  border: 1px solid #ddd;
  background-color: #fff;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
}
.tool-btn:hover {
  background-color: #f3f4f6;
}
.icon {
  font-size: 16px;
}
/*面试官字幕样式*/ 
.interviewer-subtitle {
  border-top: 1px solid #eee;
  padding-top: 20px;
}
.subtitle-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.subtitle-header h4 {
  font-size: 16px;
  color: #1f2937;
  margin: 0;
}
.subtitle-controls {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
}
.subtitle-btn {
  padding: 2px 8px;
  border-radius: 4px;
  border: 1px solid #ddd;
  background-color: #fff;
  cursor: pointer;
  font-size: 12px;
}
.subtitle-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.subtitle-content {
  height: 180px;
  padding: 12px;
  border: 1px solid #eee;
  border-radius: 6px;
  background-color: #f9fafb;
  overflow-y: auto;
  margin-bottom: 12px;
  font-size: 14px;
  line-height: 1.6;
}
.subtitle-line {
  color: #374151;
  margin: 4px 0;
}
.subtitle-line.current {
  color: #2563eb;
  font-weight: 500;
}
.subtitle-toggle {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #6b7280;
}
/* 开关样式 */
.switch {
  position: relative;
  display: inline-block;
  width: 40px;
  height: 20px;
}
.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}
.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  transition: .4s;
  border-radius: 20px;
}
.slider:before {
  position: absolute;
  content: "";
  height: 16px;
  width: 16px;
  left: 2px;
  bottom: 2px;
  background-color: white;
  transition: .4s;
  border-radius: 50%;
}
input:checked + .slider {
  background-color: #2563eb;
}
input:checked + .slider:before {
  transform: translateX(20px);
}
.toggle-text {
  font-size: 13px;
}

</style>