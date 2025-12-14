import request from '../utils/request'
 
export interface ReportSchema {
    total: number
    personality_type: string
    career_preferences: string[]
    strengths: string[]
    weaknesses: string[]
    summary:string
}

export function getReport() {
  return request<any, ReportSchema>({
    url: '/api/interviewee/generate_report',
    method: 'get',
  })
}