"""
@Time ： 2026/1/25
@File ：boss_spider.py
@requirement: Boss直聘 (DrissionPage 强制跳转版 - 修复点击无效问题)
# "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="D:\chrome_debug_profile"
"""
import scrapy
from DrissionPage import ChromiumPage
import time
import random

class BossSpider(scrapy.Spider):
    name = "boss"
    allowed_domains = ["zhipin.com"]
    start_urls = ["https://www.zhipin.com"]

    custom_settings = {
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOAD_DELAY': 0,
        'CLOSESPIDER_ITEMCOUNT': 20,
    }

    def start_requests(self):
        yield scrapy.Request(url="https://www.zhipin.com", callback=self.parse, dont_filter=True)

    def parse(self, response):
        print("=" * 50)
        print("⚔️ [Boss] 启动 DrissionPage 接管模式...")

        # 1. 接管浏览器
        try:
            dp = ChromiumPage(addr_or_opts=9222)
            print(f"✅ 接管成功: {dp.title}")
        except Exception as e:
            self.logger.error(f"❌ 接管失败: {e}")
            return

        # 打印动态网页代码
        # try:
        #     with open("boss_debug.html", "w", encoding="utf-8", errors='ignore') as f:
        #         f.write(dp.html)
        #     print("✅ 网页源码已保存为 boss_debug.html，请去项目根目录打开查看！")
        #     print("❗ 如果接下来的步骤报错，请务必查看这个 HTML 文件，看看类名变成了什么。")
        # except Exception as e:
        #     print(f"⚠️ 保存源码失败 (不影响运行): {e}")


        # 2. 定位职位卡片
        # 你的 HTML 显示是 job-card-box
        job_cards = dp.eles(".job-card-box")


        if not job_cards:
            print("⚠️ 未找到 .job-card-box，尝试滚动加载...")
            dp.scroll.to_bottom()
            time.sleep(2)
            job_cards = dp.eles(".job-card-box")

        print(f"📊 页面发现 {len(job_cards)} 个职位，目标抓取前 20 条...")

        count = 0
        for i, card in enumerate(job_cards):
            if count >= 20: break

            try:
                # --- A. 提取列表页信息 ---

                # 1. 职位名称 & 链接
                title_ele = card.ele(".job-name")
                if not title_ele: continue

                title = title_ele.text

                # 获取 href 属性
                detail_url = title_ele.attr("href")
                if detail_url and not detail_url.startswith("http"):
                    detail_url = "https://www.zhipin.com" + detail_url

                # 2. 薪资
                salary = card.ele(".job-salary").text

                # 3. 经验 & 学历
                tags = card.eles(".tag-list li")
                experience = tags[0].text if len(tags) > 0 else ""
                education = tags[1].text if len(tags) > 1 else ""

                # 4. 公司名称 (尝试多种类名)
                company = "Boss直聘企业"
                try:
                    if card.ele(".company-name"):
                        company = card.ele(".company-name").text
                    elif card.ele(".boss-name"):
                        # 有时候列表页没有公司名，只有 boss 名，这里做个兜底
                        company = card.ele(".boss-name").text
                except:
                    pass

                print(f"[{count+1}/20] 抓取: {title} | {salary}")

                # =========================================================
                # 🔥🔥🔥 核心修复点 🔥🔥🔥
                # 不要用 click.for_new_tab()，因为它可能点不到或者被拦截
                # 直接告诉浏览器：给我打开这个 URL！
                # =========================================================
                new_tab = dp.new_tab(detail_url)

                # 随机等待加载
                time.sleep(random.uniform(2, 4))

                job_description = "详情抓取失败"
                try:
                    # 详情页描述通常在 .job-sec-text
                    # 使用 wait.ele_displayed 等待元素出现，比 sleep 更稳
                    if new_tab.wait.ele_displayed(".job-sec-text", timeout=3):
                        job_description = new_tab.ele(".job-sec-text").text
                    else:
                        # 有时候可能是验证码，或者结构不同
                        print(f"    ⚠️ 详情页加载超时: {new_tab.title}")
                except Exception as e:
                    print(f"    ⚠️ 抓取详情出错: {e}")

                # 关掉详情页，切回列表页 (这步很重要，否则标签页会越来越多)
                new_tab.close()

                # --- C. 提交数据 ---
                item = {
                    'title': title,
                    'company': company,
                    'salary': salary,
                    'location': "全国",
                    'experience': experience,
                    'education': education,
                    'source_website': 'boss',
                    'detail_url': detail_url,
                    'tags': f"{experience},{education}",
                    'welfare': "",
                    'job_description': job_description
                }

                yield item
                count += 1

                # 稍微停顿
                time.sleep(1)

            except Exception as e:
                self.logger.error(f"❌ 单条解析错误: {e}")
                # 万一出错，尝试清理多余的标签页
                if dp.tabs_count > 1:
                    dp.close_tabs(others=True)

        print("🎉 Boss 任务结束！")