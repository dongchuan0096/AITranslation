from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import StreamingHttpResponse
import json
import os
from langchain_openai import ChatOpenAI
from django.conf import settings
from .services import AssistantService

# Create your views here.

class SmartAssistantAPIView(APIView):
    """
    智能助理API
    支持对话历史、上下文记忆、流式传输、自动提示词选择
    """
    
    def post(self, request):
        # 处理多种前端请求格式
        data = request.data
        
        # 提取参数
        user_message = ""
        session_id = data.get("session_id")
        stream = data.get("stream", False)
        user_id = data.get("user_id", "anonymous")
        auto_prompt = data.get("auto_prompt", True)  # 默认启用自动提示词选择
        
        if isinstance(data, dict):
            # 格式1: {"message": "你好"}
            if "message" in data and isinstance(data["message"], str):
                user_message = data["message"]
            # 格式2: {"message": {"content": "你好", "role": "user"}}
            elif "message" in data and isinstance(data["message"], dict) and "content" in data["message"]:
                user_message = data["message"]["content"]
            # 格式3: {"messages": [{"content": "你好", "role": "user"}]}
            elif "messages" in data and isinstance(data["messages"], list) and len(data["messages"]) > 0:
                last_message = data["messages"][-1]
                if isinstance(last_message, dict) and "content" in last_message:
                    user_message = last_message["content"]
        
        if not user_message:
            return Response({"error": "消息不能为空"}, status=status.HTTP_400_BAD_REQUEST)

        # 创建助理服务
        assistant = AssistantService(user_id=user_id)
        
        # 执行对话
        result = assistant.chat(user_message, session_id, stream, auto_prompt)
        
        if result['type'] == 'error':
            return Response({"error": result['error']}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        if stream:
            # 流式响应
            return self._stream_response(result, assistant)
        else:
            # 普通响应
            response_data = {
                "message": {"content": result['message']},
                "conversation_id": result['conversation_id'],
                "conversation_title": result.get('conversation_title', '新对话')
            }
            
            # 添加提示词信息
            if result.get('prompt_name'):
                response_data['prompt_info'] = {
                    'name': result['prompt_name'],
                    'confidence_score': result.get('confidence_score', 0)
                }
            
            return Response(response_data, status=status.HTTP_200_OK)

    def _stream_response(self, result, assistant):
        """处理流式响应"""
        def generate():
            try:
                # 发送开始标记
                start_data = {'type': 'start', 'conversation_id': result['conversation_id']}
                if result.get('prompt_name'):
                    start_data['prompt_info'] = {
                        'name': result['prompt_name'],
                        'confidence_score': result.get('confidence_score', 0)
                    }
                yield f"data: {json.dumps(start_data)}\n\n"
                
                # 流式获取回复
                full_content = ""
                for chunk in result['llm'].stream(result['messages']):
                    if hasattr(chunk, 'content') and chunk.content:
                        content = chunk.content
                        full_content += content
                        # 发送数据块
                        yield f"data: {json.dumps({'type': 'chunk', 'message': {'content': content}})}\n\n"
                
                # 保存助理回复
                conversation = assistant.get_conversation(result['conversation_id'])
                assistant.save_message(conversation, 'assistant', full_content)
                
                # 发送结束标记
                yield f"data: {json.dumps({'type': 'end', 'message': {'content': full_content}})}\n\n"
                
            except Exception as e:
                # 发送错误信息
                yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
        
        response = StreamingHttpResponse(
            generate(),
            content_type='text/plain; charset=utf-8'
        )
        response['Cache-Control'] = 'no-cache'
        response['X-Accel-Buffering'] = 'no'
        return response

class ConversationAPIView(APIView):
    """对话管理API"""
    
    def get(self, request):
        """获取用户的对话列表"""
        user_id = request.GET.get("user_id", "anonymous")
        assistant = AssistantService(user_id=user_id)
        conversations = assistant.get_user_conversations()
        
        data = []
        for conv in conversations:
            data.append({
                "session_id": conv.session_id,
                "title": conv.title,
                "created_at": conv.created_at.isoformat(),
                "updated_at": conv.updated_at.isoformat(),
                "message_count": conv.messages.count()
            })
        
        return Response({"conversations": data}, status=status.HTTP_200_OK)
    
    def post(self, request):
        """创建新对话"""
        user_id = request.data.get("user_id", "anonymous")
        title = request.data.get("title", "新对话")
        
        assistant = AssistantService(user_id=user_id)
        conversation = assistant.create_conversation(title)
        
        return Response({
            "session_id": conversation.session_id,
            "title": conversation.title,
            "created_at": conversation.created_at.isoformat()
        }, status=status.HTTP_201_CREATED)
    
    def put(self, request):
        """更新对话标题"""
        session_id = request.data.get("session_id")
        title = request.data.get("title")
        user_id = request.data.get("user_id", "anonymous")
        
        if not session_id or not title:
            return Response({"error": "session_id和title不能为空"}, status=status.HTTP_400_BAD_REQUEST)
        
        assistant = AssistantService(user_id=user_id)
        success = assistant.update_conversation_title(session_id, title)
        
        if success:
            return Response({"message": "更新成功"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "对话不存在"}, status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request):
        """删除对话"""
        session_id = request.data.get("session_id")
        user_id = request.data.get("user_id", "anonymous")
        
        if not session_id:
            return Response({"error": "session_id不能为空"}, status=status.HTTP_400_BAD_REQUEST)
        
        assistant = AssistantService(user_id=user_id)
        success = assistant.delete_conversation(session_id)
        
        if success:
            return Response({"message": "删除成功"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "对话不存在"}, status=status.HTTP_404_NOT_FOUND)

class MessageHistoryAPIView(APIView):
    """消息历史API"""
    
    def get(self, request):
        """获取对话的消息历史"""
        session_id = request.GET.get("session_id")
        user_id = request.GET.get("user_id", "anonymous")
        
        if not session_id:
            return Response({"error": "session_id不能为空"}, status=status.HTTP_400_BAD_REQUEST)
        
        assistant = AssistantService(user_id=user_id)
        conversation = assistant.get_conversation(session_id)
        
        messages = []
        for msg in conversation.messages.all():
            messages.append({
                "role": msg.role,
                "content": msg.content,
                "created_at": msg.created_at.isoformat()
            })
        
        return Response({
            "conversation_id": session_id,
            "title": conversation.title,
            "messages": messages
        }, status=status.HTTP_200_OK)

# 保留原有的简单聊天API作为兼容
class LangchainAssistantAPIView(APIView):
    """
    简单聊天API（兼容旧版本）
    """
    def post(self, request):
        # 处理多种前端请求格式
        data = request.data
        
        # 提取用户消息 - 支持多种格式
        user_message = ""
        stream = False
        
        if isinstance(data, dict):
            # 检查是否启用流式传输
            stream = data.get("stream", False)
            
            # 格式1: {"message": "你好"}
            if "message" in data and isinstance(data["message"], str):
                user_message = data["message"]
            # 格式2: {"message": {"content": "你好", "role": "user"}}
            elif "message" in data and isinstance(data["message"], dict) and "content" in data["message"]:
                user_message = data["message"]["content"]
            # 格式3: {"messages": [{"content": "你好", "role": "user"}]}
            elif "messages" in data and isinstance(data["messages"], list) and len(data["messages"]) > 0:
                last_message = data["messages"][-1]
                if isinstance(last_message, dict) and "content" in last_message:
                    user_message = last_message["content"]
        
        if not user_message:
            return Response({"error": "消息不能为空"}, status=status.HTTP_400_BAD_REQUEST)

        # 从settings获取模型配置
        model_type = getattr(settings, 'AI_MODEL_TYPE', 'openai')  # 默认使用OpenAI
        
        # 根据模型类型选择配置
        if model_type.lower() == "deepseek":
            # 使用DeepSeek配置
            api_key = getattr(settings, 'DEEPSEEK_API_KEY', None)
            model_name = getattr(settings, 'DEEPSEEK_MODEL', 'deepseek-chat')
            base_url = getattr(settings, 'DEEPSEEK_BASE_URL', 'https://api.deepseek.com/v1')
            
            if not api_key or api_key == "sk-your-deepseek-api-key-here":
                return Response({"error": "请在Translation/settings.py中配置正确的DEEPSEEK_API_KEY"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            # 使用OpenAI配置
            api_key = getattr(settings, 'OPENAI_API_KEY', None)
            model_name = getattr(settings, 'OPENAI_MODEL', 'gpt-3.5-turbo')
            base_url = None
            
            if not api_key or api_key == "sk-your-openai-api-key-here":
                return Response({"error": "请在Translation/settings.py中配置正确的OPENAI_API_KEY"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 构建LangChain对话
        try:
            if base_url:
                # 使用自定义base_url（DeepSeek）
                llm = ChatOpenAI(
                    openai_api_key=api_key, 
                    model=model_name,
                    openai_api_base=base_url,
                    streaming=stream  # 启用流式传输
                )
            else:
                # 使用默认OpenAI端点
                llm = ChatOpenAI(openai_api_key=api_key, model=model_name, streaming=stream)
            
            if stream:
                # 流式传输
                return self._stream_response(llm, user_message)
            else:
                # 普通响应
                reply = llm.invoke(user_message)
                return Response({"message": {"content": reply.content}}, status=status.HTTP_200_OK)
                
        except Exception as e:
            return Response({"error": f"AI服务异常: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _stream_response(self, llm, user_message):
        """处理流式响应"""
        def generate():
            try:
                # 发送开始标记
                yield f"data: {json.dumps({'type': 'start', 'message': {'content': ''}})}\n\n"
                
                # 流式获取回复
                full_content = ""
                for chunk in llm.stream(user_message):
                    if hasattr(chunk, 'content') and chunk.content:
                        content = chunk.content
                        full_content += content
                        # 发送数据块
                        yield f"data: {json.dumps({'type': 'chunk', 'message': {'content': content}})}\n\n"
                
                # 发送结束标记
                yield f"data: {json.dumps({'type': 'end', 'message': {'content': full_content}})}\n\n"
                
            except Exception as e:
                # 发送错误信息
                yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
        
        response = StreamingHttpResponse(
            generate(),
            content_type='text/plain; charset=utf-8'
        )
        response['Cache-Control'] = 'no-cache'
        response['X-Accel-Buffering'] = 'no'  # 禁用Nginx缓冲
        return response

class PromptTemplateAPIView(APIView):
    """提示词模板管理API"""
    
    def get(self, request):
        """获取提示词模板列表"""
        category = request.GET.get("category")
        user_id = request.GET.get("user_id", "anonymous")
        
        assistant = AssistantService(user_id=user_id)
        templates = assistant.get_prompt_templates(category)
        
        return Response({"templates": templates}, status=status.HTTP_200_OK)
    
    def post(self, request):
        """创建新的提示词模板"""
        try:
            from .models import PromptTemplate
            
            template = PromptTemplate.objects.create(
                name=request.data.get("name"),
                category=request.data.get("category", "general"),
                description=request.data.get("description", ""),
                keywords=request.data.get("keywords", []),
                prompt_template=request.data.get("prompt_template"),
                variables=request.data.get("variables", []),
                priority=request.data.get("priority", 1)
            )
            
            return Response({
                "id": template.id,
                "name": template.name,
                "message": "模板创建成功"
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request):
        """更新提示词模板"""
        try:
            from .models import PromptTemplate
            
            template_id = request.data.get("id")
            template = PromptTemplate.objects.get(id=template_id)
            
            # 更新字段
            for field in ["name", "category", "description", "keywords", "prompt_template", "variables", "priority"]:
                if field in request.data:
                    setattr(template, field, request.data[field])
            
            template.save()
            
            return Response({"message": "模板更新成功"}, status=status.HTTP_200_OK)
            
        except PromptTemplate.DoesNotExist:
            return Response({"error": "模板不存在"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request):
        """删除提示词模板"""
        try:
            from .models import PromptTemplate
            
            template_id = request.data.get("id")
            template = PromptTemplate.objects.get(id=template_id)
            template.is_active = False
            template.save()
            
            return Response({"message": "模板删除成功"}, status=status.HTTP_200_OK)
            
        except PromptTemplate.DoesNotExist:
            return Response({"error": "模板不存在"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
