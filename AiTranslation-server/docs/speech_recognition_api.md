# 讯飞语音识别API使用文档

## 概述

本API提供了基于讯飞开放平台的语音识别功能，支持多种音频格式和语言。

## API端点

### 1. 语音识别信息接口
**GET** `/api/speech-recognition-info/`

获取支持的音频格式、语言等信息。

**响应示例：**
```json
{
    "code": "0000",
    "msg": "获取语音识别信息成功",
    "data": {
        "supported_formats": {
            "wav": "audio/wav",
            "mp3": "audio/mp3",
            "m4a": "audio/m4a",
            "amr": "audio/amr",
            "pcm": "audio/pcm"
        },
        "supported_languages": {
            "zh_cn": "中文普通话",
            "en_us": "英文",
            "ja_jp": "日文",
            "ko_kr": "韩文"
        },
        "engine_types": {
            "sms16k": {
                "name": "16k采样率普通话音频",
                "rate": "16000",
                "language": "zh_cn"
            },
            "sms8k": {
                "name": "8k采样率普通话音频",
                "rate": "8000",
                "language": "zh_cn"
            },
            "iat": {
                "name": "16k采样率多语言音频",
                "rate": "16000",
                "language": "auto"
            }
        }
    }
}
```

### 2. 语音识别接口（Base64数据）
**POST** `/api/speech-recognition/`

通过Base64编码的音频数据进行语音识别。

**请求参数：**
```json
{
    "audio_data": "base64编码的音频数据",
    "language": "zh_cn",  // 可选，默认zh_cn
    "engine_type": "sms16k"  // 可选，默认sms16k
}
```

**响应示例：**
```json
{
    "code": "0000",
    "msg": "语音识别成功",
    "data": {
        "text": "识别出的文本内容",
        "confidence": 0.95,
        "language": "zh_cn",
        "engine_type": "sms16k"
    }
}
```

### 3. 语音识别接口（文件上传）
**POST** `/api/speech-recognition-file/`

通过文件上传进行语音识别。

**请求参数：**
- `audio_file`: 音频文件（支持wav、mp3、m4a、amr、pcm格式）
- `language`: 语言（可选，默认zh_cn）
- `engine_type`: 引擎类型（可选，默认sms16k）

**响应示例：**
```json
{
    "code": "0000",
    "msg": "语音识别成功",
    "data": {
        "text": "识别出的文本内容",
        "confidence": 0.95,
        "language": "zh_cn",
        "engine_type": "sms16k"
    }
}
```

## 配置说明

### 1. 讯飞API配置
在使用前，请先在 `apps/utils/xunfei_config.py` 中配置您的讯飞开放平台API密钥：

```python
XUNFEI_CONFIG = {
    'APP_ID': 'your_app_id',  # 您的讯飞APP_ID
    'API_KEY': 'your_api_key',  # 您的讯飞API_KEY
    'API_SECRET': 'your_api_secret',  # 您的讯飞API_SECRET
}
```

### 2. 支持的音频格式
- **WAV**: 无损音频格式
- **MP3**: 有损压缩音频格式
- **M4A**: AAC编码的音频格式
- **AMR**: 移动设备常用音频格式
- **PCM**: 原始音频数据格式

### 3. 支持的语言
- **zh_cn**: 中文普通话
- **en_us**: 英文
- **ja_jp**: 日文
- **ko_kr**: 韩文
- **fr_fr**: 法文
- **es_es**: 西班牙文
- **ru_ru**: 俄文
- **pt_pt**: 葡萄牙文
- **de_de**: 德文
- **it_it**: 意大利文

### 4. 引擎类型
- **sms16k**: 16k采样率普通话音频（推荐）
- **sms8k**: 8k采样率普通话音频
- **iat**: 16k采样率多语言音频

## 使用示例

### JavaScript示例（文件上传）
```javascript
const formData = new FormData();
formData.append('audio_file', audioFile);
formData.append('language', 'zh_cn');
formData.append('engine_type', 'sms16k');

fetch('/api/speech-recognition-file/', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => {
    if (data.code === '0000') {
        console.log('识别结果:', data.data.text);
        console.log('置信度:', data.data.confidence);
    } else {
        console.error('识别失败:', data.msg);
    }
});
```

### Python示例（Base64数据）
```python
import requests
import base64

# 读取音频文件并转换为Base64
with open('audio.wav', 'rb') as f:
    audio_data = base64.b64encode(f.read()).decode()

# 发送请求
response = requests.post('http://localhost:8000/api/speech-recognition/', json={
    'audio_data': audio_data,
    'language': 'zh_cn',
    'engine_type': 'sms16k'
})

result = response.json()
if result['code'] == '0000':
    print('识别结果:', result['data']['text'])
    print('置信度:', result['data']['confidence'])
else:
    print('识别失败:', result['msg'])
```

## 错误代码说明

| 错误代码 | 说明 |
|---------|------|
| 4001 | 音频数据不能为空 |
| 4002 | 不支持的语言或音频格式 |
| 4003 | 不支持的引擎类型 |
| 4004 | 讯飞API返回错误 |
| 4005 | 讯飞API请求失败 |
| 4006 | 语音识别异常 |
| 4007 | 文件上传语音识别异常 |

## 注意事项

1. **音频质量**: 建议使用16k采样率、单声道、PCM格式的音频以获得最佳识别效果
2. **文件大小**: 单个音频文件建议不超过10MB
3. **网络要求**: 需要稳定的网络连接访问讯飞API
4. **API限制**: 请遵守讯飞开放平台的使用限制和配额
5. **安全性**: 请妥善保管您的API密钥，不要泄露给他人 