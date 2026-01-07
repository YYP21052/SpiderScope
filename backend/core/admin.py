from django.contrib import admin
from .models import SpiderTask # 自己创建的爬虫任务类
# Register your models here.

# 后台查看是否创建成功
@admin.register(SpiderTask)
class SpiderTaskAdmin(admin.ModelAdmin):
    # 后台列表显示的字段
    list_display = ('name', 'target_url', 'status', 'created_at')
    # 侧边栏筛选器
    list_filter = ('status', 'frequency')
    # 搜索框
    search_fields = ('name', 'target_url')