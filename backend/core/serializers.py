"""
@Time ： 2026/1/8 21:52
@Auth ： CST21052
@File ：serializers.py
@IDE ：PyCharm
@Motto：Do one thing at a time, and do well.
@requirement:
"""
from rest_framework import serializers
from .models import SpiderTask, Job

# 1. 爬虫任务序列化器
class SpiderTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpiderTask
        fields = '__all__'

# 2. 职位数据序列化器
class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = '__all__'