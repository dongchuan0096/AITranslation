# 文件上传API文档

## 概述

文件上传模块提供了完整的文件上传到阿里云OSS的功能，包括文件上传、查询、删除、统计等功能。

## API接口列表

### 1. 文件上传

**接口地址**: `POST /api/file-upload/upload/`

**功能描述**: 上传文件到阿里云OSS

**请求参数**:
- `file`: 要上传的文件 (multipart/form-data)

**响应示例**:
```json
{
    "success": true,
    "message": "文件上传成功",
    "data": {
        "file_record_id": 1,
        "original_filename": "example.jpg",
        "file_size": 1024000,
        "file_size_mb": 0.98,
        "file_type": "image/jpeg",
        "oss_key": "images/2024/01/15/1705123456_abc123_example.jpg",
        "oss_url": "https://dongchuan0096.oss-cn-beijing.aliyuncs.com/images/2024/01/15/1705123456_abc123_example.jpg",
        "cdn_url": null,
        "upload_time": 1.234,
        "md5_hash": "d41d8cd98f00b204e9800998ecf8427e"
    }
}
```

### 2. 获取上传配置信息

**接口地址**: `GET /api/file-upload/info/`

**功能描述**: 获取文件上传的配置信息

**响应示例**:
```json
{
    "success": true,
    "message": "获取文件上传信息成功",
    "data": {
        "upload_config": {
            "max_file_size_mb": 100.0,
            "allowed_extensions": {
                "image": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg", ".ico"],
                "video": [".mp4", ".avi", ".mov", ".wmv", ".flv", ".webm", ".mkv", ".m4v"],
                "audio": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a"],
                "document": [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt"],
                "archive": [".zip", ".rar", ".7z", ".tar", ".gz"]
            },
            "allowed_mime_types": ["image/jpeg", "image/png", "image/gif", ...],
            "upload_paths": {
                "image": "images/{year}/{month}/{day}/",
                "video": "videos/{year}/{month}/{day}/",
                "audio": "audios/{year}/{month}/{day}/",
                "document": "documents/{year}/{month}/{day}/",
                "archive": "archives/{year}/{month}/{day}/",
                "other": "others/{year}/{month}/{day}/"
            }
        },
        "security_config": {
            "enable_md5_check": true,
            "enable_file_type_check": true,
            "enable_size_limit": true
        },
        "performance_config": {
            "chunk_size_mb": 1.0,
            "concurrent_uploads": 3,
            "retry_times": 3,
            "timeout": 30
        },
        "api_endpoints": {
            "upload": "/api/file-upload/",
            "info": "/api/file-upload-info/",
            "list": "/api/file-upload-list/",
            "delete": "/api/file-upload-delete/",
            "detail": "/api/file-upload-detail/"
        },
        "storage_provider": "阿里云对象存储(OSS)"
    }
}
```

### 3. 文件列表查询

**接口地址**: `GET /api/file-upload/list/`

**功能描述**: 查询用户上传的文件列表

**请求参数**:
- `page`: 页码 (默认: 1)
- `page_size`: 每页数量 (默认: 20)
- `file_type`: 文件类型过滤
- `upload_status`: 上传状态过滤
- `start_date`: 开始日期 (格式: YYYY-MM-DD)
- `end_date`: 结束日期 (格式: YYYY-MM-DD)
- `search`: 搜索关键词

**请求头**:
```
Authorization: Bearer <token>
```

**响应示例**:
```json
{
    "success": true,
    "message": "查询成功",
    "data": {
        "files": [
            {
                "id": 1,
                "original_filename": "example.jpg",
                "file_size": 1024000,
                "file_size_mb": 0.98,
                "file_size_kb": 1000.0,
                "file_type": "image/jpeg",
                "file_extension": ".jpg",
                "oss_url": "https://dongchuan0096.oss-cn-beijing.aliyuncs.com/images/2024/01/15/1705123456_abc123_example.jpg",
                "cdn_url": null,
                "upload_status": "success",
                "upload_time": 1.234,
                "created_at_formatted": "2024-01-15 10:30:45",
                "is_image": true,
                "is_video": false,
                "is_audio": false,
                "is_document": false
            }
        ],
        "pagination": {
            "page": 1,
            "page_size": 20,
            "total_count": 1,
            "total_pages": 1
        }
    }
}
```

### 4. 文件详情查询

**接口地址**: `GET /api/file-upload/detail/{file_id}/`

**功能描述**: 获取文件上传记录的详细信息

**请求头**:
```
Authorization: Bearer <token>
```

**响应示例**:
```json
{
    "success": true,
    "message": "获取详情成功",
    "data": {
        "id": 1,
        "user": 1,
        "original_filename": "example.jpg",
        "file_size": 1024000,
        "file_size_mb": 0.98,
        "file_size_kb": 1000.0,
        "file_type": "image/jpeg",
        "file_extension": ".jpg",
        "oss_bucket": "dongchuan0096",
        "oss_key": "images/2024/01/15/1705123456_abc123_example.jpg",
        "oss_url": "https://dongchuan0096.oss-cn-beijing.aliyuncs.com/images/2024/01/15/1705123456_abc123_example.jpg",
        "cdn_url": null,
        "upload_status": "success",
        "upload_time": 1.234,
        "error_message": null,
        "content_type": "image/jpeg",
        "md5_hash": "d41d8cd98f00b204e9800998ecf8427e",
        "created_at": "2024-01-15T10:30:45Z",
        "updated_at": "2024-01-15T10:30:45Z",
        "created_at_formatted": "2024-01-15 10:30:45",
        "updated_at_formatted": "2024-01-15 10:30:45",
        "is_image": true,
        "is_video": false,
        "is_audio": false,
        "is_document": false
    }
}
```

