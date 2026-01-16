// frontend/src/utils/request.js
import axios from 'axios'
import { ElMessage } from 'element-plus'

// 创建 axios
const service = axios.create({
  baseURL: 'http://127.0.0.1:8000', // 你的后端地址
  timeout: 5000 // 请求超时时间
})

// 请求拦截器 (Request Interceptor)
// 作用：在请求发出去之前，自动把 Token 塞进去
service.interceptors.request.use(
  (config) => {
    // 从 localStorage 拿 Token (因为这里还没进入 Vue 组件，直接读硬盘最稳)
    const token = localStorage.getItem('access_token')

    if (token) {
      // 这里的 'Bearer ' 是后端 settings.py 里定义的 AUTH_HEADER_TYPES
      // 注意 Bearer 后面有个空格！
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器 (Response Interceptor)
// 作用：如果后端报错（比如 Token 过期了），在这里统一处理
service.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    // 如果是 401 错误，说明 Token 失效或没权限
    if (error.response && error.response.status === 401) {
      ElMessage.error('登录已过期，请重新登录')
      // 可选：这里可以强制跳转回登录页，或者清空 LocalStorage
    } else {
      ElMessage.error(error.message || '请求失败')
    }
    return Promise.reject(error)
  }
)

export default service