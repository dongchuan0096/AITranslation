from django.urls import path
from .views import TextTranslateView

urlpatterns = [
    path('text-translate/', TextTranslateView.as_view(), name='text_translate'),
]    