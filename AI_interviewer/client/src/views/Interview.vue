<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import interviewImg  from  '@/img/interviewer.gif'
import defaultAvatar from '@/img/log.png'
import { createRecord } from '../api/Interview_record'

const router = useRouter()
const route = useRoute()  

// --- 弹窗与启动控制 ---
const isShowStartModal = ref(true);
const isShowEndModal = ref(false);
const isInterviewStarted = ref(false);

// --- 媒体设备与 WebSocket 控制 ---
const localStream = ref(null); 
const selfVideoRef = ref(null);
const mediaRecorder = ref(null); // 新增：媒体录制器
const ws = ref(null);            // 新增：WebSocket 对象
const userId = "user_123";       // 示例：实际应从 store 或 login info 获取

// 初始化媒体设备
const initMediaDevices = async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: true,
      audio: true
    });
    localStream.value = stream;
    if (selfVideoRef.value) {
      selfVideoRef.value.srcObject = stream;
    }
    isSelfMuted.value = false;
    isSelfVideoOff.value = false;
    return true; // 返回成功标志
  } catch (err) {
    console.error("无法获取媒体设备:", err);
    alert("无法访问摄像头或麦克风，请检查浏览器权限设置。");
    isSelfVideoOff.value = true;
    isSelfMuted.value = true;
    return false;
  }
};

// --- WebSocket 与 录制逻辑 (核心修改) ---

const initWebSocketAndRecord = () => {
  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL;

  if (!apiBaseUrl) {
    console.error("错误: 未找到 VITE_API_BASE_URL 环境变量");
    return;
  }

  // 2. 使用 URL 对象构建稳健的 WebSocket 地址
  // 这样可以自动处理端口、域名和原有的 path (如 /api)
  const urlObj = new URL(apiBaseUrl);
  
  // 协议转换: http -> ws, https -> wss
  urlObj.protocol = urlObj.protocol.replace('http', 'ws');

  // 处理路径: 确保不出现双斜杠 (//)
  // 获取 .env 中配置的基础路径 (例如 "/api")
  let basePath = urlObj.pathname;
  if (basePath.endsWith('/')) {
    basePath = basePath.slice(0, -1);
  }

  const token = localStorage.getItem('token'); // 示例：实际应从 store 或 login info 获取
  // 3. 拼接最终地址
  // 结果示例: ws://127.0.0.1:8000/api/ws/video_stream/user_123
  const wsUrl = `${urlObj.origin}${basePath}/ws/video_stream?token=${token}`;
  
  console.log("尝试连接 WebSocket:", wsUrl); 

  // 4. 建立连接
  ws.value = new WebSocket(wsUrl);

  ws.value.onopen = () => {
    console.log("WebSocket 已连接，开始传输数据");
    startRecording(); // 连接成功后，开始录制
  };

  ws.value.onerror = (error) => {
    console.error("WebSocket 错误:", error);
  };
  
  ws.value.onclose = (e) => {
    console.log("WebSocket 已断开", e.code, e.reason);
  };
};

const startRecording = () => {
  if (!localStream.value) return;

  // 设置录制格式，优先使用 webm (Chrome/Electron默认支持)
  const options = { mimeType: 'video/webm; codecs=vp9' };
  
  try {
    mediaRecorder.value = new MediaRecorder(localStream.value, options);
  } catch (e) {
    // 回退兼容
    mediaRecorder.value = new MediaRecorder(localStream.value);
  }

  // 核心：每隔 1000ms (1秒) 切片一次并触发 dataavailable
  mediaRecorder.value.ondataavailable = (event) => {
    if (event.data && event.data.size > 0 && ws.value && ws.value.readyState === WebSocket.OPEN) {
      // 将 Blob 数据直接通过 WS 发送给后端
      ws.value.send(event.data);
    }
  };

  mediaRecorder.value.start(1000); // 1000ms 时间片
};

