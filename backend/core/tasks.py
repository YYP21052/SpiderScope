"""
@Time ： 2026/1/8 20:52
@Auth ： CST21052
@File ：tasks.py
@IDE ：PyCharm
@Motto：Do one thing at a time, and do well.
@describe:爬虫任务文件，获取django派发的爬虫任务，然后通过celery调用scrapy来爬取数据
"""
import subprocess
import os
import sys
from celery import shared_task
from django.conf import settings
from .models import SpiderTask  # <--- 引入模型


@shared_task
def run_spider_task(task_id):  # <--- 注意：这里改传 task_id 而不是名字
    """
    Celery 任务：根据数据库ID启动爬虫，并同步更新状态
    """
    # 1. 获取数据库对象
    try:
        task = SpiderTask.objects.get(id=task_id)
        spider_name = "quotes"  # 暂时写死，以后可以从 task.name 获取动态名字
    except SpiderTask.DoesNotExist:
        return f"❌ 任务 ID {task_id} 不存在"

    # 2. 修改状态为：运行中
    print(f"🔄 更新状态：RUNNING (Task ID: {task_id})")
    task.status = 'RUNNING'
    task.save()

    # 3. 准备启动爬虫
    cwd = os.path.join(settings.BASE_DIR, 'crawler')
    cmd = [sys.executable, '-m', 'scrapy', 'crawl', spider_name]

    try:
        # Windows 防死锁写法
        subprocess.run(cmd, cwd=cwd, check=True)

        # 4. 爬虫结束，修改状态为：已完成
        task.status = 'COMPLETED'
        task.save()
        return f"✅ 任务 {task_id} 执行完成"

    except Exception as e:
        # 5. 如果出错，修改状态为：失败
        task.status = 'FAILED'
        task.save()
        return f"💥 任务执行失败: {str(e)}"