<script setup>
import { ref, onMounted, onUnmounted, nextTick, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import interviewImg from '@/img/interviewer.gif'
import defaultAvatar from '@/img/log.png'
import { createRecord } from '../api/Interview_record'

const router = useRouter()
const route = useRoute()

// ==================== 状态管理 ====================

// --- 弹窗与启动控制 ---
const isShowStartModal = ref(true);
const isShowEndModal = ref(false);
const isInterviewStarted = ref(false);
const isLoading = ref(false);
const loadingText = ref('');

// --- 面试会话状态 ---
const interviewStatus = ref('idle'); // idle, initializing, waiting_ready, in_progress, ended
const currentQuestionIndex = ref(0);
const totalQuestions = ref(0);
const jobName = ref('');
const interviewSummary = ref(null);

// --- 媒体设备控制 ---
const localStream = ref(null);
const selfVideoRef = ref(null);
const mediaRecorder = ref(null);
const audioRecorder = ref(null);  // 单独的音频录制器
const isRecordingAnswer = ref(false);  // 是否正在录制回答

// --- WebSocket 控制 ---
const wsVideo = ref(null);      // 视频流 WebSocket
const wsInterview = ref(null);  // 面试会话 WebSocket

// --- 音频播放 ---
const audioContext = ref(null);
const audioQueue = ref([]);
const isPlayingAudio = ref(false);
const waitingForClosingRemarks = ref(false); // 是否等待结束语播放完毕

// --- 字幕相关 ---
const isSubtitleOn = ref(true);
const subtitleLines = ref([]);
const currentSubtitle = ref('');
const subtitleContent = ref(null);
const userTranscription = ref(''); // 用户语音转录

// --- 计时器 ---
const totalTimer = ref('00:00:00');
let timerInterval = null;

// --- 设备状态 ---
const isSelfMuted = ref(false);
const isSelfVideoOff = ref(false);

// --- 面试信息 ---
const interviewerName = route.query.name || 'AI面试官'
const interviewerTitle = route.query.title || '智能面试助手'
const interviewerAvatar = route.query.avatar || defaultAvatar
const interviewerId = Number(route.query.interviewer_id) || 0
const positionId = Number(route.query.position_id) || 0

// --- 进度显示 ---
const progressText = computed(() => {
  if (totalQuestions.value === 0) return '';
  return `第 ${currentQuestionIndex.value} / ${totalQuestions.value} 题`;
});

// ==================== 工具函数 ====================

/**
 * 为PCM数据添加WAV文件头
 * @param {Uint8Array} pcmData - PCM音频数据
 * @param {number} sampleRate - 采样率 (默认24000Hz)
 * @param {number} channels - 声道数 (默认1)
 * @param {number} bitDepth - 位深度 (默认16bit)
 * @returns {Uint8Array} 带WAV头的完整音频数据
 */
const addWavHeader = (pcmData, sampleRate = 24000, channels = 1, bitDepth = 16) => {
  const dataLength = pcmData.length;
  const buffer = new ArrayBuffer(44 + dataLength);
  const view = new DataView(buffer);
  
  // RIFF chunk descriptor
  writeString(view, 0, 'RIFF');
  view.setUint32(4, 36 + dataLength, true);
  writeString(view, 8, 'WAVE');
  
  // fmt sub-chunk
  writeString(view, 12, 'fmt ');
  view.setUint32(16, 16, true); // chunk size
  view.setUint16(20, 1, true); // audio format (1 = PCM)
  view.setUint16(22, channels, true);
  view.setUint32(24, sampleRate, true);
  view.setUint32(28, sampleRate * channels * bitDepth / 8, true); // byte rate
  view.setUint16(32, channels * bitDepth / 8, true); // block align
  view.setUint16(34, bitDepth, true);
  
  // data sub-chunk
  writeString(view, 36, 'data');
  view.setUint32(40, dataLength, true);
  
  // 写入PCM数据
  const result = new Uint8Array(buffer);
  result.set(pcmData, 44);
  
  return result;
};

const writeString = (view, offset, string) => {
  for (let i = 0; i < string.length; i++) {
    view.setUint8(offset + i, string.charCodeAt(i));
  }
};

// ==================== 媒体设备初始化 ====================

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
    
    // 初始化音频上下文
    audioContext.value = new (window.AudioContext || window.webkitAudioContext)();
    
    return true;
  } catch (err) {
    console.error("无法获取媒体设备:", err);
    ElMessage.error("无法访问摄像头或麦克风，请检查浏览器权限设置。");
    isSelfVideoOff.value = true;
    isSelfMuted.value = true;
    return false;
  }
};

