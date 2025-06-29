from django.shortcuts import render
import os
import time
import hashlib
import mimetypes
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils import timezone
from django.db.models import Q, Sum
from apps.utils.response import APIResponse
from apps.utils.api_logger import log_api_access
from apps.utils.oss_uploader import oss_uploader
from .models import FileUploadRecord
from .serializers import FileUploadRecordSerializer

class FileUploadView(APIView):
    """文件上传到阿里云OSS接口"""
    
    @log_api_access(api_name="文件上传OSS", sensitive_fields=['password', 'token'])
    def post(self, request):
        """上传文件到阿里云OSS"""
        try:
            # 检查文件上传
            if 'file' not in request.FILES:
                return APIResponse.fail(msg="请上传文件", code="4001")
            
            uploaded_file = request.FILES['file']
            original_filename = uploaded_file.name
            
            # 获取当前用户（如果已认证）
            user = request.user if request.user.is_authenticated else None
            
            # 上传文件到OSS
            result = oss_uploader.upload_file(uploaded_file, original_filename, user)
            
            if result['success']:
                return APIResponse.success(
                    msg="文件上传成功",
                    data={
                        'file_record_id': result['file_record_id'],
                        'original_filename': result['original_filename'],
                        'file_size': result['file_size'],
                        'file_size_mb': round(result['file_size'] / (1024 * 1024), 2),
                        'file_type': result['file_type'],
                        'oss_key': result['oss_key'],
                        'oss_url': result['oss_url'],
                        'cdn_url': result['cdn_url'],
                        'upload_time': round(result['upload_time'], 3),
                        'md5_hash': result['md5_hash']
                    }
                )
            else:
                return APIResponse.fail(
                    msg=f"文件上传失败: {result['error']}", 
                    code="4002"
                )
                
        except Exception as e:
            return APIResponse.fail(msg=f"文件上传异常: {str(e)}", code="4003")

class FileUploadInfoView(APIView):
    """文件上传信息查询接口"""
    
    @log_api_access(api_name="文件上传信息查询")
    def get(self, request):
        """获取文件上传配置信息"""
        from apps.utils.oss_config import UPLOAD_CONFIG, SECURITY_CONFIG, PERFORMANCE_CONFIG
        
        return APIResponse.success(
            msg="获取文件上传信息成功",
            data={
                "upload_config": {
                    "max_file_size_mb": round(UPLOAD_CONFIG['MAX_FILE_SIZE'] / (1024 * 1024), 2),
                    "allowed_extensions": UPLOAD_CONFIG['ALLOWED_EXTENSIONS'],
                    "allowed_mime_types": UPLOAD_CONFIG['ALLOWED_MIME_TYPES'],
                    "upload_paths": UPLOAD_CONFIG['UPLOAD_PATH']
                },
                "security_config": {
                    "enable_md5_check": SECURITY_CONFIG['ENABLE_MD5_CHECK'],
                    "enable_file_type_check": SECURITY_CONFIG['ENABLE_FILE_TYPE_CHECK'],
                    "enable_size_limit": SECURITY_CONFIG['ENABLE_SIZE_LIMIT']
                },
                "performance_config": {
                    "chunk_size_mb": round(PERFORMANCE_CONFIG['CHUNK_SIZE'] / (1024 * 1024), 2),
                    "concurrent_uploads": PERFORMANCE_CONFIG['CONCURRENT_UPLOADS'],
                    "retry_times": PERFORMANCE_CONFIG['RETRY_TIMES'],
                    "timeout": PERFORMANCE_CONFIG['TIMEOUT']
                },
                "api_endpoints": {
                    "upload": "/api/file-upload/",
                    "info": "/api/file-upload-info/",
                    "list": "/api/file-upload-list/",
                    "delete": "/api/file-upload-delete/",
                    "detail": "/api/file-upload-detail/"
                },
                "storage_provider": "阿里云对象存储(OSS)"
            }
        )

class FileUploadListView(APIView):
    """文件上传记录列表接口"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    @log_api_access(api_name="文件上传记录查询")
    def get(self, request):
        """查询文件上传记录"""
        try:
            # 获取查询参数
            page = int(request.GET.get('page', 1))
            page_size = int(request.GET.get('page_size', 20))
            file_type = request.GET.get('file_type', '')
            upload_status = request.GET.get('upload_status', '')
            start_date = request.GET.get('start_date', '')
            end_date = request.GET.get('end_date', '')
            search = request.GET.get('search', '')
            
            # 构建查询条件
            queryset = FileUploadRecord.objects.filter(user=request.user)
            
            if file_type:
                queryset = queryset.filter(file_type__startswith=file_type)
            
            if upload_status:
                queryset = queryset.filter(upload_status=upload_status)
            
            if start_date:
                queryset = queryset.filter(created_at__date__gte=start_date)
            
            if end_date:
                queryset = queryset.filter(created_at__date__lte=end_date)
            
            if search:
                queryset = queryset.filter(
                    Q(original_filename__icontains=search) |
                    Q(oss_key__icontains=search)
                )
            
            # 分页
            total_count = queryset.count()
            start_index = (page - 1) * page_size
            end_index = start_index + page_size
            files = queryset[start_index:end_index]
            
            # 序列化数据
            serializer = FileUploadRecordSerializer(files, many=True)
            
            return APIResponse.success(
                msg="查询成功",
                data={
                    'files': serializer.data,
                    'pagination': {
                        'page': page,
                        'page_size': page_size,
                        'total_count': total_count,
                        'total_pages': (total_count + page_size - 1) // page_size
                    }
                }
            )
            
        except Exception as e:
            return APIResponse.fail(msg=f"查询失败: {str(e)}", code="5003")

class FileUploadDetailView(APIView):
    """文件上传记录详情接口"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    @log_api_access(api_name="文件上传记录详情")
    def get(self, request, file_id):
        """获取文件上传记录详情"""
        try:
            # 查找文件记录
            try:
                file_record = FileUploadRecord.objects.get(id=file_id, user=request.user)
            except FileUploadRecord.DoesNotExist:
                return APIResponse.fail(msg="文件不存在或无权限访问", code="4004")
            
            # 序列化数据
            serializer = FileUploadRecordSerializer(file_record)
            
            return APIResponse.success(
                msg="获取详情成功",
                data=serializer.data
            )
            
        except Exception as e:
            return APIResponse.fail(msg=f"获取详情失败: {str(e)}", code="5004")

