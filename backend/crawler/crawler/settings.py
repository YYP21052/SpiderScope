import os
import sys
import django

current_dir = os.path.dirname(os.path.abspath(__file__))
backend_path = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(backend_path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'spiderscope.settings'
django.setup()

BOT_NAME = "crawler"
SPIDER_MODULES = ["crawler.spiders"]
NEWSPIDER_MODULE = "crawler.spiders"
ROBOTSTXT_OBEY = False
CLOSESPIDER_ITEMCOUNT = 500

# === 列表页抓取速度设置 ===
# 因为不进详情页了，可以稍微快一点，但为了过列表页的检测，保持 3秒 比较稳
DOWNLOAD_DELAY = 3
RANDOMIZE_DOWNLOAD_DELAY = True
CONCURRENT_REQUESTS_PER_DOMAIN = 1

DEFAULT_REQUEST_HEADERS = {
   "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
   "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# 必须启用 Selenium 中间件，因为 51job 列表页是动态的
DOWNLOADER_MIDDLEWARES = {
   'crawler.middlewares.JobSeleniumMiddleware': 543,
}

# MongoDB 配置
MONGO_URI = 'mongodb://mongo_user:mongo_password@127.0.0.1:27017/?authSource=admin'
MONGO_DATABASE = 'spider_data'

# 管道配置
ITEM_PIPELINES = {
   'crawler.pipelines.JobCleaningPipeline': 200,
   'crawler.pipelines.HybridPipeline': 300,
}

FEED_EXPORT_ENCODING = "utf-8"
LOG_LEVEL = 'WARNING'