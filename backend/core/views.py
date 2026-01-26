from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django.db.models import Avg, Max, Count

# 引入 Models
from .models import SpiderTask, Job
# 引入 Serializers
from .serializers import SpiderTaskSerializer, JobSerializer, CustomTokenObtainPairSerializer
# 引入 Celery 任务
from .tasks import run_spider_task


# ============================================
# 0. 自定义登录接口 (返回用户角色)
# ============================================
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


# ============================================
# 1. 启动爬虫接口 (Admin Only)
# ============================================
class StartCrawlView(APIView):
    """
    启动爬虫任务
    POST /api/crawl/start/
    Body: {"spider_name": "51job", "keyword": "Java", "city": "Shanghai"}
    """
    # 关键权限控制：只有管理员 (is_staff=True) 可调用
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        spider_name = request.data.get("spider_name")
        # 🟢 获取动态参数 (默认为 Python, 全国)
        keyword = request.data.get("keyword", "Python")
        city = request.data.get("city", "全国")
        
        if not spider_name:
            return Response({"error": "缺少 spider_name 参数"}, status=status.HTTP_400_BAD_REQUEST)

        # 🟢 封装参数
        params = {
            "keyword": keyword,
            "city": city
        }

        # 调用 Celery 异步任务 (传入 params)
        run_spider_task.delay(spider_name, params)

        return Response({
            "msg": f"🚀 爬虫 [{spider_name}] 启动指令已发送",
            "params": params,
            "status": "pending"
        }, status=status.HTTP_200_OK)


# ============================================
# 2. 统计数据接口 (Public)
# ============================================
class StatsView(APIView):
    """
    获取职位统计数据 (供 ECharts 使用)
    GET /api/jobs/stats/
    """
    # 允许任何人访问
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        # 聚合查询 PostgreSQL
        stats = Job.objects.aggregate(
            total_jobs=Count('id'),
            avg_salary=Avg('min_salary'),
            max_salary=Max('max_salary')
        )

        # 也可以按城市分组 (示例)
        city_stats = Job.objects.values('location').annotate(
            count=Count('id')
        ).order_by('-count')[:5]  # 取前5个热门城市

        return Response({
            "overview": {
                "total": stats['total_jobs'] or 0,
                "avg_min_salary": int(stats['avg_salary'] or 0),
                "max_salary": stats['max_salary'] or 0
            },
            "city_ranking": city_stats
        })


# ============================================
# 3. 职位列表接口 (Public)
# ============================================
class JobViewSet(viewsets.ReadOnlyModelViewSet):
    """
    职位数据列表
    GET /api/jobs/list/
    """
    queryset = Job.objects.all().order_by('-id')
    serializer_class = JobSerializer
    
    # 允许任何人查看
    permission_classes = [permissions.AllowAny]


# ============================================
# 4. (保留) 爬虫任务记录接口
# ============================================
class SpiderTaskViewSet(viewsets.ModelViewSet):
    queryset = SpiderTask.objects.all().order_by('-created_at')
    serializer_class = SpiderTaskSerializer
    permission_classes = [permissions.IsAuthenticated]
