"""
@Time ： 2026/1/19
@File ：shixiseng_spider.py
@requirement: 爬取实习僧 (适配字体加密结构)
"""
import scrapy
import re

class ShixisengSpider(scrapy.Spider):
    name = "shixiseng"
    allowed_domains = ["shixiseng.com"]
    # 搜索 Python，全国
    start_urls = ["https://www.shixiseng.com/interns?keyword=Python&page=1"]

    custom_settings = {
        'CLOSESPIDER_ITEMCOUNT': 200,
        'DOWNLOAD_DELAY': 2,
    }

    def parse(self, response):
        print("=" * 50)
        print("🎓 正在解析 实习僧 (精准版)...")

        # 1. 定位最外层的卡片 (根据你提供的 class="intern-wrap interns-point intern-item")
        job_cards = response.css('.intern-wrap.intern-item')
        print(f"📊 本页发现 {len(job_cards)} 个职位")

        for card in job_cards:
            try:
                # --- 提取基础信息 (根据你的 HTML 修正) ---

                # 1. 标题 (在 .intern-detail__job 下的 a 标签)
                # 注意：这里抓下来可能是乱码，这是正常的，先存下来
                title = card.css('.intern-detail__job a.title::text').get()

                # 2. 薪资 (在 .intern-detail__job 下的 .day)
                salary = card.css('.intern-detail__job .day::text').get()

                # 3. 公司名 (在 .intern-detail__company 下的 a 标签)
                # 好消息：公司名通常不加密！
                company = card.css('.intern-detail__company a.title::text').get()

                # 4. 地点 (在 .intern-detail__job 下的 .city)
                location = card.css('.intern-detail__job .city::text').get()

                # 5. 详情链接
                relative_url = card.css('.intern-detail__job a.title::attr(href)').get()
                detail_url = response.urljoin(relative_url) if relative_url else None

                # 6. 标签 (提取 .advantage-wrap 下的 span)
                tags = card.css('.advantage-wrap .intern-label::text').getall()
                tags_str = ",".join(tags)

                # --- 判空 ---
                if not company or not detail_url:
                    continue

                # --- 构建数据 ---
                item = {
                    'title': title.strip() if title else "加密职位",
                    'company': company.strip(),
                    'salary': salary.strip() if salary else "面议",
                    'location': location.strip() if location else "全国",
                    'experience': "在校生",
                    'education': "本科",
                    'source_website': 'shixiseng',
                    'detail_url': detail_url,
                    'tags': tags_str,
                    'welfare': "",
                    'company_size': "",
                    'industry': "",
                    'job_description': ""
                }

                # 打印看看 (如果 title 是乱码，控制台可能显示方块，这是对的)
                print(f"   ✅ {item['company']} | {item['location']} | {item['salary']}")
                yield item

            except Exception as e:
                self.logger.error(f"解析错误: {e}")

        # ==========================================
        # 🔥 翻页逻辑 (保持不变)
        # ==========================================
        current_page = 1
        page_match = re.search(r'page=(\d+)', response.url)
        if page_match:
            current_page = int(page_match.group(1))

        next_page = current_page + 1
        if len(job_cards) > 0:
            print(f"🚀 [翻页] 前往第 {next_page} 页...")
            new_url = re.sub(r'page=\d+', f'page={next_page}', response.url)
            yield scrapy.Request(new_url, callback=self.parse, dont_filter=True)
        else:
            print("🛑 没有更多数据了")