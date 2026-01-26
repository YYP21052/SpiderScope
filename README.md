# 🕷️ JobRadar - 全网职位采集与分析平台

> **一个基于微服务架构的分布式职位数据采集与可视化分析中台**
>
> *From Course Project to Enterprise Solution*

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-4.2-092E20?style=flat&logo=django&logoColor=white)
![Vue](https://img.shields.io/badge/Vue.js-3.0-4FC08D?style=flat&logo=vue.js&logoColor=white)
![Scrapy](https://img.shields.io/badge/Scrapy-2.11-60A839?style=flat&logo=scrapy&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED?style=flat&logo=docker&logoColor=white)

---

##  项目背景与简介

**JobRadar** (原名 SpiderScope) 起源于一次大学课程设计，经过不断的重构与迭代，现已演变为一个具备**企业级架构雏形**的全栈采集系统。

项目旨在解决传统招聘数据采集中的痛点：平台反爬严格、数据分散杂乱、无法集中分析。通过构建自动化的数据流水线，我们实现了对 **Boss直聘**、**前程无忧 (51job)**、**实习僧**、**应届生求职网** 等主流平台的职位数据采集、清洗与结构化入库。

> ⚠️ **说明**：本项目**重在后端架构、爬虫攻防与数据处理**。前端界面使用了 Element Plus 进行快速搭建，UI较为朴素（丑）

---

## ✨ 核心亮点

- **🛡️ 深度反爬虫**
  - **Selenium 隐身模式**：自研中间件集成 CDP 协议，完美隐藏 WebDriver 特征，成功绕过 51job 等站点的检测。
  - **DrissionPage 集成**：引入新一代自动化工具 DrissionPage，专门攻克 Boss直聘 等高难度风控站点。
  - **动态采集**：支持在前端动态输入关键词与城市，告别"硬编码"爬虫，想爬什么由你决定。

- **⚙️ 分布式后端架构**
  - **Django + DRF**：构建稳健的 RESTful API 与任务调度中心。
  - **Celery + Redis**：实现高并发异步任务队列，支持多 Worker 分布式部署。
  - **混合存储**：PostgreSQL 存储业务数据，MongoDB 存储海量职位详情，各取所长。
  - **Docker 容器化**：实现了 Database、Backend、Frontend、Worker 的全链路容器化部署，一键拉起整个微服务集群。

- **🔐 安全与权限**

  - **JWT 无状态认证**：基于 SimpleJWT 实现前后端分离的安全认证。
  - **RBAC 权限模型**：实现了细粒度的权限控制，普通用户仅可浏览数据，管理员拥有爬虫启停的高级权限。

---

## 🏗 系统架构图

```mermaid
graph TD
    User(用户/求职者) -->|查看大屏| Vue[Vue 3 前端]
    Admin(管理员) -->|控制爬虫| Vue
    Vue <-->|REST API| Django[Django API 网关]
    
    subgraph "后端服务集群"
        Django -->|JWT Auth| Auth[认证服务]
        Django -->|发布任务| Redis[(Redis 消息队列)]
        Redis -->|消费任务| Celery[Celery Worker 集群]
    end

    subgraph "采集引擎"
        Celery -->|启动进程| Scrapy[Scrapy 主引擎]
        Scrapy -->|自动化驱动| Chrome[Chrome/DrissionPage]
        Chrome -->|请求/交互| Web(招聘网站: Boss/51job/实习僧...)
    end

    subgraph "数据持久化"
        Scrapy -->|清洗入库| Mongo[(MongoDB - 原始数据)]
        Django -->|查询统计| PG[(PostgreSQL - 业务/统计数据)]
    end
```

---

## 📂 项目目录结构

```text
SpiderScope/
├── backend/                # 后端核心代码
│   ├── core/               # 核心业务逻辑 (API, Tasks)
│   ├── crawler/            # Scrapy 爬虫工程
│   │   ├── spiders/        # 爬虫脚本 (51job, boss)
│   │   └── middlewares.py  # 中间件 (DrissionPage/Selenium集成)
│   ├── spiderscope/        # Django settings 配置
│   └── Dockerfile          # 后端镜像构建文件
├── frontend/               # 前端工程代码
│   ├── src/                # Vue 源码 (Views, Stores, Components)
│   └── Dockerfile          # 前端镜像构建文件 (含 Nginx)
├── docker-compose.yml      # 容器编排文件
└── README.md               # 项目说明文档

```

--- 

## 🚀 快速开始 (Docker 一键部署)

本项目已全面支持容器化 (前后端独立容器)，这是最省心的安装方式。

### 1. 前置准备
确保您的服务器或本机已安装：
- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)

### 2. 配置文件
在项目根目录创建 `.env` 文件 (可选，用于自定义配置，默认已有)：
```env
DB_NAME=spiderscope
DB_USER=postgres
...
```

### 3. 一键启动
```bash
# 编译并启动所有服务 (前端 Nginx、后端 Django、数据库、Redis、Celery)
docker-compose up -d --build
```
系统将自动执行：
- 构建 `frontend` 镜像：基于 Node.js 编译 Vue 代码，并打包进 Nginx 容器。
- 构建 `backend` 镜像：安装 Python 依赖。
- 启动 Postgres, Mongo, Redis 基础服务。

### 4. 初始化数据
容器启动后，需要进行数据库迁移和创建管理员：
```bash
# 进入后端容器
docker-compose exec backend bash

# 执行迁移
python manage.py migrate

# 创建超级管理员
python manage.py createsuperuser
```

### 5. 访问系统
- **前端页面**：访问 `http://localhost:80` (默认 80 端口)。
- **后端 API**：`http://localhost:8000` (仅调试用，正常通过前端反向代理访问)。

---

## 🛠 本地开发部署 (传统方式)

如果您想进行代码修改或调试，建议使用本地环境。

### 后端 (Backend)

```bash
cd backend
# 1. 安装依赖
pip install -r requirements.txt
# 2. 启动 Django
python manage.py runserver
# 3. 启动 Celery Worker (Windows 需加 -P eventlet)
celery -A spiderscope worker -l info -P eventlet

```

### 前端 (Frontend)

```bash
cd frontend
# 1. 安装依赖
npm install
# 2. 启动开发服务器
npm run dev

```

---
## 💡 使用手册

1.  **数据大屏**：
    打开首页，系统会自动聚合数据库中的职位信息，展示薪资分布图表。无需登录即可查看。
2.  **登录后台**：
    点击右上角 **"登录 / 管理"**，使用管理员账号登录。
3.  **爬虫控制台**：
    登录后进入控制台，选择 **"Boss直聘"** 或 **"前程无忧"**，输入关键词（如 `Python`），点击启动。
    *注意：本地运行时会弹出浏览器窗口，请勿手动关闭，静待脚本执行完毕。*

---

## 🤝 关于作者

**YYP21052**

一个热爱技术的全栈开发者。本项目始于大学课程设计，现已成为一个功能完备的演示级项目。

如果有帮到你，欢迎点个 ⭐ **Star** 支持一下！

---

## 📄 License

MIT © 2026 YYP21052