// ==================== WebSocket 连接管理 ====================

// 视频流 WebSocket (保持原有功能)
const initVideoWebSocket = () => {
  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL;
  if (!apiBaseUrl) {
    console.error("错误: 未找到 VITE_API_BASE_URL 环境变量");
    return;
  }

  const urlObj = new URL(apiBaseUrl);
  urlObj.protocol = urlObj.protocol.replace('http', 'ws');
  let basePath = urlObj.pathname;
  if (basePath.endsWith('/')) {
    basePath = basePath.slice(0, -1);
  }

  const token = localStorage.getItem('token');
  const wsUrl = `${urlObj.origin}${basePath}/ws/video_stream?token=${token}`;

  console.log("尝试连接视频 WebSocket:", wsUrl);

  wsVideo.value = new WebSocket(wsUrl);

  wsVideo.value.onopen = () => {
    console.log("视频 WebSocket 已连接");
    startVideoRecording();
  };

  wsVideo.value.onerror = (error) => {
    console.error("视频 WebSocket 错误:", error);
  };

  wsVideo.value.onclose = (e) => {
    console.log("视频 WebSocket 已断开", e.code, e.reason);
  };
};

// 面试会话 WebSocket
const initInterviewWebSocket = () => {
  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL;
  if (!apiBaseUrl) {
    console.error("错误: 未找到 VITE_API_BASE_URL 环境变量");
    return;
  }

  const urlObj = new URL(apiBaseUrl);
  urlObj.protocol = urlObj.protocol.replace('http', 'ws');
  let basePath = urlObj.pathname;
  if (basePath.endsWith('/')) {
    basePath = basePath.slice(0, -1);
  }

  const token = localStorage.getItem('token');
  
  // 🤖 使用新的 Agent API 端点（基于 LangGraph 的智能面试官）
  // 旧端点: /api/interview/ws/interview (硬编码题库)
  // 新端点: /api/interview/ws/interview/agent (AI Agent)
  const wsUrl = `${urlObj.origin}${basePath}/api/interview/ws/interview/agent?token=${token}`;

  console.log("尝试连接面试 WebSocket:", wsUrl);

  wsInterview.value = new WebSocket(wsUrl);

  wsInterview.value.onopen = () => {
    console.log("面试 WebSocket 已连接");
    interviewStatus.value = 'initializing';
    // 发送初始化请求
    sendInterviewMessage({ type: 'init' });
  };

  wsInterview.value.onmessage = (event) => {
    handleInterviewMessage(JSON.parse(event.data));
  };

  wsInterview.value.onerror = (error) => {
    console.error("面试 WebSocket 错误:", error);
    ElMessage.error("面试连接出现问题，请刷新页面重试");
  };

  wsInterview.value.onclose = (e) => {
    console.log("面试 WebSocket 已断开", e.code, e.reason);
  };
};

// 发送面试消息
const sendInterviewMessage = (message) => {
  if (wsInterview.value && wsInterview.value.readyState === WebSocket.OPEN) {
    wsInterview.value.send(JSON.stringify(message));
  }
};

// 处理面试消息
const handleInterviewMessage = async (message) => {
  console.log("收到面试消息:", message.type, message);

  switch (message.type) {
    case 'status':
      handleStatusUpdate(message.data);
      break;

    case 'opening':
      // 处理开场白（不是问题，只是欢迎语）
      console.log('[Interview] 👋 Opening:', message.text);
      // 开场白已经通过 subtitle 显示，这里只记录日志
      break;

    case 'question':
      handleQuestion(message);
      break;

    case 'subtitle':
      handleSubtitle(message);
      break;

    case 'audio':
      handleAudio(message);
      break;

    case 'audio_chunk':
      handleAudioChunk(message);
      break;

    case 'transcription':
      handleTranscription(message);
      break;

    case 'analysis':
      handleAnalysis(message);
      break;

    case 'closing':
      // 处理结束语（不需要回答，只是告别）
      console.log('[Interview] 👋 Closing:', message.text);
      // 结束语已经通过 subtitle 显示，这里只记录日志
      break;

    case 'end':
      handleInterviewEnd(message);
      break;

    case 'redirect':
      handleRedirect(message);
      break;

    case 'error':
      ElMessage.error(message.message || '发生错误');
      isLoading.value = false;
      break;
  }
};

// ==================== 消息处理函数 ====================

