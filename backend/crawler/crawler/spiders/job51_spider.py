import scrapy
import json
import re  # 👈 必须导入正则库

class Job51Spider(scrapy.Spider):
    name = "51job"
    allowed_domains = ["51job.com"]
    # 初始 URL (默认第1页)
    start_urls = ["https://we.51job.com/pc/search?keyword=Python&searchType=2&sortType=0&metro="]

    custom_settings = {
        'CLOSESPIDER_ITEMCOUNT': 200, # 抓满200条自动停止
        'DOWNLOAD_DELAY': 3,
    }

    def parse(self, response):
        print("=" * 50)
        print("🎉 正在解析 51job (混合提取+强制翻页)...")

        job_cards = response.css('.joblist-item')
        print(f"📊 本页发现 {len(job_cards)} 个职位")

        # === 1. 数据解析 (这部分你之前已经跑通了，保持不变) ===
        for card in job_cards:
            try:
                data = {}
                json_str = card.css('.joblist-item-job').attrib.get('sensorsdata')
                if json_str:
                    try:
                        data = json.loads(json_str)
                    except:
                        pass

                # 字段提取
                title = data.get('jobName') or data.get('jobTitle') or card.css('.jname::text').get()
                salary = data.get('provideSalaryString') or data.get('jobSalary') or card.css('.sal::text').get()

                company = data.get('fullCompanyName') or data.get('companyName')
                if not company:
                    company = card.css('.cname::text').get() or card.css('.cname::attr(title)').get()

                area_str = data.get('jobAreaString') or data.get('jobArea')
                location = area_str.split('·')[0] if area_str else (card.css('.info .d .k::text').get() or "全国").split('·')[0]

                job_id = data.get('jobId')
                detail_url = f"https://jobs.51job.com/all/{job_id}.html" if job_id else card.css('a::attr(href)').get()

                tags_list = data.get('jobTags', [])
                if not tags_list:
                    tags_list = card.css('.tags .tag::text').getall()
                tags_str = ",".join(tags_list)

                # 判空
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
                    'job_description': ""
                }

                print(f"   ✅ {item['title']} | {item['company']}")
                yield item

            except Exception as e:
                self.logger.error(f"解析错误: {e}")

        # ==========================================
        # 🔥🔥🔥 核心修改：手动构造下一页 URL 🔥🔥🔥
        # ==========================================

        # 1. 获取当前页码 (从 URL 里找 pageNum=X，找不到默认是 1)
        current_page = 1
        page_match = re.search(r'pageNum=(\d+)', response.url)
        if page_match:
            current_page = int(page_match.group(1))

        # 2. 计算下一页
        next_page = current_page + 1

        # 3. 只有当本页确实抓到了数据，才去翻页 (防止死循环)
        if len(job_cards) > 0:
            print(f"🚀 [翻页逻辑] 当前第 {current_page} 页，准备前往第 {next_page} 页...")

            # 4. 构造新 URL
            if 'pageNum=' in response.url:
                # 如果 URL 里已经有 pageNum，替换数字
                new_url = re.sub(r'pageNum=\d+', f'pageNum={next_page}', response.url)
            else:
                # 如果没有，直接追加参数
                new_url = response.url + f"&pageNum={next_page}"

            # 5. 发送请求
            # ⚠️ 关键点：dont_filter=True 防止 Scrapy 觉得网址相似而过滤掉
            yield scrapy.Request(new_url, callback=self.parse, dont_filter=True)
        else:
            print("🛑 未发现更多数据，停止翻页。")