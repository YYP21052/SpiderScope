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
def run_spider_task(spider_name, params=None):
    """
    Celery 任务：执行 Scrapy 爬虫 (支持动态参数)
    :param spider_name: 爬虫名称
    :param params: 字典参数, 会转换为 -a key=value 传给 scrapy
    """
    print(f"🚀 [Celery] 收到爬虫任务: {spider_name} | 参数: {params}")
    
    # 1. 定义工作目录 (确保切换到 Scrapy 项目根目录)
    cwd = os.path.join(settings.BASE_DIR, 'crawler')
    
    # 2. 构造命令 (使用当前 Python 环境)
    cmd = [sys.executable, '-m', 'scrapy', 'crawl', spider_name]

    # 🟢 注入 -a 参数
    if params:
        for key, value in params.items():
            cmd.extend(['-a', f'{key}={value}'])
    
    try:
        # 3. 使用 Popen 调用 - ⚠️ Windows GUI 关键修改
        # 移除 PIPEs，使用 shell=True 允许弹出窗口
        # shell=True 在 Windows 上有助于唤起 GUI 子进程
        process = subprocess.Popen(
            cmd, 
            cwd=cwd, 
            shell=True  # 允许弹出CMD窗口(如有)，更有利于驱动显示
        )
        
        print(f"⏳ [Celery] 爬虫 {spider_name} 正在运行 (PID: {process.pid})...")
        print("💡 提示: 请检查服务器/Worker所在的机器是否有弹出的浏览器窗口")
        
        # 等待子进程结束 (阻塞当前 Celery Worker 直到爬虫跑完)
        returncode = process.wait()
        
        if returncode == 0:
            print(f"✅ [Celery] 爬虫 {spider_name} 执行完成！")
            return f"爬虫 {spider_name} 成功结束"
        else:
            print(f"💥 [Celery] 爬虫 {spider_name} 退出码: {returncode}")
            return f"爬虫 {spider_name} 异常退出"

    except Exception as e:
        print(f"❌ [Celery] 启动报错: {str(e)}")
        return f"系统错误: {str(e)}"