const handleStatusUpdate = (data) => {
  loadingText.value = data.message || '';
  
  if (data.stage === 'ready') {
    isLoading.value = false;
    // 不再显示 waiting_ready 弹窗，直接进入面试
    // 开场白后会自动发送第一个问题
    interviewStatus.value = 'in_progress';
    jobName.value = data.job_name || '';
    totalQuestions.value = data.total_questions || 0;
    
    // 显示准备就绪提示
    console.log('[Interview] ✅ Ready, interview will start automatically');
  } else {
    isLoading.value = true;
  }
};

const handleQuestion = (message) => {
  currentQuestionIndex.value = message.index || message.question_index || 0;
  totalQuestions.value = message.total || totalQuestions.value;
  
  // 清空当前字幕，准备显示新问题
  currentSubtitle.value = '';
  userTranscription.value = '';
  
  // 重置提交状态
  canSubmitAnswer.value = false;
  isWaitingForSubmit.value = false;
  
  // 如果是追问，添加标记
  if (message.is_follow_up) {
    subtitleLines.value.push(`[追问]`);
  }
};

const handleSubtitle = (message) => {
  currentSubtitle.value = message.text || '';
  
  if (message.is_final) {
    // 字幕完成，添加到历史记录
    subtitleLines.value.push(currentSubtitle.value);
    
    // 保持历史记录不超过20条
    if (subtitleLines.value.length > 20) {
      subtitleLines.value.shift();
    }
    
    // 滚动到底部
    nextTick(() => {
      if (subtitleContent.value) {
        subtitleContent.value.scrollTop = subtitleContent.value.scrollHeight;
      }
    });
  }
};

// ==================== 音频队列管理 ====================
// 音频流缓冲区
let audioChunks = [];
let currentPlayingAudio = null;  // 当前正在播放的音频
let isPlayingQueue = false;

// 音频播放队列 - 确保按顺序播放
const audioPlayQueue = ref([]);        // 待播放的音频队列
const isAudioQueuePlaying = ref(false); // 是否正在播放队列
const canSubmitAnswer = ref(false);     // 是否可以提交回答（音频播完后才允许）
const isWaitingForSubmit = ref(false);  // 是否等待用户点击提交
// ==================== 修复结束 ====================

const handleAudio = async (message) => {
  try {
    // 解码 Base64 音频数据
    const audioData = atob(message.data);
    const arrayBuffer = new ArrayBuffer(audioData.length);
    const view = new Uint8Array(arrayBuffer);
    for (let i = 0; i < audioData.length; i++) {
      view[i] = audioData.charCodeAt(i);
    }
    
    // 创建音频 Blob 并加入队列（不立即播放）
    const audioBlob = new Blob([arrayBuffer], { type: 'audio/wav' });
    audioPlayQueue.value.push(audioBlob);
    
    // 如果队列没在播放，启动播放
    if (!isAudioQueuePlaying.value) {
      playNextAudioInQueue();
    }
    
  } catch (error) {
    console.error("音频播放失败:", error);
    // 不再自动开始录音
  }
};

const handleAudioChunk = async (message) => {
  try {
    if (message.is_final) {
      // 收到结束标记，合并所有音频块并加入播放队列
      if (audioChunks.length > 0) {
        console.log(`收到完整音频流，共 ${audioChunks.length} 个片段，加入播放队列`);
        
        // 合并所有音频数据
        const totalLength = audioChunks.reduce((acc, chunk) => acc + chunk.length, 0);
        const mergedPCM = new Uint8Array(totalLength);
        let offset = 0;
        for (const chunk of audioChunks) {
          mergedPCM.set(chunk, offset);
          offset += chunk.length;
        }
        
        // 为PCM数据添加WAV文件头
        const wavData = addWavHeader(mergedPCM, 24000, 1, 16);
        
        // 创建完整的音频 Blob 并加入队列（而不是立即播放）
        const audioBlob = new Blob([wavData], { type: 'audio/wav' });
        audioPlayQueue.value.push(audioBlob);
        audioChunks = [];  // 清空缓冲区
        
        // 如果队列没在播放，启动播放
        if (!isAudioQueuePlaying.value) {
          playNextAudioInQueue();
        }
      } else {
        // 空的音频块（可能是结束信号），清空缓冲区
        audioChunks = [];
      }
    } else if (message.data) {
      // 解码并缓存音频块
      const audioData = atob(message.data);
      const arrayBuffer = new ArrayBuffer(audioData.length);
      const view = new Uint8Array(arrayBuffer);
      for (let i = 0; i < audioData.length; i++) {
        view[i] = audioData.charCodeAt(i);
      }
      audioChunks.push(view);
    }
    
  } catch (error) {
    console.error("音频流处理失败:", error);
    audioChunks = [];
  }
};

