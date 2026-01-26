"""
Django settings for spiderscope project.
"""

import os
from pathlib import Path
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ==========================================
# 🔐 安全配置 (修复关键点)
# ==========================================
# 修复：给 SECRET_KEY 一个默认值。
# 这样即使 Docker 环境变量没传，也能用默认值启动，不会报错。
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-fix-key-123456-change-me-in-prod')

# 调试模式 (生产环境建议关掉，但演示项目开启方便排错)
DEBUG = True

# 允许所有主机 (方便 Docker 容器间通信)
ALLOWED_HOSTS = ['*']


# ==========================================
# 🔥 核心应用配置
# ==========================================
INSTALLED_APPS = [
    'django.contrib.admin',       # 管理后台
    'django.contrib.auth',        # 认证系统
    'django.contrib.contenttypes',# 内容类型
    'django.contrib.sessions',    # 会话
    'django.contrib.messages',    # 消息
    'django.contrib.staticfiles', # 静态文件

    # --- 第三方库 ---
    'rest_framework',             # DRF
    'rest_framework_simplejwt',   # JWT
    'django_celery_results',      # Celery 结果
    'corsheaders',                # 跨域

    # --- 你的应用 ---
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware', # 跨域中间件 (靠前)
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware', # 认证中间件
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'spiderscope.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'spiderscope.wsgi.application'


# ==========================================
# 🗄️ 数据库配置
# ==========================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'spider_db'),
        'USER': os.environ.get('DB_USER', 'spider_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'spider_password'),
        'HOST': os.environ.get('DB_HOST', '127.0.0.1'), # Docker 中会自动读取环境变量改为 'db'
        'PORT': '5432',
    }
}


# ==========================================
# 密码验证 & 国际化
# ==========================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'zh-hans' # 改为中文，方便看后台
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ==========================================
# ⚡ Celery 异步配置
# ==========================================
redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
CELERY_BROKER_URL = redis_url
CELERY_RESULT_BACKEND = redis_url
CELERY_TIMEZONE = 'Asia/Shanghai'


# ==========================================
# 🌐 跨域 & API 配置
# ==========================================
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",    # 本地开发 (npm run dev)
    "http://127.0.0.1:5173",
    "http://localhost",         # 🟢 新增：Docker Nginx 默认端口 (80)
    "http://127.0.0.1",         # 🟢 新增
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ]
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
    'AUTH_HEADER_CLASS':('Bearer',),
}