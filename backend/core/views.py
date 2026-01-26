from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

# 引入 Models
from .models import SpiderTask, Job
# 引入 Serializers
from .serializers import SpiderTaskSerializer, JobSerializer
# 引入 Celery 任务
from .tasks import run_spider_task

# ============================================
# 1. 职位数据接口 (Day 9 新增)
# ============================================
class JobViewSet(viewsets.ModelViewSet):
    """
    提供清洗后的职位数据
    GET /api/jobs/
    """
    queryset = Job.objects.all().order_by('-id')
    serializer_class = JobSerializer
    # 只有登录用户才能访问

    # 🔴 临时改为 AllowAny (允许任何人访问)
    # permission_classes = [permissions.AllowAny]
    # 原来是:
    permission_classes = [permissions.IsAuthenticated]


# ============================================
# 2. 爬虫任务接口 (你之前的逻辑)
# ============================================
class SpiderTaskViewSet(viewsets.ModelViewSet):
    """
    控制爬虫任务
    POST /api/tasks/ -> 创建新任务
    """
    queryset = SpiderTask.objects.all().order_by('-created_at')
    serializer_class = SpiderTaskSerializer
    # 只有登录用户才能访问
    permission_classes = [permissions.IsAuthenticated]

    # 重写创建逻辑：自动触发 Celery
    def perform_create(self, serializer):
        instance = serializer.save()
        run_spider_task.delay(instance.id)
        print(f"🚀 [JWT鉴权通过] 任务已触发: {instance.id}")

    # 获取结果 (修正为指向 Job 接口)
    @action(detail=True, methods=['get'])
    def results(self, request, pk=None):
        return Response({
            "msg": "数据已存入 PostgreSQL，请访问 /api/jobs/ 查看最新清洗后的数据",
            "link": "/api/jobs/"
        })