// 播放队列中的下一个音频
const playNextAudioInQueue = async () => {
  if (audioPlayQueue.value.length === 0) {
    // 队列为空，所有音频播放完毕
    isAudioQueuePlaying.value = false;
    isPlayingAudio.value = false;
    currentPlayingAudio = null;
    
    // 检查是否等待结束语播放完毕
    if (waitingForClosingRemarks.value) {
      console.log('[Interview] ✅ 结束语播放完毕，显示结束弹窗');
      waitingForClosingRemarks.value = false;
      
      // 停止所有设备
      stopMediaDevices();
      
      // 显示结束弹窗
      isInterviewStarted.value = false;
      isShowEndModal.value = true;
      
      // 25秒后跳转到首页
      // setTimeout(() => {
      //   router.push('/Home');
      // }, 25000);
      
      return;
    }
    
    // 允许用户提交回答（只有在面试进行中且未结束时）
    if (interviewStatus.value === 'in_progress') {
      canSubmitAnswer.value = true;
      isWaitingForSubmit.value = true;
      console.log('✅ 音频播放完毕，等待用户点击开始回答');
    }
    return;
  }
  
  isAudioQueuePlaying.value = true;
  isPlayingAudio.value = true;
  canSubmitAnswer.value = false;  // 播放时不允许提交
  
  const audioBlob = audioPlayQueue.value.shift();
  const audioUrl = URL.createObjectURL(audioBlob);
  const audio = new Audio(audioUrl);
  currentPlayingAudio = audio;  // 保存引用，用于结束时停止
  
  audio.onerror = (e) => {
    console.error("音频播放错误:", e);
    URL.revokeObjectURL(audioUrl);
    currentPlayingAudio = null;
    // 继续播放下一个
    playNextAudioInQueue();
  };
  
  audio.onended = () => {
    URL.revokeObjectURL(audioUrl);
    currentPlayingAudio = null;
    console.log(`🔊 音频播放完成，队列剩余: ${audioPlayQueue.value.length}`);
    // 继续播放下一个
    playNextAudioInQueue();
  };
  
  try {
    await audio.play();
  } catch (e) {
    console.error("音频播放失败:", e);
    currentPlayingAudio = null;
    playNextAudioInQueue();
  }
};

const handleTranscription = (message) => {
  userTranscription.value = message.text || '';
  
  if (message.is_final) {
    // 将用户回答添加到字幕历史
    subtitleLines.value.push(`[你] ${userTranscription.value}`);
    
    nextTick(() => {
      if (subtitleContent.value) {
        subtitleContent.value.scrollTop = subtitleContent.value.scrollHeight;
      }
    });
  }
};

const handleAnalysis = (message) => {
  // 显示简短的分析反馈
  console.log(`回答评分: ${message.score}, 反馈: ${message.feedback}`);
  
  if (message.action === 'end_interview') {
    ElMessage.info('面试即将结束...');
  }
};

const handleInterviewEnd = (message) => {
  console.log('[Interview] 🏁 Interview ended:', message);
  
  // 如果已经结束（用户主动结束），不重复处理
  if (interviewStatus.value === 'ended') {
    // 只更新摘要信息
    if (message.summary) {
      interviewSummary.value = message.summary;
    }
    return;
  }
  
  interviewStatus.value = 'ended';
  interviewSummary.value = message.summary;
  
  // 停止录音
  if (audioRecorder.value && audioRecorder.value.state === 'recording') {
    audioRecorder.value.stop();
  }
  isRecordingAnswer.value = false;
  
  // 停止计时
  clearInterval(timerInterval);
  
  canSubmitAnswer.value = false;
  isWaitingForSubmit.value = false;
  
  // 注意：后端现在会先发送结束语音频，再发送 end 消息
  // 所以这里**不清空音频队列**，让结束语正常播放
  // 设置标志：等待结束语播放完毕
  waitingForClosingRemarks.value = true;
  
  console.log('[Interview] ⏳ 等待结束语播放完毕...');
  console.log(`[Interview] 📢 当前音频队列长度: ${audioPlayQueue.value.length}, 正在播放: ${isAudioQueuePlaying.value}`);
  
  // 如果队列为空且没有正在播放的音频，直接显示结束弹窗
  if (audioPlayQueue.value.length === 0 && !isAudioQueuePlaying.value) {
    console.log('[Interview] ⚠️ 没有结束语音频，直接显示结束弹窗');
    waitingForClosingRemarks.value = false;
    stopMediaDevices();
    isInterviewStarted.value = false;
    isShowEndModal.value = true;
    setTimeout(() => {
      router.push('/');
    }, 5000);
  }
  
  ElMessage.success(`面试已结束，平均得分: ${message.summary?.average_score || 'N/A'}`);
};

