# 讯飞WebSocket语音识别接口文档

## 概述

本接口使用讯飞开放平台的WebSocket协议进行语音识别，相比HTTP接口具有更好的实时性和性能。

## 接口信息

- **协议**: WebSocket (WSS)
- **地址**: `wss://iat.cn-huabei-1.xf-yun.com/v1`
- **鉴权方式**: HMAC-SHA256签名
- **字符编码**: UTF-8
- **响应格式**: JSON

## 音频要求

- **采样率**: 16k或8k
- **位长**: 16bit
- **声道**: 单声道
- **格式**: WAV、MP3、PCM
- **时长**: 最长60秒

## API接口

### 1. 语音识别接口

**接口地址**: `POST /api/speech-recognition/`

**请求参数**:

| 参数名 | 类型 | 必须 | 说明 | 示例 |
|--------|------|------|------|------|
| audio_data | File/Base64 | 是 | 音频数据 | 文件上传或Base64编码 |
| language | string | 否 | 语言代码 | zh_cn |
| accent | string | 否 | 口音 | mandarin |

**支持的语言**:
- `zh_cn`: 中文普通话
- `en_us`: 英文
- `ja_jp`: 日文
- `ko_kr`: 韩文
- `fr_fr`: 法文
- `es_es`: 西班牙文
- `pt_pt`: 葡萄牙文
- `it_it`: 意大利文
- `de_de`: 德文
- `ru_ru`: 俄文

**支持的口音**:
- `mandarin`: 普通话
- `cantonese`: 粤语
- `lmz`: 四川话

**请求示例**:

```bash
# 文件上传方式
curl -X POST http://localhost:8000/api/speech-recognition/ \
  -F "audio_data=@recording.wav" \
  -F "language=zh_cn" \
  -F "accent=mandarin"

# Base64方式
curl -X POST http://localhost:8000/api/speech-recognition/ \
  -H "Content-Type: application/json" \
  -d '{
    "audio_data": "UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBSuBzvLZiTYIG2m98OScTgwOUarm7blmGgU7k9n1unEiBC13yO/eizEIHWq+8+OWT...",
    "language": "zh_cn",
    "accent": "mandarin"
  }'
```

**响应示例**:

```json
{
  "code": "200",
  "msg": "语音识别成功",
  "data": {
    "text": "你好，这是一个测试",
    "language": "zh_cn",
    "accent": "mandarin",
    "audio_format": "wav",
    "audio_duration": 1.0
  }
}
```

### 2. 文件上传语音识别接口

**接口地址**: `POST /api/speech-recognition-file/`

**请求参数**:

| 参数名 | 类型 | 必须 | 说明 | 示例 |
|--------|------|------|------|------|
| audio_file | File | 是 | 音频文件 | recording.wav |
| language | string | 否 | 语言代码 | zh_cn |
| accent | string | 否 | 口音 | mandarin |

**请求示例**:

```bash
curl -X POST http://localhost:8000/api/speech-recognition-file/ \
  -F "audio_file=@recording.wav" \
  -F "language=zh_cn" \
  -F "accent=mandarin"
```

### 3. 语音识别信息查询接口

**接口地址**: `GET /api/speech-recognition-info/`

**响应示例**:

```json
{
  "code": "200",
  "msg": "获取语音识别信息成功",
  "data": {
    "supported_formats": {
      "wav": "WAV格式（推荐）",
      "mp3": "MP3格式",
      "pcm": "PCM原始音频"
    },
    "supported_languages": {
      "zh_cn": "中文普通话",
      "en_us": "英文",
      "ja_jp": "日文"
    },
    "audio_requirements": {
      "sample_rate": "16k或8k",
      "bit_depth": "16bit",
      "channels": "单声道",
      "max_duration": "60秒",
      "protocol": "WebSocket (WSS)"
    },
    "api_url": "/api/speech-recognition/",
    "file_upload_url": "/api/speech-recognition-file/"
  }
}
```

## 错误码说明

