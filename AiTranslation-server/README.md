# AI翻译服务器 (AiTranslation-server)

## 项目概述

AI翻译服务器是一个基于Django的智能翻译和语音识别服务平台，集成了多种AI模型，提供文本翻译、图片翻译、语音识别和智能对话等功能。

## 核心技术栈

### 后端框架
- **Django 5.2.3** - 主Web框架
- **Django REST Framework 3.14.0** - API开发框架
- **Django CORS Headers 4.3.1** - 跨域资源共享支持

### 数据库
- **SQLite3** - 轻量级关系型数据库
- **Redis 5.0.0** - 缓存和会话存储
- **Celery 5.3.0** - 异步任务队列

### AI模型集成
- **OpenAI GPT-3.5-turbo** - 文本生成和翻译
- **DeepSeek Chat** - 多语言翻译和对话
- **科大讯飞语音识别** - 语音转文字服务

### 认证与安全
- **Django REST Framework Simple JWT 5.3.0** - JWT身份认证
- **Django内置安全中间件** - CSRF、XSS防护

### 语音识别技术
- **WebSocket协议** - 实时语音识别
- **讯飞开放平台API** - 专业语音识别服务
- **多格式音频支持** - WAV、MP3、M4A、AMR、PCM

### 开发工具
- **Python 3.x** - 主要开发语言
- **Requests 2.31.0** - HTTP客户端库
- **WebSocket-client 1.6.4** - WebSocket客户端
- **LangChain 0.1.0** - AI应用开发框架
- **Python-dotenv 1.0.0** - 环境变量管理

## 功能特性

### 🔤 智能翻译
- **多语言支持**: 中文、英文、日文、韩文、法文、西班牙文、俄文、德文、意大利文、葡萄牙文、阿拉伯语
- **文本翻译**: 基于AI模型的智能文本翻译
- **图片翻译**: OCR识别图片中的文字并进行翻译
- **语言自动检测**: 自动识别源文本语言

### 🎤 语音识别
- **多格式支持**: WAV、MP3、M4A、AMR、PCM音频格式
- **多语言识别**: 支持中文、英文、日文、韩文等多种语言
- **实时识别**: 基于WebSocket的流式语音识别
- **高精度识别**: 基于科大讯飞专业语音识别引擎

### 🤖 智能对话
- **AI助手**: 基于大语言模型的智能对话
- **会话管理**: 支持多轮对话和上下文记忆
- **流式响应**: 实时流式输出AI回复
- **提示词优化**: 智能提示词选择和优化

### 🔐 用户系统
- **JWT认证**: 安全的用户身份认证
- **邮箱注册**: 支持邮箱注册和验证
- **用户管理**: 完整的用户信息管理
- **API访问控制**: 基于权限的API访问控制

## 项目结构

```
AiTranslation-server/
├── apps/                          # 应用模块
│   ├── api/                       # API接口模块
│   ├── login/                     # 用户认证模块
│   ├── ai_assistant/              # AI助手模块
│   ├── knowledge_base/            # 知识库模块
│   └── utils/                     # 工具模块
├── Translation/                   # Django项目配置
│   ├── settings.py               # 项目设置
│   ├── urls.py                   # URL路由
│   └── middleware.py             # 中间件
├── docs/                         # 文档目录
├── media/                        # 媒体文件
├── requirements.txt              # Python依赖
├── manage.py                     # Django管理脚本
└── README.md                     # 项目说明
```

## 快速开始

### 环境要求
- Python 3.8+
- Redis 5.0+
- 科大讯飞开放平台账号
- OpenAI API Key (可选)
- DeepSeek API Key (可选)

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd AiTranslation-server
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置环境变量**
```bash
# 复制并编辑配置文件
cp apps/utils/xunfei_config.py.example apps/utils/xunfei_config.py
```

4. **配置API密钥**
编辑 `apps/utils/xunfei_config.py`:
```python
XUNFEI_CONFIG = {
    'APP_ID': 'your_app_id',
    'API_KEY': 'your_api_key', 
    'API_SECRET': 'your_api_secret',
}
```

5. **数据库迁移**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **启动服务**
```bash
python manage.py runserver
```

## API接口

### 认证接口
- `POST /auth/register/` - 用户注册
- `POST /auth/login/` - 用户登录
- `POST /auth/refresh/` - 刷新令牌
- `GET /auth/getUserInfo/` - 获取用户信息

### 翻译接口
- `POST /api/text-translate/` - 文本翻译
- `POST /api/translate_image/` - 图片翻译

### 语音识别接口
- `POST /api/speech-recognition/` - 语音识别(Base64)
- `POST /api/speech-recognition-file/` - 语音识别(文件上传)
- `GET /api/speech-recognition-info/` - 获取语音识别信息

### AI助手接口
- `POST /api/ai-assistant/smart-chat/` - 智能对话
- `POST /api/ai-assistant/chat/` - 简单聊天

## 配置说明

### AI模型配置
在 `Translation/settings.py` 中配置AI模型：

```python
# OpenAI配置
OPENAI_API_KEY = "your_openai_api_key"
OPENAI_MODEL = "gpt-3.5-turbo"

# DeepSeek配置  
DEEPSEEK_API_KEY = "your_deepseek_api_key"
DEEPSEEK_MODEL = "deepseek-chat"
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"

# AI模型选择
AI_MODEL_TYPE = "deepseek"  # "openai" 或 "deepseek"
```

### 邮件配置
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.163.com'
EMAIL_PORT = 465
EMAIL_HOST_USER = 'your_email@163.com'
EMAIL_HOST_PASSWORD = 'your_email_password'
EMAIL_USE_SSL = True
```

## 部署说明

### 生产环境配置
1. 设置 `DEBUG = False`
2. 配置生产数据库
3. 设置 `ALLOWED_HOSTS`
4. 配置静态文件服务
5. 使用WSGI服务器(如Gunicorn)

### Docker部署
```bash
# 构建镜像
docker build -t ai-translation-server .

# 运行容器
docker run -p 8000:8000 ai-translation-server
```

## 开发指南

### 代码规范
- 遵循PEP 8 Python代码规范
- 使用类型注解
- 编写单元测试
- 添加详细的文档注释

### 贡献指南
1. Fork项目
2. 创建功能分支
3. 提交代码
4. 创建Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 联系方式

- 项目维护者: [Your Name]
- 邮箱: [your.email@example.com]
- 项目地址: [GitHub Repository URL]

## 更新日志

### v1.0.0 (2024-01-01)
- 初始版本发布
- 支持文本翻译和语音识别
- 集成OpenAI和DeepSeek API
- 完整的用户认证系统 