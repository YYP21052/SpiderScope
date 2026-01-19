import scrapy
from core.models import Job  # 引入我们定义好的模型

class BossSpider(scrapy.Spider):
    name = "boss"  # 👈 这个名字必须在中间件的 target_spiders 列表里
    allowed_domains = ["zhipin.com"]
    
    # 直接访问登录页面
    start_urls = ["https://www.zhipin.com/web/user/?ka=header-login"]

    def parse(self, response):
        # 这里的 response 已经是 Selenium 渲染后的结果了！
        
        # 测试：打印一下页面标题，证明我们进去了
        page_title = response.css('title::text').get()
        if page_title:
            self.logger.info(f"🎉 登录后页面标题: {page_title}")
        self.logger.info(f"当前 URL: {response.url}")
        # (今天先不写解析代码，先确认能跑通)
