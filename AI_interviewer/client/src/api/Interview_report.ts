import request from '../utils/request'

interface ReportSchema {
  name: string
  position: string
  date: string
  duration: string
  emotions: { name: string, level: string }[]
  question_analysis: { question: string, score: number, comments: string }[]
  overall_score: { communication: number, logic: number, stress: number, total: number }
  strengths: string[]
  weaknesses: string[]
  summary: string
}

export function getInterviewReport() {
  return request<any, ReportSchema>({
    url: '/api/interviewee/generate_report',
    method: 'get',
  })
}