<script setup>
import { ref } from 'vue'
import { useUserStore } from '../stores/user' // 引入编写好的类
import { useRouter } from 'vue-router'
import { User, Lock } from '@element-plus/icons-vue' // 引入图标

const userStore = useUserStore() // 初始化对象
const router = useRouter()       // 初始化路由

const loading = ref(false) // 记录状态
// 登录表单
const form = ref({
  username: '',
  password: ''
})

const handleLogin = async () => {
  if (!form.value.username || !form.value.password) return

  loading.value = true
  // 调用 编写好的登录方法
  const success = await userStore.login(form.value)
  loading.value = false

  if (success) {
    // 登录成功，跳转到首页
    router.push('/')
  }
}

</script>

<template>
<div class="login-container">
    <el-card class="login-card">
      <template #header>
        <div class="card-header">
          <h2>🔐 JobRadar 登录</h2>
        </div>
      </template>

      <el-form :model="form" label-width="0px">
        <el-form-item>
          <el-input v-model="form.username" placeholder="用户名" prefix-icon="User" size="large" />
        </el-form-item>
        <el-form-item>
          <el-input
            v-model="form.password"
            placeholder="密码"
            prefix-icon="Lock"
            type="password"
            show-password
            size="large"
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" class="login-btn" @click="handleLogin" size="large">
            立即登录
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<style scoped>
.login-container {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f0f2f5;
}
.login-card {
  width: 400px;
}
.card-header {
  text-align: center;
}
.login-btn {
  width: 100%;
}
</style>