from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class APIAccessLog(models.Model):
    """API访问记录模型"""
    
    # 用户信息
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户", null=True, blank=True)
    ip_address = models.GenericIPAddressField(verbose_name="IP地址", null=True, blank=True)
    user_agent = models.TextField(verbose_name="用户代理", null=True, blank=True)
    
    # API信息
    api_name = models.CharField(max_length=100, verbose_name="API名称")
    api_path = models.CharField(max_length=200, verbose_name="API路径")
    http_method = models.CharField(max_length=10, verbose_name="HTTP方法")
    
    # 请求信息
    request_data = models.JSONField(verbose_name="请求数据", null=True, blank=True)
    request_params = models.JSONField(verbose_name="请求参数", null=True, blank=True)
    
    # 响应信息
    response_status = models.IntegerField(verbose_name="响应状态码", null=True, blank=True)
    response_data = models.JSONField(verbose_name="响应数据", null=True, blank=True)
    error_message = models.TextField(verbose_name="错误信息", null=True, blank=True)
    
    # 性能信息
    execution_time = models.FloatField(verbose_name="执行时间(秒)", null=True, blank=True)
    request_size = models.IntegerField(verbose_name="请求大小(字节)", null=True, blank=True)
    response_size = models.IntegerField(verbose_name="响应大小(字节)", null=True, blank=True)
    
    # 时间信息
    created_at = models.DateTimeField(verbose_name="创建时间", default=timezone.now)
    updated_at = models.DateTimeField(verbose_name="更新时间", auto_now=True)
    
    # 额外信息
    is_success = models.BooleanField(verbose_name="是否成功", default=True)
    api_version = models.CharField(max_length=20, verbose_name="API版本", default="v1")
    
    class Meta:
        db_table = 'api_access_log'
        verbose_name = "API访问记录"
        verbose_name_plural = "API访问记录"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['api_name', 'created_at']),
            models.Index(fields=['ip_address', 'created_at']),
            models.Index(fields=['is_success', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username if self.user else '匿名用户'} - {self.api_name} - {self.created_at}"
    
    @property
    def duration_ms(self):
        """执行时间（毫秒）"""
        return round(self.execution_time * 1000, 2) if self.execution_time else 0
    
    @property
    def request_size_kb(self):
        """请求大小（KB）"""
        return round(self.request_size / 1024, 2) if self.request_size else 0
    
    @property
    def response_size_kb(self):
        """响应大小（KB）"""
        return round(self.response_size / 1024, 2) if self.response_size else 0

class APIUsageStatistics(models.Model):
    """API使用统计模型"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    api_name = models.CharField(max_length=100, verbose_name="API名称")
    date = models.DateField(verbose_name="日期")
    
    # 统计信息
    total_requests = models.IntegerField(verbose_name="总请求数", default=0)
    successful_requests = models.IntegerField(verbose_name="成功请求数", default=0)
    failed_requests = models.IntegerField(verbose_name="失败请求数", default=0)
    total_execution_time = models.FloatField(verbose_name="总执行时间", default=0)
    total_request_size = models.BigIntegerField(verbose_name="总请求大小", default=0)
    total_response_size = models.BigIntegerField(verbose_name="总响应大小", default=0)
    
    # 时间信息
    created_at = models.DateTimeField(verbose_name="创建时间", default=timezone.now)
    updated_at = models.DateTimeField(verbose_name="更新时间", auto_now=True)
    
    class Meta:
        db_table = 'api_usage_statistics'
        verbose_name = "API使用统计"
        verbose_name_plural = "API使用统计"
        unique_together = ['user', 'api_name', 'date']
        ordering = ['-date', '-total_requests']
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['api_name', 'date']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.api_name} - {self.date}"
    
    @property
    def success_rate(self):
        """成功率"""
        return round(self.successful_requests / self.total_requests * 100, 2) if self.total_requests > 0 else 0
    
    @property
    def avg_execution_time(self):
        """平均执行时间"""
        return round(self.total_execution_time / self.total_requests, 3) if self.total_requests > 0 else 0

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
