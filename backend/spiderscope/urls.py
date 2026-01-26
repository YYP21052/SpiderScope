from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# 👇 这里现在应该正常了，因为 core/views.py 里确实有这两个类
from core.views import SpiderTaskViewSet, JobViewSet

router = DefaultRouter()
router.register(r'tasks', SpiderTaskViewSet)
router.register(r'jobs', JobViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)), # 挂载路由

    # JWT 认证
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]