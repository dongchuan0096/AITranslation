from django.urls import path
from .views import (
    FileUploadView,
    FileUploadInfoView,
    FileUploadListView,
    FileUploadDetailView,
    FileUploadDeleteView,
    FileUploadBatchDeleteView,
    FileUploadStatisticsView
)

app_name = 'file_upload'

urlpatterns = [
    # 文件上传相关接口
    path('upload/', FileUploadView.as_view(), name='file_upload'),
    path('info/', FileUploadInfoView.as_view(), name='file_upload_info'),
    path('list/', FileUploadListView.as_view(), name='file_upload_list'),
    path('detail/<int:file_id>/', FileUploadDetailView.as_view(), name='file_upload_detail'),
    path('delete/<int:file_id>/', FileUploadDeleteView.as_view(), name='file_upload_delete'),
    path('batch-delete/', FileUploadBatchDeleteView.as_view(), name='file_upload_batch_delete'),
    path('statistics/', FileUploadStatisticsView.as_view(), name='file_upload_statistics'),
] 