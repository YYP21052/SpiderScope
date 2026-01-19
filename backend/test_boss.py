from DrissionPage import ChromiumPage
import time
import random


def scrape_boss_limit_5():
    print("=" * 50)
    print("⚔️ 启动深度抓取测试 (仅限前 5 条)...")

    # 1. 接管浏览器 (确保你已经手动打开并登录了 Boss)
    try:
        page = ChromiumPage(addr_or_opts=9222)
        print(f"✅ 接管成功: {page.title}")
    except Exception as e:
        print(f"❌ 接管失败，请确认是否已通过命令行启动 Chrome。\n错误: {e}")
        return

    # 2. 获取列表卡片
    # 注意：根据你提供的 HTML，核心类名是 .job-card-box
    job_cards = page.eles(".job-card-box")

    if not job_cards:
        print("⚠️ 未找到职位列表，请手动滚动页面或确认类名是否正确。")
        return

    print(f"📊 本页共发现 {len(job_cards)} 个职位，我们将只抓取前 5 个...")
    print("-" * 50)

    # 🔥 核心修改：使用切片 [:5] 只取前 5 个
    target_cards = job_cards[:5]

    for i, card in enumerate(target_cards):
        try:
            # --- 列表页数据 ---
            # 获取职位名和链接对象
            title_ele = card.ele(".job-name", timeout=2)
            if not title_ele:
                print(f"⚠️ 第 {i + 1} 条数据异常，跳过")
                continue

            title = title_ele.text
            detail_link = title_ele.attr("href")  # 获取链接

            # 获取公司名 (用于日志显示)
            company = card.ele(".boss-name").text

            print(f"[{i + 1}/5] 正在抓取: {title} ({company})")

            # --- 详情页操作 ---
            # 1. 新标签页打开链接
            tab = page.new_tab(detail_link)

            # 2. 等待加载 (随机 1.5 - 3 秒)
            tab.wait.load_start()
            time.sleep(random.uniform(1.5, 3))

            # 3. 提取职位描述 (Class: .job-sec-text)
            description_ele = tab.ele(".job-sec-text", timeout=3)

            if description_ele:
                # 提取前 60 个字预览
                desc_preview = description_ele.text.replace("\n", " ").strip()[:60]
                print(f"    📝 详情预览: {desc_preview}...")
            else:
                print("    ⚠️ 未找到职位描述文本")

            # 4. 这里的 tab.url 就是真实的详情页 URL
            print(f"    🔗 真实URL: {tab.url}")

            # 5. 关闭标签页 (非常重要！否则浏览器会卡死)
            tab.close()

            print("-" * 30)

            # 列表页稍微停顿，模拟人类浏览
            time.sleep(1)

        except Exception as e:
            print(f"❌ 第 {i + 1} 条抓取发生错误: {e}")
            # 异常处理：确保出错时也能关闭新开的标签页
            if 'tab' in locals() and tab.states.is_alive:
                tab.close()

    print("🎉 5 条测试任务完成！")


if __name__ == "__main__":
    scrape_boss_limit_5()