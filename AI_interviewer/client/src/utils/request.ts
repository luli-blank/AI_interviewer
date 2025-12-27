import axios from 'axios'




// 1. 创建 axios 实例
const service = axios.create({
  // 读取 .env 中的地址，如果读不到就用空字符串(防止报错)
    baseURL: import.meta.env.VITE_API_BASE_URL || '', 
    timeout: 60000 // 请求超时时间 60秒 (文件上传可能较慢)
})

// 2. 请求拦截器：每次请求前自动带上 Token
service.interceptors.request.use(
  (config) => {
    // 确保 headers 存在
    if (!config.headers) config.headers = {} as any
    
    // 从浏览器缓存取出 token
    const token = localStorage.getItem('token')
    if (token) {
      // 这里的 Header key 取决于后端，通常是 Authorization 或 X-Token
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 3. 响应拦截器：脱壳处理 & 统一报错
service.interceptors.response.use(
  (response) => {
    // Axios 默认包了一层 data，我们这里直接返回后端的数据
    const res = response.data
    return res
  },
  (error) => {
    // 处理 401 (未授权) 等网络错误
    console.error('请求拦截器报错:', error)
    return Promise.reject(error)
  }
)

export default service