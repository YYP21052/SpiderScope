"""
@Time ： 2026/1/19
@File ：yjs_spider.py
@requirement: 爬取应届生求职网 (新版动态页，基于 51job 架构)
"""
import scrapy
import json

class YjsSpider(scrapy.Spider):
    name = "yingjiesheng"
    allowed_domains = ["yingjiesheng.com"]
    # 搜索 Python
    start_urls = ["https://q.yingjiesheng.com/jobs/search/Python"]

    custom_settings = {
        'CLOSESPIDER_ITEMCOUNT': 200,
        'DOWNLOAD_DELAY': 3,
    }

    def parse(self, response):
        print("=" * 50)
        print("🎓 正在解析 应届生 (JSON混合动力版)...")

        # 1. 定位职位卡片
        # 根据你提供的 HTML，外层 class 是 "sensors_exposure item-content"
        job_cards = response.css('.item-content')
        print(f"📊 本页发现 {len(job_cards)} 个职位")

        for card in job_cards:
            try:
                # --- 1. 尝试解析 JSON (sensorsdata) ---
                data = {}
                json_str = card.attrib.get('sensorsdata')
                if json_str:
                    try:
                        data = json.loads(json_str)
                    except:
                        pass

                # --- 2. 字段提取 (优先 CSS，因为你提供的 HTML 结构很完整) ---

                # [标题]
                title = data.get('jobTitle')
                if not title:
                    # CSS 替补: class="left-title-name" 下的 .text-cut
                    title = card.css('.left-title-name .text-cut::text').get()

                # [公司]
                company = data.get('companyName')
                if not company:
                    # CSS 替补: class="left-detail-company"
                    company = card.css('.left-detail-company::text').get()

                # [薪资] (JSON里可能没有 salary，直接用 CSS 抓)
                # CSS: class="right-salary"
                salary = card.css('.right-salary::text').get()

                # [标签 & 地点]
                # 页面上有一排标签: 上海 | 在校生/应届生 | 本科 | 五险一金...
                # class="left-tag-item"
                tags_raw = card.css('.left-tag-item::text').getall()

                # 第一个标签通常是地点
                location = tags_raw[0] if tags_raw else "全国"

                # 剩下的拼成 tags 字符串
                tags_str = ",".join(tags_raw)

                # [详情链接]
                # 这里的 href 长这样: https://q.yingjiesheng.com/jobdetail/170310047.html?property=...
                # 我们只需要提取 ? 前面的部分，或者直接用 jobId 拼接
                job_id = data.get('jobId')
                if job_id:
                    detail_url = f"https://q.yingjiesheng.com/jobdetail/{job_id}.html"
                else:
                    raw_url = card.css('a.search-list-href::attr(href)').get()
                    detail_url = raw_url.split('?')[0] if raw_url else None

                # [经验 & 学历]
                # 应届生网站比较特殊，经验通常在标签里，我们简单处理
                experience = "应届/在校"
                education = "本科" # 默认值，也可以遍历 tags_raw 来匹配 "本科"/"硕士"

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
                    'job_description': ""
                }

                print(f"   ✅ {item['title']} | {item['company']}")
                yield item

            except Exception as e:
                self.logger.error(f"解析错误: {e}")

        # --- 翻页逻辑 ---
        # 应届生新版通常是滚动加载或者数字分页，既然我们复用了 Selenium 中间件
        # 我们可以尝试寻找 "下一页" 按钮 (class="btn-next") 并点击
        # 但为了稳妥，Day 8 我们先抓第一页即可。
        # 如果你想翻页，原理和 51job 一样，需要分析它的翻页按钮 class