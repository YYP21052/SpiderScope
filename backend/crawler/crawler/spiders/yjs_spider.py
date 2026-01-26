"""
@Time ： 2026/1/25
@File ：yjs_spider.py
@requirement: 爬取应届生求职网 (只抓列表模式)
"""
import scrapy
import json
import re

class YjsSpider(scrapy.Spider):
    name = "yingjiesheng"
    allowed_domains = ["yingjiesheng.com"]
    # 搜索 Python
    start_urls = ["https://q.yingjiesheng.com/jobs/search/Python"]

    custom_settings = {
        # 🔥 与 51job 保持一致：抓满 200 条收工
        'CLOSESPIDER_ITEMCOUNT': 200,
        'DOWNLOAD_DELAY': 3,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'CONCURRENT_REQUESTS': 1, # 保持温和
    }

    def parse(self, response):
        print("=" * 50)
        print("🎓 正在解析 应届生 (只抓列表模式)...")

        # 1. 定位职位卡片
        job_cards = response.css('.item-content')
        print(f"📊 本页发现 {len(job_cards)} 个职位")

        for card in job_cards:
            try:
                # --- 尝试解析 JSON (sensorsdata) ---
                data = {}
                json_str = card.attrib.get('sensorsdata')
                if json_str:
                    try:
                        data = json.loads(json_str)
                    except:
                        pass

                # --- 字段提取 ---

                # [标题]
                title = data.get('jobTitle')
                if not title:
                    title = card.css('.left-title-name .text-cut::text').get()

                # [公司]
                company = data.get('companyName')
                if not company:
                    company = card.css('.left-detail-company::text').get()

                # [薪资]
                salary = card.css('.right-salary::text').get()

                # [标签 & 地点]
                tags_raw = card.css('.left-tag-item::text').getall()
                location = tags_raw[0] if tags_raw else "全国" # 通常第一个是地点
                tags_str = ",".join(tags_raw)

                # [详情链接]
                job_id = data.get('jobId')
                if job_id:
                    detail_url = f"https://q.yingjiesheng.com/jobdetail/{job_id}.html"
                else:
                    raw_url = card.css('a.search-list-href::attr(href)').get()
                    detail_url = raw_url.split('?')[0] if raw_url else None

                # [经验 & 学历]
                # 简单逻辑：在标签里找 "本科"/"硕士"
                education = "本科"
                for tag in tags_raw:
                    if "硕士" in tag: education = "硕士"
                    elif "博士" in tag: education = "博士"
                    elif "大专" in tag: education = "大专"

                experience = "应届/在校" # 应届生网站默认属性

                # --- 判空 ---
                if not title or not detail_url:
                    continue

                item = {
                    'title': title.strip(),
                    'company': company.strip() if company else "详见详情",
                    'salary': salary.strip() if salary else "校招薪资",
                    'location': location.strip(),
                    'experience': experience,
                    'education': education,
                    'source_website': 'yingjiesheng',
                    'detail_url': detail_url,
                    'tags': tags_str,
                    'welfare': "",
                    'company_size': "",
                    'industry': "",
                    # 🔥 核心修改：统一标记为待抓取，不进详情页
                    'job_description': "待抓取"
                }

                print(f"   ✅ [列表] {item['title']} | {item['company']}")

                # 🔥 直接提交给 Pipeline
                yield item

            except Exception as e:
                self.logger.error(f"解析错误: {e}")

        # --- 翻页逻辑 (URL 递增) ---
        # 假设 URL 模式: .../search/Python -> .../search/Python/2
        current_page = 1
        # 尝试从 URL 提取页码
        match = re.search(r'/(\d+)$', response.url)
        if match:
            current_page = int(match.group(1))

        next_page = current_page + 1

        if len(job_cards) > 0:
            print(f"🚀 [翻页] 准备前往第 {next_page} 页...")

            # 构造下一页 URL
            if current_page == 1:
                # 如果当前是第一页 (无页码)，直接追加 /2
                new_url = f"{response.url}/{next_page}"
            else:
                # 如果当前有页码，替换之
                new_url = re.sub(r'/\d+$', f'/{next_page}', response.url)

            # 这里的 dont_filter=True 很重要，防止被去重
            yield scrapy.Request(new_url, callback=self.parse, dont_filter=True)
        else:
            print("🛑 没有更多数据了")