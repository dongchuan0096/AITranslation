from rest_framework_simplejwt.tokens import RefreshToken
from datetime import timedelta
from django.conf import settings

class JWTUtils:
    """JWT工具类，用于管理token的过期时间"""
    
    @staticmethod
    def create_tokens_for_user(user, access_token_lifetime=None, refresh_token_lifetime=None):
        """
        为用户创建访问令牌和刷新令牌
        
        Args:
            user: 用户对象
            access_token_lifetime: 访问令牌过期时间（timedelta对象），默认使用settings中的配置
            refresh_token_lifetime: 刷新令牌过期时间（timedelta对象），默认使用settings中的配置
        
        Returns:
            dict: 包含access_token和refresh_token的字典
        """
        refresh = RefreshToken.for_user(user)
        
        # 如果指定了自定义过期时间，则设置
        if access_token_lifetime:
            refresh.access_token.set_exp(lifetime=access_token_lifetime)
        
        if refresh_token_lifetime:
            refresh.set_exp(lifetime=refresh_token_lifetime)
        
        return {
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh)
        }
    
    @staticmethod
    def create_short_lived_token(user, hours=1):
        """创建短期访问令牌（1小时）"""
        return JWTUtils.create_tokens_for_user(
            user, 
            access_token_lifetime=timedelta(hours=hours)
        )
    
    @staticmethod
    def create_long_lived_token(user, days=30):
        """创建长期访问令牌（30天）"""
        return JWTUtils.create_tokens_for_user(
            user, 
            access_token_lifetime=timedelta(days=days)
        )
    
    @staticmethod
    def create_session_token(user, minutes=30):
        """创建会话令牌（30分钟）"""
        return JWTUtils.create_tokens_for_user(
            user, 
            access_token_lifetime=timedelta(minutes=minutes)
        ) 