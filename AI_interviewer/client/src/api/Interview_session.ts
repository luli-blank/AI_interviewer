/**
 * 面试会话相关API
 */
import request from '../utils/request'

/**
 * 获取面试会话状态
 * @param sessionId 会话ID
 */
export function getSessionStatus(sessionId: string) {
  return request({
    url: `/interview/session/${sessionId}`,
    method: 'get'
  })
}

/**
 * 获取用户的面试历史记录列表
 * @param userId 用户ID
 */
export function getInterviewHistory(userId: string) {
  return request({
    url: `/interview/history/${userId}`,
    method: 'get'
  })
}

/**
 * 下载面试记录CSV文件
 * @param filename 文件名
 */
export function downloadInterviewRecord(filename: string) {
  const baseUrl = import.meta.env.VITE_API_BASE_URL || ''
  window.open(`${baseUrl}/interview/download/${filename}`, '_blank')
}

/**
 * 构建面试WebSocket URL
 */
export function buildInterviewWSUrl(): string {
  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL
  if (!apiBaseUrl) {
    throw new Error('VITE_API_BASE_URL not configured')
  }

  const urlObj = new URL(apiBaseUrl)
  urlObj.protocol = urlObj.protocol.replace('http', 'ws')
  
  let basePath = urlObj.pathname
  if (basePath.endsWith('/')) {
    basePath = basePath.slice(0, -1)
  }

  const token = localStorage.getItem('token')
  return `${urlObj.origin}${basePath}/interview/ws/interview?token=${token}`
}

/**
 * 构建视频流WebSocket URL
 */
export function buildVideoWSUrl(): string {
  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL
  if (!apiBaseUrl) {
    throw new Error('VITE_API_BASE_URL not configured')
  }

  const urlObj = new URL(apiBaseUrl)
  urlObj.protocol = urlObj.protocol.replace('http', 'ws')
  
  let basePath = urlObj.pathname
  if (basePath.endsWith('/')) {
    basePath = basePath.slice(0, -1)
  }

  const token = localStorage.getItem('token')
  return `${urlObj.origin}${basePath}/ws/video_stream?token=${token}`
}