const handleRedirect = (message) => {
  if (message.target === 'home') {
    router.back();
  }
};

// ==================== 录制控制 ====================

// 视频录制（保持原有功能）
const startVideoRecording = () => {
  if (!localStream.value) return;

  const options = { mimeType: 'video/webm; codecs=vp9' };

  try {
    mediaRecorder.value = new MediaRecorder(localStream.value, options);
  } catch (e) {
    mediaRecorder.value = new MediaRecorder(localStream.value);
  }

  mediaRecorder.value.ondataavailable = (event) => {
    if (event.data && event.data.size > 0 && wsVideo.value && wsVideo.value.readyState === WebSocket.OPEN) {
      wsVideo.value.send(event.data);
    }
  };

  mediaRecorder.value.start(1000);
};

// 开始录制用户回答
const startRecordingAnswer = () => {
  if (!localStream.value || isRecordingAnswer.value) return;
  
  isRecordingAnswer.value = true;
  const audioChunks = [];
  
  // 创建仅音频的流
  const audioStream = new MediaStream(localStream.value.getAudioTracks());
  
  try {
    audioRecorder.value = new MediaRecorder(audioStream, { mimeType: 'audio/webm' });
  } catch (e) {
    audioRecorder.value = new MediaRecorder(audioStream);
  }
  
  audioRecorder.value.ondataavailable = (event) => {
    if (event.data.size > 0) {
      audioChunks.push(event.data);
    }
  };
  
  audioRecorder.value.onstop = async () => {
    isRecordingAnswer.value = false;
    
    // 合并音频数据
    const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
    
    // 转换为 Base64 并发送
    const reader = new FileReader();
    reader.onloadend = () => {
      const base64Data = reader.result.split(',')[1];
      sendInterviewMessage({
        type: 'audio',
        data: base64Data
      });
    };
    reader.readAsDataURL(audioBlob);
  };
  
  // 开始录制（不再设置自动超时，由用户手动点击提交）
  audioRecorder.value.start();
  console.log('[Recording] 🎤 Started recording - waiting for user to submit');
};

// 停止录制用户回答
const stopRecordingAnswer = () => {
  if (audioRecorder.value && audioRecorder.value.state === 'recording') {
    audioRecorder.value.stop();
  }
};

// 手动提交回答
const submitAnswer = () => {
  if (!canSubmitAnswer.value && !isRecordingAnswer.value) {
    ElMessage.warning('请等待面试官说完后再提交回答');
    return;
  }
  
  // 如果还在等待提交状态，开始录音
  if (isWaitingForSubmit.value && !isRecordingAnswer.value) {
    isWaitingForSubmit.value = false;
    startRecordingAnswer();
    ElMessage.info('正在录音，再次点击提交完成回答');
    return;
  }
  
  // 如果正在录音，停止并提交
  if (isRecordingAnswer.value) {
    stopRecordingAnswer();
    canSubmitAnswer.value = false;
    ElMessage.success('回答已提交');
  }
};

// 使用文本回答（调试用）
const submitTextAnswer = (text) => {
  sendInterviewMessage({
    type: 'text',
    data: text
  });
};

// ==================== 停止所有媒体 ====================

const stopMediaDevices = () => {
  // 停止音频录制
  if (audioRecorder.value && audioRecorder.value.state !== 'inactive') {
    audioRecorder.value.stop();
  }
  
  // 停止视频录制
  if (mediaRecorder.value && mediaRecorder.value.state !== 'inactive') {
    mediaRecorder.value.stop();
  }

  // 关闭视频 WebSocket
  if (wsVideo.value) {
    wsVideo.value.close();
    wsVideo.value = null;
  }

  // 关闭面试 WebSocket
  if (wsInterview.value) {
    wsInterview.value.close();
    wsInterview.value = null;
  }

  // 停止媒体流
  if (localStream.value) {
    localStream.value.getTracks().forEach(track => track.stop());
    localStream.value = null;
    if (selfVideoRef.value) {
      selfVideoRef.value.srcObject = null;
    }
  }
  
  // 关闭音频上下文
  if (audioContext.value) {
    audioContext.value.close();
    audioContext.value = null;
  }
};

// ==================== 用户操作处理 ====================

// 点击"确认开始"
const handleStartInterview = async () => {
  isLoading.value = true;
  loadingText.value = '正在初始化媒体设备...';
  
  const success = await initMediaDevices();
  if (success) {
    isShowStartModal.value = false;
    isInterviewStarted.value = true;
    startTotalTimer();

    // 启动视频流 WebSocket
    initVideoWebSocket();

    // 启动面试会话 WebSocket
    initInterviewWebSocket();
  } else {
    isLoading.value = false;
  }
};

