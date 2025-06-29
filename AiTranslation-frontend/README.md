# AiTranslation-frontend

## 项目简介

AiTranslation-frontend 是一个基于 Vue3、Vite、Naive UI、Ant Design X 的智能翻译与 AI 助手前端项目。支持文本翻译、语音识别与翻译、AI Copilot 聊天等功能，界面美观，体验流畅，可对接自定义后端（如 Django/FastAPI）。

---

## 主要功能

- 🌐 多语言文本翻译
- 🎤 语音识别与语音翻译
- 🤖 AI Copilot 聊天助手（支持上下文对话）
- 🌓 主题切换、国际化
- 🔒 用户登录/登出、Token 失效自动处理

---

## 技术栈

- Vue 3
- Vite
- TypeScript
- Naive UI
- Ant Design X
- unplugin-icons
- axios

---

## 快速开始

### 1. 安装依赖

```bash
pnpm install
# 或
npm install
```

### 2. 配置环境变量

在根目录新建 `.env` 文件，配置后端 API 地址：

```
VITE_API_BASE_URL=http://localhost:8000
```

### 3. 启动开发环境

```bash
pnpm dev
# 或
npm run dev
```

### 4. 打包构建

```bash
pnpm build
# 或
npm run build
```

---

## 主要接口说明

### AI Copilot 聊天接口

- **POST** `/api/ai-assistant/chat/`
- **请求体示例**：

  ```json
  {
    "model": "your-model",
    "message": {
      "content": "你好",
      "role": "user"
    },
    "messages": [
      {
        "content": "你好",
        "role": "user"
      }
    ],
    "stream": false
  }
  ```

- **响应体示例**：

  ```json
  {
    "message": {
      "content": "你好，我是AI助手！"
    }
  }
  ```

### Token 失效处理

- 后端返回如下内容时，前端会自动登出并跳转登录页：

  ```json
  {
    "code": "token_not_valid",
    "detail": "Given token not valid for any token type"
  }
  ```

---

## 目录结构

```
├── src/                # 源码目录
│   ├── views/          # 页面组件
│   ├── components/     # 通用组件
│   ├── store/          # 状态管理
│   ├── service/        # API 请求
│   └── ...             
├── public/             # 静态资源
├── package.json
├── vite.config.ts
├── README.md
└── ...
```

---

## 常见问题

- **如何对接自己的后端？**  
  修改 `.env` 文件中的 `VITE_API_BASE_URL`，并保证后端接口返回格式与前端一致即可。

- **如何自定义主题/国际化？**  
  项目已内置主题切换和多语言，详见 `src/store/modules/theme` 和 `src/locales/`。

- **Token 失效如何处理？**  
  前端会自动检测 token 失效并跳转登录页，无需手动处理。

---

## 许可证

[MIT License](./LICENSE)

---

如需详细开发文档或二次开发支持，请查阅源码或联系项目维护者。
