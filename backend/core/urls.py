"""
@Time ： 2026/1/8 21:53
@Auth ： CST21052
@File ：urls.py
@IDE ：PyCharm
@Motto：Do one thing at a time, and do well.
@requirement:
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SpiderTaskViewSet, JobViewSet, StartCrawlView, StatsView

# 创建一个路由器
router = DefaultRouter()
router.register(r'tasks', SpiderTaskViewSet)
# 如果想要标准 RESTful 风格，也可以注册 jobs
# router.register(r'jobs', JobViewSet)

urlpatterns = [
    # 1. 爬虫启动 (POST)
    path('crawl/start/', StartCrawlView.as_view(), name='crawl-start'),
    
    # 2. 统计数据 (GET)
    path('jobs/stats/', StatsView.as_view(), name='job-stats'),
    
    # 3. 职位列表 (GET) - 显式匹配 /api/jobs/list/
    path('jobs/list/', JobViewSet.as_view({'get': 'list'}), name='job-list'),

    # 4. 原有功能 (Tasks)
    path('', include(router.urls)),
]