from django.contrib import admin
from .models import APIAccessLog, APIUsageStatistics

@admin.register(APIAccessLog)
class APIAccessLogAdmin(admin.ModelAdmin):
    """API访问记录管理"""
    list_display = [
        'id', 'user', 'api_name', 'http_method', 'ip_address', 
        'is_success', 'execution_time', 'created_at'
    ]
    list_filter = [
        'is_success', 'http_method', 'api_name', 'created_at', 
        'user', 'ip_address'
    ]
    search_fields = ['api_name', 'api_path', 'ip_address', 'user__username']
    readonly_fields = [
        'created_at', 'updated_at', 'execution_time', 'request_size', 
        'response_size', 'duration_ms', 'request_size_kb', 'response_size_kb'
    ]
    date_hierarchy = 'created_at'
    list_per_page = 50
    
    fieldsets = (
        ('基本信息', {
            'fields': ('user', 'ip_address', 'user_agent', 'api_name', 'api_path', 'http_method')
        }),
        ('请求信息', {
            'fields': ('request_data', 'request_params', 'request_size', 'request_size_kb')
        }),
        ('响应信息', {
            'fields': ('response_status', 'response_data', 'response_size', 'response_size_kb', 'error_message')
        }),
        ('性能信息', {
            'fields': ('execution_time', 'duration_ms', 'is_success')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at', 'api_version')
        }),
    )

@admin.register(APIUsageStatistics)
class APIUsageStatisticsAdmin(admin.ModelAdmin):
    """API使用统计管理"""
    list_display = [
        'id', 'user', 'api_name', 'date', 'total_requests', 
        'successful_requests', 'failed_requests', 'success_rate', 'avg_execution_time'
    ]
    list_filter = ['date', 'api_name', 'user']
    search_fields = ['api_name', 'user__username']
    readonly_fields = [
        'created_at', 'updated_at', 'success_rate', 'avg_execution_time'
    ]
    date_hierarchy = 'date'
    list_per_page = 50
    
    fieldsets = (
        ('基本信息', {
            'fields': ('user', 'api_name', 'date')
        }),
        ('统计信息', {
            'fields': (
                'total_requests', 'successful_requests', 'failed_requests', 
                'success_rate', 'total_execution_time', 'avg_execution_time'
            )
        }),
        ('大小统计', {
            'fields': ('total_request_size', 'total_response_size')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at')
        }),
    )
