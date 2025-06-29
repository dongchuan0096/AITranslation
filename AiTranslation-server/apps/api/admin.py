from django.contrib import admin
from .models import APIAccessLog, APIUsageStatistics, FileUploadRecord

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

@admin.register(FileUploadRecord)
class FileUploadRecordAdmin(admin.ModelAdmin):
    """文件上传记录管理"""
    list_display = [
        'id', 'user', 'original_filename', 'file_size_mb', 'file_type', 
        'upload_status', 'upload_time', 'created_at'
    ]
    list_filter = [
        'upload_status', 'file_type', 'created_at', 'user', 'oss_bucket'
    ]
    search_fields = [
        'original_filename', 'oss_key', 'user__username', 'oss_bucket'
    ]
    readonly_fields = [
        'created_at', 'updated_at', 'file_size_mb', 'file_size_kb',
        'is_image', 'is_video', 'is_audio', 'is_document'
    ]
    date_hierarchy = 'created_at'
    list_per_page = 50
    
    fieldsets = (
        ('基本信息', {
            'fields': ('user', 'original_filename', 'file_size', 'file_size_mb', 'file_size_kb')
        }),
        ('文件信息', {
            'fields': ('file_type', 'file_extension', 'content_type', 'md5_hash')
        }),
        ('存储信息', {
            'fields': ('oss_bucket', 'oss_key', 'oss_url', 'cdn_url')
        }),
        ('上传信息', {
            'fields': ('upload_status', 'upload_time', 'error_message')
        }),
        ('文件类型判断', {
            'fields': ('is_image', 'is_video', 'is_audio', 'is_document')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def has_add_permission(self, request):
        """禁止手动添加记录"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """允许修改记录"""
        return True
    
    def has_delete_permission(self, request, obj=None):
        """允许删除记录"""
        return True
