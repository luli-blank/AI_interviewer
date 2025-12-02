import request from '../utils/request'

// --- 1. 定义数据类型 (TypeScript 最佳实践) ---

// 选项结构
export interface SurveyOption {
  label: string
  value: string
}

// 题目结构
export interface SurveyQuestion {
  id: string
  title: string
  required: boolean
  options: SurveyOption[]
}

// 接口返回的整体结构
// 注意：这里的字段名 (code, message, data) 需要和你后端实际返回的一致
export interface SurveyResponse {
  code: number
  msg: string
  data: SurveyQuestion[]
}

// --- 2. 定义 API 请求函数 ---

export function getQuestions() {
  // 使用封装好的 request，自动继承 BaseURL 和拦截器配置
  return request<any, SurveyResponse>({
    url: '/api/interviewee/questions', // 接口地址
    method: 'get'
  })
}