| 错误码 | 说明 |
|--------|------|
| 4001 | 音频数据不能为空 |
| 4002 | 不支持的语言 |
| 4003 | 不支持的音频格式 |
| 4004 | 音频长度超过60秒限制 |
| 4005 | 语音识别失败 |
| 4006 | 语音识别异常 |
| 4007 | 文件上传语音识别异常 |

## 鉴权机制

### 签名生成规则

1. **获取密钥**: 从讯飞开放平台获取APIKey和APISecret

2. **生成时间戳**: 使用RFC1123格式的UTC时间
   ```
   Wed, 10 Jul 2019 07:35:43 GMT
   ```

3. **生成签名原始字段**:
   ```
   host: iat.cn-huabei-1.xf-yun.com
   date: Wed, 10 Jul 2019 07:35:43 GMT
   GET /v1 HTTP/1.1
   ```

4. **使用HMAC-SHA256签名**:
   ```python
   signature_sha = hmac.new(
       api_secret.encode('utf-8'),
       signature_origin.encode('utf-8'),
       digestmod=hashlib.sha256
   ).digest()
   signature = base64.b64encode(signature_sha).decode()
   ```

5. **生成authorization**:
   ```python
   authorization_origin = f'api_key="{api_key}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature}"'
   authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode()
   ```

6. **构建WebSocket URL**:
   ```
   wss://iat.cn-huabei-1.xf-yun.com/v1?authorization=xxx&date=xxx&host=xxx
   ```

## 使用示例

### Python示例

```python
import requests

# 文件上传方式
with open('recording.wav', 'rb') as f:
    files = {'audio_data': f}
    data = {
        'language': 'zh_cn',
        'accent': 'mandarin'
    }
    response = requests.post(
        'http://localhost:8000/api/speech-recognition/',
        files=files,
        data=data
    )
    print(response.json())

# Base64方式
import base64

with open('recording.wav', 'rb') as f:
    audio_base64 = base64.b64encode(f.read()).decode()
    
data = {
    'audio_data': audio_base64,
    'language': 'zh_cn',
    'accent': 'mandarin'
}
response = requests.post(
    'http://localhost:8000/api/speech-recognition/',
    json=data
)
print(response.json())
```

### JavaScript示例

```javascript
// 文件上传方式
const formData = new FormData();
formData.append('audio_data', audioFile);
formData.append('language', 'zh_cn');
formData.append('accent', 'mandarin');

fetch('/api/speech-recognition/', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => console.log(data));

// Base64方式
const audioBase64 = btoa(String.fromCharCode(...new Uint8Array(audioArrayBuffer)));

fetch('/api/speech-recognition/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        audio_data: audioBase64,
        language: 'zh_cn',
        accent: 'mandarin'
    })
})
.then(response => response.json())
.then(data => console.log(data));
```

## 测试工具

项目提供了WebSocket连接测试脚本：

```bash
python test_websocket_connection.py
```

该脚本会：
1. 检查讯飞API配置
2. 测试WebSocket连接
3. 验证鉴权机制
4. 提供详细的错误信息

## 注意事项

1. **音频格式**: 推荐使用WAV格式，确保采样率为16k或8k
2. **文件大小**: 音频文件不应过大，建议控制在合理范围内
3. **网络连接**: WebSocket连接需要稳定的网络环境
4. **超时设置**: 识别超时时间为30秒，连接超时时间为10秒
5. **错误处理**: 建议实现重试机制处理网络异常

## 故障排除

### 常见问题

1. **WebSocket连接失败**
   - 检查网络连接
   - 验证API配置是否正确
   - 确认时间戳格式

2. **鉴权失败**
   - 检查APIKey和APISecret
   - 确认时间戳在300秒偏差内
   - 验证签名生成逻辑

3. **音频识别失败**
   - 检查音频格式和参数
   - 确认音频长度不超过60秒
   - 验证音频质量

### 调试方法

1. 使用测试脚本验证连接
2. 查看详细的日志输出
3. 检查讯飞开放平台控制台
4. 验证音频文件格式 