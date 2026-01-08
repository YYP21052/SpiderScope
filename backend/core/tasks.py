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
import sys  # <--- 新增
from celery import shared_task
from django.conf import settings


@shared_task
def run_spider_task(spider_name):
    """
    Celery 任务：启动爬虫（Windows 兼容优化版）
    """
    print(f"🕷️ 收到任务：准备启动爬虫 [{spider_name}] ...")

    # 1. 定位 Scrapy 项目目录
    cwd = os.path.join(settings.BASE_DIR, 'crawler')

    # 2. 拼接命令：使用当前的 python.exe 去运行 scrapy 模块
    # 这样比直接调用 'scrapy' 命令更稳定，能确保用对虚拟环境
    cmd = [sys.executable, '-m', 'scrapy', 'crawl', spider_name]

    try:
        # 3. 执行命令 (Windows 下不要使用 capture_output=True，容易死锁)
        # 我们直接让它在当前窗口运行，这样你能在 Celery 窗口直接看到 Scrapy 的日志
        subprocess.run(cmd, cwd=cwd, check=True)

        # 既然没有捕获输出，我们就简单返回成功
        return f"✅ 爬虫 {spider_name} 执行指令已发送完毕"

    except subprocess.CalledProcessError as e:
        return f"❌ 爬虫执行失败，错误码: {e.returncode}"
    except Exception as e:
        return f"💥 发生未知异常: {str(e)}"