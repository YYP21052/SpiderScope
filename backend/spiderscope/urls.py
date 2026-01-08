"""
URL configuration for spiderscope project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include  # <--- 注意：一定要加上 include

urlpatterns = [
    path('admin/', admin.site.urls),

    # 把 core 应用的 API 挂载到 /api/ 下
    # 以后访问接口就是：http://127.0.0.1:8000/api/tasks/
    path('api/', include('core.urls')),
]