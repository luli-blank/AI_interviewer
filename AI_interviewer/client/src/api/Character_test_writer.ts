import request from '../utils/request'

// --- 1. 定义数据类型 ---

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

// --- 新增：提交相关的数据类型 ---

// 单个问答对结构
export interface SubmitAnswerItem {
  question_text: string // 题目原文
  answer_text: string   // 选项原文
}

// 提交给后端的整体 Payload 结构
export interface SubmitPayload {
  submission_time: string // ISO 8601 时间字符串
  answers: SubmitAnswerItem[]
}

// --- 定义 API 响应结构 ---

// 获取题目列表的响应
export interface SurveyResponse {
  code: number
  msg: string
  data: SurveyQuestion[]
}

// 通用响应 (用于提交问卷，后端可能只返回 code 和 msg，data 为 null)
export interface GeneralResponse {
  code: number
  msg: string
  data: any
}

// --- 2. 定义 API 请求函数 ---

/**
 * 获取问卷题目
 */
export function getQuestions() {
  // 这里的泛型 <any, SurveyResponse> 是为了让 TS 知道返回的数据结构
  // 第一个参数是请求体的类型(这里是any或undefined)，第二个是响应体的类型
  return request<any, SurveyResponse>({
    url: '/api/interviewee/questions', // 保持你原有的 URL
    method: 'get'
  })
}

/**
 * 提交问卷
 * @param data 包含时间戳和完整问答对的数据对象
 */
export function submitSurvey(data: SubmitPayload) {
  return request<any, GeneralResponse>({
    url: '/api/interviewee/submit_survey', // 假设后端路由在此路径
    method: 'post',
    data: data // 将构建好的 payload 放入 request body
  })
}