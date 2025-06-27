# 语音识别API使用示例

## 概述

本文档提供了语音识别API的详细使用示例，包括各种调用方式和参数说明。

## API端点

| 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 语音识别信息 | GET | `/api/speech-recognition-info/` | 获取支持的格式和配置信息 |
| 语音识别 | POST | `/api/speech-recognition/` | 通过Base64数据识别 |
| 文件上传识别 | POST | `/api/speech-recognition-file/` | 通过文件上传识别 |

## 1. 获取语音识别信息

### 请求示例

```bash
curl -X GET "http://localhost:8000/api/speech-recognition-info/"
```

### 响应示例

```json
{
    "success": true,
    "message": "获取语音识别信息成功",
    "data": {
        "supported_formats": {
            "wav": "WAV格式（推荐，16kHz单声道）",
            "mp3": "MP3格式（16kHz单声道）",
            "pcm": "PCM原始音频（16kHz单声道）"
        },
        "supported_languages": {
            "zh_cn": "中文普通话",
            "en_us": "英文",
            "ja_jp": "日文",
            "ko_kr": "韩文",
            "fr_fr": "法文",
            "es_es": "西班牙文",
            "ru_ru": "俄文",
            "pt_pt": "葡萄牙文",
            "de_de": "德文",
            "it_it": "意大利文"
        },
        "audio_requirements": {
            "sample_rate": "16kHz（推荐）或8kHz",
            "bit_depth": "16bit",
            "channels": "单声道",
            "max_duration": "60秒",
            "max_file_size": "50MB",
            "protocol": "WebSocket (WSS) - 官方接口"
        },
        "api_endpoints": {
            "recognition": "/api/speech-recognition/",
            "file_upload": "/api/speech-recognition-file/",
            "info": "/api/speech-recognition-info/"
        },
        "recognition_method": "xunfei_official_websocket",
        "provider": "科大讯飞开放平台"
    }
}
```

## 2. 文件上传语音识别

### 请求示例

#### cURL

```bash
curl -X POST "http://localhost:8000/api/speech-recognition-file/" \
  -H "Content-Type: multipart/form-data" \
  -F "audio_file=@/path/to/audio.wav" \
  -F "language=zh_cn" \
  -F "accent=mandarin"
```

#### Python requests

```python
import requests

# 准备文件
with open('audio.wav', 'rb') as f:
    files = {'audio_file': f}
    data = {
        'language': 'zh_cn',
        'accent': 'mandarin'
    }
    
    response = requests.post(
        'http://localhost:8000/api/speech-recognition-file/',
        files=files,
        data=data,
        timeout=120
    )

if response.status_code == 200:
    result = response.json()
    print(f"识别结果: {result['data']['text']}")
else:
    print(f"识别失败: {response.text}")
```

#### JavaScript (Fetch API)

```javascript
const formData = new FormData();
formData.append('audio_file', audioFile);
formData.append('language', 'zh_cn');
formData.append('accent', 'mandarin');

fetch('/api/speech-recognition-file/', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        console.log('识别结果:', data.data.text);
    } else {
        console.error('识别失败:', data.message);
    }
})
.catch(error => {
    console.error('请求失败:', error);
});
```

### 响应示例

```json
{
    "success": true,
    "message": "语音识别成功",
    "data": {
        "text": "你好，这是一个语音识别测试",
        "language": "zh_cn",
        "accent": "mandarin",
        "audio_format": "wav",
        "file_size": 1024000,
        "recognition_method": "xunfei_official_websocket"
    }
}
```

## 3. Base64编码音频数据识别

### 请求示例

#### cURL

```bash
# 将音频文件转换为Base64
AUDIO_BASE64=$(base64 -w 0 /path/to/audio.wav)

curl -X POST "http://localhost:8000/api/speech-recognition/" \
  -H "Content-Type: application/json" \
  -d '{
    "audio_data": "'$AUDIO_BASE64'",
    "audio_format": "wav",
    "language": "zh_cn",
    "accent": "mandarin"
  }'
```

