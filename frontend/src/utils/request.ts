import axios from 'axios'
import { ElMessage } from 'element-plus'

const request = axios.create({
  baseURL: 'http://localhost:18080/api', // 指向咱们的 Java 后端
  timeout: 10000
})

// 请求拦截器：自动带上 Token
request.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => Promise.reject(error)
)

// 响应拦截器：统一报错
request.interceptors.response.use(
  response => response.data,
  error => {
    if (error.response && error.response.status === 401) {
      ElMessage.error('登录已过期，请重新登录')
      localStorage.removeItem('token')
      window.location.href = '/login'
    } else {
      ElMessage.error(error.response?.data?.message || '请求失败')
    }
    return Promise.reject(error)
  }
)

export default request