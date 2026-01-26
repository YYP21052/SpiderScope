"""
@Time ： 2026/1/25
@File ：shixiseng_spider.py
@requirement: 爬取实习僧 (只抓列表模式)
"""
import scrapy
import re

class ShixisengSpider(scrapy.Spider):
    name = "shixiseng"
    allowed_domains = ["shixiseng.com"]
    # 搜索 Python，全国
    start_urls = ["https://www.shixiseng.com/interns?keyword=Python&page=1"]

    custom_settings = {
        # 🔥 标准化配置：抓满 200 条收工
        'CLOSESPIDER_ITEMCOUNT': 200,

        # 保持温和的抓取速度
        'DOWNLOAD_DELAY': 3,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'CONCURRENT_REQUESTS': 1,
    }

    def parse(self, response):
        print("=" * 50)
        print("🎓 正在解析 实习僧 (只抓列表模式)...")

        # 1. 定位职位卡片
        job_cards = response.css('.intern-wrap.intern-item')
        print(f"📊 本页发现 {len(job_cards)} 个职位")

        for card in job_cards:
            try:
                # --- 字段提取 ---

                # [标题]
                # 注意：实习僧有字体加密，部分文字可能显示为乱码（方块），
                # 对于演示项目，直接存下来即可，无需复杂的解密逻辑。
                title = card.css('.intern-detail__job a.title::text').get()

                # [薪资]
                salary = card.css('.intern-detail__job .day::text').get()

                # [公司]
                company = card.css('.intern-detail__company a.title::text').get()

                # [地点]
                location = card.css('.intern-detail__job .city::text').get()

                # [详情链接]
                relative_url = card.css('.intern-detail__job a.title::attr(href)').get()
                detail_url = response.urljoin(relative_url) if relative_url else None

                # [标签]
                tags = card.css('.advantage-wrap .intern-label::text').getall()
                tags_str = ",".join(tags)

                # --- 判空 ---
                if not company or not detail_url:
                    continue

                item = {
                    'title': title.strip() if title else "加密职位",
                    'company': company.strip(),
                    'salary': salary.strip() if salary else "面议",
                    'location': location.strip() if location else "全国",
                    'experience': "在校生", # 实习僧默认都是实习
                    'education': "本科",   # 默认本科
                    'source_website': 'shixiseng',
                    'detail_url': detail_url,
                    'tags': tags_str,
                    'welfare': "",
                    'company_size': "",
                    'industry': "",
                    # 🔥 核心修改：统一标记为待抓取
                    'job_description': "待抓取"
                }

                print(f"   ✅ [列表] {item['company']} | {item['salary']}")

                # 🔥 直接提交给 Pipeline
                yield item

            except Exception as e:
                self.logger.error(f"解析错误: {e}")

        # ==========================================
        # 翻页逻辑 (URL 替换法)
        # ==========================================
        current_page = 1
        page_match = re.search(r'page=(\d+)', response.url)
        if page_match:
            current_page = int(page_match.group(1))

        next_page = current_page + 1

        # 只有当本页抓到数据时才翻页
        if len(job_cards) > 0:
            print(f"🚀 [翻页] 准备前往第 {next_page} 页...")
            # 替换 URL 中的 page 参数
            if 'page=' in response.url:
                new_url = re.sub(r'page=\d+', f'page={next_page}', response.url)
            else:
                new_url = f"{response.url}&page={next_page}"

            yield scrapy.Request(new_url, callback=self.parse, dont_filter=True)
        else:
            print("🛑 没有更多数据了")