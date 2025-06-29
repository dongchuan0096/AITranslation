import re
import json
from typing import List, Dict, Tuple, Optional
from django.db.models import Q
from django.db import models
from .models import PromptTemplate, PromptSelection, Conversation

class PromptSelector:
    """智能提示词选择器"""
    
    def __init__(self):
        self.prompt_templates = self._get_default_templates()
        self.context_window = 5  # 上下文窗口大小
    
    def _get_default_templates(self) -> List[Dict]:
        """获取默认提示词模板"""
        return [
            {
                "name": "文本翻译专家",
                "category": "translation",
                "description": "专业的文本翻译助手，支持多语言翻译",
                "keywords": ["翻译", "translate", "文本", "text", "语言", "language", "中英", "英中", "日文", "韩文"],
                "prompt_template": """你是一位专业的翻译专家，精通多种语言之间的翻译。

请将用户提供的文本进行翻译，要求：
1. 保持原文的意思和语气
2. 使用准确、自然的表达
3. 如果是专业术语，请使用标准翻译
4. 保留原文的格式和标点符号
5. 如果原文有特殊标记或注释，请一并翻译

请翻译以下内容：
{text}

如果用户没有指定目标语言，请询问目标语言。如果指定了目标语言，请直接翻译。""",
                "variables": ["text"],
                "priority": 10
            },
            {
                "name": "语音翻译助手",
                "category": "translation",
                "description": "专门处理语音转文本和翻译的服务",
                "keywords": ["语音", "voice", "speech", "音频", "audio", "听写", "转写", "语音识别"],
                "prompt_template": """你是一位专业的语音翻译助手，专门处理语音转文本和翻译服务。

请帮助用户处理语音相关内容：
1. 如果是语音转文本，请提供准确的文字记录
2. 如果是语音翻译，请提供原文和翻译
3. 处理方言、口音等特殊情况
4. 保持语音的语调和情感

用户需求：{text}

请根据用户的具体需求提供相应的服务。""",
                "variables": ["text"],
                "priority": 9
            },
            {
                "name": "漫画翻译专家",
                "category": "translation",
                "description": "专门处理漫画、图片中的文字翻译",
                "keywords": ["漫画", "manga", "comic", "图片", "image", "截图", "字幕", "subtitle", "气泡", "bubble"],
                "prompt_template": """你是一位专业的漫画翻译专家，专门处理漫画、图片中的文字翻译。

请帮助用户翻译漫画或图片中的文字：
1. 识别并翻译图片中的文字内容
2. 保持漫画的幽默感和文化特色
3. 处理拟声词、语气词等特殊表达
4. 保持对话的自然流畅
5. 注意文化差异和本地化

用户提供的图片或文字内容：{text}

请提供准确的翻译，并说明翻译的考虑因素。""",
                "variables": ["text"],
                "priority": 8
            },
            {
                "name": "多语言翻译器",
                "category": "translation",
                "description": "支持多种语言之间的互译",
                "keywords": ["多语言", "multilingual", "互译", "双向", "中英日韩", "法语", "德语", "西班牙语"],
                "prompt_template": """你是一位多语言翻译专家，精通中文、英文、日文、韩文、法文、德文、西班牙文等多种语言。

请根据用户需求进行翻译：
1. 准确识别源语言和目标语言
2. 提供高质量的翻译结果
3. 保持原文的语调和风格
4. 处理文化差异和表达习惯
5. 提供翻译说明和注意事项

翻译内容：{text}
源语言：{source_language}
目标语言：{target_language}

请提供翻译结果。""",
                "variables": ["text", "source_language", "target_language"],
                "priority": 7
            },
            {
                "name": "技术文档翻译",
                "category": "translation",
                "description": "专门翻译技术文档、代码注释等",
                "keywords": ["技术", "technical", "文档", "document", "代码", "code", "注释", "comment", "API", "函数"],
                "prompt_template": """你是一位技术文档翻译专家，专门处理技术文档、代码注释、API文档等的翻译。

请帮助翻译技术相关内容：
1. 保持技术术语的准确性
2. 使用标准的技术翻译
3. 保持文档的结构和格式
4. 处理代码注释和变量名
5. 提供技术背景说明

技术内容：{text}

请提供专业的技术翻译。""",
                "variables": ["text"],
                "priority": 6
            },
            {
                "name": "代码助手",
                "category": "coding",
                "description": "专业的编程助手，帮助编写、调试和优化代码",
                "keywords": ["代码", "编程", "code", "program", "函数", "function", "类", "class", "算法", "algorithm"],
                "prompt_template": """你是一位专业的编程助手，精通多种编程语言。

请帮助用户解决编程问题：
1. 编写清晰、高效的代码
2. 提供详细的代码解释
3. 指出潜在的问题和优化建议
4. 遵循最佳编程实践
5. 提供测试用例和示例

用户需求：{text}

请提供专业的编程帮助。""",
                "variables": ["text"],
                "priority": 9
            },
            {
                "name": "代码审查专家",
                "category": "coding",
                "description": "专业的代码审查和优化建议",
                "keywords": ["审查", "review", "优化", "optimize", "重构", "refactor", "性能", "performance"],
                "prompt_template": """你是一位专业的代码审查专家，擅长代码质量分析和优化建议。

请对用户提供的代码进行审查：
1. 检查代码质量和可读性
2. 识别潜在的性能问题
3. 提供重构和优化建议
4. 检查安全漏洞
5. 建议最佳实践

代码内容：{text}

请提供详细的代码审查报告。""",
                "variables": ["text"],
                "priority": 8
            },
            {
                "name": "写作助手",
                "category": "writing",
                "description": "专业的写作助手，帮助改进文章质量和表达",
                "keywords": ["写作", "write", "文章", "article", "文案", "copy", "编辑", "edit"],
                "prompt_template": """你是一位专业的写作助手，擅长各种文体的写作和编辑。

请帮助用户改进写作：
1. 检查语法和拼写错误
2. 改进句子结构和表达
3. 增强文章的逻辑性和连贯性
4. 提供写作建议和技巧
5. 保持原文的风格和语气

写作内容：{text}

请提供专业的写作建议和改进。""",
                "variables": ["text"],
                "priority": 8
            },
            {
                "name": "数据分析师",
                "category": "analysis",
                "description": "专业的数据分析和洞察",
                "keywords": ["分析", "analyze", "数据", "data", "统计", "statistics", "图表", "chart"],
                "prompt_template": """你是一位专业的数据分析师，擅长数据分析和洞察。

请帮助用户进行数据分析：
1. 分析数据趋势和模式
2. 提供统计分析和解释
3. 生成数据可视化建议
4. 识别异常值和问题
5. 提供数据驱动的建议

分析需求：{text}

请提供专业的数据分析报告。""",
                "variables": ["text"],
                "priority": 7
            },
            {
                "name": "创意写作助手",
                "category": "creative",
                "description": "激发创意和想象力的写作助手",
                "keywords": ["创意", "creative", "故事", "story", "小说", "novel", "诗歌", "poetry"],
                "prompt_template": """你是一位富有创意的写作助手，擅长激发想象力和创造力。

请帮助用户进行创意写作：
1. 提供创意灵感和想法
2. 帮助构建故事情节
3. 创造生动的角色和场景
4. 改进文学表达和修辞
5. 激发读者的情感共鸣

创意需求：{text}

请提供富有创意的写作帮助。""",
                "variables": ["text"],
                "priority": 7
            }
        ]
    
    def select_prompt(self, user_message: str, conversation_id: str = None, context_messages: List[str] = None) -> Tuple[PromptTemplate, float]:
        """根据用户消息和上下文智能选择最合适的提示词模板"""
        # 获取上下文信息
        context = self._get_conversation_context(conversation_id, context_messages)
        
        # 计算每个模板的匹配分数
        scores = []
        
        for template_data in self.prompt_templates:
            score = self._calculate_enhanced_match_score(user_message, template_data, context)
            scores.append((template_data, score))
        
        # 按分数排序，选择最高分的模板
        scores.sort(key=lambda x: x[1], reverse=True)
        best_template_data, best_score = scores[0]
        
        # 创建或获取数据库中的模板
        template = self._get_or_create_template(best_template_data)
        
        # 记录选择历史
        if conversation_id:
            self._record_selection(conversation_id, user_message, template, best_score, context)
        
        return template, best_score
    
    def _get_conversation_context(self, conversation_id: str = None, context_messages: List[str] = None) -> Dict:
        """获取对话上下文信息"""
        context = {
            'recent_messages': [],
            'user_preferences': {},
            'conversation_topic': None,
            'language_patterns': []
        }
        
        if conversation_id:
            try:
                conversation = Conversation.objects.get(session_id=conversation_id)
                # 获取最近的对话历史
                recent_messages = conversation.messages.order_by('-created_at')[:self.context_window]
                context['recent_messages'] = [msg.content for msg in reversed(recent_messages)]
                
                # 分析用户偏好
                context['user_preferences'] = self._analyze_user_preferences(conversation)
                
                # 识别对话主题
                context['conversation_topic'] = self._identify_conversation_topic(context['recent_messages'])
                
                # 分析语言模式
                context['language_patterns'] = self._analyze_language_patterns(context['recent_messages'])
                
            except Conversation.DoesNotExist:
                pass
        
        if context_messages:
            context['recent_messages'].extend(context_messages[-self.context_window:])
        
        return context
    
    def _analyze_user_preferences(self, conversation: Conversation) -> Dict:
        """分析用户偏好"""
        preferences = {
            'preferred_categories': {},
            'avoided_categories': {},
            'response_style': 'neutral'
        }
        
        # 分析历史选择记录
        selections = PromptSelection.objects.filter(conversation=conversation).order_by('-created_at')[:10]
        
        for selection in selections:
            category = selection.selected_prompt.category
            score = selection.confidence_score
            
            if score > 0.7:  # 高置信度选择
                preferences['preferred_categories'][category] = preferences['preferred_categories'].get(category, 0) + 1
            elif score < 0.3:  # 低置信度选择
                preferences['avoided_categories'][category] = preferences['avoided_categories'].get(category, 0) + 1
        
        return preferences
    
    def _identify_conversation_topic(self, messages: List[str]) -> str:
        """识别对话主题"""
        if not messages:
            return "general"
        
        # 简单的主题识别逻辑
        all_text = " ".join(messages).lower()
        
        topic_keywords = {
            "translation": ["翻译", "translate", "语言", "language"],
            "coding": ["代码", "编程", "code", "program"],
            "writing": ["写作", "文章", "write", "article"],
            "analysis": ["分析", "analyze", "数据", "data"],
            "creative": ["创意", "creative", "故事", "story"]
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in all_text for keyword in keywords):
                return topic
        
        return "general"
    
    def _analyze_language_patterns(self, messages: List[str]) -> List[str]:
        """分析语言模式"""
        patterns = []
        
        for message in messages:
            # 检测语言类型
            if re.search(r'[a-zA-Z]', message) and re.search(r'[\u4e00-\u9fff]', message):
                patterns.append("mixed_language")
            elif re.search(r'[\u4e00-\u9fff]', message):
                patterns.append("chinese")
            elif re.search(r'[a-zA-Z]', message):
                patterns.append("english")
            
            # 检测特殊模式
            if re.search(r'[0-9]+', message):
                patterns.append("contains_numbers")
            if re.search(r'[^\w\s]', message):
                patterns.append("contains_symbols")
        
        return list(set(patterns))
    
    def _calculate_enhanced_match_score(self, user_message: str, template_data: Dict, context: Dict) -> float:
        """计算增强的匹配分数"""
        score = 0.0
        message_lower = user_message.lower()
        
        # 1. 基础关键词匹配
        for keyword in template_data["keywords"]:
            if keyword.lower() in message_lower:
                score += 2.0
        
        # 2. 分类匹配
        category_keywords = {
            "translation": ["翻译", "translate", "语言", "language"],
            "coding": ["代码", "编程", "code", "program"],
            "writing": ["写作", "文章", "write", "article"],
            "analysis": ["分析", "analyze", "数据", "data"],
            "creative": ["创意", "creative", "故事", "story"],
            "education": ["教育", "学习", "education", "learn"],
            "business": ["商业", "商务", "business", "commerce"]
        }
        
        category = template_data["category"]
        if category in category_keywords:
            for keyword in category_keywords[category]:
                if keyword.lower() in message_lower:
                    score += 1.5
        
        # 3. 上下文匹配
        if context['conversation_topic'] == category:
            score += 1.0
        
        # 4. 用户偏好匹配
        user_prefs = context['user_preferences']
        if category in user_prefs.get('preferred_categories', {}):
            score += 0.5 * user_prefs['preferred_categories'][category]
        if category in user_prefs.get('avoided_categories', {}):
            score -= 0.3 * user_prefs['avoided_categories'][category]
        
        # 5. 语言模式匹配
        language_patterns = context['language_patterns']
        if "mixed_language" in language_patterns and category == "translation":
            score += 0.8
        if "contains_numbers" in language_patterns and category == "analysis":
            score += 0.6
        
        # 6. 优先级加分
        score += template_data.get("priority", 1) * 0.1
        
        # 7. 使用频率加分（从数据库获取）
        try:
            template = PromptTemplate.objects.get(name=template_data["name"])
            score += min(template.usage_count * 0.01, 0.5)  # 最多加0.5分
        except PromptTemplate.DoesNotExist:
            pass
        
        return max(score, 0.0)  # 确保分数不为负数
    
    def _get_or_create_template(self, template_data: Dict) -> PromptTemplate:
        """获取或创建提示词模板"""
        try:
            template = PromptTemplate.objects.get(name=template_data["name"])
            return template
        except PromptTemplate.DoesNotExist:
            # 创建新模板
            template = PromptTemplate.objects.create(
                name=template_data["name"],
                category=template_data["category"],
                description=template_data["description"],
                keywords=template_data["keywords"],
                prompt_template=template_data["prompt_template"],
                variables=template_data["variables"],
                priority=template_data.get("priority", 1)
            )
            return template
    
    def _record_selection(self, conversation_id: str, user_message: str, template: PromptTemplate, score: float, context: Dict):
        """记录提示词选择历史"""
        try:
            conversation = Conversation.objects.get(session_id=conversation_id)
            
            PromptSelection.objects.create(
                conversation=conversation,
                user_message=user_message,
                selected_prompt=template,
                confidence_score=score
            )
            
            # 更新模板使用次数
            template.usage_count += 1
            template.save()
            
        except Exception as e:
            print(f"记录提示词选择失败: {e}")
    
    def format_prompt(self, template: PromptTemplate, **kwargs) -> str:
        """格式化提示词模板"""
        prompt = template.prompt_template
        
        # 替换变量
        for var_name, var_value in kwargs.items():
            placeholder = "{" + var_name + "}"
            prompt = prompt.replace(placeholder, str(var_value))
        
        return prompt
    
    def get_templates_by_category(self, category: str) -> List[PromptTemplate]:
        """根据分类获取模板"""
        return PromptTemplate.objects.filter(category=category, is_active=True).order_by('-priority', '-usage_count')
    
    def get_all_templates(self) -> List[PromptTemplate]:
        """获取所有模板"""
        return PromptTemplate.objects.filter(is_active=True).order_by('-priority', '-usage_count')
    
    def get_user_preferences(self, user_id: str) -> Dict:
        """获取用户偏好分析"""
        preferences = {
            'preferred_categories': {},
            'total_selections': 0,
            'average_confidence': 0.0
        }
        
        try:
            # 获取用户的所有对话
            conversations = Conversation.objects.filter(user_id=user_id)
            
            # 分析所有选择记录
            all_selections = PromptSelection.objects.filter(conversation__in=conversations)
            
            if all_selections.exists():
                preferences['total_selections'] = all_selections.count()
                preferences['average_confidence'] = all_selections.aggregate(
                    avg_score=models.Avg('confidence_score')
                )['avg_score'] or 0.0
                
                # 统计分类偏好
                for selection in all_selections:
                    category = selection.selected_prompt.category
                    preferences['preferred_categories'][category] = preferences['preferred_categories'].get(category, 0) + 1
        
        except Exception as e:
            print(f"获取用户偏好失败: {e}")
        
        return preferences
    
    def suggest_templates(self, user_message: str, limit: int = 3) -> List[Dict]:
        """为用户消息推荐多个提示词模板"""
        context = self._get_conversation_context()
        scores = []
        
        for template_data in self.prompt_templates:
            score = self._calculate_enhanced_match_score(user_message, template_data, context)
            scores.append((template_data, score))
        
        # 按分数排序，返回前N个
        scores.sort(key=lambda x: x[1], reverse=True)
        
        suggestions = []
        for template_data, score in scores[:limit]:
            if score > 0.5:  # 只推荐有意义的模板
                suggestions.append({
                    'name': template_data['name'],
                    'category': template_data['category'],
                    'description': template_data['description'],
                    'confidence_score': score
                })
        
        return suggestions 