from django.urls import path
from .views import LoginView, RegisterView, SendEmailCodeView, EmailLoginView, RefreshTokenView, GetUserInfoView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('send_email_code/', SendEmailCodeView.as_view(), name='send_email_code'),
    path('email_login/', EmailLoginView.as_view(), name='email_login'),
    path('refreshToken/', RefreshTokenView.as_view(), name='refresh_token'),
    path('getUserInfo', GetUserInfoView.as_view(), name='get_user_info'),
]