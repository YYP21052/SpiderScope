<template>
  <div class="app-container">
    <div class="header">
      <div class="logo">
        <h2>📊 JobRadar 数据大屏</h2>
      </div>
      <div class="user-info">
        <!-- 🔴 修改：点击按钮弹出表单 -->
        <!-- 🟢 导航到爬虫控制台 -->
        <el-button 
          v-if="userStore.accessToken" 
          type="success" 
          @click="$router.push('/crawl')"
        >
          🕷️ 进入爬虫控制台
        </el-button>
        <el-button v-else type="primary" @click="$router.push('/login')">
          登录 / 管理
        </el-button>

        <span v-if="userStore.accessToken" class="welcome-text">
          <el-icon><User /></el-icon> 欢迎, {{ userStore.username }}
        </span>
        <el-button v-if="userStore.accessToken" type="danger" plain size="small" @click="handleLogout">
          退出
        </el-button>


      </div>
    </div>

    <!-- ...stats-row and charts... --> 
    <!-- (保留中间的 stats-row, chart-card, table-card 不变) -->
    
    <el-row :gutter="20" class="stats-row">
      <el-col :span="8">
        <el-card shadow="hover" class="stats-card">
          <template #header>📦 总职位数</template>
          <!-- 使用后端聚合数据 -->
          <div class="stats-num">{{ statsOverview.total || 0 }}</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="stats-card">
          <template #header>💰 平均起薪 (月)</template>
          <div class="stats-num" style="color: #67C23A">¥ {{ statsOverview.avg_min_salary || 0 }}</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="stats-card">
          <template #header>🚀 最高薪资 (月)</template>
          <div class="stats-num" style="color: #F56C6C">¥ {{ statsOverview.max_salary || 0 }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="chart-card" shadow="never" v-loading="loading">
      <div id="salaryChart" style="width: 100%; height: 400px;"></div>
    </el-card>

    <el-card class="table-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span>📋 职位详细列表</span>
          <el-button type="primary" size="small" @click="refreshAll">🔄 刷新数据</el-button>
        </div>
      </template>

      <el-table :data="jobs" stripe style="width: 100%" height="400">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="title" label="职位名称" width="200" show-overflow-tooltip />
        <el-table-column prop="company" label="公司名称" width="200" show-overflow-tooltip />
        <el-table-column label="薪资范围" width="180">
          <template #default="scope">
            <el-tag type="success" v-if="scope.row.min_salary">
              {{ scope.row.min_salary }} - {{ scope.row.max_salary }} 元
            </el-tag>
            <span v-else>面议</span>
          </template>
        </el-table-column>
        <el-table-column prop="location" label="城市" width="100" />
        <el-table-column prop="education" label="学历" width="100" />
        <el-table-column prop="source_website" label="来源" width="100">
          <template #default="scope">
            <el-tag type="info" effect="plain">{{ scope.row.source_website }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作">
          <template #default="scope">
            <el-link type="primary" :href="scope.row.detail_url" target="_blank">查看原帖</el-link>
          </template>
        </el-table-column>
      </el-table>
    </el-card>



  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import axios from 'axios'
import * as echarts from 'echarts'
import { useUserStore } from '../stores/user'
import { useRouter } from 'vue-router'
import { User } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// --- 变量定义 ---
const userStore = useUserStore()
const router = useRouter()
const loading = ref(false)

const jobs = ref([]) 
const statsOverview = ref({ total: 0, avg_min_salary: 0, max_salary: 0 })

// --- 核心逻辑 ---

// ... (fetchList 等函数保持不变，因为我们已经在上一步更新了它们)

// ... (后面代码保持不变) ...

// 1. 获取列表数据
const fetchList = async () => {
  const token = userStore.accessToken
  // 🟢 修改：不强制登录
  const config = {}
  if (token) {
     config.headers = { 'Authorization': `Bearer ${token}` }
  }

  try {
    const res = await axios.get('http://127.0.0.1:8000/api/jobs/list/', config)
    jobs.value = res.data
    // 列表获取后渲染图表
    renderChart()
  } catch (err) {
    console.error(err)
    // 只有 401 且确实有 token 时才可能是过期
    if (err.response?.status === 401 && token) {
        userStore.logout()
    }
  }
}

// 2. 获取统计数据 (新接口)
const fetchStats = async () => {
  try {
    // 这个接口是 AllowAny，不需要 Token，但带上也没事
    const res = await axios.get('http://127.0.0.1:8000/api/jobs/stats/')
    statsOverview.value = res.data.overview
  } catch (err) {
    console.error("Fetch stats failed", err)
  }
}

// 整合刷新
const refreshAll = async () => {
    loading.value = true
    await Promise.all([fetchList(), fetchStats()])
    loading.value = false
    ElMessage.success('数据已更新')
}

// 3. 渲染 ECharts 图表
const renderChart = () => {
  // 数据清洗：将薪资归类到各个区间
  const ranges = { '10k以下': 0, '10k-15k': 0, '15k-20k': 0, '20k-30k': 0, '30k以上': 0 }

  jobs.value.forEach(job => {
    const salary = job.min_salary
    if (salary === 0) return // 跳过面议

    if (salary < 10000) ranges['10k以下']++
    else if (salary < 15000) ranges['10k-15k']++
    else if (salary < 20000) ranges['15k-20k']++
    else if (salary < 30000) ranges['20k-30k']++
    else ranges['30k以上']++
  })

  // 等待 DOM 更新后初始化图表
  nextTick(() => {
    const chartDom = document.getElementById('salaryChart')
    // 防止重复初始化 (如果已有实例则先销毁)
    if (echarts.getInstanceByDom(chartDom)) {
      echarts.getInstanceByDom(chartDom).dispose()
    }

    const myChart = echarts.init(chartDom)
    const option = {
      title: { text: 'Python 职位起薪分布', left: 'center' },
      tooltip: { trigger: 'axis' },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: {
        type: 'category',
        data: Object.keys(ranges),
        axisLabel: { interval: 0 }
      },
      yAxis: { type: 'value', name: '职位数量' },
      series: [
        {
          name: '职位数',
          type: 'bar',
          data: Object.values(ranges),
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#83bff6' },
              { offset: 0.5, color: '#188df0' },
              { offset: 1, color: '#188df0' }
            ])
          },
          label: { show: true, position: 'top' }
        }
      ]
    }
    myChart.setOption(option)

    // 监听窗口大小改变，图表自适应
    window.addEventListener('resize', () => myChart.resize())
  })
}

// 4. 退出登录
const handleLogout = () => {
  ElMessageBox.confirm('确定要退出登录吗?', '提示', {
    confirmButtonText: '退出',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    userStore.logout()
  })
}

onMounted(() => {
  refreshAll()
})
</script>

<style scoped>
.app-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  background: white;
  padding: 15px 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.05);
}
.logo h2 { margin: 0; color: #409EFF; }
.user-info { display: flex; align-items: center; gap: 15px; }
.welcome-text { color: #606266; font-size: 14px; display: flex; align-items: center; gap: 5px; }

.stats-row { margin-bottom: 20px; }
.stats-card { text-align: center; }
.stats-num { font-size: 24px; font-weight: bold; margin-top: 10px; }

.chart-card { margin-bottom: 20px; }
.table-card { background: white; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>