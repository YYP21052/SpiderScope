import scrapy
import json
import re


class Job51Spider(scrapy.Spider):
    name = "51job"
    allowed_domains = ["51job.com"]
    # 移除写死的 start_urls
    
    custom_settings = {
        # 只爬列表，速度可以稍微快一点点
        'CLOSESPIDER_ITEMCOUNT': 200,
        'DOWNLOAD_DELAY': 5, # 稍微调慢一点，稳一点
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        # Selenium 超时设置 (如果在中间件里实现了的话，这里是个提示)
        'SELENIUM_TIMEOUT': 15, 
    }

    def __init__(self, keyword='Python', city='全国', *args, **kwargs):
        super(Job51Spider, self).__init__(*args, **kwargs)
        self.keyword = keyword
        self.city = city
        
        print(f" [51job] 初始化爬虫 | 关键词: {keyword} | 城市: {city}")
        
        # 动态构造 URL
        # 注意：城市筛选比较复杂 (metro code)，暂时只支持关键词搜索，后续可扩展
        self.start_urls = [
            f"https://we.51job.com/pc/search?keyword={keyword}&searchType=2&sortType=0&metro="
        ]

    def parse(self, response):
        print("=" * 50)
        # 打印当前搜索条件
        print(f" 正在解析 51job 列表页 (Key: {self.keyword})...")

        job_cards = response.css('.joblist-item')
        print(f" 本页发现 {len(job_cards)} 个职位")

        # === 1. 数据解析 ===
        for card in job_cards:
            try:
                data = {}
                # 尝试从隐藏的 json 属性中获取结构化数据
                json_str = card.css('.joblist-item-job').attrib.get('sensorsdata')
                if json_str:
                    try:
                        data = json.loads(json_str)
                    except:
                        pass

                # 提取基础信息
                title = data.get('jobName') or data.get('jobTitle') or card.css('.jname::text').get()
                salary = data.get('provideSalaryString') or data.get('jobSalary') or card.css('.sal::text').get()

                company = data.get('fullCompanyName') or data.get('companyName')
                if not company:
                    company = card.css('.cname::text').get() or card.css('.cname::attr(title)').get()

                area_str = data.get('jobAreaString') or data.get('jobArea')
                location = area_str.split('·')[0] if area_str else \
                (card.css('.info .d .k::text').get() or "全国").split('·')[0]

                job_id = data.get('jobId')
                detail_url = f"https://jobs.51job.com/all/{job_id}.html" if job_id else card.css('a::attr(href)').get()

                tags_list = data.get('jobTags', [])
                if not tags_list:
                    tags_list = card.css('.tags .tag::text').getall()
                tags_str = ",".join(tags_list)

                if not company or not detail_url or not title:
                    continue

                item = {
                    'title': title.strip(),
                    'company': company.strip(),
                    'salary': salary if salary else "面议",
                    'location': location,
                    'experience': data.get('workYearString') or data.get('jobYear') or "",
                    'education': data.get('degreeString') or data.get('jobDegree') or "",
                    'source_website': '51job',
                    'detail_url': detail_url,
                    'tags': tags_str,
                    'welfare': "",
                    'company_size': '',
                    'industry': '',
                    # 🔥 核心修改：这里不再去抓详情，直接标记状态
                    'job_description': "待抓取"
                }

                print(f"    [列表] {item['title']} | {item['company']}")

                # 🔥 直接提交给 Pipeline，不去详情页了
                yield item

            except Exception as e:
                self.logger.error(f"解析错误: {e}")

        # === 2. 翻页逻辑 ===
        current_page = 1
        page_match = re.search(r'pageNum=(\d+)', response.url)
        if page_match:
            current_page = int(page_match.group(1))

        next_page = current_page + 1

        if len(job_cards) > 0:
            print(f"🚀 [翻页] 准备前往第 {next_page} 页...")
            if 'pageNum=' in response.url:
                new_url = re.sub(r'pageNum=\d+', f'pageNum={next_page}', response.url)
            else:
                new_url = response.url + f"&pageNum={next_page}"

            # 这里依然需要 Selenium 中间件去加载下一页
            yield scrapy.Request(new_url, callback=self.parse, dont_filter=True)
        else:
            print(" 没有更多数据了")