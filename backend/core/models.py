from django.db import models
from django.contrib.auth.models import User

# 爬虫类，数据库链接
# 任务状态选项
STATUS_CHOICES = (
    ('PENDING', '等待中'),
    ('RUNNING', '运行中'),
    ('COMPLETED', '已完成'),
    ('FAILED', '失败'),
)


class SpiderTask(models.Model):
    """
    爬虫任务表：记录用户想要爬什么
    """
    # 任务名称，比如 "抓取Boss直聘Python岗"
    name = models.CharField("任务名称", max_length=100)

    # 目标网址
    target_url = models.URLField("目标URL", help_text="请输入要抓取的网站地址")

    # [核心亮点] PostgreSQL 专属 JSONField
    # 这里可以存任意字典，比如 {"city": "beijing", "keywords": ["python", "django"]}
    # 不需要频繁修改数据库表结构，非常适合爬虫配置
    # 加上 null=True，给它“免死金牌”
    spider_config = models.JSONField("爬虫配置", default=dict, blank=True, null=True)

    # 爬虫的抓取频率，比如 "daily", "weekly"
    frequency = models.CharField("抓取频率", max_length=50, default="daily")

    # 任务状态
    status = models.CharField("当前状态", max_length=20, choices=STATUS_CHOICES, default='PENDING')

    # 关联用户：负责记录是谁创建的这个任务？
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="创建人", null=True, blank=True)

    # 时间记录
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        db_table = 'spider_task'  # 数据库里显示的表名
        verbose_name = "爬虫任务"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name



class Job(models.Model):
    '''
    职位表：适配 Boss直聘、前程无忧、智联、猎聘 的通用数据结构
    '''
    # --- 基础信息 ---
    title = models.CharField(max_length=255, verbose_name="职位名称")
    salary = models.CharField(max_length=100, verbose_name="薪资范围", null=True, blank=True)
    company = models.CharField(max_length=255, verbose_name="公司名称")
    location = models.CharField(max_length=100, verbose_name="工作地点", null=True, blank=True)
    
    # --- 进阶要求 (新增) ---
    experience = models.CharField(max_length=50, verbose_name="经验要求", null=True, blank=True) 
    education = models.CharField(max_length=50, verbose_name="学历要求", null=True, blank=True) 
    
    # --- 公司画像 (新增) ---
    industry = models.CharField(max_length=100, verbose_name="所属行业", null=True, blank=True)
    company_size = models.CharField(max_length=50, verbose_name="公司规模", null=True, blank=True)
    
    # --- 职位详情 (新增) ---
    tags = models.CharField(max_length=255, verbose_name="技能标签", null=True, blank=True)
    welfare = models.CharField(max_length=255, verbose_name="福利待遇", null=True, blank=True)
    job_description = models.TextField(verbose_name="职位描述", null=True, blank=True)

    # --- 系统字段 ---
    source_website = models.CharField(
        max_length=50,
        verbose_name="来源平台",
        choices=[
            ('boss', 'BOSS直聘'),
            ('51job', '前程无忧'),
            ('shixiseng', '实习僧'),  # 新增
            ('yingjiesheng', '应届生求职网'),  # 新增
            ('lagou', '拉勾网')  # 新增
        ],
        default="unknown"
    )
    
    detail_url = models.URLField(unique=True, verbose_name="详情页URL") 
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="抓取时间")

    class Meta:
        verbose_name = "职位信息"
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.company}"