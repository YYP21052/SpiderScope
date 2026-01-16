# Scrapy settings for crawler project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import os
import sys
import django

# 获取当前文件的路径
# current: .../backend/crawler/crawler/
current_dir = os.path.dirname(os.path.abspath(__file__))
# print(f"当前文件路径：{current_dir}")

# 往上跳 2 层，找到 backend 目录
#  .../backend/crawler/crawler <- 目前
#  .../backend/crawler
#  .../backend (这里有 manage.py)
backend_path = os.path.dirname(os.path.dirname(current_dir))

# 将 backend 目录加入系统路径，这样 Python 才能找到 'spiderscope' 模块
sys.path.append(backend_path)

# --- 调试代码 ---
# print(f"DEBUG: Backend 路径设为: {backend_path}")
# print(f"DEBUG: Backend 目录下有哪些文件? {os.listdir(backend_path)}")
# -------------------------------------

# 指定 Django 的配置文件 (假设你的 Django 项目名叫 spiderscope)
os.environ['DJANGO_SETTINGS_MODULE'] = 'spiderscope.settings'

# 启动 Django
django.setup()


BOT_NAME = "crawler"

SPIDER_MODULES = ["crawler.spiders"]
NEWSPIDER_MODULE = "crawler.spiders"

ADDONS = {}


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = "crawler (+http://www.yourdomain.com)"

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Concurrency and throttling settings
#CONCURRENT_REQUESTS = 16
CONCURRENT_REQUESTS_PER_DOMAIN = 1
DOWNLOAD_DELAY = 1

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#    "Accept-Language": "en",
#}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    "crawler.middlewares.CrawlerSpiderMiddleware": 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    "crawler.middlewares.CrawlerDownloaderMiddleware": 543,
#}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
# pipe一般为关闭状态
# ITEM_PIPELINES = {
#    "crawler.pipelines.CrawlerPipeline": 300,
#}
# 启用管道，数字 300 表示优先级（数字越小越先执行）
ITEM_PIPELINES = {
   # 这里的 key 格式是：文件夹名.文件名.类名
   'crawler.pipelines.JobPostgresPipeline': 300,

   # 保留 Mongo 的功能
   # 'crawler.pipelines.MongoPipeline': 400,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = "httpcache"
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
FEED_EXPORT_ENCODING = "utf-8"
