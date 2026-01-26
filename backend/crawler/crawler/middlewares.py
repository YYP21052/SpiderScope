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


from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

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
        # Boss 爬虫跳过 (使用 DrissionPage)
        if spider.name == 'boss':
            spider.logger.info("⚔️ [Boss] 检测到 DrissionPage 模式，跳过中间件 Selenium 启动...")
            return

        spider.logger.info(f"🚀 [Selenium] 正在配置高隐身模式浏览器...")

        options = Options()
        # ⚠️ 注释掉 headless 模式，确保可以看到窗口
        # options.add_argument('--headless') 
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument("--disable-popup-blocking")
        
        # 显式指定窗口大小，避免某些反爬
        options.add_argument("--window-size=1400,900")

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
                # 尝试往上一级找
                project_root_up = os.path.dirname(project_root) # backend/
                driver_path_up = os.path.join(project_root_up, "chromedriver.exe")
                if os.path.exists(driver_path_up):
                    driver_path = driver_path_up

            service = None
            if os.path.exists(driver_path):
                spider.logger.info(f"📂 使用本地驱动: {driver_path}")
                service = Service(executable_path=driver_path)
            else:
                spider.logger.warning(f"⚠️ 未找到本地驱动 {driver_path}，尝试使用系统 PATH 中驱动...")
                service = Service()

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

            spider.logger.info("✅ [Selenium] 浏览器启动成功")

        except Exception as e:
            spider.logger.error(f"❌ 浏览器启动失败: {e}")
            self.driver = None

    def spider_closed(self, spider):
        if spider.name == 'boss':
            return
        if self.driver:
            spider.logger.info("🛑 正在关闭浏览器...")
            self.driver.quit()

    def process_request(self, request, spider):
        # Boss 爬虫跳过
        if spider.name == 'boss':
             return HtmlResponse(url=request.url, body=b"", encoding='utf-8', request=request)
             
        # ... (rest of logic)
        if not self.driver:
            return None

        # 白名单：只处理 51job/shixiseng/yingjiesheng (已移除 lagou)
        target_spiders = ['51job', 'shixiseng', 'yingjiesheng']
        if spider.name not in target_spiders:
            return None

        try:
            # 防止重复刷新
            if self.driver.current_url != request.url:
                # 显式设置页面加载超时，防止卡死
                self.driver.set_page_load_timeout(20)
                try:
                    self.driver.get(request.url)
                except TimeoutException:
                    spider.logger.warning("⚠️ 页面加载超时，尝试直接解析已加载内容...")
                    self.driver.execute_script("window.stop();")
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
                        
                        try:
                            # 🟢 优化：使用显式等待替代死等，防卡死
                            wait = WebDriverWait(self.driver, 10)
                            
                            input_box = wait.until(
                                EC.element_to_be_clickable((By.ID, "jump_page"))
                            )
                            input_box.clear()
                            input_box.send_keys(str(target_page))
                            
                            # 稍微歇一下防识别
                            time.sleep(0.5)
                            
                            jump_btn = wait.until(
                                EC.element_to_be_clickable((By.CLASS_NAME, "jumpPage"))
                            )
                            jump_btn.click()
                            
                            # 等待页面刷新完成 (检测 joblist 被重绘，或者简单 sleep)
                            time.sleep(5)
                            
                        except TimeoutException:
                            spider.logger.warning("⚠️ [翻页] 找不到翻页输入框，可能只有一页或元素变动")
                        except Exception as e:
                            spider.logger.warning(f"⚠️ [翻页] 操作遇到未知问题: {e}")

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