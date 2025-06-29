from rest_framework import serializers
from .models import FileUploadRecord

class FileUploadRecordSerializer(serializers.ModelSerializer):
    """文件上传记录序列化器"""
    
    file_size_mb = serializers.ReadOnlyField()
    file_size_kb = serializers.ReadOnlyField()
    is_image = serializers.ReadOnlyField()
    is_video = serializers.ReadOnlyField()
    is_audio = serializers.ReadOnlyField()
    is_document = serializers.ReadOnlyField()
    created_at_formatted = serializers.SerializerMethodField()
    updated_at_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = FileUploadRecord
        fields = [
            'id', 'user', 'original_filename', 'file_size', 'file_size_mb', 'file_size_kb',
            'file_type', 'file_extension', 'oss_bucket', 'oss_key', 'oss_url', 'cdn_url',
            'upload_status', 'upload_time', 'error_message', 'content_type', 'md5_hash',
            'created_at', 'updated_at', 'created_at_formatted', 'updated_at_formatted',
            'is_image', 'is_video', 'is_audio', 'is_document'
        ]
        read_only_fields = [
            'id', 'user', 'file_size_mb', 'file_size_kb', 'oss_bucket', 'oss_key', 
            'oss_url', 'cdn_url', 'upload_status', 'upload_time', 'error_message',
            'created_at', 'updated_at', 'created_at_formatted', 'updated_at_formatted',
            'is_image', 'is_video', 'is_audio', 'is_document'
        ]
    
    def get_created_at_formatted(self, obj):
        """格式化创建时间"""
        return obj.created_at.strftime('%Y-%m-%d %H:%M:%S') if obj.created_at else None
    
    def get_updated_at_formatted(self, obj):
        """格式化更新时间"""
        return obj.updated_at.strftime('%Y-%m-%d %H:%M:%S') if obj.updated_at else None

class FileUploadSummarySerializer(serializers.ModelSerializer):
    """文件上传记录摘要序列化器"""
    
    file_size_mb = serializers.ReadOnlyField()
    is_image = serializers.ReadOnlyField()
    is_video = serializers.ReadOnlyField()
    is_audio = serializers.ReadOnlyField()
    is_document = serializers.ReadOnlyField()
    created_at_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = FileUploadRecord
        fields = [
            'id', 'original_filename', 'file_size_mb', 'file_type', 'file_extension',
            'oss_url', 'upload_status', 'upload_time', 'created_at_formatted',
            'is_image', 'is_video', 'is_audio', 'is_document'
        ]
    
    def get_created_at_formatted(self, obj):
        """格式化创建时间"""
        return obj.created_at.strftime('%Y-%m-%d %H:%M:%S') if obj.created_at else None 