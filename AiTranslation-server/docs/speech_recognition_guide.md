# 讯飞语音识别模块使用指南

## 概述

本项目集成了科大讯飞的语音识别功能，基于官方WebSocket接口实现，支持多种音频格式的语音转文字功能。

## 功能特性

- ✅ 支持多种音频格式：WAV、MP3、M4A、AMR、PCM
- ✅ 支持多语言识别：中文、英文、日文、韩文等
- ✅ 基于官方WebSocket接口，稳定可靠
- ✅ 支持流式识别，实时返回结果
- ✅ 自动配置管理，易于集成
- ✅ 完整的错误处理和日志记录

## 安装配置

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置讯飞API密钥

编辑 `apps/utils/xunfei_config.py` 文件，填入您的讯飞开放平台API密钥：

```python
XUNFEI_CONFIG = {
    'APP_ID': 'your_app_id',           # 您的讯飞APP_ID
    'API_KEY': 'your_api_key',         # 您的讯飞API_KEY
    'API_SECRET': 'your_api_secret',   # 您的讯飞API_SECRET
}
```

### 3. 获取API密钥

1. 访问 [科大讯飞开放平台](https://www.xfyun.cn/)
2. 注册并登录账号
3. 创建新应用，选择"语音听写（流式）"服务
4. 获取APP_ID、API_KEY和API_SECRET

## 使用方法

### 1. 基本使用

```python
from apps.utils.spark_mucl_cn_iat import create_xunfei_speech_recognition

# 创建语音识别客户端
asr_client = create_xunfei_speech_recognition()

# 识别音频文件
result = asr_client.recognize_audio_file('path/to/audio.wav')

if result['success']:
    print(f"识别结果: {result['text']}")
else:
    print(f"识别失败: {result['error']}")
```

### 2. 使用服务类

```python
from apps.utils.speech_recognition_example import create_speech_recognition_service

# 创建语音识别服务
speech_service = create_speech_recognition_service()

# 识别音频文件
result = speech_service.recognize_audio('path/to/audio.wav')

if result['success']:
    print(f"识别结果: {result['text']}")
else:
    print(f"识别失败: {result['error']}")
```

### 3. Django API集成

```python
from django.http import JsonResponse
from apps.utils.speech_recognition_example import speech_recognition_api

# 在Django视图中使用
def my_view(request):
    return speech_recognition_api(request)
```

### 4. 命令行使用

```bash
# 基本识别
python apps/utils/speech_recognition_example.py audio.wav

# 保存结果到文件
python apps/utils/speech_recognition_example.py audio.wav -o result.txt
```

## API接口

### 语音识别API

**请求地址：** `POST /api/speech/recognize/`

**请求参数：**
- `audio_file`: 音频文件 (multipart/form-data)

**响应格式：**
```json
{
    "success": true,
    "data": {
        "text": "识别的文本内容",
        "language": "zh_cn",
        "file_size": 1024000,
        "file_format": "wav"
    },
    "message": "识别成功"
}
```

**错误响应：**
```json
{
    "success": false,
    "message": "错误信息"
}
```

## 支持的音频格式

| 格式 | 说明 | 推荐采样率 |
|------|------|------------|
| WAV  | 无损音频格式 | 16kHz |
| MP3  | 有损压缩格式 | 16kHz |
| M4A  | AAC编码格式 | 16kHz |
| AMR  | 语音压缩格式 | 8kHz |
| PCM  | 原始音频数据 | 16kHz |

## 音频要求

- **采样率**: 推荐16kHz，支持8kHz
- **位深度**: 16bit
- **声道**: 单声道
- **文件大小**: 最大50MB
- **时长**: 建议不超过60秒

## 错误处理

### 常见错误码

| 错误码 | 说明 | 解决方案 |
|--------|------|----------|
| 10001 | 参数错误 | 检查API密钥配置 |
| 10002 | 网络错误 | 检查网络连接 |
| 10003 | 服务错误 | 联系讯飞技术支持 |
| 10004 | 音频格式错误 | 检查音频格式和参数 |
| 10005 | 音频数据错误 | 检查音频文件完整性 |

### 错误处理示例

```python
result = asr_client.recognize_audio_file('audio.wav')

if not result['success']:
    error = result['error']
    if '10001' in error:
        print("配置错误，请检查API密钥")
    elif '10002' in error:
        print("网络连接失败")
    elif '10004' in error:
        print("音频格式不支持")
    else:
        print(f"未知错误: {error}")
```

## 性能优化

### 1. 音频预处理

```python
import librosa
import soundfile as sf

def preprocess_audio(input_file, output_file):
    """音频预处理：转换为16kHz单声道"""
    # 加载音频
    audio, sr = librosa.load(input_file, sr=16000, mono=True)
    
    # 保存为WAV格式
    sf.write(output_file, audio, 16000)
    
    return output_file
```

### 2. 批量处理

```python
import os
from concurrent.futures import ThreadPoolExecutor

def batch_recognize(audio_files, max_workers=3):
    """批量识别音频文件"""
    speech_service = create_speech_recognition_service()
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(
            speech_service.recognize_audio, 
            audio_files
        ))
    
    return results
```

## 测试

### 运行测试

```bash
# 运行配置测试
python test_speech_recognition.py
```

### 测试音频文件

准备一个测试音频文件：
- 格式：WAV
- 采样率：16kHz
- 时长：5-10秒
- 内容：清晰的普通话语音

## 注意事项

1. **API配额**: 注意讯飞API的调用次数限制
2. **网络环境**: 确保服务器能访问讯飞API
3. **音频质量**: 音频质量直接影响识别准确率
4. **并发限制**: 避免同时发起过多识别请求
5. **错误重试**: 建议实现错误重试机制

## 故障排除

### 1. 连接失败

```bash
# 检查网络连接
ping iat.cn-huabei-1.xf-yun.com

# 检查防火墙设置
telnet iat.cn-huabei-1.xf-yun.com 443
```

### 2. 配置错误

```python
# 检查配置
from apps.utils.xunfei_config import XUNFEI_CONFIG
print(XUNFEI_CONFIG)
```

### 3. 音频问题

```python
# 检查音频文件
import wave

with wave.open('audio.wav', 'rb') as wav_file:
    print(f"声道数: {wav_file.getnchannels()}")
    print(f"采样率: {wav_file.getframerate()}")
    print(f"采样宽度: {wav_file.getsampwidth()}")
```

## 更新日志

### v1.0.0 (2024-01-01)
- 初始版本发布
- 支持基本语音识别功能
- 集成官方WebSocket接口

## 技术支持

- 官方文档: [讯飞开放平台](https://doc.xfyun.cn/)
- 错误码查询: [错误码列表](https://www.xfyun.cn/document/error-code)
- 技术支持: [讯飞论坛](http://bbs.xfyun.cn/) 