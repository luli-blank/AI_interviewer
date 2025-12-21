import request from '../utils/request'

export interface InterviewRecord {
  id: number
  user_id: number
  position_id: number
  interviewer_id: number
  time: string
  position_name?: string
  interviewer_name?: string
}

export interface CreateRecordParams {
  position_id: number
  interviewer_id: number
}

export function createRecord(data: CreateRecordParams) {
  return request<any, InterviewRecord>({
    url: '/api/interviewee/create_record',
    method: 'post',
    data
  })
}

export function getRecords() {
  return request<any, InterviewRecord[]>({
    url: '/api/interviewee/get_records',
    method: 'get'
  })
}
