import os
import sys
import django
import re
import pymongo
from itemadapter import ItemAdapter
from asgiref.sync import sync_to_async

# 初始化 Django
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_path = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(backend_path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spiderscope.settings')
django.setup()

from core.models import Job


# 1. 清洗管道
class JobCleaningPipeline:
    def process_item(self, item, spider):
        raw_salary = item.get('salary', '')
        min_val, max_val = 0, 0
        if raw_salary:
            try:
                factor = 1.0
                if '万' in raw_salary:
                    factor = 10000.0
                elif '千' in raw_salary or 'k' in raw_salary.lower():
                    factor = 1000.0
                if '天' in raw_salary: factor = 30.0

                nums = re.findall(r'(\d+\.?\d*)', raw_salary)
                if len(nums) >= 2:
                    min_val = int(float(nums[0]) * factor)
                    max_val = int(float(nums[1]) * factor)
                elif len(nums) == 1:
                    min_val = int(float(nums[0]) * factor)
                    max_val = min_val
            except:
                pass
        item['min_salary'] = min_val
        item['max_salary'] = max_val
        return item


# 2. 双库分流管道
class HybridPipeline:
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'spider_data')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        self.collection = self.db['job_details']
        spider.logger.info("✅ MongoDB 连接成功")

    def close_spider(self, spider):
        self.client.close()

    async def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        data = adapter.asdict()

        # A. 存入 PostgreSQL (列表信息)
        pg_defaults = {
            'title': data.get('title'),
            'company': data.get('company'),
            'location': data.get('location'),
            'salary': data.get('salary'),
            'min_salary': data.get('min_salary', 0),
            'max_salary': data.get('max_salary', 0),
            'experience': data.get('experience'),
            'education': data.get('education'),
            'source_website': data.get('source_website', spider.name),
            'tags': data.get('tags'),
            'welfare': data.get('welfare'),
        }

        job_pg_id = None
        try:
            def save_pg():
                obj, created = Job.objects.update_or_create(
                    detail_url=data.get('detail_url'),
                    defaults=pg_defaults
                )
                return obj, created

            job_obj, created = await sync_to_async(save_pg)()
            job_pg_id = job_obj.id
        except Exception as e:
            spider.logger.error(f"❌ PG Error: {e}")
            return item

        # B. 存入 MongoDB (即使没有详情，也先占个位)
        mongo_doc = {
            'url': data.get('detail_url'),
            'pg_id': job_pg_id,
            'title': data.get('title'),
            # 这里目前会存入 "待抓取"
            'job_description': data.get('job_description', '待抓取'),
            'spider': spider.name,
            'crawled_at': data.get('crawled_at'),
            'updated_at': django.utils.timezone.now()
        }

        try:
            self.collection.update_one(
                {'url': data.get('detail_url')},
                {'$set': mongo_doc},
                upsert=True
            )
            # 简化日志，只提示存库成功
            print(f"✅ [入库成功] {data.get('title')}")
        except Exception as e:
            spider.logger.error(f"❌ Mongo Error: {e}")

        return item