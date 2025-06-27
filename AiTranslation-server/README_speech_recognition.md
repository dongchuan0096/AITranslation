# 语音识别功能实现总结

## 概述

本项目已成功集成了科大讯飞的语音识别功能，基于官方WebSocket接口实现，提供了完整的REST API服务。

## 实现的功能

### ✅ 核心功能
- **语音转文字**: 支持多种音频格式的语音识别
- **多语言支持**: 中文、英文、日文、韩文等多种语言
- **多种输入方式**: 文件上传、Base64编码数据
- **实时识别**: 基于WebSocket的流式识别
- **错误处理**: 完整的错误处理和日志记录

### ✅ API接口
- `GET /api/speech-recognition-info/` - 获取支持的格式和配置信息
- `POST /api/speech-recognition/` - 通过Base64数据识别
- `POST /api/speech-recognition-file/` - 通过文件上传识别

### ✅ 技术特性
- **官方接口**: 基于科大讯飞官方WebSocket接口
- **配置管理**: 统一的配置文件和密钥管理
- **临时文件处理**: 自动清理临时文件
- **API日志**: 完整的API访问日志记录
- **响应标准化**: 统一的API响应格式

## 文件结构

```
apps/
├── utils/
│   ├── spark_mucl_cn_iat.py          # 官方语音识别接口实现
│   ├── xunfei_config.py              # 讯飞API配置
│   ├── response.py                   # API响应工具
│   └── api_logger.py                 # API日志记录
├── api/
│   ├── views.py                      # API视图实现
│   └── urls.py                       # URL路由配置
└── models.py                         # 数据模型

docs/
├── speech_recognition_guide.md       # 详细使用指南
└── api_usage_examples.md            # API使用示例

test_api_interface.py                 # API接口测试脚本
start_and_test.py                     # 启动和测试脚本
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置API密钥

编辑 `apps/utils/xunfei_config.py`:

```python
XUNFEI_CONFIG = {
    'APP_ID': 'your_app_id',
    'API_KEY': 'your_api_key', 
    'API_SECRET': 'your_api_secret',
}
```

### 3. 启动服务

```bash
# 方式1: 使用启动脚本
python start_and_test.py

# 方式2: 手动启动
python manage.py runserver
```

### 4. 测试接口

```bash
# 测试API接口
python test_api_interface.py

# 或者使用curl
curl http://localhost:8000/api/speech-recognition-info/
```

## API使用示例

### 文件上传识别

```python
import requests

with open('audio.wav', 'rb') as f:
    files = {'audio_file': f}
    data = {'language': 'zh_cn', 'accent': 'mandarin'}
    
    response = requests.post(
        'http://localhost:8000/api/speech-recognition-file/',
        files=files,
        data=data
    )

result = response.json()
if result['success']:
    print(f"识别结果: {result['data']['text']}")
```

### Base64数据识别

```python
import requests
import base64

with open('audio.wav', 'rb') as f:
    audio_base64 = base64.b64encode(f.read()).decode('utf-8')

data = {
    'audio_data': audio_base64,
    'audio_format': 'wav',
    'language': 'zh_cn',
    'accent': 'mandarin'
}

response = requests.post(
    'http://localhost:8000/api/speech-recognition/',
    json=data
)

result = response.json()
if result['success']:
    print(f"识别结果: {result['data']['text']}")
```

## 支持的音频格式

| 格式 | 说明 | 推荐参数 |
|------|------|----------|
| WAV | 无损音频格式 | 16kHz, 16bit, 单声道 |
| MP3 | 有损压缩格式 | 16kHz, 单声道 |
| PCM | 原始音频数据 | 16kHz, 16bit, 单声道 |

## 音频要求

- **采样率**: 16kHz（推荐）或8kHz
- **位深度**: 16bit
- **声道**: 单声道
- **时长**: 最长60秒
- **文件大小**: 最大50MB

## 错误处理

| 错误码 | 说明 | 解决方案 |
|--------|------|----------|
| 4001 | 音频数据为空 | 检查音频数据 |
| 4002 | 不支持的语言 | 使用支持的语言代码 |
| 4003 | 不支持的音频格式 | 转换为支持的格式 |
| 4004 | 音频长度超限 | 缩短音频时长 |
| 4005 | 识别失败 | 检查网络和配置 |
| 4006 | 服务器异常 | 检查服务器日志 |

## 性能优化

1. **音频预处理**: 确保音频格式正确
2. **文件大小**: 控制音频文件大小
3. **并发控制**: 避免过多并发请求
4. **错误重试**: 实现重试机制
5. **缓存结果**: 缓存相同音频的识别结果

## 监控和日志

- **API访问日志**: 记录所有API调用
- **错误日志**: 详细的错误信息记录
- **性能统计**: 响应时间和成功率统计
- **使用统计**: API使用情况统计

## 安全考虑

1. **API密钥保护**: 配置文件中的密钥安全存储
2. **文件上传限制**: 文件大小和格式限制
3. **输入验证**: 严格的参数验证
4. **临时文件清理**: 自动清理临时文件
5. **错误信息过滤**: 避免敏感信息泄露

## 扩展功能

### 可扩展的功能
- **批量识别**: 支持多个音频文件批量处理
- **实时流识别**: 支持实时音频流识别
- **多语言混合**: 支持多语言混合识别
- **自定义词汇**: 支持自定义词汇识别
- **音频预处理**: 内置音频格式转换

### 集成建议
- **前端界面**: 开发Web界面进行语音识别
- **移动应用**: 集成到移动应用中
- **语音助手**: 作为语音助手的输入模块
- **会议记录**: 用于会议语音转文字
- **字幕生成**: 用于视频字幕生成

## 故障排除

### 常见问题

1. **配置错误**
   ```
   检查 apps/utils/xunfei_config.py 中的API密钥配置
   ```

2. **网络连接问题**
   ```
   确保服务器能访问讯飞API服务器
   检查防火墙设置
   ```

3. **音频格式问题**
   ```
   确保音频格式符合要求
   使用音频转换工具进行格式转换
   ```

4. **依赖问题**
   ```
   安装缺失的Python包
   pip install -r requirements.txt
   ```

### 调试方法

1. **查看日志**
   ```bash
   python manage.py runserver --verbosity=2
   ```

2. **测试配置**
   ```python
   from apps.utils.xunfei_config import XUNFEI_CONFIG
   print(XUNFEI_CONFIG)
   ```

3. **测试连接**
   ```python
   from apps.utils.spark_mucl_cn_iat import create_xunfei_speech_recognition
   client = create_xunfei_speech_recognition()
   ```

## 更新日志

### v1.0.0 (2024-01-01)
- ✅ 集成科大讯飞官方WebSocket接口
- ✅ 实现完整的REST API服务
- ✅ 支持多种音频格式和语言
- ✅ 完整的错误处理和日志记录
- ✅ 提供详细的使用文档和示例

## 技术支持

- **官方文档**: [科大讯飞开放平台](https://doc.xfyun.cn/)
- **错误码查询**: [错误码列表](https://www.xfyun.cn/document/error-code)
- **技术支持**: [讯飞论坛](http://bbs.xfyun.cn/)

## 许可证

本项目基于MIT许可证开源。

---

**注意**: 使用前请确保已正确配置科大讯飞API密钥，并遵守相关使用条款和限制。 