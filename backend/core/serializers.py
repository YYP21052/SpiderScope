"""
@Time ： 2026/1/8 21:52
@Auth ： CST21052
@File ：serializers.py
@IDE ：PyCharm
@Motto：Do one thing at a time, and do well.
@requirement:
"""
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import SpiderTask, Job

# 1. 自定义 JWT 登录序列化器 (返回更多用户信息)
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        # attrs 包含 username/password，self.user 已由父类验证成功
        
        # 注入自定义字段到响应体中
        data['username'] = self.user.username
        data['is_staff'] = self.user.is_staff
        data['is_superuser'] = self.user.is_superuser
        
        return data

# 2. 爬虫任务序列化器
class SpiderTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpiderTask
        fields = '__all__'

# 3. 职位数据序列化器
class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = '__all__'