const stopRecordingAndWS = () => {
  // 停止录制
  if (mediaRecorder.value && mediaRecorder.value.state !== 'inactive') {
    mediaRecorder.value.stop();
  }
  
  // 关闭 WebSocket
  if (ws.value) {
    ws.value.close();
    ws.value = null;
  }
};

// 停止所有媒体流 (释放设备)
const stopMediaDevices = () => {
  stopRecordingAndWS(); // 确保先停止录制传输
  
  if (localStream.value) {
    localStream.value.getTracks().forEach(track => track.stop());
    localStream.value = null;
    if (selfVideoRef.value) {
      selfVideoRef.value.srcObject = null;
    }
  }

};

// 点击“确认开始”
const handleStartInterview = async () => {
  const success = await initMediaDevices();
  if (success) {
    isShowStartModal.value = false;
    isInterviewStarted.value = true;
    startTotalTimer();
    
    // 启动 WebSocket 和录制
    initWebSocketAndRecord();
    
    if (isSubtitleOn.value) {
      startSubtitleSimulation();
    }
  }
};


// 保存面试记录
const saveInterviewRecord = async () => {
  if (interviewerId && positionId) {
    try {
      await createRecord({
        position_id: positionId,
        interviewer_id: interviewerId
      })
      ElMessage.success('面试记录已保存')
    } catch (error) {
      console.error('保存面试记录失败:', error)
      ElMessage.error('保存面试记录失败')
    }
  }
}

// 新增：点击“结束面试”
const handleEndInterview = () => {
  // 1. 停止计时和字幕
  clearInterval(timerInterval);
  clearInterval(subtitleInterval);
  
  // 2. 核心：停止录制设备
  stopMediaDevices();
  
  // 3. 更新状态
  isInterviewStarted.value = false;
  
  // 4. 保存记录
  saveInterviewRecord();

  // 5. 显示结束弹窗
  isShowEndModal.value = true;
};

// 新增：结束后返回首页或跳转报告页
const goBackHome = () => {
  router.push({ name: 'Home' }) // 假设首页路由是 '/'，你可以改为 '/report' 等
};

// 前往面试复盘
const goToReview = () => {
  
}

const goBack = () => {
  router.push({ name: 'Home' }) 
}

// --- 面试基础信息 ---
const interviewerName = route.query.name || '面试官'
const interviewerTitle = route.query.title || '资深产品专家'
const interviewerAvatar = route.query.avatar || defaultAvatar
const interviewerId = Number(route.query.interviewer_id)
const positionId = Number(route.query.position_id)

const totalTimer = ref('00:00:00'); 
let timerInterval = null;

const isSelfMuted = ref(false); 
const isSelfVideoOff = ref(false); 

// 自身麦克风切换
const toggleSelfMute = () => {
  if (localStream.value) {
    const audioTracks = localStream.value.getAudioTracks();
    if (audioTracks.length > 0) {
      const newState = !audioTracks[0].enabled;
      audioTracks[0].enabled = newState;
      isSelfMuted.value = !newState;
    }
  } else {
    isSelfMuted.value = !isSelfMuted.value;
  }
};

// 自身摄像头切换
const toggleSelfVideo = async () => {
  if (!localStream.value && isSelfVideoOff.value && isInterviewStarted.value) {
    await initMediaDevices();
    return;
  }

  if (localStream.value) {
    const videoTracks = localStream.value.getVideoTracks();
    if (videoTracks.length > 0) {
      const newState = !videoTracks[0].enabled;
      videoTracks[0].enabled = newState;
      isSelfVideoOff.value = !newState;
    }
  }
};

// 面试笔记
const interviewNotes = ref('');

// --- 字幕相关逻辑 ---
const isSubtitleOn = ref(true); 
const speed = ref(1); 
const subtitleLines = ref([
  '你好，很高兴今天能和你进行这次面试。',
  '首先想了解一下，你为什么想要应聘产品经理这个岗位？',
  '可以具体说说你在校期间做过的相关产品项目吗？'
]); 
const currentSubtitle = ref(''); 
const subtitleContent = ref(null); 
let subtitleInterval = null; 

