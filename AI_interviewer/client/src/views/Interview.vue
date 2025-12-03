<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { useRouter, useRoute } from 'vue-router'

const route = useRoute() 

// --- 弹窗与启动控制 ---
const isShowStartModal = ref(true); // 控制弹窗显示
const isInterviewStarted = ref(false); // 控制面试是否正式开始

// 点击“确认”开始面试
const handleStartInterview = () => {
  isShowStartModal.value = false;
  isInterviewStarted.value = true;
  
  // 开始各项计时和逻辑
  startTotalTimer();
  if (isSubtitleOn.value) {
    startSubtitleSimulation();
  }
};

// --- 面试基础信息 ---
const interviewerName = route.query.name || '面试官'
const interviewerTitle = route.query.title || '资深产品专家'

// 面试累计时长
const totalTimer = ref('00:00:00'); // 初始设为0
let timerInterval = null;

// 自身控制
const isSelfMuted = ref(false); // 自身麦克风状态
const isSelfVideoOff = ref(false); // 自身摄像头状态

// 面试笔记
const interviewNotes = ref('');

// --- 字幕相关逻辑 (修复了原代码的作用域嵌套问题) ---
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

// 模拟话术库 (原代码中未定义，这里补全以防报错)
const interviewScript = [
  "看到你的简历上提到你对数据分析很感兴趣，能举个例子吗？",
  "在团队合作中，如果开发认为你的需求无法实现，你会怎么处理？",
  "你觉得什么样的产品才算是一个好产品？",
  "对于我们公司的这款App，你有什么改进建议吗？",
  "好的，今天的面试就到这里，后续HR会联系你。"
];

// 页面卸载清除计时器
onUnmounted(() => {
  clearInterval(timerInterval);
  clearInterval(subtitleInterval);
});

// 累计计时逻辑（时:分:秒）
const startTotalTimer = () => {
  let time = 0; // 从0开始
  // 初始化显示
  totalTimer.value = '00:00:00';
  
  timerInterval = setInterval(() => {
    time++;
    const hours = Math.floor(time / 3600).toString().padStart(2, '0');
    const minutes = Math.floor((time % 3600) / 60).toString().padStart(2, '0');
    const seconds = (time % 60).toString().padStart(2, '0');
    totalTimer.value = `${hours}:${minutes}:${seconds}`;
  }, 1000);
};

// 字幕开关切换
const toggleSubtitle = () => {
  // 只有面试开始后，开关才生效
  if (!isInterviewStarted.value) return;

  if (isSubtitleOn.value) {
    startSubtitleSimulation();
  } else {
    clearInterval(subtitleInterval);
    currentSubtitle.value = '';
  }
};

// 模拟字幕实时生成
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
    
    <!-- 新增：开始面试确认弹窗 -->
    <div v-if="isShowStartModal" class="start-modal-overlay">
      <div class="start-modal">
        <div class="modal-icon">📹</div>
        <h3>准备好开始面试了吗？</h3>
        <p>点击确认后，面试官将开始提问并开始计时。</p>
        <button class="start-btn" @click="handleStartInterview">确认开始</button>
      </div>
    </div>

    <!-- 面试演练主区域 (添加 blur 类实现背景模糊效果) -->
    <div class="practice-container" :class="{ 'blur-bg': isShowStartModal }">
      <!-- 面试基础信息 -->
      <div class="practice-header">
        <div class="job-info">
          <h2>性格测试</h2>
          <p>面试状态: 
            <span class="status-text" :class="{'pending': !isInterviewStarted}">
              {{ isInterviewStarted ? '正在进行' : '等待开始' }}
            </span> 
            · 累计时长: <span class="timer">{{ totalTimer }}</span>
          </p>
        </div>
        <div class="status-tag">{{ isInterviewStarted ? '进行中' : '准备中' }}</div>
      </div>

      <!-- 核心面试区域：面试官+实时交互 -->
      <div class="interview-main">
       
        <!-- 实时面试交互区 -->
        <div class="interview-interactive">
          <!-- 视频/语音交互区 -->
          <div class="video-area">
            <div class="interviewer-video">
              <!-- 根据状态显示不同内容 -->
              <img 
                v-if="isInterviewStarted && !isSelfVideoOff"
                src="https://via.placeholder.com/600x400?text=面试官视频画面" 
                alt="面试官视频" 
                class="video-frame"
              />
              <div class="video-off" v-else>
                <span class="video-off-text">
                  {{ isInterviewStarted ? '面试官视频已关闭' : '面试尚未开始' }}
                </span>
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
            <!-- 替换为你的本地路径或占位图 -->
            <img src="https://via.placeholder.com/64" alt="面试官头像" />
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
              <p class="subtitle-line current">
                <span v-if="!isInterviewStarted" style="color:#999; font-style:italic;">等待面试开始...</span>
                {{ currentSubtitle }}
              </p>
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
  position: relative; /* 为绝对定位的弹窗做参考 */
}

/* --- 新增：弹窗样式 --- */
.start-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.6); /* 半透明遮罩 */
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000; /* 保证在最上层 */
  backdrop-filter: blur(4px); /* 背景模糊效果 */
}

.start-modal {
  background-color: #fff;
  padding: 32px 40px;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  width: 400px;
  animation: modalPop 0.3s ease-out;
}

.modal-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.start-modal h3 {
  margin: 0 0 12px 0;
  color: #1f2937;
  font-size: 22px;
}

.start-modal p {
  color: #6b7280;
  margin-bottom: 24px;
}

.start-btn {
  background-color: #2563eb;
  color: white;
  border: none;
  padding: 12px 32px;
  border-radius: 24px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
  width: 100%;
}

.start-btn:hover {
  background-color: #1d4ed8;
}

@keyframes modalPop {
  from { opacity: 0; transform: scale(0.9); }
  to { opacity: 1; transform: scale(1); }
}

/* 背景模糊辅助类 */
.blur-bg {
  filter: blur(2px);
  pointer-events: none; /* 弹窗出现时，禁止点击背景内容 */
}

/* 演练容器 */
.practice-container {
  max-width: 1200px;
  margin: 40px auto;
  padding: 0 20px;
  transition: filter 0.3s;
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
.status-text.pending {
  color: #f59e0b; /* 黄色表示等待中 */
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
  z-index: 10;
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
</style>