#### Python requests

```python
import requests
import base64

# 读取音频文件并转换为Base64
with open('audio.wav', 'rb') as f:
    audio_data = f.read()
    audio_base64 = base64.b64encode(audio_data).decode('utf-8')

# 发送请求
data = {
    'audio_data': audio_base64,
    'audio_format': 'wav',
    'language': 'zh_cn',
    'accent': 'mandarin'
}

response = requests.post(
    'http://localhost:8000/api/speech-recognition/',
    json=data,
    timeout=120
)

if response.status_code == 200:
    result = response.json()
    print(f"识别结果: {result['data']['text']}")
else:
    print(f"识别失败: {response.text}")
```

#### JavaScript (Fetch API)

```javascript
// 将音频文件转换为Base64
function fileToBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = () => {
            const base64 = reader.result.split(',')[1];
            resolve(base64);
        };
        reader.onerror = error => reject(error);
    });
}

// 使用示例
fileToBase64(audioFile).then(base64 => {
    const data = {
        audio_data: base64,
        audio_format: 'wav',
        language: 'zh_cn',
        accent: 'mandarin'
    };

    fetch('/api/speech-recognition/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('识别结果:', data.data.text);
        } else {
            console.error('识别失败:', data.message);
        }
    })
    .catch(error => {
        console.error('请求失败:', error);
    });
});
```

### 响应示例

```json
{
    "success": true,
    "message": "语音识别成功",
    "data": {
        "text": "你好，这是一个语音识别测试",
        "language": "zh_cn",
        "accent": "mandarin",
        "audio_format": "wav",
        "audio_duration": 5.2,
        "recognition_method": "xunfei_official_websocket"
    }
}
```

## 4. 错误处理

### 常见错误响应

#### 4001 - 音频数据为空

```json
{
    "success": false,
    "message": "音频数据不能为空",
    "code": "4001"
}
```

#### 4002 - 不支持的语言

```json
{
    "success": false,
    "message": "不支持的语言: invalid_language",
    "code": "4002"
}
```

#### 4003 - 不支持的音频格式

```json
{
    "success": false,
    "message": "不支持的音频格式: flac，仅支持wav、mp3、pcm",
    "code": "4003"
}
```

#### 4004 - 音频长度超限

```json
{
    "success": false,
    "message": "音频长度超过60秒限制: 75.3秒",
    "code": "4004"
}
```

#### 4005 - 识别失败

```json
{
    "success": false,
    "message": "语音识别失败: 网络连接超时",
    "code": "4005"
}
```

#### 4006 - 服务器异常

```json
{
    "success": false,
    "message": "语音识别异常: 配置文件错误",
    "code": "4006"
}
```

## 5. 完整示例

### Python完整示例

```python
import requests
import base64
import json
import time

class SpeechRecognitionClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def get_info(self):
        """获取语音识别信息"""
        response = requests.get(f"{self.base_url}/api/speech-recognition-info/")
        return response.json()
    
    def recognize_file(self, file_path, language='zh_cn', accent='mandarin'):
        """通过文件上传识别"""
        with open(file_path, 'rb') as f:
            files = {'audio_file': f}
            data = {
                'language': language,
                'accent': accent
            }
            
            response = requests.post(
                f"{self.base_url}/api/speech-recognition-file/",
                files=files,
                data=data,
                timeout=120
            )
        
        return response.json()
    
    def recognize_base64(self, audio_data, audio_format='wav', language='zh_cn', accent='mandarin'):
        """通过Base64数据识别"""
        if isinstance(audio_data, bytes):
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        else:
            audio_base64 = audio_data
        
        data = {
            'audio_data': audio_base64,
            'audio_format': audio_format,
            'language': language,
            'accent': accent
        }
        
        response = requests.post(
            f"{self.base_url}/api/speech-recognition/",
            json=data,
            timeout=120
        )
        
        return response.json()

# 使用示例
def main():
    client = SpeechRecognitionClient()
    
    # 1. 获取API信息
    print("获取API信息...")
    info = client.get_info()
    print(json.dumps(info, ensure_ascii=False, indent=2))
    
    # 2. 文件识别
    print("\n文件识别...")
    result = client.recognize_file('test_audio.wav')
    if result['success']:
        print(f"识别结果: {result['data']['text']}")
    else:
        print(f"识别失败: {result['message']}")
    
    # 3. Base64识别
    print("\nBase64识别...")
    with open('test_audio.wav', 'rb') as f:
        audio_data = f.read()
    
    result = client.recognize_base64(audio_data)
    if result['success']:
        print(f"识别结果: {result['data']['text']}")
    else:
        print(f"识别失败: {result['message']}")

if __name__ == "__main__":
    main()
```