const interviewScript = [
  "看到你的简历上提到你对数据分析很感兴趣，能举个例子吗？",
  "在团队合作中，如果开发认为你的需求无法实现，你会怎么处理？",
  "你觉得什么样的产品才算是一个好产品？",
  "对于我们公司的这款App，你有什么改进建议吗？",
  "好的，今天的面试就到这里，后续HR会联系你。"
];

onUnmounted(() => {
  clearInterval(timerInterval);
  clearInterval(subtitleInterval);
  stopMediaDevices(); 
});

const startTotalTimer = () => {
  let time = 0; 
  totalTimer.value = '00:00:00';
  
  timerInterval = setInterval(() => {
    time++;
    const hours = Math.floor(time / 3600).toString().padStart(2, '0');
    const minutes = Math.floor((time % 3600) / 60).toString().padStart(2, '0');
    const seconds = (time % 60).toString().padStart(2, '0');
    totalTimer.value = `${hours}:${minutes}:${seconds}`;
  }, 1000);
};

const toggleSubtitle = () => {
  if (!isInterviewStarted.value) return;

  if (isSubtitleOn.value) {
    startSubtitleSimulation();
  } else {
    clearInterval(subtitleInterval);
    currentSubtitle.value = '';
  }
};

const startSubtitleSimulation = () => {
  clearInterval(subtitleInterval);
  const interval = 3000 / speed.value;
  let scriptIndex = 0;
  
  subtitleInterval = setInterval(() => {
    if (currentSubtitle.value) {
      subtitleLines.value.push(currentSubtitle.value);
      if (subtitleLines.value.length > 10) {
        subtitleLines.value.shift();
      }
    }
    currentSubtitle.value = interviewScript[scriptIndex % interviewScript.length];
    scriptIndex++;
    
    if (subtitleContent.value) {
      subtitleContent.value.scrollTop = subtitleContent.value.scrollHeight;
    }
  }, interval);
};

</script>

