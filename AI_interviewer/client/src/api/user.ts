import request from '../utils/request'

// 定义接口返回的数据类型（根据你后端实际返回调整，这里仅作参考）
interface LoginResponse {
  code: number
  message: string
  data?: {
    token: string
    [key: string]: any
  }
}

// 登录接口
export function loginApi(data: object) {
  return request<any, LoginResponse>({
    url: '/api/interviewee/login', // 这里会自动拼接到 baseURL 后面
    method: 'post',
    data // 发送的用户名密码
  })
}