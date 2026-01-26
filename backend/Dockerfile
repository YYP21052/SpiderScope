# 使用官方 Python 3.10 镜像作为基础镜像
FROM python:3.10-slim

# 设置环境变量
# 防止 Python 写入 pyc 文件
ENV PYTHONDONTWRITEBYTECODE 1
# 防止 Python 缓冲 stdout/stderr
ENV PYTHONUNBUFFERED 1

# 设置工作目录
WORKDIR /app

# 安装系统依赖
# 1. netcat: 用于 wait-for-it 脚本 (等待数据库启动)
# 2. Chrome & Chromedriver 依赖库 (用于 Selenium)
RUN apt-get update && apt-get install -y \
    netcat-openbsd \
    gnupg \
    wget \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# --- 安装 Google Chrome (可选，如果不想在 Docker 里跑爬虫可以不装，但为了完整性建议装) ---
# 注意：在 Docker 里跑 Chrome 比较麻烦，需要特殊配置 (--no-sandbox)
# 这里先安装基础依赖，实际 Chrome二 进制文件可能需要手动下载或使用特定镜像
# 为了简化，如果是生产环境，建议爬虫节点单独部署。
# 这里我们假设这个 Dockerfile 主要用于跑 Django 和 Celery (不含 GUI 爬虫)
# 或者使用无头模式。

# 复制依赖文件
COPY requirements.txt /app/

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码
COPY . /app/

# 暴露端口
EXPOSE 8000

# 启动脚本 (默认命令，会被 docker-compose 覆盖)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
