#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生产环境部署配置示例
展示如何配置Django支持多线程/多进程
"""

# Gunicorn 配置 (多进程 + 多线程)
GUNICORN_CONFIG = {
    # 基本配置
    'bind': '0.0.0.0:8000',
    'workers': 4,  # 进程数 = CPU核心数 * 2 + 1
    'threads': 2,  # 每个进程的线程数
    'worker_class': 'sync',  # 同步工作模式
    
    # 性能配置
    'max_requests': 1000,  # 每个worker处理的最大请求数
    'max_requests_jitter': 100,  # 随机化重启时间
    'timeout': 30,  # 请求超时时间
    'keepalive': 2,  # Keep-alive连接数
    
    # 日志配置
    'accesslog': '-',  # 访问日志输出到stdout
    'errorlog': '-',   # 错误日志输出到stderr
    'loglevel': 'info',
    
    # 进程配置
    'preload_app': True,  # 预加载应用
    'worker_tmp_dir': '/dev/shm',  # 临时目录使用内存
}

# Uvicorn 配置 (异步 + 多进程)
UVICORN_CONFIG = {
    'host': '0.0.0.0',
    'port': 8000,
    'workers': 4,  # 进程数
    'loop': 'asyncio',  # 事件循环类型
    'http': 'httptools',  # HTTP协议实现
    
    # 性能配置
    'limit_concurrency': 1000,  # 并发连接限制
    'limit_max_requests': 1000,  # 最大请求数
    'timeout_keep_alive': 5,  # Keep-alive超时
    
    # 日志配置
    'log_level': 'info',
    'access_log': True,
}

# Nginx 配置示例
NGINX_CONFIG = """
upstream django_backend {
    # 负载均衡配置
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
    server 127.0.0.1:8003;
    
    # 连接配置
    keepalive 32;
}

server {
    listen 80;
    server_name your-domain.com;
    
    # 静态文件
    location /static/ {
        alias /path/to/your/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # 媒体文件
    location /media/ {
        alias /path/to/your/media/;
        expires 30d;
    }
    
    # Django应用
    location / {
        proxy_pass http://django_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时配置
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
        
        # 缓冲配置
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }
}
"""

# Docker Compose 配置示例
DOCKER_COMPOSE_CONFIG = """
version: '3.8'

services:
  web:
    build: .
    command: gunicorn --workers=4 --threads=2 --bind=0.0.0.0:8000 Translation.wsgi:application
    ports:
      - "8000:8000"
    environment:
      - DJANGO_SETTINGS_MODULE=Translation.settings
    volumes:
      - .:/app
    depends_on:
      - db
      - redis
  
  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=aitranslation
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"
  
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - web

volumes:
  postgres_data:
"""

# 启动脚本示例
START_SCRIPT = """#!/bin/bash
# 生产环境启动脚本

# 1. 使用Gunicorn启动（推荐）
gunicorn --workers=4 --threads=2 --bind=0.0.0.0:8000 Translation.wsgi:application

# 2. 使用Uvicorn启动（异步）
# uvicorn Translation.asgi:application --host=0.0.0.0 --port=8000 --workers=4

# 3. 使用Daphne启动（WebSocket支持）
# daphne -b 0.0.0.0 -p 8000 Translation.asgi:application
"""

# 性能监控配置
PERFORMANCE_MONITORING = {
    'django_debug_toolbar': {
        'enabled': False,  # 生产环境禁用
    },
    'prometheus': {
        'enabled': True,
        'port': 9090,
    },
    'sentry': {
        'enabled': True,
        'dsn': 'your-sentry-dsn',
    },
}

if __name__ == "__main__":
    print("生产环境部署配置示例")
    print("=" * 50)
    print("\n1. Gunicorn配置:")
    print(GUNICORN_CONFIG)
    print("\n2. Nginx配置示例:")
    print(NGINX_CONFIG)
    print("\n3. 启动命令:")
    print("gunicorn --workers=4 --threads=2 --bind=0.0.0.0:8000 Translation.wsgi:application") 