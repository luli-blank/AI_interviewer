import request from '../utils/request'
 
export interface ReportSchema {
    total: number
    personality_type: string
    career_preferences: string[]
    strengths: string[]
    weaknesses: string[]
    summary:string

    competency_radar: CompetencyRadarItem[]
    motivation_values: MotivationValues
}

export interface CompetencyRadarItem {
  name: string
  score: number
}

export interface MotivationValues {
  maslow_focus: string[]
  motivation_summary: string
  ideal_environment: string[]
  risk_warnings: string[]
}

export function getReport() {
  return request<any, ReportSchema>({
    url: '/api/interviewee/generate_report',
    method: 'get',
  })
}