<template>
  <div class="interview-practice">
    
    <!-- 1. 开始面试确认弹窗 -->
    <div v-if="isShowStartModal" class="start-modal-overlay">
      <div class="start-modal">
        <div class="modal-icon">📹</div>
        <h3>准备好开始面试了吗？</h3>
        <p>点击确认后，浏览器将请求摄像头和麦克风权限。</p>
        <button class="start-btn" @click="handleStartInterview">确认开始</button>
      </div>
    </div>

    <!-- 2. 新增：面试结束弹窗 -->
    <div v-if="isShowEndModal" class="start-modal-overlay">
      <div class="start-modal">
        <div class="modal-icon">🏁</div>
        <h3>面试已结束</h3>
        <p>摄像头与录音已关闭，您可以返回查看结果。</p>
        <!-- 点击后跳转或刷新 -->
        <button class="start-btn" @click="goBackHome">返回首页</button>
      </div>
    </div>

    <!-- 面试演练主区域 -->
    <!-- 注意：这里增加了 isShowEndModal 的模糊判断 -->
    <div class="practice-container" :class="{ 'blur-bg': isShowStartModal || isShowEndModal }">
      <!-- 面试基础信息 -->
      <div class="practice-header">
        <div class="job-info">
          <h2>性格测试</h2>
          <p>面试状态: 
            <span class="status-text" :class="{'pending': !isInterviewStarted}">
              {{ isInterviewStarted ? '正在进行' : '已结束/等待中' }}
            </span> 
            · 累计时长: <span class="timer">{{ totalTimer }}</span>
          </p>
        </div>
        <div class="status-tag">{{ isInterviewStarted ? '进行中' : '休息中' }}</div>
      </div>

      <!-- 核心面试区域 -->
      <div class="interview-main">
       
        <div class="interview-interactive">
          <div class="video-area">
            <div class="interviewer-video">
              <img 
                v-if="isInterviewStarted"
                :src= "interviewImg"
                alt="面试官视频" 
                class="video-frame"
              />
              <div class="video-off" v-else>
                <span class="video-off-text">面试未进行</span>
              </div>
            </div>

            <div class="self-video">
              <!-- 视频标签：面试开始且未关闭摄像头时显示 -->
              <!-- 增加了 v-show 控制，防止流停止后黑屏影响美观 -->
              <video 
                v-show="isInterviewStarted && !isSelfVideoOff"
                ref="selfVideoRef"
                autoplay 
                playsinline
                muted
                class="self-video-frame"
              ></video>
              
              <!-- 占位图：面试未开始 或 摄像头被手动关闭 -->
              <div v-if="!isInterviewStarted || isSelfVideoOff" class="self-video-placeholder">
                <span>{{ !isInterviewStarted ? '设备未启动' : '摄像头已关闭' }}</span>
              </div>
            </div>
          </div>

          <!-- 面试交互控制 -->
          <div class="interactive-controls">
            <button 
              class="interactive-btn" 
              :class="{ 'active': isSelfMuted }"
              @click="toggleSelfMute"
              :disabled="!isInterviewStarted" 
            >
              <span class="icon">{{ isSelfMuted ? '🔇' : '🎤' }}</span>
              {{ isSelfMuted ? '打开麦克风' : '关闭麦克风' }}
            </button>
            
            <button 
              class="interactive-btn" 
              :class="{ 'active': isSelfVideoOff }"
              @click="toggleSelfVideo"
              :disabled="!isInterviewStarted"
            >
              <span class="icon">{{ isSelfVideoOff ? '📷' : '🚫' }}</span>
              {{ isSelfVideoOff ? '打开摄像头' : '关闭摄像头' }}
            </button>
            
            <!-- 修改：移除举手按钮，绑定结束面试事件 -->
            <button class="interactive-btn emergency" @click="handleEndInterview">
              🛑 结束面试
            </button>
          </div>
        </div>

         <!-- 面试官信息展示区 -->
        <div class="interviewer-panel">
          <div class="interviewer-avatar">
            <img :src= "interviewerAvatar" alt="面试官头像" />
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
          <div class="interviewer-subtitle">
            <div class="subtitle-header">
              <h4>面试官实时字幕</h4>
            </div>
            <div class="subtitle-content" ref="subtitleContent">
              <p v-for="(line, index) in subtitleLines" :key="index" class="subtitle-line">
                {{ line }}
              </p>
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
  position: relative; 
}

/* 弹窗样式 (复用) */
.start-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.6); 
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000; 
  backdrop-filter: blur(4px); 
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