class FileUploadDeleteView(APIView):
    """文件删除接口"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    @log_api_access(api_name="文件删除")
    def delete(self, request, file_id):
        """删除文件"""
        try:
            # 查找文件记录
            try:
                file_record = FileUploadRecord.objects.get(id=file_id, user=request.user)
            except FileUploadRecord.DoesNotExist:
                return APIResponse.fail(msg="文件不存在或无权限删除", code="4004")
            
            # 从OSS删除文件
            delete_result = oss_uploader.delete_file(file_record.oss_key)
            
            if delete_result['success']:
                # 删除数据库记录
                file_record.delete()
                return APIResponse.success(msg="文件删除成功")
            else:
                return APIResponse.fail(msg=f"OSS文件删除失败: {delete_result['error']}", code="4005")
                
        except Exception as e:
            return APIResponse.fail(msg=f"文件删除异常: {str(e)}", code="4006")

class FileUploadBatchDeleteView(APIView):
    """批量删除文件接口"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    @log_api_access(api_name="批量删除文件")
    def post(self, request):
        """批量删除文件"""
        try:
            file_ids = request.data.get('file_ids', [])
            if not file_ids:
                return APIResponse.fail(msg="请选择要删除的文件", code="4001")
            
            # 查找文件记录
            file_records = FileUploadRecord.objects.filter(
                id__in=file_ids, 
                user=request.user
            )
            
            if not file_records.exists():
                return APIResponse.fail(msg="没有找到要删除的文件", code="4002")
            
            success_count = 0
            failed_count = 0
            failed_files = []
            
            for file_record in file_records:
                try:
                    # 从OSS删除文件
                    delete_result = oss_uploader.delete_file(file_record.oss_key)
                    
                    if delete_result['success']:
                        # 删除数据库记录
                        file_record.delete()
                        success_count += 1
                    else:
                        failed_count += 1
                        failed_files.append({
                            'id': file_record.id,
                            'filename': file_record.original_filename,
                            'error': delete_result['error']
                        })
                        
                except Exception as e:
                    failed_count += 1
                    failed_files.append({
                        'id': file_record.id,
                        'filename': file_record.original_filename,
                        'error': str(e)
                    })
            
            return APIResponse.success(
                msg=f"批量删除完成，成功: {success_count}，失败: {failed_count}",
                data={
                    'success_count': success_count,
                    'failed_count': failed_count,
                    'failed_files': failed_files
                }
            )
            
        except Exception as e:
            return APIResponse.fail(msg=f"批量删除异常: {str(e)}", code="4007")

class FileUploadStatisticsView(APIView):
    """文件上传统计接口"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    @log_api_access(api_name="文件上传统计")
    def get(self, request):
        """获取文件上传统计信息"""
        try:
            # 获取查询参数
            start_date = request.GET.get('start_date', '')
            end_date = request.GET.get('end_date', '')
            
            # 构建查询条件
            queryset = FileUploadRecord.objects.filter(user=request.user)
            
            if start_date:
                queryset = queryset.filter(created_at__date__gte=start_date)
            
            if end_date:
                queryset = queryset.filter(created_at__date__lte=end_date)
            
            # 统计信息
            total_files = queryset.count()
            total_size = queryset.aggregate(total_size=Sum('file_size'))['total_size'] or 0
            success_files = queryset.filter(upload_status='success').count()
            failed_files = queryset.filter(upload_status='failed').count()
            
            # 按文件类型统计
            type_stats = {}
            for record in queryset:
                file_type = record.file_type.split('/')[0] if '/' in record.file_type else 'other'
                if file_type not in type_stats:
                    type_stats[file_type] = {'count': 0, 'size': 0}
                type_stats[file_type]['count'] += 1
                type_stats[file_type]['size'] += record.file_size
            
            # 按日期统计
            date_stats = {}
            for record in queryset:
                date_str = record.created_at.strftime('%Y-%m-%d')
                if date_str not in date_stats:
                    date_stats[date_str] = {'count': 0, 'size': 0}
                date_stats[date_str]['count'] += 1
                date_stats[date_str]['size'] += record.file_size
            
            return APIResponse.success(
                msg="获取统计信息成功",
                data={
                    'overview': {
                        'total_files': total_files,
                        'total_size_mb': round(total_size / (1024 * 1024), 2),
                        'success_files': success_files,
                        'failed_files': failed_files,
                        'success_rate': round(success_files / total_files * 100, 2) if total_files > 0 else 0
                    },
                    'type_statistics': type_stats,
                    'date_statistics': date_stats
                }
            )
            
        except Exception as e:
            return APIResponse.fail(msg=f"获取统计信息失败: {str(e)}", code="5005")
