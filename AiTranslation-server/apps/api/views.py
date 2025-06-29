from django.shortcuts import render
import requests
import base64
import hashlib
import hmac
import json
import time
import os
import tempfile
from urllib.parse import urlencode
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Q, Count, Avg, Sum
from apps.utils.response import APIResponse
from apps.utils.xunfei_config import XUNFEI_CONFIG, XUNFEI_ASR_URL, SUPPORTED_AUDIO_FORMATS, SUPPORTED_LANGUAGES, ENGINE_TYPES
from apps.utils.api_logger import log_api_access
from apps.utils.spark_mucl_cn_iat import create_xunfei_speech_recognition
from apps.api.models import APIAccessLog, APIUsageStatistics, FileUploadRecord
from apps.utils.oss_uploader import oss_uploader
import re
import random
import soundfile as sf
import wave
import contextlib
from django.conf import settings

#flask接口
SPARK_API_HOST = "127.0.0.1:5000"

LANGUAGE_DISPLAY = {
    'zh_cn': '中文',
    'en': '英语',
    'ja': '日语',
    'ko': '韩语',
    'fr': '法语',
    'es': '西班牙语',
    'ru': '俄语',
    'de': '德语',
    'it': '意大利语',
    'pt': '葡萄牙语',
    'ar': '阿拉伯语',
    # 可根据 SUPPORTED_LANGUAGES 补充
}
ACCENT_DISPLAY = {
    'mandarin': '普通话',
    'cantonese': '粤语',
    'sichuan': '四川话',
    # 可补充
}

def parse_bubble_texts(bubble_texts):
    """
    将 bubble_texts 字段的每个元素从字符串解析为字典
    输入示例:
        [
            '"detected": "ja",\n"translation": "xxx"',
            '"detected": "ja",\n"translation": "yyy"'
        ]
    输出示例:
        [
            {"detected": "ja", "translation": "xxx"},
            {"detected": "ja", "translation": "yyy"}
        ]
    """
    result = []
    for item in bubble_texts:
        detected = None
        translation = None
        detected_match = re.search(r'"detected"\s*:\s*"([^"]+)"', item)
        translation_match = re.search(r'"translation"\s*:\s*"([^"]+)"', item)
        if detected_match:
            detected = detected_match.group(1)
        if translation_match:
            translation = translation_match.group(1)
        result.append({
            "detected": detected,
            "translation": translation
        })
    return result

class TextTranslateView(APIView):
    @log_api_access(api_name="文本翻译", sensitive_fields=['password', 'token'])
    def post(self, request):
        # 获取请求数据
        request_data = request.data.copy()
        
        # 直接将处理后的参数转发到本地后端的 /api/spark/text-translate
        spark_url = f"http://{SPARK_API_HOST}/api/text-translate/"
        try:
            resp = requests.post(spark_url, json=request_data, timeout=100)
            return Response(resp.json(), status=resp.status_code)
        except Exception as e:
            return APIResponse.fail(msg=f"Spark接口调用异常: {str(e)}", code="4003")

