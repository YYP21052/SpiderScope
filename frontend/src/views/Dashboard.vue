<template>
  <div class="app-container">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
      <h2>🕷️ JobRadar 爬虫控制台</h2>

      <div>
        <span style="margin-right: 15px; color: #666;">
          欢迎回来, {{ userStore.username }}
        </span>
        <el-button type="danger" plain @click="handleLogout">
          退出登录
        </el-button>
      </div>
    </div>

    <div class="header-actions">
      <el-button type="primary" size="large" @click="fetchTasks">
        🔄 刷新列表
      </el-button>
      <el-button type="success" size="large" @click="dialogVisible = true">
        ➕ 新建任务
      </el-button>
    </div>

    <el-table :data="tasks" style="width: 100%; margin-top: 20px" border v-loading="loading">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="name" label="任务名称" width="180">
        <template #default="scope"><strong>{{ scope.row.name }}</strong></template>
      </el-table-column>
      <el-table-column prop="target_url" label="目标 URL" show-overflow-tooltip />
      <el-table-column prop="status" label="状态" width="120">
        <template #default="scope">
          <el-tag :type="getStatusType(scope.row.status)">{{ scope.row.status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="frequency" label="频率" width="100" />
      <el-table-column label="操作" width="220">
        <template #default="scope">
          <el-button size="small" type="primary" plain @click="handleViewResults(scope.row.id)">
            👀 查看数据
          </el-button>
          <el-button size="small" type="danger" plain @click="handleDelete(scope.row.id)">
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" title="新建爬虫任务" width="500px">
      <el-form :model="createForm" label-width="100px">
        <el-form-item label="任务名称">
          <el-input v-model="createForm.name" placeholder="例如：Quotes 每日抓取" />
        </el-form-item>
        <el-form-item label="目标 URL">
          <el-input v-model="createForm.target_url" placeholder="https://..." />
        </el-form-item>
        <el-form-item label="执行频率">
          <el-select v-model="createForm.frequency" placeholder="选择频率">
            <el-option label="单次执行" value="once" />
            <el-option label="每天一次" value="daily" />
            <el-option label="每周一次" value="weekly" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleCreate">立即创建并运行</el-button>
        </span>
      </template>
    </el-dialog>

    <el-dialog v-model="resultDialogVisible" title="抓取结果 (MongoDB Data)" width="800px">
      <el-table v-if="spiderResults.length > 0" :data="spiderResults" border height="400">
        <el-table-column prop="text" label="名言内容" show-overflow-tooltip />
        <el-table-column prop="author" label="作者" width="150" />
        <el-table-column prop="tags" label="标签">
          <template #default="scope">
            <el-tag size="small" v-for="tag in scope.row.tags" :key="tag" style="margin-right:5px">
              {{ tag }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-else description="暂无数据或数据加载中" />
    </el-dialog>

  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import request from '../utils/request'
import { useUserStore } from '../stores/user'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'

// --- 变量定义 ---
const tasks = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const createForm = reactive({ name: '', target_url: 'https://quotes.toscrape.com/', frequency: 'once', spider_config: {} })
const userStore = useUserStore()
const router = useRouter()

// 新增：控制结果弹窗和存储结果数据
const resultDialogVisible = ref(false)
const spiderResults = ref([])

// --- 核心功能 ---

// 获取任务列表
const fetchTasks = async () => {
  loading.value = true
  try {
    // 用 request 代替 axios
    // 去掉 http://127... 前缀 (request.js 里配置了 baseURL)
    const response = await request.get('/api/tasks/')
    tasks.value = response.data
  } catch (error) {
    // 错误处理交给 request.js 的拦截器了，这里可以不写，或者简单记录
    console.error(error)
  } finally {
    loading.value = false
  }
}

// 创建任务
const handleCreate = async () => {
  if (!createForm.name || !createForm.target_url) {
    ElMessage.warning('请填写完整信息')
    return
  }
  try {
    // Post 请求也改成 request
    await request.post('/api/tasks/', createForm)

    ElMessage.success('任务创建成功！后台正在启动爬虫...')
    dialogVisible.value = false
    fetchTasks()
    createForm.name = ''
  } catch (error) {
    console.error(error) // 错误信息由拦截器统一弹出，这里不用重复弹窗
  }
}

// 删除任务
const handleDelete = (id) => {
  ElMessageBox.confirm('确定要删除这个任务吗?', '警告', { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' })
      .then(async () => {
        // Delete 请求也改成 request
        await request.delete(`/api/tasks/${id}/`)
        ElMessage.success('删除成功')
        fetchTasks()
      })
}

// 新增：查看数据逻辑
const handleViewResults = async (id) => {
  resultDialogVisible.value = true
  spiderResults.value = []

  try {
    //  Get 详情也改成 request
    const response = await request.get(`/api/tasks/${id}/results/`)
    spiderResults.value = response.data
    ElMessage.success(`成功加载 ${response.data.length} 条数据`)
  } catch (error) {
    console.error(error)
  }
}

const getStatusType = (status) => {
  const map = { 'PENDING': 'info', 'RUNNING': 'warning', 'COMPLETED': 'success', 'FAILED': 'danger' }
  return map[status] || 'info'
}

// 👇 新增：登出函数
const handleLogout = () => {
  ElMessageBox.confirm('确定要退出登录吗?', '提示', {
    confirmButtonText: '退出',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    userStore.logout() //
    // logout 内部会刷新页面，路由会自动把你踢回登录页
  })
}

onMounted(() => {
  fetchTasks()
})
</script>

<style>
.app-container { max-width: 1200px; margin: 0 auto; padding: 40px 20px; font-family: sans-serif; }
.header-actions { margin-bottom: 20px; display: flex; gap: 15px; }
</style>