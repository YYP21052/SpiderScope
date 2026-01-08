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
from .views import SpiderTaskViewSet

# 创建一个路由器，它会自动生成 /tasks/, /tasks/1/ 这种网址
router = DefaultRouter()
# 注册我们的 ViewSet
router.register(r'tasks', SpiderTaskViewSet)

urlpatterns = [
    # 比如访问 http://.../api/tasks/ 就会路由到这里
    path('', include(router.urls)),
]