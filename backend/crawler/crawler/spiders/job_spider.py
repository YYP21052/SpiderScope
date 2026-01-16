"""
@Time ： 2026/1/16
@Auth ： CST21052
@File ：job_spider.py
@IDE ：PyCharm
@Motto：Do one thing at a time, and do well.
@requirement:
"""
import scrapy

class JobSpider(scrapy.Spider):
    # 这个名字非常重要，命令行里用的就是它
    name = "job_spider"

    allowed_domains = ["books.toscrape.com"]
    start_urls = ["http://books.toscrape.com/catalogue/category/books/travel_2/index.html"]

    def parse(self, response):
        # 找到页面上所有的书 (article 标签)
        books = response.css('article.product_pod')

        for book in books:
            # 1. 提取数据
            title = book.css('h3 a::attr(title)').get()
            price = book.css('p.price_color::text').get()
            relative_url = book.css('h3 a::attr(href)').get()
            full_url = response.urljoin(relative_url)  # 拼接完整 URL

            # 2. 包装成字典 (对应 Pipeline 里的 item)
            # 我们把书的信息“伪装”成职位信息
            yield {
                'title': title,  # 书名 -> 职位名
                'company': "Python Books Inc.",  # 虚拟公司
                'salary': price,  # 价格 -> 薪资
                'location': "London, UK",  # 虚拟地点
                'detail_url': full_url,  # 详情页 (用来去重)
                'source_website': "BooksScrape"  # 来源
            }

        # (可选) 翻页逻辑：如果还有下一页，继续爬
        next_page = response.css('li.next a::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse)