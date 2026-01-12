import { createApp } from 'vue'
import App from './App.vue'

// 1. 引入 Element Plus 和 它的 CSS
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

const app = createApp(App)

// 2. 使用插件
app.use(ElementPlus)

app.mount('#app')