// 用户确认准备好开始
const handleReadyToStart = () => {
  interviewStatus.value = 'in_progress';
  sendInterviewMessage({ type: 'ready' });
};

// 点击"结束面试"
const handleEndInterview = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要结束面试吗？',
      '确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    );
    
    console.log('[Interview] 🛑 User requested end interview');
    
    // 停止计时
    clearInterval(timerInterval);
    
    // 停止录音
    if (audioRecorder.value && audioRecorder.value.state === 'recording') {
      audioRecorder.value.stop();
    }
    
    // 清空当前音频队列（不包括即将到来的结束语）
    // 停止当前正在播放的音频
    if (currentPlayingAudio) {
      currentPlayingAudio.pause();
      currentPlayingAudio.src = '';
      currentPlayingAudio = null;
    }
    audioPlayQueue.value = [];
    audioChunks = [];
    isAudioQueuePlaying.value = false;
    isPlayingAudio.value = false;
    
    // 发送结束消息给后端
    sendInterviewMessage({ type: 'end' });
    
    // 更新状态
    interviewStatus.value = 'ended';
    canSubmitAnswer.value = false;
    isWaitingForSubmit.value = false;
    
    // 设置标志：等待结束语播放完毕
    // 后端会发送结束语音频，等待音频队列播放完后再显示弹窗
    waitingForClosingRemarks.value = true;
    
    console.log('[Interview] ⏳ 已发送结束请求，等待结束语播放完毕...');
    
  } catch (error) {
    // 用户取消
    console.log('[Interview] ❌ 用户取消结束面试');
  }
};

// 返回首页
const goBackHome = () => {
  router.back();
};

// 保存面试记录
const saveInterviewRecord = async () => {
  if (interviewerId && positionId) {
    try {
      await createRecord({
        position_id: positionId,
        interviewer_id: interviewerId
      });
      ElMessage.success('面试记录已保存');
    } catch (error) {
      console.error('保存面试记录失败:', error);
    }
  }
};

// ==================== 设备控制 ====================

// 麦克风切换
const toggleSelfMute = () => {
  if (localStream.value) {
    const audioTracks = localStream.value.getAudioTracks();
    if (audioTracks.length > 0) {
      const newState = !audioTracks[0].enabled;
      audioTracks[0].enabled = newState;
      isSelfMuted.value = !newState;
    }
  }
};

// 摄像头切换
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

// 字幕开关
const toggleSubtitle = () => {
  isSubtitleOn.value = !isSubtitleOn.value;
};

// ==================== 计时器 ====================

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

// ==================== 生命周期 ====================

onUnmounted(() => {
  clearInterval(timerInterval);
  
  // 停止当前播放的音频
  if (currentPlayingAudio) {
    currentPlayingAudio.pause();
    currentPlayingAudio.src = '';
    currentPlayingAudio = null;
  }
  
  stopMediaDevices();
  // 清理音频队列
  audioPlayQueue.value = [];
  audioChunks = [];
  isAudioQueuePlaying.value = false;
});
</script>

