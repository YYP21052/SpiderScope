import time
import re
import os
import random
from scrapy.http import HtmlResponse
from scrapy import signals
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


class JobSeleniumMiddleware:
    def __init__(self):
        self.driver = None

    @classmethod
    def from_crawler(cls, crawler):
        middleware = cls()
        crawler.signals.connect(middleware.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(middleware.spider_closed, signal=signals.spider_closed)
        return middleware

    def spider_opened(self, spider):
        # =========================================================
        # 🔥 修改点 1：如果是 boss 爬虫，直接忽略！
        # 因为 boss 爬虫使用的是 DrissionPage 接管，不需要这里启动 Selenium
        # =========================================================
        if spider.name == 'boss':
            spider.logger.info("⚔️ [Boss] 检测到 DrissionPage 模式，跳过中间件 Selenium 启动...")
            return

        spider.logger.info(f"🚀 [Selenium] 正在配置高隐身模式浏览器...")

        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument("--disable-popup-blocking")

        # 🔥 基础隐身设置
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        try:
            # 路径查找逻辑
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)  # backend/crawler/
            driver_path = os.path.join(project_root, "chromedriver.exe")

            if not os.path.exists(driver_path):
                project_root = os.path.dirname(project_root)  # backend/
                driver_path = os.path.join(project_root, "chromedriver.exe")

            if not os.path.exists(driver_path):
                spider.logger.warning(f"⚠️ 未找到驱动，尝试系统默认路径...")
                service = Service()
            else:
                spider.logger.info(f"📂 使用本地驱动: {driver_path}")
                service = Service(executable_path=driver_path)

            self.driver = webdriver.Chrome(service=service, options=options)

            # 🔥🔥🔥 核弹级隐身 (给 51job/应届生/实习僧 使用) 🔥🔥🔥
            stealth_js = """
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
            Object.defineProperty(navigator, 'languages', { get: () => ['zh-CN', 'zh'] });
            window.chrome = { runtime: {} };
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                Promise.resolve({ state: 'granted' }) :
                originalQuery(parameters)
            );
            """
            self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": stealth_js
            })

            self.driver.set_window_size(1400, 900)
            spider.logger.info("✅ [Selenium] 浏览器启动成功")

        except Exception as e:
            spider.logger.error(f"❌ 浏览器启动失败: {e}")
            self.driver = None

    def spider_closed(self, spider):
        # Boss 爬虫没有启动 Selenium，所以不需要关闭
        if spider.name == 'boss':
            return

        if self.driver:
            spider.logger.info("🛑 正在关闭浏览器...")
            self.driver.quit()

    def process_request(self, request, spider):
        # =========================================================
        # 🔥 修改点 2：如果是 boss 爬虫，直接返回伪造响应！
        # 这样 Scrapy 就不会去下载，而是直接进 parse 函数让 DrissionPage 接管
        # =========================================================
        if spider.name == 'boss':
            return HtmlResponse(
                url=request.url,
                body=b"", # 空内容，反正 DrissionPage 不用这个
                encoding='utf-8',
                request=request
            )

        # --- 以下是原本的 Selenium 处理逻辑 (给其他爬虫用) ---
        if not self.driver:
            return None

        # 白名单：只处理 51job/shixiseng/yingjiesheng (已移除 lagou)
        target_spiders = ['51job', 'shixiseng', 'yingjiesheng']
        if spider.name not in target_spiders:
            return None

        try:
            # 防止重复刷新
            if self.driver.current_url != request.url:
                self.driver.get(request.url)
            else:
                spider.logger.info("⚡ 浏览器已在当前页面，跳过加载...")

            # 等待逻辑
            if spider.name == '51job':
                time.sleep(random.uniform(2, 5))
            else:
                time.sleep(random.uniform(2, 4))

            # --- 51job 翻页逻辑 ---
            if spider.name == '51job' and 'pageNum=' in request.url:
                page_match = re.search(r'pageNum=(\d+)', request.url)
                if page_match:
                    target_page = int(page_match.group(1))
                    if target_page > 1:
                        spider.logger.info(f"⚡ [51job] 正在跳转第 {target_page} 页...")
                        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        time.sleep(1)
                        try:
                            input_box = self.driver.find_element(By.ID, "jump_page")
                            input_box.clear()
                            input_box.send_keys(str(target_page))
                            time.sleep(0.5)
                            jump_btn = self.driver.find_element(By.CLASS_NAME, "jumpPage")
                            jump_btn.click()
                            time.sleep(5)
                        except Exception as e:
                            spider.logger.warning(f"翻页操作遇到小问题: {e}")

                self.driver.execute_script("window.scrollBy(0, 500);")

            return HtmlResponse(
                url=self.driver.current_url,
                body=self.driver.page_source,
                encoding='utf-8',
                request=request
            )

        except Exception as e:
            spider.logger.error(f"❌ Selenium 运行异常: {e}")
            return None