class ImageTranslateProxyView(APIView):
    """
    转发图片翻译请求到 Flask 服务
    """
    def post(self, request):
        try:
            data = request.data if isinstance(request.data, dict) else request.data.dict()
            flask_url = f"http://{SPARK_API_HOST}/api/translate_image"
            resp = requests.post(flask_url, json=data, timeout=120)
            resp_json = resp.json()
            if "data" in resp_json and "bubble_texts" in resp_json["data"]:
                resp_json["data"]["bubble_texts"] = parse_bubble_texts(resp_json["data"]["bubble_texts"])
            return Response(resp_json, status=resp.status_code)
        except Exception as e:
            return Response({"error": f"图片翻译转发异常: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SpeechRecognitionView(APIView):
    """讯飞语音识别接口 - 基于官方WebSocket接口"""
    
    def process_audio_data(self, audio_data):
        """处理音频数据，支持多种格式"""
        try:
            # 如果是文件对象
            if hasattr(audio_data, 'read'):
                return audio_data.read()
            
            # 如果是字符串（Base64编码）
            elif isinstance(audio_data, str):
                return base64.b64decode(audio_data)
            
            # 如果是字节数据
            elif isinstance(audio_data, bytes):
                return audio_data
            
            # 如果是字节数组
            elif isinstance(audio_data, bytearray):
                return bytes(audio_data)
            
            else:
                raise ValueError(f"不支持的音频数据类型: {type(audio_data)}")
                
        except Exception as e:
            raise ValueError(f"音频数据处理失败: {str(e)}")
    
    def save_temp_audio_file(self, audio_data, audio_format):
        """保存音频数据到临时文件"""
        try:
            # 创建临时文件
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f'.{audio_format}')
            temp_file.write(audio_data)
            temp_file.close()
            return temp_file.name
        except Exception as e:
            raise ValueError(f"保存临时音频文件失败: {str(e)}")
    
    def save_permanent_audio_file(self, audio_data, audio_format):
        """保存音频数据到永久目录"""
        save_dir = os.path.join('media', 'voice_records')
        os.makedirs(save_dir, exist_ok=True)
        filename = f"{int(time.time())}_{random.randint(1000,9999)}.{audio_format}"
        save_path = os.path.join(save_dir, filename)
        with open(save_path, 'wb') as f:
            f.write(audio_data)
        return save_path
    
    def check_audio_properties(self, audio_path, audio_format):
        """检测音频文件属性，返回(是否合格, 错误信息)"""
        try:
            if audio_format in ['mp3', 'flac', 'ogg', 'wav']:
                info = sf.info(audio_path)
                if info.samplerate not in [16000, 8000]:
                    return False, f"采样率为{info.samplerate}Hz，需为16kHz或8kHz"
                if info.channels != 1:
                    return False, f"声道数为{info.channels}，需为单声道"
                # 位深判断
                if '16' not in str(info.subtype):
                    return False, f"采样位数为{info.subtype}，需为16bit"
                return True, None
            elif audio_format == 'pcm':
                # PCM原始流，假定16k/16bit/单声道，无法直接检测
                return True, None
            else:
                return False, f"暂不支持检测该格式: {audio_format}"
        except Exception as e:
            # wav兜底
            if audio_format == 'wav':
                try:
                    with contextlib.closing(wave.open(audio_path, 'rb')) as wf:
                        if wf.getframerate() not in [16000, 8000]:
                            return False, f"采样率为{wf.getframerate()}Hz，需为16kHz或8kHz"
                        if wf.getnchannels() != 1:
                            return False, f"声道数为{wf.getnchannels()}，需为单声道"
                        if wf.getsampwidth() * 8 != 16:
                            return False, f"采样位数为{wf.getsampwidth() * 8}bit，需为16bit"
                        return True, None
                except Exception as e2:
                    return False, f"音频属性检测失败: {e2}"
            return False, f"音频属性检测失败: {e}"

    @log_api_access(api_name="语音识别", sensitive_fields=['password', 'token', 'api_key', 'secret'])
    def post(self, request):
        """语音识别接口"""
        temp_file_path = None
        try:
            # 获取音频数据
            audio_data = None
            audio_format = request.data.get('audio_format', 'wav')  # 音频格式
            language = request.data.get('language', 'zh_cn')  # 语言
            accent = request.data.get('accent', 'mandarin')  # 口音
            
            # 检查是否有文件上传
            if 'audio_file' in request.FILES:
                audio_file = request.FILES['audio_file']
                audio_data = audio_file.read()
                audio_format = audio_file.name.split('.')[-1].lower()
            elif 'audio_data' in request.FILES:
                audio_file = request.FILES['audio_data']
                audio_data = audio_file.read()
                audio_format = audio_file.name.split('.')[-1].lower()
            else:
                # 从请求数据中获取音频数据
                audio_data_raw = request.data.get('audio_data')
                if not audio_data_raw:
                    return APIResponse.fail(msg="音频数据不能为空", code="4001")
                
                # 处理音频数据
                audio_data = self.process_audio_data(audio_data_raw)
            
            if not audio_data:
                return APIResponse.fail(msg="音频数据不能为空", code="4001")
            
            # 验证语言支持
            if language not in SUPPORTED_LANGUAGES:
                return APIResponse.fail(msg=f"不支持的语言: {language}", code="4002")
            
            # 验证音频格式
            if audio_format not in ['wav', 'mp3', 'pcm']:
                return APIResponse.fail(msg=f"不支持的音频格式: {audio_format}，仅支持wav、mp3、pcm", code="4003")
            
            # 检查音频长度（最长60秒，假设16k采样率）
            audio_duration = len(audio_data) / (16000 * 2)  # 16k采样率，16bit = 2字节
            if audio_duration > 60:
                return APIResponse.fail(msg=f"音频长度超过60秒限制: {audio_duration:.1f}秒", code="4004")
            
            print(f"讯飞语音识别 (官方接口):")
            print(f"  音频大小: {len(audio_data)} 字节")
            print(f"  音频格式: {audio_format}")
            print(f"  语言: {language}")
            print(f"  口音: {accent}")
            print(f"  预计时长: {audio_duration:.1f}秒")
            
            # 保存音频数据到临时文件
            temp_file_path = self.save_temp_audio_file(audio_data, audio_format)
            
            # 检查音频属性
            ok, err = self.check_audio_properties(temp_file_path, audio_format)
            if not ok:
                return APIResponse.fail(msg=f"音频属性不符合要求: {err}", code="4003")

            # 保存一份到永久目录
            permanent_path = self.save_permanent_audio_file(audio_data, audio_format)
            
            # 创建语音识别客户端
            asr_client = create_xunfei_speech_recognition()
            
            # 执行语音识别
            result = asr_client.recognize_audio_file(temp_file_path)
            lang_disp = LANGUAGE_DISPLAY.get(language, language)
            accent_disp = ACCENT_DISPLAY.get(accent, accent)
            if result['success']:
                return APIResponse.success(
                    msg="语音识别成功",
                    data={
                        "text": result['text'],
                        "language": lang_disp,
                        "accent": accent_disp,
                        "audio_format": audio_format,
                        "audio_duration": round(audio_duration, 1),
                        "recognition_method": "xunfei_official_websocket",
                        "audio_saved_path": permanent_path
                    }
                )
            else:
                return APIResponse.fail(
                    msg=f"语音识别失败: {result['error']}", 
                    code="4005"
                )
                
        except Exception as e:
            return APIResponse.fail(msg=f"语音识别异常: {str(e)}", code="4006")
        finally:
            # 清理临时文件
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                except Exception as e:
                    print(f"清理临时文件失败: {e}")

class SpeechRecognitionFileView(APIView):
    """文件上传语音识别接口"""
    
    @log_api_access(api_name="文件上传语音识别", sensitive_fields=['password', 'token'])
    def post(self, request):
        """文件上传语音识别"""
        temp_file_path = None
        
        try:
            # 检查文件上传
            if 'audio_file' not in request.FILES:
                return APIResponse.fail(msg="请上传音频文件", code="4001")
            
            audio_file = request.FILES['audio_file']
            file_size = audio_file.size
            file_extension = audio_file.name.split('.')[-1].lower()
            
            # 验证文件格式
            if file_extension not in ['wav', 'mp3', 'm4a', 'amr', 'pcm']:
                return APIResponse.fail(msg=f"不支持的音频格式: {file_extension}", code="4002")
            
            # 验证文件大小（最大50MB）
            max_size = 50 * 1024 * 1024
            if file_size > max_size:
                return APIResponse.fail(msg=f"文件大小超过限制: {file_size} > {max_size}", code="4003")
            
            # 保存到临时文件
            temp_file_path = tempfile.mktemp(suffix=f'.{file_extension}')
            with open(temp_file_path, 'wb') as f:
                for chunk in audio_file.chunks():
                    f.write(chunk)
            
            try:
                # 创建语音识别客户端
                asr_client = create_xunfei_speech_recognition()
                
                # 执行语音识别
                result = asr_client.recognize_audio_file(temp_file_path)
                
                if result['success']:
                    return APIResponse.success(
                        msg="语音识别成功",
                        data={
                            "text": result['text'],
                            "language": request.data.get('language', 'zh_cn'),
                            "accent": request.data.get('accent', 'mandarin'),
                            "audio_format": file_extension,
                            "file_size": file_size,
                            "recognition_method": "xunfei_official_websocket"
                        }
                    )
                else:
                    return APIResponse.fail(
                        msg=f"语音识别失败: {result['error']}", 
                        code="4005"
                    )
                    
            finally:
                # 清理临时文件
                if os.path.exists(temp_file_path):
                    try:
                        os.unlink(temp_file_path)
                    except Exception as e:
                        print(f"清理临时文件失败: {e}")
            
        except Exception as e:
            return APIResponse.fail(msg=f"文件上传语音识别异常: {str(e)}", code="4007")

class SpeechRecognitionInfoView(APIView):
    """语音识别信息接口"""
    
    @log_api_access(api_name="语音识别信息查询")
    def get(self, request):
        """获取支持的音频格式、语言等信息"""
        return APIResponse.success(
            msg="获取语音识别信息成功",
            data={
                "supported_formats": {
                    "wav": "WAV格式（推荐，16kHz单声道）",
                    "mp3": "MP3格式（16kHz单声道）",
                    "pcm": "PCM原始音频（16kHz单声道）"
                },
                "supported_languages": SUPPORTED_LANGUAGES,
                "audio_requirements": {
                    "sample_rate": "16kHz（推荐）或8kHz",
                    "bit_depth": "16bit",
                    "channels": "单声道",
                    "max_duration": "60秒",
                    "max_file_size": "50MB",
                    "protocol": "WebSocket (WSS) - 官方接口"
                },
                "api_endpoints": {
                    "recognition": "/api/speech-recognition/",
                    "file_upload": "/api/speech-recognition-file/",
                    "info": "/api/speech-recognition-info/"
                },
                "recognition_method": "xunfei_official_websocket",
                "provider": "科大讯飞开放平台"
            }
        )

class APIAccessLogView(APIView):
    """API访问记录查询接口"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    @log_api_access(api_name="API访问记录查询")
    def get(self, request):
        """查询API访问记录"""
        try:
            # 获取查询参数
            page = int(request.GET.get('page', 1))
            page_size = int(request.GET.get('page_size', 20))
            api_name = request.GET.get('api_name', '')
            start_date = request.GET.get('start_date', '')
            end_date = request.GET.get('end_date', '')
            is_success = request.GET.get('is_success', '')
            
            # 构建查询条件
            queryset = APIAccessLog.objects.filter(user=request.user)
            
            if api_name:
                queryset = queryset.filter(api_name__icontains=api_name)
            
            if start_date:
                queryset = queryset.filter(created_at__date__gte=start_date)
            
            if end_date:
                queryset = queryset.filter(created_at__date__lte=end_date)
            
            if is_success in ['true', 'false']:
                queryset = queryset.filter(is_success=(is_success == 'true'))
            
            # 分页
            total_count = queryset.count()
            start_index = (page - 1) * page_size
            end_index = start_index + page_size
            logs = queryset[start_index:end_index]
            
            # 统计数据
            stats = {
                'total_requests': total_count,
                'successful_requests': queryset.filter(is_success=True).count(),
                'failed_requests': queryset.filter(is_success=False).count(),
                'avg_execution_time': queryset.aggregate(avg_time=Avg('execution_time'))['avg_time'] or 0,
                'total_request_size': queryset.aggregate(total_size=Sum('request_size'))['total_size'] or 0,
            }
            
            # 格式化数据
            log_data = []
            for log in logs:
                log_data.append({
                    'id': log.id,
                    'api_name': log.api_name,
                    'api_path': log.api_path,
                    'http_method': log.http_method,
                    'ip_address': log.ip_address,
                    'is_success': log.is_success,
                    'execution_time': log.execution_time,
                    'request_size_kb': log.request_size_kb,
                    'response_size_kb': log.response_size_kb,
                    'created_at': log.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'error_message': log.error_message
                })
            
            return APIResponse.success(
                msg="查询成功",
                data={
                    'logs': log_data,
                    'pagination': {
                        'page': page,
                        'page_size': page_size,
                        'total_count': total_count,
                        'total_pages': (total_count + page_size - 1) // page_size
                    },
                    'statistics': stats
                }
            )
            
        except Exception as e:
            return APIResponse.fail(msg=f"查询失败: {str(e)}", code="5001")

class APIUsageStatisticsView(APIView):
    """API使用统计查询接口"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    @log_api_access(api_name="API使用统计查询")
    def get(self, request):
        """查询API使用统计"""
        try:
            # 获取查询参数
            start_date = request.GET.get('start_date', '')
            end_date = request.GET.get('end_date', '')
            api_name = request.GET.get('api_name', '')
            
            # 构建查询条件
            queryset = APIUsageStatistics.objects.filter(user=request.user)
            
            if start_date:
                queryset = queryset.filter(date__gte=start_date)
            
            if end_date:
                queryset = queryset.filter(date__lte=end_date)
            
            if api_name:
                queryset = queryset.filter(api_name__icontains=api_name)
            
            # 获取统计数据
            stats = queryset.order_by('-date')
            
            # 格式化数据
            stats_data = []
            for stat in stats:
                stats_data.append({
                    'api_name': stat.api_name,
                    'date': stat.date.strftime('%Y-%m-%d'),
                    'total_requests': stat.total_requests,
                    'successful_requests': stat.successful_requests,
                    'failed_requests': stat.failed_requests,
                    'success_rate': stat.success_rate,
                    'avg_execution_time': stat.avg_execution_time,
                    'total_request_size_mb': round(stat.total_request_size / (1024 * 1024), 2),
                    'total_response_size_mb': round(stat.total_response_size / (1024 * 1024), 2)
                })
            
            # 汇总统计
            total_stats = {
                'total_requests': sum(s.total_requests for s in stats),
                'successful_requests': sum(s.successful_requests for s in stats),
                'failed_requests': sum(s.failed_requests for s in stats),
                'avg_execution_time': stats.aggregate(avg_time=Avg('avg_execution_time'))['avg_time'] or 0,
                'total_request_size_mb': round(sum(s.total_request_size for s in stats) / (1024 * 1024), 2),
                'total_response_size_mb': round(sum(s.total_response_size for s in stats) / (1024 * 1024), 2)
            }
            
            if total_stats['total_requests'] > 0:
                total_stats['overall_success_rate'] = round(
                    total_stats['successful_requests'] / total_stats['total_requests'] * 100, 2
                )
            else:
                total_stats['overall_success_rate'] = 0
            
            return APIResponse.success(
                msg="查询成功",
                data={
                    'statistics': stats_data,
                    'summary': total_stats
                }
            )
            
        except Exception as e:
            return APIResponse.fail(msg=f"查询失败: {str(e)}", code="5002")

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
                    "delete": "/api/file-upload-delete/"
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
            
            # 分页
            total_count = queryset.count()
            start_index = (page - 1) * page_size
            end_index = start_index + page_size
            files = queryset[start_index:end_index]
            
            # 格式化数据
            file_data = []
            for file_record in files:
                file_data.append({
                    'id': file_record.id,
                    'original_filename': file_record.original_filename,
                    'file_size': file_record.file_size,
                    'file_size_mb': file_record.file_size_mb,
                    'file_type': file_record.file_type,
                    'file_extension': file_record.file_extension,
                    'oss_url': file_record.oss_url,
                    'cdn_url': file_record.cdn_url,
                    'upload_status': file_record.upload_status,
                    'upload_time': file_record.upload_time,
                    'created_at': file_record.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'is_image': file_record.is_image,
                    'is_video': file_record.is_video,
                    'is_audio': file_record.is_audio,
                    'is_document': file_record.is_document
                })
            
            return APIResponse.success(
                msg="查询成功",
                data={
                    'files': file_data,
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