<template>
  <div class="interview-practice">

    <div v-if="isShowStartModal" class="start-modal-overlay">
      <div class="start-modal">
        <div class="modal-icon">📹</div>
        <h3>准备好开始AI面试了吗？</h3>
        <p>点击确认后，浏览器将请求摄像头和麦克风权限。<br>
          AI面试官将根据您的简历进行智能提问。</p>
        <button class="start-btn" @click="handleStartInterview" :disabled="isLoading">
          {{ isLoading ? loadingText : '确认开始' }}
        </button>
      </div>
    </div>

    <div v-if="isLoading && isInterviewStarted && interviewStatus === 'initializing'" class="start-modal-overlay">
      <div class="start-modal">
        <div class="modal-icon">⏳</div>
        <h3>正在准备面试...</h3>
        <p>{{ loadingText }}</p>
        <div class="loading-spinner"></div>
      </div>
    </div>

    <div v-if="interviewStatus === 'waiting_ready' && !isShowEndModal" class="start-modal-overlay">
      <div class="start-modal">
        <div class="modal-icon">🎯</div>
        <h3>准备就绪</h3>
        <p>目标岗位: <strong>{{ jobName }}</strong><br>
          共准备了 <strong>{{ totalQuestions }}</strong> 个问题<br><br>
          准备好后点击开始正式面试</p>
        <button class="start-btn" @click="handleReadyToStart">
          开始面试
        </button>
      </div>
    </div>

    <div v-if="isShowEndModal" class="start-modal-overlay">
      <div class="start-modal">
        <div class="modal-icon">🏁</div>
        <h3>面试已结束</h3>
        <div v-if="interviewSummary" class="summary-info">
          <p>总问题数: {{ interviewSummary.total_questions }}</p>
          <p>平均得分: {{ interviewSummary.average_score }}/10</p>
          <p>面试时长: {{ interviewSummary.duration_minutes }} 分钟</p>
        </div>
        <p>摄像头与录音已关闭，面试记录已保存。</p>
        <button class="start-btn" @click="goBackHome">返回首页</button>
      </div>
    </div>

    <div class="practice-container" :class="{ 'blur-bg': isShowStartModal || isShowEndModal || interviewStatus === 'waiting_ready' || (isLoading && interviewStatus === 'initializing') }">
      
      <div class="practice-header">
        <div class="job-info">
          <h2>AI智能面试 {{ jobName ? `- ${jobName}` : '' }}</h2>
          <p>
            面试状态:
            <span class="status-text" :class="{ 'pending': !isInterviewStarted || interviewStatus !== 'in_progress' }">
              {{ interviewStatus === 'in_progress' ? '正在进行' : interviewStatus === 'ended' ? '已结束' : '等待中' }}
            </span>
            · 累计时长: <span class="timer">{{ totalTimer }}</span>
            <span v-if="totalQuestions > 0" class="progress">· {{ progressText }}</span>
          </p>
        </div>
        <div class="status-tag" :class="{ 'recording': isRecordingAnswer }">
          {{ isRecordingAnswer ? '🔴 录音中' : (interviewStatus === 'in_progress' ? '进行中' : '休息中') }}
        </div>
      </div>

      <div class="interview-main">

        <div class="interview-interactive">
          <div class="video-area">
            <div class="interviewer-video">
              <img v-if="isInterviewStarted" :src="interviewImg" alt="AI面试官" class="video-frame" />
              <div class="video-off" v-else>
                <span class="video-off-text">面试未进行</span>
              </div>
            </div>

            <div class="self-video">
              <video v-show="isInterviewStarted && !isSelfVideoOff" ref="selfVideoRef" autoplay playsinline muted
                class="self-video-frame"></video>
              <div v-if="!isInterviewStarted || isSelfVideoOff" class="self-video-placeholder">
                <span>{{ !isInterviewStarted ? '设备未启动' : '摄像头已关闭' }}</span>
              </div>
            </div>
            
            <div v-if="userTranscription && isRecordingAnswer" class="user-transcription">
              <span class="transcription-label">您的回答:</span>
              <span class="transcription-text">{{ userTranscription }}</span>
            </div>
          </div>

          <div class="interactive-controls">
            <button class="interactive-btn" :class="{ 'active': isSelfMuted }" @click="toggleSelfMute"
              :disabled="!isInterviewStarted">
              <span class="icon">{{ isSelfMuted ? '🔇' : '🎤' }}</span>
              {{ isSelfMuted ? '打开麦克风' : '关闭麦克风' }}
            </button>

            <button class="interactive-btn" :class="{ 'active': isSelfVideoOff }" @click="toggleSelfVideo"
              :disabled="!isInterviewStarted">
              <span class="icon">{{ isSelfVideoOff ? '📷' : '🚫' }}</span>
              {{ isSelfVideoOff ? '打开摄像头' : '关闭摄像头' }}
            </button>

            <button v-if="isRecordingAnswer" class="interactive-btn submit-btn recording" @click="submitAnswer">
              🔴 提交回答
            </button>
            <button v-else-if="isWaitingForSubmit && canSubmitAnswer" class="interactive-btn submit-btn ready" @click="submitAnswer">
              🎤 开始回答
            </button>
            <button v-else-if="isPlayingAudio || isAudioQueuePlaying" class="interactive-btn" disabled>
              🔊 面试官讲话中...
            </button>

            <button class="interactive-btn emergency" @click="handleEndInterview" :disabled="interviewStatus === 'ended'">
              🛑 结束面试
            </button>
          </div>
        </div>

        <div class="interviewer-panel">
          <div class="interviewer-avatar">
            <img :src="interviewerAvatar" alt="面试官头像" />
          </div>
          <div class="interviewer-info">
            <h3>{{ interviewerName }}</h3>
            <p class="position">{{ interviewerTitle }}</p>
            <p class="specialty">擅长领域：智能面试、简历分析、能力评估</p>
            <div class="interviewer-tags">
              <span class="tag">AI驱动</span>
              <span class="tag">实时分析</span>
              <span class="tag">智能追问</span>
            </div>
          </div>
          
          <div class="interviewer-subtitle">
            <div class="subtitle-header">
              <h4>实时对话字幕</h4>
              <span v-if="isPlayingAudio" class="speaking-indicator">🔊 播放中...</span>
            </div>
            <div class="subtitle-content" ref="subtitleContent">
              <p v-for="(line, index) in subtitleLines" :key="index" class="subtitle-line"
                :class="{ 'user-line': line.startsWith('[你]') }">
                {{ line }}
              </p>
              <p v-if="currentSubtitle" class="subtitle-line current">
                {{ currentSubtitle }}
              </p>
              <p v-if="!isInterviewStarted && subtitleLines.length === 0" class="subtitle-line waiting">
                等待面试开始...
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

