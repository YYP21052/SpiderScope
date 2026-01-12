from rest_framework import viewsets, status
from rest_framework.decorators import action  # 动作装饰器
from rest_framework.response import Response
import pymongo

from .models import SpiderTask
from .serializers import SpiderTaskSerializer
from .tasks import run_spider_task  # 引入刚才写的任务


class SpiderTaskViewSet(viewsets.ModelViewSet):
    queryset = SpiderTask.objects.all().order_by('-created_at')
    serializer_class = SpiderTaskSerializer

    # 1. 重写创建逻辑：创建后自动触发 Celery
    def perform_create(self, serializer):
        # 先保存进数据库，拿到实例
        instance = serializer.save()
        # 触发异步任务，把 ID 传过去
        run_spider_task.delay(instance.id)
        print(f"🚀 已触发自动调度，任务ID: {instance.id}")

    # 2. 自定义接口：查看爬取结果
    # 访问地址：GET /api/tasks/{id}/results/
    @action(detail=True, methods=['get'])
    def results(self, request, pk=None):
        # 连接 MongoDB (注意：生产环境应该把连接池放在全局，这里为了演示直接连)
        client = pymongo.MongoClient("mongodb://mongo_user:mongo_password@localhost:27017/")
        db = client["spider_data"]
        collection = db["quotes"]

        # 简单粗暴：把所有数据都取出来（实际业务应该按任务ID筛选，我们后面再优化）
        # 这里的 .find({}, {'_id': 0}) 意思是：不返回 _id 字段，因为它不能直接被 JSON 序列化
        data = list(collection.find({}, {'_id': 0}).limit(50))  # 只看前50条

        client.close()
        return Response(data)