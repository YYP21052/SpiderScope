# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pymongo


class MongoPipeline:
    def __init__(self):
        # todo 连接 Docker 里的 MongoDB
        # 格式：mongodb://账号:密码@IP:端口/
        # 注意：这里的账号密码必须和你 docker-compose.yml 里写的一致
        self.mongo_uri = "mongodb://mongo_user:mongo_password@localhost:27017/"
        self.mongo_db = "spider_data"  # 数据库名称
        self.collection_name = "quotes"  # 数据表的名字

    def open_spider(self, spider):
        """爬虫启动时调用：建立数据库连接"""
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        # 确保索引（可选，但在生产环境很重要，这里先只建连接）

    def close_spider(self, spider):
        """爬虫关闭时调用：断开连接"""
        self.client.close()

    def process_item(self, item, spider):
        """核心方法：每抓到一个 item 都会经过这里"""
        # 往 'quotes' 表里插入一条数据
        self.db[self.collection_name].insert_one(dict(item))

        # 打印一下日志，让你知道数据存进去了
        print(f"✅ 已保存到 MongoDB: {item['text'][:20]}...")

        # 必须返回 item，否则后续的管道（如果有）就收不到数据了
        return item