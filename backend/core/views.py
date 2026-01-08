from rest_framework import viewsets
from .models import SpiderTask
from .serializers import SpiderTaskSerializer

class SpiderTaskViewSet(viewsets.ModelViewSet):
    """
    API 端点：允许查看或编辑爬虫任务
    """
    # 告诉 DRF 要查哪些数据：查所有任务，按创建时间倒序排（最新的在前面）
    queryset = SpiderTask.objects.all().order_by('-created_at')
    # 告诉 DRF 用哪个翻译官
    serializer_class = SpiderTaskSerializer