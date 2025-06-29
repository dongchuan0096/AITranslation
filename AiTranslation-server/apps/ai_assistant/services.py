import uuid
import json
from typing import List, Dict, Any
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from django.conf import settings
from .models import Conversation, Message, AssistantConfig, Tool
from .prompt_selector import PromptSelector

class AssistantService:
    """智能助理服务类"""
    
    def __init__(self, user_id: str = None):
        self.user_id = user_id or "anonymous"
        self.config = self._get_default_config()
        self.prompt_selector = PromptSelector()
    
    def _get_default_config(self) -> AssistantConfig:
        """获取默认配置"""
        try:
            config = AssistantConfig.objects.filter(is_active=True).first()
            if config:
                return config
            
            # 如果没有配置，创建一个默认配置
            config = AssistantConfig.objects.create(
                name="默认配置",
                system_prompt="你是一个有用的AI助理。请用中文回答用户的问题。",
                model_type=getattr(settings, 'AI_MODEL_TYPE', 'openai'),
                model_name=getattr(settings, 'OPENAI_MODEL', 'gpt-3.5-turbo'),
                max_tokens=2000,
                temperature=0.7,
                max_history=10,
                is_active=True
            )
            return config
            
        except Exception as e:
            print(f"创建默认配置失败: {e}")
            # 如果数据库表不存在，返回默认配置
            return type('Config', (), {
                'system_prompt': "你是一个有用的AI助理。请用中文回答用户的问题。",
                'model_type': getattr(settings, 'AI_MODEL_TYPE', 'openai'),
                'model_name': getattr(settings, 'OPENAI_MODEL', 'gpt-3.5-turbo'),
                'max_tokens': 2000,
                'temperature': 0.7,
                'max_history': 10
            })()
    
    def create_conversation(self, title: str = None) -> Conversation:
        """创建新对话"""
        session_id = str(uuid.uuid4())
        title = title or "新对话"
        
        conversation = Conversation.objects.create(
            user_id=self.user_id,
            session_id=session_id,
            title=title
        )
        return conversation
    
    def get_conversation(self, session_id: str) -> Conversation:
        """获取对话"""
        try:
            return Conversation.objects.get(session_id=session_id, user_id=self.user_id)
        except Conversation.DoesNotExist:
            return self.create_conversation()
    
    def save_message(self, conversation: Conversation, role: str, content: str, tokens_used: int = 0):
        """保存消息"""
        return Message.objects.create(
            conversation=conversation,
            role=role,
            content=content,
            tokens_used=tokens_used
        )
    
    def get_conversation_history(self, conversation: Conversation, max_messages: int = None) -> List[Dict]:
        """获取对话历史"""
        max_messages = max_messages or self.config.max_history
        messages = conversation.messages.order_by('-created_at')[:max_messages]
        
        # 转换为LangChain消息格式
        history = []
        for msg in reversed(messages):  # 按时间正序
            if msg.role == 'user':
                history.append(HumanMessage(content=msg.content))
            elif msg.role == 'assistant':
                history.append(AIMessage(content=msg.content))
            elif msg.role == 'system':
                history.append(SystemMessage(content=msg.content))
        
        return history
    
    def _get_llm(self, streaming: bool = False) -> ChatOpenAI:
        """获取LLM实例"""
        if self.config.model_type.lower() == "deepseek":
            api_key = getattr(settings, 'DEEPSEEK_API_KEY', None)
            model_name = getattr(settings, 'DEEPSEEK_MODEL', 'deepseek-chat')
            base_url = getattr(settings, 'DEEPSEEK_BASE_URL', 'https://api.deepseek.com/v1')
            
            return ChatOpenAI(
                openai_api_key=api_key,
                model=model_name,
                openai_api_base=base_url,
                streaming=streaming,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature
            )
        else:
            api_key = getattr(settings, 'OPENAI_API_KEY', None)
            model_name = getattr(settings, 'OPENAI_MODEL', 'gpt-3.5-turbo')
            
            return ChatOpenAI(
                openai_api_key=api_key,
                model=model_name,
                streaming=streaming,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature
            )
    
    def _select_and_format_prompt(self, user_message: str, conversation_id: str = None) -> str:
        """自动选择并格式化提示词"""
        # 自动选择最合适的提示词模板
        template, confidence_score = self.prompt_selector.select_prompt(user_message, conversation_id)
        
        # 格式化提示词
        formatted_prompt = self.prompt_selector.format_prompt(template, text=user_message)
        
        return formatted_prompt, template.name, confidence_score
    
    def chat(self, message: str, session_id: str = None, stream: bool = False, auto_prompt: bool = True) -> Dict[str, Any]:
        """智能对话"""
        # 获取或创建对话
        conversation = self.get_conversation(session_id) if session_id else self.create_conversation()
        
        # 保存用户消息
        self.save_message(conversation, 'user', message)
        
        # 获取对话历史
        history = self.get_conversation_history(conversation)
        
        # 构建消息列表
        if auto_prompt:
            # 使用自动选择的提示词
            system_prompt, prompt_name, confidence_score = self._select_and_format_prompt(message, conversation.session_id)
            messages = [SystemMessage(content=system_prompt)] + history
        else:
            # 使用默认系统提示词
            messages = [SystemMessage(content=self.config.system_prompt)] + history + [HumanMessage(content=message)]
        
        # 获取LLM
        llm = self._get_llm(streaming=stream)
        
        if stream:
            # 流式响应
            return {
                'type': 'stream',
                'conversation_id': conversation.session_id,
                'llm': llm,
                'messages': messages,
                'prompt_name': prompt_name if auto_prompt else None,
                'confidence_score': confidence_score if auto_prompt else None
            }
        else:
            # 普通响应
            try:
                if auto_prompt:
                    # 直接使用格式化后的提示词
                    response = llm.invoke(system_prompt)
                else:
                    response = llm.invoke(messages)
                
                assistant_message = response.content
                
                # 保存助理回复
                self.save_message(conversation, 'assistant', assistant_message)
                
                return {
                    'type': 'response',
                    'conversation_id': conversation.session_id,
                    'message': assistant_message,
                    'conversation_title': conversation.title,
                    'prompt_name': prompt_name if auto_prompt else None,
                    'confidence_score': confidence_score if auto_prompt else None
                }
            except Exception as e:
                return {
                    'type': 'error',
                    'error': str(e)
                }
    
    def get_user_conversations(self) -> List[Conversation]:
        """获取用户的对话列表"""
        return Conversation.objects.filter(
            user_id=self.user_id, 
            is_active=True
        ).order_by('-updated_at')
    
    def update_conversation_title(self, session_id: str, title: str) -> bool:
        """更新对话标题"""
        try:
            conversation = Conversation.objects.get(session_id=session_id, user_id=self.user_id)
            conversation.title = title
            conversation.save()
            return True
        except Conversation.DoesNotExist:
            return False
    
    def delete_conversation(self, session_id: str) -> bool:
        """删除对话"""
        try:
            conversation = Conversation.objects.get(session_id=session_id, user_id=self.user_id)
            conversation.is_active = False
            conversation.save()
            return True
        except Conversation.DoesNotExist:
            return False
    
    def get_prompt_templates(self, category: str = None) -> List[Dict]:
        """获取提示词模板列表"""
        if category:
            templates = self.prompt_selector.get_templates_by_category(category)
        else:
            templates = self.prompt_selector.get_all_templates()
        
        data = []
        for template in templates:
            data.append({
                'id': template.id,
                'name': template.name,
                'category': template.category,
                'description': template.description,
                'keywords': template.keywords,
                'priority': template.priority,
                'usage_count': template.usage_count
            })
        
        return data 