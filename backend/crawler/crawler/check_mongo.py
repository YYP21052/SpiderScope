"""
@Time ： 2026/1/7 21:36
@Auth ： CST21052
@File ：check_mongo.py
@IDE ：PyCharm
@Motto：Do one thing at a time, and do well.
@requirement:
"""
# todo 检测爬虫爬到的数据是否存储在mongoSQL中
import pymongo

# 连接数据库
client = pymongo.MongoClient("mongodb://mongo_user:mongo_password@localhost:27017/")
db = client["spider_data"]
collection = db["quotes"]

# 统计数量
count = collection.count_documents({})
print(f"🔥 数据库里现在有 {count} 条名言！")

# 打印第一条看看
print("第一条数据是：", collection.find_one())