"""
@Time ： 2026/1/8 21:52
@Auth ： CST21052
@File ：serializers.py
@IDE ：PyCharm
@Motto：Do one thing at a time, and do well.
@requirement:
"""
from rest_framework import serializers
from .models import SpiderTask

class SpiderTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpiderTask
        # 这里的 '__all__' 表示把模型里所有字段都翻译成 JSON
        # 如果只想暴露特定字段，可以用 fields = ['id', 'name', 'status']
        fields = '__all__'