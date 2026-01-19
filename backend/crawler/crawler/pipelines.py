# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import os
import sys
import django
from asgiref.sync import sync_to_async

# ==========================================
# 1. 初始化 Django 环境 (必须在导入 models 之前)
# ==========================================
# 获取当前路径: .../backend/crawler/crawler/
current_dir = os.path.dirname(os.path.abspath(__file__))
# 获取 backend 路径: .../backend/
backend_path = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(backend_path)

# 指定 Django 配置文件
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spiderscope.settings')

# 启动 Django (这一步至关重要！)
django.setup()

# 只有在 setup() 之后才能导入模型
from core.models import Job


# ==========================================
# 2. PostgreSQL Pipeline (存入 Django)
# ==========================================
class JobPostgresPipeline:
    async def process_item(self, item, spider):
        # ✅ 修正：定义白名单，允许这些爬虫的数据通过
        target_spiders = ['51job', 'boss', 'shixiseng', 'yingjiesheng', 'lagou']

        # 如果当前爬虫不在白名单里，直接跳过
        if spider.name not in target_spiders:
            return item

        try:
            # 定义一个同步函数来干脏活累活 (Django ORM 是同步的)
            def save_to_db():
                # update_or_create: 根据 detail_url 查重
                # 有则更新，无则创建
                obj, created = Job.objects.update_or_create(
                    detail_url=item.get('detail_url'),
                    defaults={
                        'title': item.get('title'),
                        'company': item.get('company'),
                        'salary': item.get('salary', '面议'),
                        'location': item.get('location', '全国'),
                        'source_website': item.get('source_website', 'unknown'),
                        'experience': item.get('experience', ''),
                        'education': item.get('education', ''),
                        'industry': item.get('industry', ''),
                        'company_size': item.get('company_size', ''),
                        'tags': item.get('tags', ''),
                        'welfare': item.get('welfare', ''),
                        'job_description': item.get('job_description', '')
                    }
                )
                return obj, created

            # 🚀 在异步环境里调用同步数据库操作
            job, created = await sync_to_async(save_to_db)()

            action = "✨ 新增" if created else "♻️ 更新"
            # 打印明显的日志
            spider.logger.info(f"💾 [Django] {action}: {item['title']} - {item['company']}")

        except Exception as e:
            spider.logger.error(f"❌ [Django] 入库失败: {e}")

        return item

# ==========================================
# 2. 旧代码：MongoDB Pipeline (暂时注释掉)
# ==========================================
# import pymongo
# class MongoPipeline:
#     def __init__(self):
#     # 格式：mongodb://账号:密码@IP:端口/
#     # 注意：这里的账号密码必须和你 docker-compose.yml 里写的一致
#         self.mongo_uri = "mongodb://mongo_user:mongo_password@localhost:27017/"
#         self.mongo_db = "spider_data" # 数据库名称
#         self.collection_name = "quotes" # 数据表的名字
#
#
#     def open_spider(self, spider):
#         """
#         爬虫启动时调用：建立数据库连接
#         """
#         self.client = pymongo.MongoClient(self.mongo_uri)
#         self.db = self.client[self.mongo_db]
#         # 确保索引（可选，但在生产环境很重要，这里先只建连接）
#
#     def close_spider(self, spider):
#         """
#         爬虫关闭时调用：断开连接
#         """
#         self.client.close()
#
#     def process_item(self, item, spider):
#         """
#         核心方法：每抓到一个 item 都会经过这里
#         """
#         # 往 'quotes' 表里插入一条数据
#         self.db[self.collection_name].insert_one(dict(item))
#         # 打印一下日志，让你知道数据存进去了
#         print(f"✅ 已保存到 MongoDB: {item['text'][:20]}...")
#         # 必须返回 item，否则后续的管道（如果有）就收不到数据了
#         return item