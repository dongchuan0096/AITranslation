# 阿里云对象存储(OSS)配置
# 请在此处配置您的阿里云OSS信息

# 阿里云OSS配置
OSS_CONFIG = {
    'ACCESS_KEY_ID': 'LTAI5tRafbdeXMctHTVnZVhm',  # 请替换为您的AccessKey ID
    'ACCESS_KEY_SECRET': 'mHC1Md3SxpLIWVwyXQwn9YPox6qaIj',  # 请替换为您的AccessKey Secret
    'ENDPOINT': 'https://oss-cn-hangzhou.aliyuncs.com',  # OSS访问域名，根据您的地区修改
    'BUCKET_NAME': 'dongchuan0096',  # 存储桶名称
    'REGION': 'cn-beijing',  # 地域，根据您的存储桶所在地域修改
}

# CDN配置（可选）
CDN_CONFIG = {
    'ENABLED': False,  # 是否启用CDN
    'DOMAIN': 'https://your-cdn-domain.com',  # CDN域名
}

# 文件上传配置
UPLOAD_CONFIG = {
    'MAX_FILE_SIZE': 100 * 1024 * 1024,  # 最大文件大小：100MB
    'ALLOWED_EXTENSIONS': {
        # 图片格式
        'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg', '.ico'],
        # 视频格式
        'video': ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv', '.m4v'],
        # 音频格式
        'audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a'],
        # 文档格式
        'document': ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt'],
        # 压缩格式
        'archive': ['.zip', '.rar', '.7z', '.tar', '.gz'],
    },
    'ALLOWED_MIME_TYPES': [
        # 图片
        'image/jpeg', 'image/png', 'image/gif', 'image/bmp', 'image/webp', 'image/svg+xml',
        # 视频
        'video/mp4', 'video/avi', 'video/quicktime', 'video/x-ms-wmv', 'video/x-flv', 'video/webm',
        # 音频
        'audio/mpeg', 'audio/wav', 'audio/flac', 'audio/aac', 'audio/ogg', 'audio/x-ms-wma',
        # 文档
        'application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/vnd.ms-powerpoint', 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        'text/plain',
        # 压缩
        'application/zip', 'application/x-rar-compressed', 'application/x-7z-compressed',
        'application/x-tar', 'application/gzip',
    ],
    'UPLOAD_PATH': {
        'image': 'images/{year}/{month}/{day}/',
        'video': 'videos/{year}/{month}/{day}/',
        'audio': 'audios/{year}/{month}/{day}/',
        'document': 'documents/{year}/{month}/{day}/',
        'archive': 'archives/{year}/{month}/{day}/',
        'other': 'others/{year}/{month}/{day}/',
    },
    'FILE_NAME_PATTERN': '{timestamp}_{random}_{original_name}',  # 文件名模式
}

# 安全配置
SECURITY_CONFIG = {
    'ENABLE_MD5_CHECK': True,  # 启用MD5校验
    'ENABLE_FILE_TYPE_CHECK': True,  # 启用文件类型检查
    'ENABLE_SIZE_LIMIT': True,  # 启用文件大小限制
    'ENABLE_VIRUS_SCAN': False,  # 启用病毒扫描（需要额外配置）
}

# 性能配置
PERFORMANCE_CONFIG = {
    'CHUNK_SIZE': 1024 * 1024,  # 分片大小：1MB
    'CONCURRENT_UPLOADS': 3,  # 并发上传数
    'RETRY_TIMES': 3,  # 重试次数
    'TIMEOUT': 30,  # 超时时间（秒）
}

# 存储策略配置
STORAGE_CONFIG = {
    'ENABLE_VERSIONING': False,  # 启用版本控制
    'ENABLE_LIFECYCLE': True,  # 启用生命周期管理
    'RETENTION_DAYS': 365,  # 文件保留天数
    'ENABLE_ENCRYPTION': False,  # 启用服务端加密
}

# 访问控制配置
ACCESS_CONTROL_CONFIG = {
    'DEFAULT_ACL': 'public-read',  # 默认访问权限：private, public-read, public-read-write
    'ENABLE_SIGNED_URL': True,  # 启用签名URL
    'SIGNED_URL_EXPIRE': 3600,  # 签名URL过期时间（秒）
}

# 监控配置
MONITORING_CONFIG = {
    'ENABLE_UPLOAD_LOG': True,  # 启用上传日志
    'ENABLE_METRICS': True,  # 启用指标监控
    'ENABLE_ALERT': False,  # 启用告警
}

