# API访问记录功能文档

## 概述

本系统实现了完整的API访问记录功能，自动记录每个用户的API操作，包括请求信息、响应信息、性能指标等，并提供查询和统计功能。

## 功能特性

### 🔍 **自动记录**
- 所有API请求自动记录到数据库
- 记录用户信息、IP地址、请求参数、响应结果
- 计算执行时间、请求大小、响应大小
- 过滤敏感字段（密码、token等）

### 📊 **统计分析**
- 按用户、API、日期统计使用情况
- 计算成功率、平均执行时间
- 统计请求和响应数据量

### 🔐 **安全保护**
- 自动过滤敏感字段
- 支持匿名用户记录
- 用户只能查看自己的记录

## 数据库模型

### APIAccessLog（API访问记录）
```python
class APIAccessLog(models.Model):
    # 用户信息
    user = models.ForeignKey(User, ...)  # 用户
    ip_address = models.GenericIPAddressField(...)  # IP地址
    user_agent = models.TextField(...)  # 用户代理
    
    # API信息
    api_name = models.CharField(...)  # API名称
    api_path = models.CharField(...)  # API路径
    http_method = models.CharField(...)  # HTTP方法
    
    # 请求信息
    request_data = models.JSONField(...)  # 请求数据
    request_params = models.JSONField(...)  # 请求参数
    
    # 响应信息
    response_status = models.IntegerField(...)  # 响应状态码
    response_data = models.JSONField(...)  # 响应数据
    error_message = models.TextField(...)  # 错误信息
    
    # 性能信息
    execution_time = models.FloatField(...)  # 执行时间
    request_size = models.IntegerField(...)  # 请求大小
    response_size = models.IntegerField(...)  # 响应大小
    
    # 时间信息
    created_at = models.DateTimeField(...)  # 创建时间
    updated_at = models.DateTimeField(...)  # 更新时间
    
    # 额外信息
    is_success = models.BooleanField(...)  # 是否成功
    api_version = models.CharField(...)  # API版本
```

### APIUsageStatistics（API使用统计）
```python
class APIUsageStatistics(models.Model):
    user = models.ForeignKey(User, ...)  # 用户
    api_name = models.CharField(...)  # API名称
    date = models.DateField(...)  # 日期
    
    # 统计信息
    total_requests = models.IntegerField(...)  # 总请求数
    successful_requests = models.IntegerField(...)  # 成功请求数
    failed_requests = models.IntegerField(...)  # 失败请求数
    total_execution_time = models.FloatField(...)  # 总执行时间
    total_request_size = models.BigIntegerField(...)  # 总请求大小
    total_response_size = models.BigIntegerField(...)  # 总响应大小
```

## API接口

### 1. 获取API访问记录
**GET** `/api/access-logs/`

获取当前用户的API访问记录，支持分页和筛选。

**请求参数：**
- `page`: 页码（默认1）
- `page_size`: 每页数量（默认20）
- `api_name`: API名称筛选
- `start_date`: 开始日期（格式：YYYY-MM-DD）
- `end_date`: 结束日期（格式：YYYY-MM-DD）
- `is_success`: 是否成功（true/false）

**响应示例：**
```json
{
    "code": "0000",
    "msg": "获取API访问记录成功",
    "data": {
        "logs": [
            {
                "id": 1,
                "api_name": "文本翻译",
                "api_path": "/api/text-translate/",
                "http_method": "POST",
                "ip_address": "127.0.0.1",
                "execution_time": 0.5,
                "duration_ms": 500.0,
                "request_size_kb": 2.5,
                "response_size_kb": 1.2,
                "is_success": true,
                "response_status": 200,
                "error_message": null,
                "created_at": "2024-01-15 10:30:00"
            }
        ],
        "pagination": {
            "page": 1,
            "page_size": 20,
            "total_count": 100,
            "total_pages": 5
        }
    }
}
```

### 2. 获取API使用统计
**GET** `/api/usage-statistics/`

获取当前用户的API使用统计信息。

**请求参数：**
- `days`: 查询天数（默认7天）
- `api_name`: API名称筛选

**响应示例：**
```json
{
    "code": "0000",
    "msg": "获取API使用统计成功",
    "data": {
        "statistics": [
            {
                "date": "2024-01-15",
                "api_name": "文本翻译",
                "total_requests": 50,
                "successful_requests": 48,
                "failed_requests": 2,
                "success_rate": 96.0,
                "avg_execution_time": 0.5,
                "total_request_size_mb": 0.1,
                "total_response_size_mb": 0.05
            }
        ],
        "overall_stats": {
            "total_requests": 150,
            "successful_requests": 145,
            "failed_requests": 5,
            "overall_success_rate": 96.67,
            "avg_execution_time": 0.6,
            "total_request_size_mb": 0.3,
            "total_response_size_mb": 0.15
        },
        "date_range": {
            "start_date": "2024-01-09",
            "end_date": "2024-01-15",
            "days": 7
        }
    }
}
```

## 使用装饰器

### 基本用法
```python
from apps.utils.api_logger import log_api_access

class MyAPIView(APIView):
    @log_api_access(api_name="我的API")
    def post(self, request):
        # API逻辑
        return Response({"message": "success"})
```

### 自定义敏感字段
```python
@log_api_access(
    api_name="敏感API", 
    sensitive_fields=['password', 'token', 'secret_key']
)
def my_api_method(self, request):
    # API逻辑
    pass
```

### 自动获取API名称
```python
@log_api_access()  # 不指定api_name，自动使用类名和方法名
def post(self, request):
    # API逻辑
    pass
```

## 管理后台

在Django管理后台中可以查看和管理API访问记录：

### 访问记录管理
- 列表显示：ID、用户、API名称、HTTP方法、IP地址、是否成功、执行时间、创建时间
- 筛选功能：按成功状态、HTTP方法、API名称、创建时间、用户、IP地址筛选
- 搜索功能：支持API名称、API路径、IP地址、用户名搜索
- 只读字段：创建时间、更新时间、执行时间、请求大小、响应大小等

### 使用统计管理
- 列表显示：ID、用户、API名称、日期、总请求数、成功请求数、失败请求数、成功率、平均执行时间
- 筛选功能：按日期、API名称、用户筛选
- 搜索功能：支持API名称、用户名搜索
- 只读字段：创建时间、更新时间、成功率、平均执行时间等

## 配置说明

### 敏感字段配置
默认过滤的敏感字段：
- `password`: 密码
- `token`: 令牌
- `api_key`: API密钥
- `secret`: 密钥

可以通过装饰器参数自定义：
```python
@log_api_access(sensitive_fields=['password', 'token', 'custom_secret'])
```

### 性能考虑
- 日志记录在后台异步进行，不影响API响应速度
- 数据库索引优化，支持快速查询
- 定期清理过期日志数据

## 注意事项

1. **权限控制**: 用户只能查看自己的API访问记录
2. **数据安全**: 敏感字段自动过滤，不会记录到数据库
3. **性能影响**: 日志记录对API性能影响极小
4. **存储空间**: 建议定期清理过期日志数据
5. **隐私保护**: 遵守相关隐私法规，合理使用访问记录

## 错误代码

| 错误代码 | 说明 |
|---------|------|
| 4008 | 获取API访问记录失败 |
| 4009 | 获取API使用统计失败 | 