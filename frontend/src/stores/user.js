// frontend/src/stores/user.js
import { defineStore } from "pinia";
import { ref } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'


export const useUserStore = defineStore('user',()=>{
    // 从硬盘中获取 token 防止token被刷新后丢失
    const accessToken = ref(localStorage.getItem('access_token') || ' ')
    const refreshToken=ref(localStorage.getItem('refresh_token') || ' ')
    const username = ref(localStorage.getItem('username') || ' ')

    const login = async (loginForm)=>{
        try{
            // 发送请求给 Django
            const response = await axios.post('http://127.0.0.1:8000/api/token/',loginForm)

            const {access,refresh} =response.data

            accessToken.value = access
            refreshToken.value = refresh
            username.value = loginForm.username


            localStorage.setItem('access_token', access)
            localStorage.setItem('refresh_token', refresh)
            localStorage.setItem('username', loginForm.username)

            return true
        }catch (error){
            ElMessage.error('登录失败，请检查用户名或密码')
            return false
        }
    }
    // 登出功能
    const logout=()=>{
        // 清空内存
        accessToken.value = ''
        refreshToken.value = ''
        username.value = ''

        // 清空硬盘
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        localStorage.removeItem('username')

        location.reload() // 强制刷新页面，重置所有状态
    }

    return { accessToken, refreshToken, username, login, logout }
})
