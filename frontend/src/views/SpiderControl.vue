<template>
  <div class="crawl-container">
    <div class="header">
      <h2>🕷️ 爬虫控制台</h2>
      <div class="user-info">
        <span>欢迎, {{ userStore.username }}</span>
        <el-button type="info" size="small" @click="$router.push('/')">返回首页</el-button>
        <el-button type="danger" size="small" @click="userStore.logout()">登出</el-button>
      </div>
    </div>

    <!-- 专门的爬虫启动卡片 -->
    <el-card class="control-box">
      <template #header>
        <div class="card-header">
          <span>🚀 启动一次新的抓取任务</span>
        </div>
      </template>

      <el-form label-position="top" :model="crawlForm" class="crawl-form">
        <el-form-item label="选择爬虫 (Spider)">
          <el-select v-model="crawlForm.spider_name" placeholder="选择目标网站" size="large" style="width: 100%">
            <!-- 🟢 支持 4 个爬虫 -->
            <el-option label="BOSS直聘 (Boss)" value="boss" />
            <el-option label="前程无忧 (51job)" value="51job" />
            <el-option label="实习僧 (Shixiseng)" value="shixiseng" />
            <el-option label="应届生求职网 (Yingjiesheng)" value="yingjiesheng" />
          </el-select>
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="职位关键词 (Keyword)">
              <el-input v-model="crawlForm.keyword" placeholder="例如: Java, Python" size="large">
                <template #prefix>
                   <el-icon><Search /></el-icon>
                </template>
              </el-input>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="城市 (City)">
              <el-input v-model="crawlForm.city" placeholder="例如: Shanghai, 全国" size="large">
                <template #prefix>
                   <el-icon><Location /></el-icon>
                </template>
              </el-input>
            </el-form-item>
          </el-col>
        </el-row>

        <div class="action-area">
          <el-button 
            type="primary" 
            size="large" 
            :loading="crawling" 
            @click="submitCrawl" 
            class="start-btn"
          >
            🔥 立即启动爬虫
          </el-button>
        </div>
        
        <div class="tips">
          <p>⚠️ 注意：Selenium 浏览器启动可能需要几秒钟，请耐心等待。</p>
          <p>⚠️ 如果浏览器窗口未弹出，请检查任务栏或相关驱动配置。</p>
        </div>
      </el-form>
      
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import axios from 'axios'
import { useUserStore } from '../stores/user'
import { ElMessage } from 'element-plus'
import { Search, Location } from '@element-plus/icons-vue'

const userStore = useUserStore()
const crawling = ref(false)

const crawlForm = reactive({
  spider_name: 'boss',
  keyword: 'Python',
  city: '全国'
})

const submitCrawl = async () => {
    if (!crawlForm.keyword) {
      ElMessage.warning('请输入关键词')
      return
    }
    
    crawling.value = true
    try {
        const token = userStore.accessToken
       
        await axios.post('http://127.0.0.1:8000/api/crawl/start/', 
            { 
              spider_name: crawlForm.spider_name,
              keyword: crawlForm.keyword,
              city: crawlForm.city 
            }, 
            { headers: { 'Authorization': `Bearer ${token}` } }
        )
        ElMessage.success(`🚀 [${crawlForm.spider_name}] 任务已触发，请观察后台浏览器窗口!`)
    } catch (err) {
        console.error(err)
        ElMessage.error('启动失败：' + (err.response?.data?.detail || err.message))
    } finally {
        crawling.value = false
    }
}
</script>

<style scoped>
.crawl-container {
  max-width: 800px;
  margin: 40px auto;
  padding: 0 20px;
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}
.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
}
.control-box {
  background: white;
  border-radius: 12px;
}
.crawl-form {
  padding: 20px 0;
}
.action-area {
  margin-top: 30px;
  text-align: center;
}
.start-btn {
  width: 100%;
  font-weight: bold;
  letter-spacing: 1px;
}
.tips {
  margin-top: 20px;
  color: #909399;
  font-size: 13px;
  background: #f4f4f5;
  padding: 10px;
  border-radius: 4px;
}
</style>
