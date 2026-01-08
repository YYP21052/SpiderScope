"""
@Time ： 2026/1/8 20:45
@Auth ： CST21052
@File ：celery.py
@IDE ：PyCharm
@Motto：Do one thing at a time, and do well.
@describe:异步文件，配置 Celery
"""
import os
from celery import Celery

# 1. 设置默认的 Django 配置文件路径
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spiderscope.settings')

# 2. 创建 Celery 实例，名字叫 'spiderscope'
app = Celery('spiderscope')

# 3. 告诉 Celery 去哪里找配置（我们要去 settings.py 里找以 CELERY_ 开头的配置）
app.config_from_object('django.conf:settings', namespace='CELERY')

# 4. 自动发现每个 App 下的 tasks.py 文件
app.autodiscover_tasks()