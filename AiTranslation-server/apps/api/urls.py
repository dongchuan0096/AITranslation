from django.urls import path
from .views import (
    TextTranslateView, 
    SpeechRecognitionView, 
    SpeechRecognitionFileView, 
    SpeechRecognitionInfoView,
    APIAccessLogView,
    APIUsageStatisticsView,
    ImageTranslateProxyView,
    FileUploadView,
    FileUploadInfoView,
    FileUploadListView,
    FileUploadDeleteView
)

urlpatterns = [
    path('translate_image/', ImageTranslateProxyView.as_view(), name='image_translate'),
    path('text-translate/', TextTranslateView.as_view(), name='text_translate'),
    path('speech-recognition/', SpeechRecognitionView.as_view(), name='speech_recognition'),
    path('speech-recognition-file/', SpeechRecognitionFileView.as_view(), name='speech_recognition_file'),
    path('speech-recognition-info/', SpeechRecognitionInfoView.as_view(), name='speech_recognition_info'),
    path('access-logs/', APIAccessLogView.as_view(), name='api_access_logs'),
    path('usage-statistics/', APIUsageStatisticsView.as_view(), name='api_usage_statistics'),
    # 文件上传相关接口
    path('file-upload/', FileUploadView.as_view(), name='file_upload'),
    path('file-upload-info/', FileUploadInfoView.as_view(), name='file_upload_info'),
    path('file-upload-list/', FileUploadListView.as_view(), name='file_upload_list'),
    path('file-upload-delete/<int:file_id>/', FileUploadDeleteView.as_view(), name='file_upload_delete'),
]    