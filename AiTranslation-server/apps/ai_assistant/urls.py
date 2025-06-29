from django.urls import path
from .views import (
    LangchainAssistantAPIView, 
    SmartAssistantAPIView, 
    ConversationAPIView, 
    MessageHistoryAPIView,
    PromptTemplateAPIView
)

urlpatterns = [
    # 简单聊天API（兼容旧版本）
    path('chat/', LangchainAssistantAPIView.as_view(), name='langchain_chat'),
    
    # 智能助理API
    path('smart-chat/', SmartAssistantAPIView.as_view(), name='smart_assistant_chat'),
    
    # 对话管理API
    path('conversations/', ConversationAPIView.as_view(), name='conversation_management'),
    
    # 消息历史API
    path('messages/', MessageHistoryAPIView.as_view(), name='message_history'),
    
    # 提示词模板管理API
    path('prompt-templates/', PromptTemplateAPIView.as_view(), name='prompt_template_management'),
] 