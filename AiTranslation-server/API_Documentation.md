# AI翻译服务器 API 接口文档

## 概述

AI翻译服务器是一个基于Django REST Framework的多功能AI服务平台，提供文本翻译、语音识别、智能助理等功能。

**基础URL**: `http://your-domain.com`

## 目录

1. [认证模块](#认证模块)
2. [翻译API](#翻译api)
3. [语音识别API](#语音识别api)
4. [智能助理API](#智能助理api)
5. [系统管理API](#系统管理api)
6. [错误码说明](#错误码说明)

---

## 认证模块

### 1. 用户登录

**接口地址**: `POST /auth/login/`

**请求参数**:
```json
{
    "userName": "用户名或邮箱",
    "password": "密码",
    "tokenType": "token类型(可选: short/long/session/default)"
}
```

**响应示例**:
```json
{
    "code": 200,
    "msg": "登录成功",
    "data": {
        "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "refreshToken": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
}
```

### 2. 用户注册

**接口地址**: `POST /auth/register/`

**请求参数**:
```json
{
    "email": "邮箱地址",
    "password": "密码",
    "code": "邮箱验证码",
    "tokenType": "token类型(可选)"
}
```

**响应示例**:
```json
{
    "code": 200,
    "msg": "注册成功",
    "data": {
        "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "refreshToken": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
}
```

### 3. 发送邮箱验证码

**接口地址**: `POST /auth/send_email_code/`

**请求参数**:
```json
{
    "email": "邮箱地址"
}
```

**响应示例**:
```json
{
    "code": 200,
    "msg": "验证码已发送"
}
```

### 4. 邮箱登录

**接口地址**: `POST /auth/email_login/`

**请求参数**:
```json
{
    "email": "邮箱地址",
    "code": "验证码"
}
```

### 5. 刷新Token

**接口地址**: `POST /auth/refreshToken/`

**请求参数**:
```json
{
    "refreshToken": "刷新令牌"
}
```

### 6. 获取用户信息

**接口地址**: `GET /auth/getUserInfo`

**请求头**:
```
Authorization: Bearer <token>
```

**响应示例**:
```json
{
    "code": 200,
    "msg": "获取用户信息成功",
    "data": {
        "id": 1,
        "username": "user@example.com",
        "email": "user@example.com"
    }
}
```

---

## 翻译API

### 1. 文本翻译

**接口地址**: `POST /api/text-translate/`

**请求参数**:
```json
{
    "text": "要翻译的文本",
    "source_lang": "源语言代码",
    "target_lang": "目标语言代码"
}
```

**支持的语言**:
- `zh_cn`: 中文
- `en`: 英语
- `ja`: 日语
- `ko`: 韩语
- `fr`: 法语
- `es`: 西班牙语
- `ru`: 俄语
- `de`: 德语
- `it`: 意大利语
- `pt`: 葡萄牙语
- `ar`: 阿拉伯语

**响应示例**:
```json
{
    "translation": "翻译结果",
    "source_lang": "zh_cn",
    "target_lang": "en"
}
```

### 2. 图片翻译

**接口地址**: `POST /api/translate_image/`

**请求参数**:
```json
{
    "image": "base64编码的图片数据",
    "source_lang": "源语言代码",
    "target_lang": "目标语言代码"
}
```

**响应示例**:
```json
{
    "data": {
        "bubble_texts": [
            {
                "detected": "ja",
                "translation": "翻译结果"
            }
        ]
    }
}
```

---

## 语音识别API

### 1. 语音识别

**接口地址**: `POST /api/speech-recognition/`

**请求参数**:
```json
{
    "audio_data": "base64编码的音频数据",
    "audio_format": "音频格式(wav/mp3/flac/pcm)",
    "language": "语言代码",
    "accent": "口音类型(可选)"
}
```

**支持的音频格式**:
- `wav`: WAV格式
- `mp3`: MP3格式
- `flac`: FLAC格式
- `pcm`: PCM原始流

**音频要求**:
- 采样率: 16kHz 或 8kHz
- 声道: 单声道
- 位深: 16bit

**支持的语言和口音**:
- 中文: `mandarin`(普通话), `cantonese`(粤语), `sichuan`(四川话)
- 英语: `en`
- 日语: `ja`
- 韩语: `ko`

**响应示例**:
```json
{
    "result": "识别结果",
    "language": "zh_cn",
    "confidence": 0.95
}
```

### 2. 文件上传语音识别

**接口地址**: `POST /api/speech-recognition-file/`

**请求方式**: `multipart/form-data`

**请求参数**:
- `audio_file`: 音频文件
- `language`: 语言代码
- `accent`: 口音类型(可选)

### 3. 语音识别信息查询

**接口地址**: `GET /api/speech-recognition-info/`

**响应示例**:
```json
{
    "supported_formats": ["wav", "mp3", "flac", "pcm"],
    "supported_languages": {
        "zh_cn": "中文",
        "en": "英语",
        "ja": "日语",
        "ko": "韩语"
    },
    "supported_accents": {
        "mandarin": "普通话",
        "cantonese": "粤语",
        "sichuan": "四川话"
    }
}
```

---

## 智能助理API

### 1. 智能对话

**接口地址**: `POST /api/ai-assistant/smart-chat/`

**请求参数**:
```json
{
    "message": "用户消息",
    "session_id": "会话ID(可选)",
    "stream": false,
    "user_id": "用户ID(可选)",
    "auto_prompt": true
}
```

**响应示例**:
```json
{
    "message": {
        "content": "AI回复内容"
    },
    "conversation_id": "会话ID",
    "conversation_title": "对话标题",
    "prompt_info": {
        "name": "使用的提示词模板名称",
        "confidence_score": 0.85
    }
}
```

**流式响应格式**:
```
data: {"type": "start", "conversation_id": "xxx"}

data: {"type": "chunk", "message": {"content": "部分回复"}}

data: {"type": "end", "message": {"content": "完整回复"}}
```

### 2. 简单聊天(兼容旧版本)

**接口地址**: `POST /api/ai-assistant/chat/`

**请求参数**:
```json
{
    "message": "用户消息",
    "session_id": "会话ID(可选)",
    "stream": false
}
```

### 3. 对话管理

#### 3.1 获取对话列表

**接口地址**: `GET /api/ai-assistant/conversations/`

**请求参数**:
```
user_id: 用户ID(可选)
```

**响应示例**:
```json
{
    "conversations": [
        {
            "session_id": "会话ID",
            "title": "对话标题",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
            "message_count": 10
        }
    ]
}
```

#### 3.2 创建新对话

**接口地址**: `POST /api/ai-assistant/conversations/`

**请求参数**:
```json
{
    "user_id": "用户ID(可选)",
    "title": "对话标题"
}
```

#### 3.3 更新对话标题

**接口地址**: `PUT /api/ai-assistant/conversations/`

**请求参数**:
```json
{
    "session_id": "会话ID",
    "title": "新标题",
    "user_id": "用户ID(可选)"
}
```

#### 3.4 删除对话

**接口地址**: `DELETE /api/ai-assistant/conversations/`

**请求参数**:
```json
{
    "session_id": "会话ID",
    "user_id": "用户ID(可选)"
}
```

### 4. 消息历史

**接口地址**: `GET /api/ai-assistant/messages/`

**请求参数**:
```
session_id: 会话ID
user_id: 用户ID(可选)
```

**响应示例**:
```json
{
    "messages": [
        {
            "role": "user",
            "content": "用户消息",
            "created_at": "2024-01-01T00:00:00Z"
        },
        {
            "role": "assistant",
            "content": "AI回复",
            "created_at": "2024-01-01T00:00:01Z"
        }
    ]
}
```

### 5. 提示词模板管理

#### 5.1 获取提示词模板列表

**接口地址**: `GET /api/ai-assistant/prompt-templates/`

**请求参数**:
```
category: 分类(可选)
```

**响应示例**:
```json
{
    "templates": [
        {
            "id": 1,
            "name": "编程助手",
            "category": "coding",
            "description": "专门用于编程问题的提示词",
            "keywords": ["代码", "编程", "bug"],
            "priority": 1,
            "usage_count": 100
        }
    ]
}
```

#### 5.2 创建提示词模板

**接口地址**: `POST /api/ai-assistant/prompt-templates/`

**请求参数**:
```json
{
    "name": "模板名称",
    "category": "分类",
    "description": "描述",
    "keywords": ["关键词1", "关键词2"],
    "prompt_template": "提示词模板内容",
    "variables": ["变量1", "变量2"],
    "priority": 1
}
```

#### 5.3 更新提示词模板

**接口地址**: `PUT /api/ai-assistant/prompt-templates/`

**请求参数**:
```json
{
    "id": 1,
    "name": "新名称",
    "category": "新分类",
    "description": "新描述",
    "keywords": ["新关键词"],
    "prompt_template": "新模板内容",
    "variables": ["新变量"],
    "priority": 2
}
```

#### 5.4 删除提示词模板

**接口地址**: `DELETE /api/ai-assistant/prompt-templates/`

**请求参数**:
```json
{
    "id": 1
}
```

---

## 系统管理API

### 1. API访问记录查询

**接口地址**: `GET /api/access-logs/`

**请求头**:
```
Authorization: Bearer <token>
```

**请求参数**:
```
start_date: 开始日期(YYYY-MM-DD)
end_date: 结束日期(YYYY-MM-DD)
api_name: API名称(可选)
user_id: 用户ID(可选)
page: 页码(可选)
page_size: 每页数量(可选)
```

**响应示例**:
```json
{
    "logs": [
        {
            "id": 1,
            "api_name": "文本翻译",
            "user_id": "user123",
            "request_data": "请求数据",
            "response_data": "响应数据",
            "status_code": 200,
            "execution_time": 1.5,
            "created_at": "2024-01-01T00:00:00Z"
        }
    ],
    "total": 100,
    "page": 1,
    "page_size": 20
}
```

### 2. API使用统计

**接口地址**: `GET /api/usage-statistics/`

**请求头**:
```
Authorization: Bearer <token>
```

**请求参数**:
```
start_date: 开始日期(YYYY-MM-DD)
end_date: 结束日期(YYYY-MM-DD)
group_by: 分组方式(api_name/user_id/date)
```

**响应示例**:
```json
{
    "statistics": [
        {
            "api_name": "文本翻译",
            "total_calls": 1000,
            "success_rate": 0.95,
            "avg_response_time": 1.2,
            "total_users": 50
        }
    ]
}
```

---

## 错误码说明

### 认证相关错误码

| 错误码 | 说明 |
|--------|------|
| 1001 | 用户名或密码错误 |
| 1002 | 邮箱、验证码和密码不能为空 |
| 1003 | 邮箱已注册 |
| 1004 | 验证码错误或已过期 |
| 1005 | 邮箱不能为空 |
| 1006 | 邮箱和验证码不能为空 |
| 1007 | 验证码错误或已过期 |
| 1008 | 用户不存在 |

### Token相关错误码

| 错误码 | 说明 |
|--------|------|
| 2001 | 缺少refreshToken |
| 2002 | refreshToken无效或已过期 |

### API调用错误码

| 错误码 | 说明 |
|--------|------|
| 4001 | 请求参数错误 |
| 4002 | 音频格式不支持 |
| 4003 | Spark接口调用异常 |
| 4004 | 音频属性不符合要求 |
| 5001 | 服务器内部错误 |

### 通用响应格式

**成功响应**:
```json
{
    "code": 200,
    "msg": "操作成功",
    "data": {}
}
```

**错误响应**:
```json
{
    "code": 错误码,
    "msg": "错误信息",
    "data": null
}
```

---

## 使用示例

### Python示例

```python
import requests
import json

# 基础URL
base_url = "http://your-domain.com"

# 1. 用户登录
login_data = {
    "userName": "your_email@example.com",
    "password": "your_password"
}
response = requests.post(f"{base_url}/auth/login/", json=login_data)
token = response.json()["data"]["token"]

# 2. 文本翻译
headers = {"Authorization": f"Bearer {token}"}
translate_data = {
    "text": "你好世界",
    "source_lang": "zh_cn",
    "target_lang": "en"
}
response = requests.post(f"{base_url}/api/text-translate/", json=translate_data, headers=headers)
print(response.json())

# 3. 智能对话
chat_data = {
    "message": "请帮我写一个Python函数",
    "session_id": "session_123",
    "stream": False
}
response = requests.post(f"{base_url}/api/ai-assistant/smart-chat/", json=chat_data, headers=headers)
print(response.json())
```

### JavaScript示例

```javascript
// 基础URL
const baseUrl = 'http://your-domain.com';

// 1. 用户登录
async function login(username, password) {
    const response = await fetch(`${baseUrl}/auth/login/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            userName: username,
            password: password
        })
    });
    const data = await response.json();
    return data.data.token;
}

// 2. 文本翻译
async function translateText(text, sourceLang, targetLang, token) {
    const response = await fetch(`${baseUrl}/api/text-translate/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
            text: text,
            source_lang: sourceLang,
            target_lang: targetLang
        })
    });
    return await response.json();
}

// 3. 流式智能对话
async function streamChat(message, sessionId, token) {
    const response = await fetch(`${baseUrl}/api/ai-assistant/smart-chat/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
            message: message,
            session_id: sessionId,
            stream: true
        })
    });
    
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    
    while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');
        
        for (const line of lines) {
            if (line.startsWith('data: ')) {
                const data = JSON.parse(line.slice(6));
                console.log(data);
            }
        }
    }
}
```

---

## 注意事项

1. **认证**: 大部分API需要JWT token认证，请在请求头中添加 `Authorization: Bearer <token>`
2. **音频格式**: 语音识别API对音频格式有严格要求，请确保符合规范
3. **流式响应**: 智能对话的流式响应使用Server-Sent Events格式
4. **错误处理**: 请根据错误码进行相应的错误处理
5. **速率限制**: 请注意API的调用频率限制
6. **数据格式**: 所有请求和响应均使用JSON格式

---

## 更新日志

- **v1.0.0**: 初始版本，包含基础翻译和语音识别功能
- **v1.1.0**: 新增智能助理功能
- **v1.2.0**: 新增图片翻译功能
- **v1.3.0**: 优化流式响应和错误处理

---

如有问题，请联系技术支持团队。 