from django.db import models
from django.contrib.auth.models import User
import json

class Conversation(models.Model):
    """对话会话模型"""
    user_id = models.CharField(max_length=100, verbose_name="用户ID")
    session_id = models.CharField(max_length=100, unique=True, verbose_name="会话ID")
    title = models.CharField(max_length=200, default="新对话", verbose_name="对话标题")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    is_active = models.BooleanField(default=True, verbose_name="是否活跃")

    class Meta:
        db_table = 'ai_assistant_conversation'
        verbose_name = '对话会话'
        verbose_name_plural = '对话会话'

    def __str__(self):
        return f"{self.user_id} - {self.title}"

class Message(models.Model):
    """消息模型"""
    ROLE_CHOICES = [
        ('user', '用户'),
        ('assistant', '助理'),
        ('system', '系统'),
    ]
    
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages', verbose_name="对话")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, verbose_name="角色")
    content = models.TextField(verbose_name="消息内容")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    tokens_used = models.IntegerField(default=0, verbose_name="使用的token数")
    
    class Meta:
        db_table = 'ai_assistant_message'
        verbose_name = '消息'
        verbose_name_plural = '消息'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.conversation.title} - {self.role}: {self.content[:50]}"

class AssistantConfig(models.Model):
    """智能助理配置模型"""
    name = models.CharField(max_length=100, unique=True, verbose_name="配置名称")
    system_prompt = models.TextField(default="你是一个有用的AI助理。", verbose_name="系统提示词")
    model_type = models.CharField(max_length=20, default="openai", verbose_name="模型类型")
    model_name = models.CharField(max_length=50, default="gpt-3.5-turbo", verbose_name="模型名称")
    max_tokens = models.IntegerField(default=2000, verbose_name="最大token数")
    temperature = models.FloatField(default=0.7, verbose_name="温度")
    max_history = models.IntegerField(default=10, verbose_name="最大历史消息数")
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    
    class Meta:
        db_table = 'ai_assistant_config'
        verbose_name = '助理配置'
        verbose_name_plural = '助理配置'

    def __str__(self):
        return self.name

class Tool(models.Model):
    """工具模型"""
    name = models.CharField(max_length=100, unique=True, verbose_name="工具名称")
    description = models.TextField(verbose_name="工具描述")
    function_name = models.CharField(max_length=100, verbose_name="函数名称")
    parameters = models.JSONField(default=dict, verbose_name="参数定义")
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    
    class Meta:
        db_table = 'ai_assistant_tool'
        verbose_name = '工具'
        verbose_name_plural = '工具'

    def __str__(self):
        return self.name

class PromptTemplate(models.Model):
    """提示词模板模型"""
    CATEGORY_CHOICES = [
        ('general', '通用'),
        ('coding', '编程'),
        ('writing', '写作'),
        ('analysis', '分析'),
        ('translation', '翻译'),
        ('creative', '创意'),
        ('education', '教育'),
        ('business', '商业'),
        ('other', '其他'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="模板名称")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general', verbose_name="分类")
    description = models.TextField(verbose_name="模板描述")
    keywords = models.JSONField(default=list, verbose_name="关键词列表")
    prompt_template = models.TextField(verbose_name="提示词模板")
    variables = models.JSONField(default=list, verbose_name="模板变量")
    priority = models.IntegerField(default=1, verbose_name="优先级")
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    usage_count = models.IntegerField(default=0, verbose_name="使用次数")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    
    class Meta:
        db_table = 'ai_assistant_prompt_template'
        verbose_name = '提示词模板'
        verbose_name_plural = '提示词模板'
        ordering = ['-priority', '-usage_count']

    def __str__(self):
        return f"{self.category} - {self.name}"

class PromptSelection(models.Model):
    """提示词选择记录模型"""
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='prompt_selections', verbose_name="对话")
    user_message = models.TextField(verbose_name="用户消息")
    selected_prompt = models.ForeignKey(PromptTemplate, on_delete=models.CASCADE, verbose_name="选择的提示词")
    confidence_score = models.FloatField(default=0.0, verbose_name="置信度")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    
    class Meta:
        db_table = 'ai_assistant_prompt_selection'
        verbose_name = '提示词选择记录'
        verbose_name_plural = '提示词选择记录'

    def __str__(self):
        return f"{self.conversation.title} - {self.selected_prompt.name}"
