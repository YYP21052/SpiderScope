import time
import re
import os
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
        spider.logger.info(f"🚀 [Selenium] 正在启动浏览器 (强制本地模式)...")

        chrome_options = Options()
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--disable-popup-blocking")
        # chrome_options.add_argument("--headless") # 调试时不开启

        try:
            # =========================================================
            # 🔥 核心修改：指定本地驱动路径 (不联网)
            # =========================================================

            # 1. 自动寻找路径：假设你把 chromedriver.exe 放在了 backend/crawler/ 下
            # 获取当前文件 (middlewares.py) 的目录: .../backend/crawler/crawler/
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # 往上找两层，找到 backend/crawler/
            project_root = os.path.dirname(current_dir)

            # 拼接路径
            driver_path = os.path.join(project_root, "chromedriver.exe")

            # 检查文件到底在不在
            if not os.path.exists(driver_path):
                # 如果不在，再试一下上一层 (有时候目录结构不同)
                project_root = os.path.dirname(project_root)  # .../backend/
                driver_path = os.path.join(project_root, "chromedriver.exe")

            if not os.path.exists(driver_path):
                raise FileNotFoundError(f"❌ 找不到驱动文件！请确保 chromedriver.exe 在 {project_root} 目录下")

            spider.logger.info(f"📂 使用本地驱动: {driver_path}")

            # 2. 启动服务，明确指定 executable_path
            service = Service(executable_path=driver_path)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)

            self.driver.set_window_size(1400, 900)
            spider.logger.info("✅ [Selenium] 浏览器启动成功！")

        except Exception as e:
            spider.logger.error(f"❌ 浏览器启动失败: {e}")
            self.driver = None

    def spider_closed(self, spider):
        if self.driver:
            self.driver.quit()

    def process_request(self, request, spider):
        if not self.driver:
            return None

        target_spiders = ['boss', '51job', 'shixiseng', 'yingjiesheng', 'lagou']
        if spider.name not in target_spiders:
            return None

        try:
            self.driver.get(request.url)
            time.sleep(3)

            # --- 51job 翻页逻辑 ---
            if spider.name == '51job':
                page_match = re.search(r'pageNum=(\d+)', request.url)
                if page_match:
                    target_page = int(page_match.group(1))
                    if target_page > 1:
                        spider.logger.info(f"⚡ [51job] 跳转第 {target_page} 页...")
                        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        time.sleep(1)
                        self.driver.find_element(By.ID, "jump_page").clear()
                        self.driver.find_element(By.ID, "jump_page").send_keys(str(target_page))
                        time.sleep(0.5)
                        self.driver.find_element(By.CLASS_NAME, "jumpPage").click()
                        time.sleep(5)

                self.driver.execute_script("window.scrollBy(0, 500);")
                time.sleep(1)

            # --- Boss 逻辑 ---
            elif spider.name == 'boss':
                if "login" in self.driver.current_url:
                    spider.logger.warning("🚨 请扫码登录...")
                    time.sleep(15)

            return HtmlResponse(
                url=self.driver.current_url,
                body=self.driver.page_source,
                encoding='utf-8',
                request=request
            )
        except Exception as e:
            spider.logger.error(f"❌ 运行异常: {e}")
            return None