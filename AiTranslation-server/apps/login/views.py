from django.shortcuts import render
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework import status  
import random
from datetime import timedelta
from django.utils import timezone
from .models import UserProfile, EmailCode
from apps.utils.response import APIResponse
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

class LoginView(APIView):
    def post(self, request):
        username = request.data.get('userName')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return APIResponse.success(msg="登录成功", data={"token": str(refresh.access_token), "refreshToken": str(refresh)})
        else:
            return APIResponse.fail(msg="用户名或密码错误", code="1001")

class RegisterView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        code = request.data.get('code')
        if not email or not password or not code:
            return APIResponse.fail(msg="邮箱、验证码和密码不能为空", code="1002")
        if UserProfile.objects.filter(email=email).exists():
            return APIResponse.fail(msg="邮箱已注册", code="1003")
        now = timezone.now()
        valid_time = now - timedelta(minutes=5)
        email_code = EmailCode.objects.filter(email=email, code=code, created_at__gte=valid_time).order_by('-created_at').first()
        if not email_code:
            return APIResponse.fail(msg="验证码错误或已过期", code="1004")
        user = User.objects.create_user(username=email, password=password, email=email)
        UserProfile.objects.create(user=user, email=email)
        refresh = RefreshToken.for_user(user)
        return APIResponse.success(msg="注册成功", data={"token": str(refresh.access_token), "refreshToken": str(refresh)})


class SendEmailCodeView(APIView):
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return APIResponse.fail(msg="邮箱不能为空", code="1005")
        code = "%06d" % random.randint(0, 999999)
        EmailCode.objects.create(email=email, code=code)
        # 发送邮件
        send_mail(
            subject='您的验证码',
            message=f'您的验证码是：{code}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        return APIResponse.success(msg="验证码已发送")

class EmailLoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('code')
        if not email or not code:
            return APIResponse.fail(msg="邮箱和验证码不能为空", code="1006")
        now = timezone.now()
        valid_time = now - timedelta(minutes=5)
        email_code = EmailCode.objects.filter(email=email, code=code, created_at__gte=valid_time).order_by('-created_at').first()
        if not email_code:
            return APIResponse.fail(msg="验证码错误或已过期", code="1007")
        try:
            user_profile = UserProfile.objects.get(email=email)
            user = user_profile.user
        except UserProfile.DoesNotExist:
            return APIResponse.fail(msg="用户不存在", code="1008")
        token, created = Token.objects.get_or_create(user=user)
        return APIResponse.success(msg="登录成功", data={"token": token.key, "refreshToken": ""})

class RefreshTokenView(APIView):
    def post(self, request):
        refresh_token = request.data.get('refreshToken')
        if not refresh_token:
            return APIResponse.fail(msg="缺少refreshToken", code="2001")
        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
            return APIResponse.success(msg="刷新成功", data={"token": access_token})
        except TokenError as e:
            return APIResponse.fail(msg="refreshToken无效或已过期", code="2002")

class GetUserInfoView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
        }
        return APIResponse.success(msg="获取用户信息成功", data=data)

