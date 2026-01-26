"""
@Time ： 2026/1/25
@File ：fill_details.py
@requirement: 独立脚本，从 Mongo 读取 "待抓取" 记录，访问 URL 补全 job_description
"""
import time
import random
import pymongo
from DrissionPage import ChromiumPage

# =================配置区域=================
MONGO_URI = 'mongodb://mongo_user:mongo_password@127.0.0.1:27017/?authSource=admin'
DB_NAME = 'spider_data'
COLLECTION_NAME = 'job_details'

# 针对不同网站，定义多个备选选择器 (优先级从左到右)
SELECTORS = {
    '51job.com': ['.bmsg.job_msg.inbox', '.job_msg', '.tBorderTop_box'], # 51job 多种结构
    'yingjiesheng.com': ['.job-intro', '.job_detail', '.content'],
    'shixiseng.com': ['.job_detail', '.intern-detail__desc'],
    'zhipin.com': ['.job-sec-text']
}
# ==========================================

def get_mongo_collection():
    client = pymongo.MongoClient(MONGO_URI)
    db = client[DB_NAME]
    return db[COLLECTION_NAME]

def clean_text(text_ele):
    """简单清洗文本，去除多余空白"""
    if not text_ele:
        return ""
    # DrissionPage .text 会智能提取可见文本
    text = text_ele.text
    # 去除多余的换行和空格
    return text.strip()

def main():
    print("🚀 启动详情补全脚本 (ETL Worker - 增强版)...")

    collection = get_mongo_collection()

    # 查找任务：排除 Boss (因为它需要频繁扫码)，专注补全 51job/应届生/实习僧
    query = {
        'job_description': '待抓取',
        'url': {'$not': {'$regex': 'zhipin.com'}}
    }

    pending_tasks = list(collection.find(query))
    total = len(pending_tasks)

    if total == 0:
        print("✅ MongoDB 里没有需要补全的数据，任务结束！")
        return

    print(f"📊 发现 {total} 条待抓取的数据，浏览器启动中...")

    # 启动浏览器
    dp = ChromiumPage()

    success_count = 0

    try:
        for index, doc in enumerate(pending_tasks):
            url = doc['url']
            title = doc.get('title', '未知职位')

            print(f"\n[{index + 1}/{total}] 正在处理: {title}")
            print(f"    🔗 {url}")

            # 1. 匹配选择器列表
            target_selectors = None
            for domain, sels in SELECTORS.items():
                if domain in url:
                    target_selectors = sels
                    break

            if not target_selectors:
                print("    ⚠️ 未知域名的 URL，跳过")
                continue

            try:
                # 2. 访问页面
                dp.get(url)

                # 智能等待：检查页面是否包含关键的 滑块 或 验证 元素
                # 如果出现滑块，暂停等待人工介入
                if dp.ele("#nc_1_n1z", timeout=1) or "验证" in dp.title:
                    print("    🚨 检测到滑块/验证！请在浏览器中手动完成...")
                    time.sleep(10) # 给你 10 秒时间手动滑
                else:
                    # 正常随机等待
                    time.sleep(random.uniform(2, 4))

                # 3. 尝试提取内容 (轮询所有备选选择器)
                content_ele = None
                for sel in target_selectors:
                    content_ele = dp.ele(sel)
                    if content_ele:
                        break # 找到了就停止

                if content_ele:
                    # 提取文本
                    description = clean_text(content_ele)

                    # 简单的有效性检查
                    if len(description) > 20:
                        collection.update_one(
                            {'_id': doc['_id']},
                            {
                                '$set': {
                                    'job_description': description,
                                    'updated_at': time.strftime("%Y-%m-%d %H:%M:%S")
                                }
                            }
                        )
                        print(f"    ✅ 抓取成功 ({len(description)}字)")
                        success_count += 1
                    else:
                        print(f"    ⚠️ 内容过短 ({len(description)}字)，可能抓错或已下架")
                        # 标记为失败，防止死循环
                        collection.update_one({'_id': doc['_id']}, {'$set': {'job_description': '抓取失败/过短'}})
                else:
                    print("    ❌ 未找到详情元素 (反爬拦截或页面结构变更)")
                    # 调试：打印一下当前标题，看看是不是被拦截了
                    print(f"       当前页面标题: {dp.title}")
                    collection.update_one({'_id': doc['_id']}, {'$set': {'job_description': '抓取失败'}})

            except Exception as e:
                print(f"    ❌ 发生错误: {e}")

            # 休息一下，防止封 IP
            time.sleep(random.uniform(2, 5))

    except KeyboardInterrupt:
        print("\n🛑 用户手动停止任务")
    finally:
        dp.close()
        print(f"\n🎉 任务结束！本次成功补全: {success_count}/{total}")

if __name__ == "__main__":
    main()