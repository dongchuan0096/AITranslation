from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class FileUploadRecord(models.Model):
    """文件上传记录模型"""
    
    # 用户信息
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户", null=True, blank=True)
    
    # 文件信息
    original_filename = models.CharField(max_length=255, verbose_name="原始文件名")
    file_size = models.BigIntegerField(verbose_name="文件大小(字节)")
    file_type = models.CharField(max_length=50, verbose_name="文件类型")
    file_extension = models.CharField(max_length=20, verbose_name="文件扩展名")
    
    # 存储信息
    oss_bucket = models.CharField(max_length=100, verbose_name="OSS存储桶")
    oss_key = models.CharField(max_length=500, verbose_name="OSS对象键")
    oss_url = models.URLField(max_length=1000, verbose_name="OSS访问URL")
    cdn_url = models.URLField(max_length=1000, verbose_name="CDN加速URL", null=True, blank=True)
    
    # 上传信息
    upload_status = models.CharField(max_length=20, verbose_name="上传状态", default="success")
    upload_time = models.FloatField(verbose_name="上传耗时(秒)", null=True, blank=True)
    error_message = models.TextField(verbose_name="错误信息", null=True, blank=True)
    
    # 元数据
    content_type = models.CharField(max_length=100, verbose_name="内容类型", null=True, blank=True)
    md5_hash = models.CharField(max_length=32, verbose_name="MD5哈希值", null=True, blank=True)
    
    # 时间信息
    created_at = models.DateTimeField(verbose_name="创建时间", default=timezone.now)
    updated_at = models.DateTimeField(verbose_name="更新时间", auto_now=True)
    
    class Meta:
        db_table = 'file_upload_record'
        verbose_name = "文件上传记录"
        verbose_name_plural = "文件上传记录"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['file_type', 'created_at']),
            models.Index(fields=['upload_status', 'created_at']),
            models.Index(fields=['oss_key']),
        ]
    
    def __str__(self):
        return f"{self.original_filename} - {self.user.username if self.user else '匿名用户'} - {self.created_at}"
    
    @property
    def file_size_mb(self):
        """文件大小（MB）"""
        return round(self.file_size / (1024 * 1024), 2)
    
    @property
    def file_size_kb(self):
        """文件大小（KB）"""
        return round(self.file_size / 1024, 2)
    
    @property
    def is_image(self):
        """是否为图片文件"""
        return self.file_type.startswith('image/')
    
    @property
    def is_video(self):
        """是否为视频文件"""
        return self.file_type.startswith('video/')
    
    @property
    def is_audio(self):
        """是否为音频文件"""
        return self.file_type.startswith('audio/')
    
    @property
    def is_document(self):
        """是否为文档文件"""
        document_types = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument']
        return any(self.file_type.startswith(doc_type) for doc_type in document_types)
