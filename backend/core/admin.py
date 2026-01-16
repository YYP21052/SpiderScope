from django.contrib import admin
from .models import SpiderTask, Job


# --- 源代码 (SpiderTask) ---
@admin.register(SpiderTask)
class SpiderTaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'target_url', 'status', 'created_at')


# ---  新增：注册 Job 表 ---
@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    # list_display 决定了在列表页显示哪些列
    list_display = ('title', 'company', 'salary', 'location', 'created_at')

    # search_fields 让你能搜索这些字段
    search_fields = ('title', 'company')

    # list_filter 让你能按来源或时间筛选
    list_filter = ('source_website', 'created_at')