### 5. 文件删除

**接口地址**: `DELETE /api/file-upload/delete/{file_id}/`

**功能描述**: 删除指定的文件

**请求头**:
```
Authorization: Bearer <token>
```

**响应示例**:
```json
{
    "success": true,
    "message": "文件删除成功"
}
```

### 6. 批量删除文件

**接口地址**: `POST /api/file-upload/batch-delete/`

**功能描述**: 批量删除多个文件

**请求参数**:
```json
{
    "file_ids": [1, 2, 3]
}
```

**请求头**:
```
Authorization: Bearer <token>
```

**响应示例**:
```json
{
    "success": true,
    "message": "批量删除完成，成功: 2，失败: 1",
    "data": {
        "success_count": 2,
        "failed_count": 1,
        "failed_files": [
            {
                "id": 3,
                "filename": "example.pdf",
                "error": "OSS文件删除失败: 文件不存在"
            }
        ]
    }
}
```

### 7. 文件上传统计

**接口地址**: `GET /api/file-upload/statistics/`

**功能描述**: 获取文件上传统计信息

**请求参数**:
- `start_date`: 开始日期 (格式: YYYY-MM-DD)
- `end_date`: 结束日期 (格式: YYYY-MM-DD)

**请求头**:
```
Authorization: Bearer <token>
```

**响应示例**:
```json
{
    "success": true,
    "message": "获取统计信息成功",
    "data": {
        "overview": {
            "total_files": 10,
            "total_size_mb": 25.5,
            "success_files": 9,
            "failed_files": 1,
            "success_rate": 90.0
        },
        "type_statistics": {
            "image": {
                "count": 5,
                "size": 10485760
            },
            "document": {
                "count": 3,
                "size": 5242880
            },
            "video": {
                "count": 2,
                "size": 10485760
            }
        },
        "date_statistics": {
            "2024-01-15": {
                "count": 5,
                "size": 10485760
            },
            "2024-01-14": {
                "count": 3,
                "size": 5242880
            }
        }
    }
}
```

## 错误代码说明

| 错误代码 | 说明 | 解决方案 |
|---------|------|----------|
| 4001 | 请上传文件 | 检查是否选择了文件 |
| 4002 | 文件上传失败 | 检查文件格式和大小 |
| 4003 | 文件上传异常 | 检查网络连接和OSS配置 |
| 4004 | 文件不存在或无权限 | 检查文件ID和用户权限 |
| 4005 | OSS文件删除失败 | 检查OSS配置和文件状态 |
| 4006 | 文件删除异常 | 检查网络连接 |
| 4007 | 批量删除异常 | 检查文件ID列表 |
| 5003 | 查询失败 | 检查查询参数 |
| 5004 | 获取详情失败 | 检查文件ID |
| 5005 | 获取统计信息失败 | 检查日期参数 |

## 支持的文件类型

### 图片格式
- JPG, JPEG, PNG, GIF, BMP, WebP, SVG, ICO

### 视频格式
- MP4, AVI, MOV, WMV, FLV, WebM, MKV, M4V

### 音频格式
- MP3, WAV, FLAC, AAC, OGG, WMA, M4A

### 文档格式
- PDF, DOC, DOCX, XLS, XLSX, PPT, PPTX, TXT

### 压缩格式
- ZIP, RAR, 7Z, TAR, GZ

## 文件大小限制

- 最大文件大小: 100MB
- 建议文件大小: 小于50MB

## 安全特性

- MD5校验: 确保文件完整性
- 文件类型检查: 防止恶意文件上传
- 文件大小限制: 防止大文件攻击
- 用户权限控制: 只能访问自己的文件

## 使用示例

### JavaScript示例

```javascript
// 文件上传
const formData = new FormData();
formData.append('file', fileInput.files[0]);

fetch('/api/file-upload/upload/', {
    method: 'POST',
    body: formData,
    headers: {
        'Authorization': 'Bearer ' + token
    }
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        console.log('上传成功:', data.data.oss_url);
    } else {
        console.error('上传失败:', data.message);
    }
});

// 获取文件列表
fetch('/api/file-upload/list/?page=1&page_size=20', {
    headers: {
        'Authorization': 'Bearer ' + token
    }
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        console.log('文件列表:', data.data.files);
    }
});
```

### Python示例

```python
import requests

# 文件上传
def upload_file(file_path, token):
    with open(file_path, 'rb') as f:
        files = {'file': f}
        headers = {'Authorization': f'Bearer {token}'}
        
        response = requests.post(
            'http://localhost:8000/api/file-upload/upload/',
            files=files,
            headers=headers
        )
        
        return response.json()

# 获取文件列表
def get_file_list(token, page=1):
    headers = {'Authorization': f'Bearer {token}'}
    params = {'page': page, 'page_size': 20}
    
    response = requests.get(
        'http://localhost:8000/api/file-upload/list/',
        headers=headers,
        params=params
    )
    
    return response.json()
```

## 注意事项

1. **认证要求**: 除了上传和获取配置信息外，其他接口都需要JWT认证
2. **文件权限**: 用户只能访问和操作自己上传的文件
3. **存储策略**: 文件按类型和日期自动分类存储
4. **CDN支持**: 支持配置CDN加速域名
5. **错误处理**: 所有接口都有完整的错误处理和日志记录 