.modal-icon { font-size: 48px; margin-bottom: 16px; }
.start-modal h3 { margin: 0 0 12px 0; color: #1f2937; font-size: 22px; }
.start-modal p { color: #6b7280; margin-bottom: 24px; }
.start-btn { background-color: #2563eb; color: white; border: none; padding: 12px 32px; border-radius: 24px; font-size: 16px; font-weight: 500; cursor: pointer; transition: background-color 0.2s; width: 100%; }
.start-btn:hover { background-color: #1d4ed8; }

@keyframes modalPop { from { opacity: 0; transform: scale(0.9); } to { opacity: 1; transform: scale(1); } }
.blur-bg { filter: blur(2px); pointer-events: none; }

/* 容器与布局 */
.practice-container { max-width: 1200px; margin: 40px auto; padding: 0 20px; transition: filter 0.3s; }
.practice-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 32px; padding: 16px 24px; background-color: #fff; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
.job-info h2 { font-size: 20px; color: #1f2937; margin: 0; }
.job-info p { font-size: 14px; color: #6b7280; margin-top: 4px; }
.status-text { color: #10b981; font-weight: 500; }
.status-text.pending { color: #f59e0b; }
.status-tag { background-color: #eff6ff; color: #2563eb; padding: 4px 12px; border-radius: 16px; font-size: 13px; font-weight: 500; }

.interview-main { display: flex; gap: 24px; margin-bottom: 32px; }
.interviewer-panel { width: 300px; background-color: #fff; border-radius: 8px; padding: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); display: flex; flex-direction: column; gap: 20px; }
.interviewer-avatar { text-align: center; object-fit: contain;}
.interviewer-avatar img { width: 64px; height: 64px; border-radius: 50%; object-fit: cover; border: 2px solid #eee; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
.interviewer-info { text-align: center; }
.interviewer-info h3 { font-size: 18px; color: #1f2937; margin: 0; }
.position { font-size: 14px; color: #6b7280; margin: 4px 0; }
.specialty { font-size: 13px; color: #9ca3af; margin: 8px 0; }
.interviewer-tags { display: flex; flex-wrap: wrap; justify-content: center; gap: 8px; margin-top: 12px; }
.tag { font-size: 12px; color: #2563eb; background-color: #eff6ff; padding: 2px 8px; border-radius: 4px; }

.interview-interactive { flex: 1; display: flex; flex-direction: column; gap: 20px; }
.video-area { background-color: #000; border-radius: 8px; position: relative; height: 550px; overflow: hidden; }
.interviewer-video { width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; }
.video-frame { width: 100%; height: 100%; object-fit: contain; background-color: #c5efb3;}
.video-off { width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; background-color: #111827; }
.video-off-text { color: #9ca3af; font-size: 16px; }

/* 自身视频区域 */
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
  background-color: #333; 
}

.self-video-frame {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transform: scaleX(-1); 
}

.self-video-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #1f2937;
  color: #9ca3af;
  font-size: 12px;
}

/* 控制按钮 */
.interactive-controls { display: flex; gap: 12px; justify-content: center; padding: 16px; background-color: #fff; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
.interactive-btn { padding: 10px 20px; border-radius: 6px; border: 1px solid #ddd; background-color: #fff; cursor: pointer; font-size: 14px; display: flex; align-items: center; gap: 8px; transition: all 0.2s; }
.interactive-btn:disabled { opacity: 0.6; cursor: not-allowed; } /* 禁用样式 */

.interactive-btn.active {
  background-color: #fef2f2;
  color: #ef4444;
  border-color: #fecaca;
}

.interactive-btn.emergency { background-color: #ef4444; color: #fff; border-color: #ef4444; }
.interactive-btn.emergency:hover { background-color: #dc2626; }

/* 字幕部分 */
.interviewer-subtitle { border-top: 1px solid #eee; padding-top: 20px; }
.subtitle-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.subtitle-header h4 { font-size: 16px; color: #1f2937; margin: 0; }
.subtitle-content { height: 180px; padding: 12px; border: 1px solid #eee; border-radius: 6px; background-color: #f9fafb; overflow-y: auto; margin-bottom: 12px; font-size: 14px; line-height: 1.6; }
.subtitle-line { color: #374151; margin: 4px 0; }
.subtitle-line.current { color: #2563eb; font-weight: 500; }
.subtitle-toggle { display: flex; align-items: center; gap: 8px; font-size: 13px; color: #6b7280; }
.switch { position: relative; display: inline-block; width: 40px; height: 20px; }
.switch input { opacity: 0; width: 0; height: 0; }
.slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: #ccc; transition: .4s; border-radius: 20px; }
.slider:before { position: absolute; content: ""; height: 16px; width: 16px; left: 2px; bottom: 2px; background-color: white; transition: .4s; border-radius: 50%; }
input:checked + .slider { background-color: #2563eb; }
input:checked + .slider:before { transform: translateX(20px); }
</style>