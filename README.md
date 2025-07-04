# AI翻译助手项目

## 项目预览

本项目是一个基于AI的智能翻译助手系统，包含前端管理界面和后端API服务。系统支持多种AI模型（OpenAI、DeepSeek等），提供文本翻译、文件翻译等功能，并集成了用户认证、文件上传等完整功能模块。

### 主要功能
- 🤖 多AI模型支持（OpenAI GPT、DeepSeek等）
- 🌐 智能文本翻译
- 📁 文件翻译支持
- 👤 用户认证与权限管理
- 📧 邮件服务集成
- 🔄 异步任务处理
- 🎨 现代化管理界面

### 主要页面





![image-20250704092050914](C:\Users\Administrator\AppData\Roaming\Typora\typora-user-images\image-20250704092050914.png)

![image-20250704092136007](C:\Users\Administrator\AppData\Roaming\Typora\typora-user-images\image-20250704092136007.png)

![image-20250704092452043](C:\Users\Administrator\AppData\Roaming\Typora\typora-user-images\image-20250704092452043.png)

![image-20250704092738941](C:\Users\Administrator\AppData\Roaming\Typora\typora-user-images\image-20250704092738941.png)

![image-20250704093124906](C:\Users\Administrator\AppData\Roaming\Typora\typora-user-images\image-20250704093124906.png)

![image-20250704093138071](C:\Users\Administrator\AppData\Roaming\Typora\typora-user-images\image-20250704093138071.png)

![image-20250704093147622](C:\Users\Administrator\AppData\Roaming\Typora\typora-user-images\image-20250704093147622.png)

![image-20250704094033427](C:\Users\Administrator\AppData\Roaming\Typora\typora-user-images\image-20250704094033427.png)

![image-20250704094048816](C:\Users\Administrator\AppData\Roaming\Typora\typora-user-images\image-20250704094048816.png)

---

## 技术栈

### 前端技术栈
- **框架**: Vue 3.5.17 + TypeScript 5.8.3
- **构建工具**: Vite 7.0.0
- **UI组件库**: Naive UI 2.42.0 + Ant Design Vue
- **状态管理**: Pinia 3.0.3
- **路由**: Vue Router 4.5.1
- **HTTP客户端**: Axios + Alova
- **样式**: UnoCSS + Sass
- **图表**: ECharts 5.6.0 + AntV G2/G6
- **国际化**: Vue I18n 11.1.7
- **代码规范**: ESLint + Prettier

### 后端技术栈
- **框架**: Django 5.2.3 + Django REST Framework 3.14.0
- **数据库**: SQLite（开发）/ 支持MySQL、PostgreSQL
- **认证**: JWT (djangorestframework-simplejwt 5.3.0)
- **AI集成**: 
  - OpenAI API (openai 1.12.0)
  - DeepSeek API
  - LangChain 0.1.0
- **异步任务**: Celery 5.3.0 + Redis 5.0.0
- **文件存储**: 阿里云OSS (oss2 2.18.0)
- **跨域处理**: django-cors-headers 4.3.1
- **WebSocket**: websocket-client 1.6.4

### 开发工具
- **包管理**: pnpm (前端) + pip (后端)
- **版本控制**: Git
- **代码提交**: simple-git-hooks + lint-staged
- **类型检查**: vue-tsc
- **代码检查**: ESLint + Vue ESLint Parser

### 部署相关
- **容器化**: Docker + Docker Compose
- **环境变量**: python-dotenv
- **静态文件**: Django Static Files
- **邮件服务**: SMTP (163邮箱)

---

## 快速开始

### 环境要求
- Node.js >= 18.20.0
- Python >= 3.8
- pnpm >= 8.7.0
- Redis (用于Celery异步任务)

### 前端启动
```bash
cd AiTranslation-frontend
pnpm install
pnpm dev
```

### 后端启动
```bash
cd AiTranslation-server
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### 环境配置
1. 复制并配置环境变量文件
2. 配置AI服务API密钥
3. 配置数据库连接
4. 启动Redis服务

### 开发命令
- `pnpm dev`: 启动前端开发服务器
- `pnpm build`: 构建前端生产版本
- `python manage.py runserver`: 启动Django开发服务器
- `python manage.py migrate`: 执行数据库迁移
- `python manage.py createsuperuser`: 创建管理员用户

---

## 项目结构

```
project/
├── AiTranslation-frontend/     # 前端项目
│   ├── src/                   # 源代码
│   ├── packages/              # 子包模块
│   ├── package.json           # 前端依赖配置
│   └── tsconfig.json          # TypeScript配置
├── AiTranslation-server/      # 后端项目
│   ├── Translation/           # Django项目配置
│   │   └── settings.py        # Django设置文件
│   ├── apps/                  # Django应用模块
│   ├── requirements.txt       # Python依赖配置
│   └── manage.py             # Django管理脚本
├── yolov12/                   # YOLO目标检测模块
├── Saber-Translator-main/     # 翻译器主模块
└── README.md                  # 项目说明文档
```


---

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。