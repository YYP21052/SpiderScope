<template>
  <div class="app-container">
    <h1>🕷️ SpiderScope 爬虫控制台</h1>

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
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

// --- 变量定义 ---
const tasks = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const createForm = reactive({ name: '', target_url: 'https://quotes.toscrape.com/', frequency: 'once', spider_config: {} })

// 新增：控制结果弹窗和存储结果数据
const resultDialogVisible = ref(false)
const spiderResults = ref([])

// --- 核心功能 ---

// 1. 获取任务列表
const fetchTasks = async () => {
  loading.value = true
  try {
    const response = await axios.get('http://127.0.0.1:8000/api/tasks/')
    tasks.value = response.data
  } catch (error) {
    ElMessage.error('无法连接后端')
  } finally {
    loading.value = false
  }
}

// 2. 创建任务
const handleCreate = async () => {
  if (!createForm.name || !createForm.target_url) {
    ElMessage.warning('请填写完整信息')
    return
  }
  try {
    await axios.post('http://127.0.0.1:8000/api/tasks/', createForm)
    ElMessage.success('任务创建成功！后台正在启动爬虫...')
    dialogVisible.value = false
    fetchTasks()
    createForm.name = ''
  } catch (error) {
    ElMessage.error('创建失败: ' + error.message)
  }
}

// 3. 删除任务
const handleDelete = (id) => {
  ElMessageBox.confirm('确定要删除这个任务吗?', '警告', { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' })
      .then(async () => {
        await axios.delete(`http://127.0.0.1:8000/api/tasks/${id}/`)
        ElMessage.success('删除成功')
        fetchTasks()
      })
}

// 4. 新增：查看数据逻辑
const handleViewResults = async (id) => {
  // 先打开弹窗，显示加载状态
  resultDialogVisible.value = true
  spiderResults.value = [] // 清空之前的数据

  try {
    // 请求 Django 的 results 接口
    const response = await axios.get(`http://127.0.0.1:8000/api/tasks/${id}/results/`)
    spiderResults.value = response.data
    ElMessage.success(`成功加载 ${response.data.length} 条数据`)
  } catch (error) {
    ElMessage.error('获取数据失败，请检查 Django 是否报错')
  }
}

const getStatusType = (status) => {
  const map = { 'PENDING': 'info', 'RUNNING': 'warning', 'COMPLETED': 'success', 'FAILED': 'danger' }
  return map[status] || 'info'
}

onMounted(() => {
  fetchTasks()
})
</script>

<style>
.app-container { max-width: 1200px; margin: 0 auto; padding: 40px 20px; font-family: sans-serif; }
.header-actions { margin-bottom: 20px; display: flex; gap: 15px; }
</style>