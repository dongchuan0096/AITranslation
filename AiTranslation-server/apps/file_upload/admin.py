from django.contrib import admin
from .models import FileUploadRecord

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
