import time
import json
import hashlib
from functools import wraps
from django.utils import timezone
from django.http import JsonResponse
from django.core.files.uploadedfile import UploadedFile, InMemoryUploadedFile
from django.core.serializers.json import DjangoJSONEncoder
from apps.api.models import APIAccessLog, APIUsageStatistics

def log_api_access(api_name=None, sensitive_fields=None):
    """
    API访问记录装饰器
    
    Args:
        api_name: API名称，如果不提供则自动获取
        sensitive_fields: 敏感字段列表，这些字段不会被记录
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(self, request, *args, **kwargs):
            start_time = time.time()
            
            # 获取API名称
            if api_name:
                current_api_name = api_name
            else:
                current_api_name = f"{self.__class__.__name__}_{request.method.lower()}"
            
            # 获取用户信息
            user = request.user if hasattr(request, 'user') and request.user.is_authenticated else None
            
            # 获取IP地址
            ip_address = get_client_ip(request)
            
            # 获取用户代理
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            # 获取请求数据（在读取请求体之前）
            request_data = get_request_data(request, sensitive_fields)
            request_params = get_request_params(request, sensitive_fields)
            
            # 计算请求大小
            request_size = calculate_request_size(request)
            
            # 执行原始视图函数
            try:
                response = view_func(self, request, *args, **kwargs)
                execution_time = time.time() - start_time
                
                # 获取响应数据
                response_data = get_response_data(response)
                response_status = getattr(response, 'status_code', 200)
                is_success = response_status < 400
                error_message = None
                
            except Exception as e:
                execution_time = time.time() - start_time
                response_data = None
                response_status = 500
                is_success = False
                error_message = str(e)
                response = JsonResponse({
                    'code': '5000',
                    'msg': f'服务器内部错误: {str(e)}',
                    'data': None
                }, status=500)
            
            # 计算响应大小
            response_size = calculate_response_size(response)
            
            # 记录访问日志
            try:
                log_entry = APIAccessLog.objects.create(
                    user=user,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    api_name=current_api_name,
                    api_path=request.path,
                    http_method=request.method,
                    request_data=request_data,
                    request_params=request_params,
                    response_status=response_status,
                    response_data=response_data,
                    error_message=error_message,
                    execution_time=execution_time,
                    request_size=request_size,
                    response_size=response_size,
                    is_success=is_success,
                    api_version='v1'
                )
                
                # 更新使用统计
                if user:
                    update_usage_statistics(user, current_api_name, is_success, execution_time, request_size, response_size)
                
            except Exception as e:
                # 记录日志失败不应该影响正常API响应
                print(f"API访问记录失败: {str(e)}")
            
            return response
        
        return wrapper
    return decorator

def get_client_ip(request):
    """获取客户端IP地址"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def get_request_data(request, sensitive_fields=None):
    """获取请求数据，过滤敏感字段"""
    if sensitive_fields is None:
        sensitive_fields = ['password', 'token', 'api_key', 'secret']
    
    try:
        if request.method == 'GET':
            data = dict(request.GET)
        else:
            # 处理POST/PUT等请求
            if hasattr(request, 'data'):
                data = request.data.copy() if request.data else {}
            elif hasattr(request, 'POST'):
                data = request.POST.copy() if request.POST else {}
            else:
                data = {}
            
            # 处理文件上传
            if hasattr(request, 'FILES') and request.FILES:
                files_info = {}
                for field_name, uploaded_file in request.FILES.items():
                    if isinstance(uploaded_file, (UploadedFile, InMemoryUploadedFile)):
                        files_info[field_name] = {
                            'name': uploaded_file.name,
                            'size': uploaded_file.size,
                            'content_type': uploaded_file.content_type,
                            'type': 'file'
                        }
                data['files'] = files_info
            
            # 过滤敏感字段
            for field in sensitive_fields:
                if field in data:
                    data[field] = '***'
        
        # 确保数据可以被JSON序列化
        return json.loads(json.dumps(data, cls=DjangoJSONEncoder, default=str))
    except Exception as e:
        print(f"获取请求数据失败: {str(e)}")
        return {}

def get_request_params(request, sensitive_fields=None):
    """获取请求参数，过滤敏感字段"""
    if sensitive_fields is None:
        sensitive_fields = ['password', 'token', 'api_key', 'secret']
    
    try:
        params = {}
        
        # URL参数
        if request.GET:
            params['query_params'] = dict(request.GET)
        
        # 路径参数
        if hasattr(request, 'resolver_match') and request.resolver_match:
            params['path_params'] = request.resolver_match.kwargs
        
        # 过滤敏感字段
        for field in sensitive_fields:
            if 'query_params' in params and field in params['query_params']:
                params['query_params'][field] = '***'
        
        # 确保数据可以被JSON序列化
        return json.loads(json.dumps(params, cls=DjangoJSONEncoder, default=str))
    except Exception as e:
        print(f"获取请求参数失败: {str(e)}")
        return {}

def get_response_data(response):
    """获取响应数据"""
    try:
        if hasattr(response, 'content'):
            # 确保响应内容已经渲染
            if not response.is_rendered:
                response.render()
            content = response.content.decode('utf-8')
            if content:
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    # 如果不是JSON格式，返回字符串
                    return {'raw_content': content[:1000]}  # 限制长度
            return None
        return None
    except Exception as e:
        print(f"获取响应数据失败: {str(e)}")
        return None

def calculate_request_size(request):
    """计算请求大小"""
    try:
        size = 0
        
        # URL长度
        size += len(request.path)
        
        # 查询参数
        if request.GET:
            size += len(str(request.GET))
        
        # 请求体（只在没有文件上传时计算）
        if not (hasattr(request, 'FILES') and request.FILES):
            if hasattr(request, 'body'):
                size += len(request.body)
        
        # 文件大小
        if hasattr(request, 'FILES') and request.FILES:
            for uploaded_file in request.FILES.values():
                if hasattr(uploaded_file, 'size'):
                    size += uploaded_file.size
        
        return size
    except Exception as e:
        print(f"计算请求大小失败: {str(e)}")
        return 0

def calculate_response_size(response):
    """计算响应大小"""
    try:
        if hasattr(response, 'content'):
            # 确保响应内容已经渲染
            if not response.is_rendered:
                response.render()
            return len(response.content)
        return 0
    except Exception as e:
        print(f"计算响应大小失败: {str(e)}")
        return 0

def update_usage_statistics(user, api_name, is_success, execution_time, request_size, response_size):
    """更新API使用统计"""
    try:
        today = timezone.now().date()
        
        # 获取或创建统计记录
        stats, created = APIUsageStatistics.objects.get_or_create(
            user=user,
            api_name=api_name,
            date=today,
            defaults={
                'total_requests': 0,
                'successful_requests': 0,
                'failed_requests': 0,
                'total_execution_time': 0,
                'total_request_size': 0,
                'total_response_size': 0,
            }
        )
        
        # 更新统计信息
        stats.total_requests += 1
        if is_success:
            stats.successful_requests += 1
        else:
            stats.failed_requests += 1
        
        stats.total_execution_time += execution_time
        stats.total_request_size += request_size
        stats.total_response_size += response_size
        
        stats.save()
        
    except Exception as e:
        print(f"更新使用统计失败: {str(e)}")

class APILoggerMixin:
    """API日志记录Mixin类"""
    
    def log_api_access(self, request, api_name=None, sensitive_fields=None):
        """记录API访问的便捷方法"""
        return log_api_access(api_name, sensitive_fields)(lambda self, request, *args, **kwargs: None)(self, request) 