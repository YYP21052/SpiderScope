// frontend/src/stores/user.js
import { defineStore } from "pinia";
import { ref } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

export const useUserStore = defineStore('user', () => {
    // 1. 初始化状态
    // ⚠️ 修改：默认值改为 '' (空字符串)，避免逻辑判断出错
    const accessToken = ref(localStorage.getItem('access_token') || '')
    const refreshToken = ref(localStorage.getItem('refresh_token') || '')
    const username = ref(localStorage.getItem('username') || '')
    // 新增：用户是否为管理员
    const isStaff = ref(localStorage.getItem('is_staff') === 'true')

    // 2. 登录动作
    const login = async (loginForm) => {
        try {
            // 发送请求给 Django
            // 注意：这里我们假设后端接口是 /api/token/
            const response = await axios.post('http://127.0.0.1:8000/api/token/', loginForm)

            const { access, refresh, is_staff, is_superuser } = response.data

            // 更新 Pinia 状态
            accessToken.value = access
            refreshToken.value = refresh
            username.value = loginForm.username
            // 只要是 staff 或者是 superuser 都算管理员
            const isAdmin = is_staff || is_superuser
            isStaff.value = isAdmin

            // 更新硬盘 (Local Storage)
            localStorage.setItem('access_token', access)
            localStorage.setItem('refresh_token', refresh)
            localStorage.setItem('username', loginForm.username)
            localStorage.setItem('is_staff', isAdmin)

            ElMessage.success(`欢迎回来, ${loginForm.username}!`)
            return true
        } catch (error) {
            console.error(error)
            ElMessage.error('登录失败，请检查用户名或密码')
            return false
        }
    }

    // 3. 登出动作
    const logout = () => {
        // 清空内存
        accessToken.value = ''
        refreshToken.value = ''
        username.value = ''
        isStaff.value = false

        // 清空硬盘
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        localStorage.removeItem('username')
        localStorage.removeItem('is_staff')

        // 刷新页面，确保路由守卫重新执行
        location.reload()
    }

    return { accessToken, refreshToken, username, isStaff, login, logout }
})