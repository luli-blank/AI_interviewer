import request from '../utils/request'

export interface Interviewer {
  id: number
  name: string
  title?: string
  description?: string
  avatar?: string
  position_name?: string
}

export interface Position {
  id: number 
  position_name: string
  description?: string
  interviewers: Interviewer[]
} 


export function getPosition() {
    return request<any, Position[]>({
    url: '/api/interviewee/get_position',
    method: 'get',
  })
}

