import request from '../utils/request'

export function createInterviewSession(data: FormData) {
  return request<any, { sessionId: string }>({
    url: '/api/interview/upload_resume',
    method: 'post',
    data,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}