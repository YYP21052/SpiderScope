import scrapy


class QuotesSpider(scrapy.Spider):
    name = "quotes"
    # 限制域名，限制只能访问allowed_domains中的域名，防止跑偏
    allowed_domains = ["quotes.toscrape.com"]
    # 爬虫开始的网址
    start_urls = ["https://quotes.toscrape.com/"]

    def parse(self, response):
        # Scrapy 的核心优势：CSS 选择器
        # 找到页面上所有的 class="quote" 的方块
        for quote in response.css('div.quote'):
            yield {
                # 意思：在当前方块里，找 class="text" 的 span 标签，提取里面的文字(::text)
                'text': quote.css('span.text::text').get(),
                # 意思：找 class="author" 的 small 标签，提取文字
                'author': quote.css('small.author::text').get(),
                # 意思：找 class="tags" 的 div 下面所有的 a 标签，提取文字
                # .getall() 会返回一个列表，比如 ['life', 'love']
                'tags': quote.css('div.tags a.tag::text').getall(),
            }

        # 翻页逻辑（自动爬下一页）
        # 寻找下一页的链接
        # 在 HTML 里，翻页按钮通常是 <li class="next"><a href="/page/2/">Next</a></li>
        # ::attr(href) 意思是：提取 a 标签里的 href 属性值（即 /page/2/）
        next_page = response.css('li.next a::attr(href)').get()
        # 如果找到了下一页（只要 next_page 不是空的）
        if next_page is not None:
            # 告诉 Scrapy：去跟进(follow)这个链接
            # 关键点：self.parse
            # 意思是：下载完下一页后，请继续用当前的 parse 函数来处理这一页的数据。
            # 这就形成了一个无限循环，直到没有下一页为止。
            yield response.follow(next_page, self.parse)