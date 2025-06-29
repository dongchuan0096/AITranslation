from django.db import models
from django.contrib.auth.models import User
import uuid
import os

class KnowledgeBase(models.Model):
    """知识库模型"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, verbose_name="知识库名称")
    description = models.TextField(blank=True, verbose_name="知识库描述")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="创建者")
    is_public = models.BooleanField(default=False, verbose_name="是否公开")
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        db_table = 'knowledge_base'
        verbose_name = '知识库'
        verbose_name_plural = '知识库'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name

class Document(models.Model):
    """文档模型"""
    DOCUMENT_TYPES = [
        ('pdf', 'PDF文档'),
        ('docx', 'Word文档'),
        ('txt', '文本文件'),
        ('md', 'Markdown文件'),
        ('html', 'HTML文件'),
        ('json', 'JSON文件'),
        ('csv', 'CSV文件'),
        ('other', '其他文件'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    knowledge_base = models.ForeignKey(KnowledgeBase, on_delete=models.CASCADE, related_name='documents', verbose_name="所属知识库")
    title = models.CharField(max_length=200, verbose_name="文档标题")
    file_path = models.FileField(upload_to='knowledge_base/documents/', verbose_name="文件路径")
    file_type = models.CharField(max_length=10, choices=DOCUMENT_TYPES, verbose_name="文件类型")
    file_size = models.BigIntegerField(default=0, verbose_name="文件大小(字节)")
    content = models.TextField(blank=True, verbose_name="文档内容")
    is_processed = models.BooleanField(default=False, verbose_name="是否已处理")
    is_indexed = models.BooleanField(default=False, verbose_name="是否已索引")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        db_table = 'knowledge_base_document'
        verbose_name = '文档'
        verbose_name_plural = '文档'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.knowledge_base.name} - {self.title}"
    
    def get_file_extension(self):
        """获取文件扩展名"""
        return os.path.splitext(self.file_path.name)[1].lower()

class DocumentChunk(models.Model):
    """文档分块模型"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='chunks', verbose_name="所属文档")
    content = models.TextField(verbose_name="分块内容")
    chunk_index = models.IntegerField(verbose_name="分块索引")
    start_position = models.IntegerField(default=0, verbose_name="起始位置")
    end_position = models.IntegerField(default=0, verbose_name="结束位置")
    embedding = models.JSONField(null=True, blank=True, verbose_name="向量嵌入")
    metadata = models.JSONField(default=dict, verbose_name="元数据")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    
    class Meta:
        db_table = 'knowledge_base_document_chunk'
        verbose_name = '文档分块'
        verbose_name_plural = '文档分块'
        ordering = ['chunk_index']
        unique_together = ['document', 'chunk_index']
    
    def __str__(self):
        return f"{self.document.title} - 分块{self.chunk_index}"

class SearchQuery(models.Model):
    """搜索查询记录模型"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    knowledge_base = models.ForeignKey(KnowledgeBase, on_delete=models.CASCADE, related_name='search_queries', verbose_name="知识库")
    query = models.TextField(verbose_name="查询内容")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="查询用户")
    results_count = models.IntegerField(default=0, verbose_name="结果数量")
    response_time = models.FloatField(default=0.0, verbose_name="响应时间(秒)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="查询时间")
    
    class Meta:
        db_table = 'knowledge_base_search_query'
        verbose_name = '搜索查询'
        verbose_name_plural = '搜索查询'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.knowledge_base.name} - {self.query[:50]}"

class KnowledgeBaseConfig(models.Model):
    """知识库配置模型"""
    knowledge_base = models.OneToOneField(KnowledgeBase, on_delete=models.CASCADE, related_name='config', verbose_name="知识库")
    chunk_size = models.IntegerField(default=1000, verbose_name="分块大小")
    chunk_overlap = models.IntegerField(default=200, verbose_name="分块重叠")
    embedding_model = models.CharField(max_length=50, default='text-embedding-ada-002', verbose_name="嵌入模型")
    similarity_threshold = models.FloatField(default=0.7, verbose_name="相似度阈值")
    max_results = models.IntegerField(default=5, verbose_name="最大结果数")
    auto_update = models.BooleanField(default=True, verbose_name="自动更新")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        db_table = 'knowledge_base_config'
        verbose_name = '知识库配置'
        verbose_name_plural = '知识库配置'
    
    def __str__(self):
        return f"{self.knowledge_base.name} - 配置" 