### JavaScript完整示例

```javascript
class SpeechRecognitionClient {
    constructor(baseUrl = 'http://localhost:8000') {
        this.baseUrl = baseUrl;
    }
    
    async getInfo() {
        const response = await fetch(`${this.baseUrl}/api/speech-recognition-info/`);
        return await response.json();
    }
    
    async recognizeFile(file, language = 'zh_cn', accent = 'mandarin') {
        const formData = new FormData();
        formData.append('audio_file', file);
        formData.append('language', language);
        formData.append('accent', accent);
        
        const response = await fetch(`${this.baseUrl}/api/speech-recognition-file/`, {
            method: 'POST',
            body: formData
        });
        
        return await response.json();
    }
    
    async recognizeBase64(audioData, audioFormat = 'wav', language = 'zh_cn', accent = 'mandarin') {
        const data = {
            audio_data: audioData,
            audio_format: audioFormat,
            language: language,
            accent: accent
        };
        
        const response = await fetch(`${this.baseUrl}/api/speech-recognition/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        return await response.json();
    }
    
    fileToBase64(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.readAsDataURL(file);
            reader.onload = () => {
                const base64 = reader.result.split(',')[1];
                resolve(base64);
            };
            reader.onerror = error => reject(error);
        });
    }
}

// 使用示例
async function main() {
    const client = new SpeechRecognitionClient();
    
    try {
        // 1. 获取API信息
        console.log('获取API信息...');
        const info = await client.getInfo();
        console.log(info);
        
        // 2. 文件识别
        const fileInput = document.getElementById('audioFile');
        if (fileInput.files.length > 0) {
            console.log('文件识别...');
            const result = await client.recognizeFile(fileInput.files[0]);
            if (result.success) {
                console.log('识别结果:', result.data.text);
            } else {
                console.error('识别失败:', result.message);
            }
        }
        
        // 3. Base64识别
        if (fileInput.files.length > 0) {
            console.log('Base64识别...');
            const base64 = await client.fileToBase64(fileInput.files[0]);
            const result = await client.recognizeBase64(base64);
            if (result.success) {
                console.log('识别结果:', result.data.text);
            } else {
                console.error('识别失败:', result.message);
            }
        }
        
    } catch (error) {
        console.error('请求失败:', error);
    }
}

// HTML示例
/*
<input type="file" id="audioFile" accept=".wav,.mp3,.pcm">
<button onclick="main()">开始识别</button>
*/
```

## 6. 性能优化建议

1. **音频预处理**: 确保音频格式为16kHz单声道WAV格式
2. **文件大小**: 控制音频文件大小在合理范围内
3. **并发控制**: 避免同时发起过多识别请求
4. **错误重试**: 实现错误重试机制
5. **缓存结果**: 对相同音频文件缓存识别结果

## 7. 注意事项

1. 确保Django服务器正在运行
2. 检查讯飞API配置是否正确
3. 音频文件格式和参数符合要求
4. 网络连接稳定
5. 注意API调用频率限制 