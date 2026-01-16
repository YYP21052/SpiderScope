# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from itemadapter import ItemAdapter
from core.models import Job
from asgiref.sync import sync_to_async # 引入这个转换器，把sync转为async

# ==========================================
# 使用PostgreSQL Pipeline (存入 Django)
# ==========================================
class JobPostgresPipeline:
    async def process_item(self, item, spider):
        # 只有当爬虫是 job_spider 时，才执行这个逻辑
        # 这样不会影响你之前的 quote 爬虫
        if spider.name != 'job_spider':
            return item

        try:

            # Django ORM 的黑魔法：update_or_create
            # 作用：根据 detail_url 判断，如果数据库里有就更新，没有就创建
            # 定义一个同步函数来干脏活累活
            def save_to_db():
                return Job.objects.update_or_create(
                    detail_url=item['detail_url'],
                    defaults={
                        'title': item['title'],
                        'company': item['company'],
                        'location': item.get('location', 'Remote'),
                        'salary': item.get('salary', 'N/A'),
                        'source_website': item.get('source_website', 'unknown')
                    }
                )

            # 👇 4. 使用 sync_to_async 包装并在线程池里运行，加上 await 等待结果
            job, created = await sync_to_async(save_to_db)()

            if created:
                spider.logger.info(f"🆕 [Django] 成功入库新职位: {item['title']}")
            else:
                spider.logger.info(f"♻️ [Django] 职位已存在(已更新): {item['title']}")

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