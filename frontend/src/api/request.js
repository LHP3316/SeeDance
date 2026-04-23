import axios from 'axios'
import { ElMessage } from 'element-plus'

// 从环境变量获取API地址，如果没有则使用相对路径
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

const request = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000
})

request.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

request.interceptors.response.use(
  response => response.data,
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    ElMessage.error(error.response?.data?.detail || '请求失败')
    return Promise.reject(error)
  }
)

export default request