/* 弹窗样式 */
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
  width: 420px;
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
  line-height: 1.6;
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

.start-btn:hover:not(:disabled) {
  background-color: #1d4ed8;
}

.start-btn:disabled {
  background-color: #9ca3af;
  cursor: not-allowed;
}

.summary-info {
  background-color: #f3f4f6;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
  text-align: left;
}

.summary-info p {
  margin: 8px 0;
  color: #374151;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e5e7eb;
  border-top-color: #2563eb;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 20px auto 0;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@keyframes modalPop {
  from {
    opacity: 0;
    transform: scale(0.9);
  }

  to {
    opacity: 1;
    transform: scale(1);
  }
}

.blur-bg {
  filter: blur(2px);
  pointer-events: none;
}

/* 容器与布局 */
.practice-container {
  max-width: 1200px;
  margin: 40px auto;
  padding: 0 20px;
  transition: filter 0.3s;
}

.practice-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
  padding: 16px 24px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
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
  color: #f59e0b;
}

.progress {
  color: #2563eb;
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

.status-tag.recording {
  background-color: #fef2f2;
  color: #ef4444;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.6;
  }
}

.interview-main {
  display: flex;
  gap: 24px;
  margin-bottom: 32px;
}

.interviewer-panel {
  width: 300px;
  background-color: #fff;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.interviewer-avatar {
  text-align: center;
  object-fit: contain;
}

.interviewer-avatar img {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #eee;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
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

.interview-interactive {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

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
  object-fit: contain;
  background-color: #c5efb3;
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

/* 用户语音转录显示 */
.user-transcription {
  position: absolute;
  bottom: 180px;
  left: 20px;
  right: 230px;
  background-color: rgba(0, 0, 0, 0.8);
  color: #fff;
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 14px;
}

.transcription-label {
  color: #10b981;
  font-weight: 500;
  margin-right: 8px;
}

.transcription-text {
  color: #fff;
}

/* 控制按钮 */
.interactive-controls {
  display: flex;
  gap: 12px;
  justify-content: center;
  padding: 16px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
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
  transition: all 0.2s;
}

.interactive-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.interactive-btn.active {
  background-color: #fef2f2;
  color: #ef4444;
  border-color: #fecaca;
}

.interactive-btn.submit-btn {
  background-color: #10b981;
  color: #fff;
  border-color: #10b981;
}

.interactive-btn.submit-btn.ready {
  background-color: #3b82f6;
  border-color: #3b82f6;
  animation: pulse 1.5s ease-in-out infinite;
}

.interactive-btn.submit-btn.recording {
  background-color: #ef4444;
  border-color: #ef4444;
  animation: recording-pulse 1s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.4); }
  50% { transform: scale(1.02); box-shadow: 0 0 0 8px rgba(59, 130, 246, 0); }
}

@keyframes recording-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.interactive-btn.submit-btn:hover {
  background-color: #059669;
}

.interactive-btn.emergency {
  background-color: #ef4444;
  color: #fff;
  border-color: #ef4444;
}

.interactive-btn.emergency:hover:not(:disabled) {
  background-color: #dc2626;
}

/* 字幕部分 */
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

.speaking-indicator {
  font-size: 12px;
  color: #10b981;
  animation: pulse 1s infinite;
}

.subtitle-content {
  height: 200px;
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
  margin: 8px 0;
  padding: 4px 0;
}

.subtitle-line.current {
  color: #2563eb;
  font-weight: 500;
}

.subtitle-line.user-line {
  color: #059669;
  background-color: #ecfdf5;
  padding: 4px 8px;
  border-radius: 4px;
}

.subtitle-line.waiting {
  color: #9ca3af;
  font-style: italic;
}

.subtitle-toggle {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #6b7280;
}

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

input:checked+.slider {
  background-color: #2563eb;
}

input:checked+.slider:before {
  transform: translateX(20px);
}
</style>