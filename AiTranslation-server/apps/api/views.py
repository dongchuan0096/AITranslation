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
from apps.api.models import APIAccessLog, APIUsageStatistics
import re
import random
import soundfile as sf
import wave
import contextlib

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
        # 直接将收到的参数转发到本地后端的 /api/spark/text-translate
        spark_url = f"http://{SPARK_API_HOST}/api/text-translate/"
        try:
            resp = requests.post(spark_url, json=request.data, timeout=100)
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
        """通过文件上传进行语音识别"""
        try:
            # 获取上传的音频文件
            audio_file = request.FILES.get('audio_file')
            
            if not audio_file:
                return APIResponse.fail(msg="请上传音频文件", code="4001")
            
            # 检查文件类型
            file_extension = audio_file.name.split('.')[-1].lower()
            if file_extension not in ['wav', 'mp3', 'pcm']:
                return APIResponse.fail(msg=f"不支持的音频格式: {file_extension}，仅支持wav、mp3、pcm", code="4002")
            
            # 检查文件大小
            file_size = audio_file.size
            max_size = 50 * 1024 * 1024  # 50MB
            if file_size > max_size:
                return APIResponse.fail(msg=f"文件过大: {file_size / 1024 / 1024:.1f}MB (最大50MB)", code="4003")
            
            # 保存临时文件
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_extension}')
            for chunk in audio_file.chunks():
                temp_file.write(chunk)
            temp_file.close()
            temp_file_path = temp_file.name
            
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
        """获取当前用户的API访问记录"""
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
                try:
                    start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
                    queryset = queryset.filter(created_at__gte=start_datetime)
                except ValueError:
                    pass
            
            if end_date:
                try:
                    end_datetime = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
                    queryset = queryset.filter(created_at__lt=end_datetime)
                except ValueError:
                    pass
            
            if is_success in ['true', 'false']:
                queryset = queryset.filter(is_success=(is_success == 'true'))
            
            # 分页
            total_count = queryset.count()
            start_index = (page - 1) * page_size
            end_index = start_index + page_size
            
            logs = queryset[start_index:end_index]
            
            # 格式化数据
            log_list = []
            for log in logs:
                log_list.append({
                    'id': log.id,
                    'api_name': log.api_name,
                    'api_path': log.api_path,
                    'http_method': log.http_method,
                    'ip_address': log.ip_address,
                    'execution_time': log.execution_time,
                    'duration_ms': log.duration_ms,
                    'request_size_kb': log.request_size_kb,
                    'response_size_kb': log.response_size_kb,
                    'is_success': log.is_success,
                    'response_status': log.response_status,
                    'error_message': log.error_message,
                    'created_at': log.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                })
            
            return APIResponse.success(
                msg="获取API访问记录成功",
                data={
                    'logs': log_list,
                    'pagination': {
                        'page': page,
                        'page_size': page_size,
                        'total_count': total_count,
                        'total_pages': (total_count + page_size - 1) // page_size
                    }
                }
            )
            
        except Exception as e:
            return APIResponse.fail(msg=f"获取API访问记录失败: {str(e)}", code="4008")

class APIUsageStatisticsView(APIView):
    """API使用统计查询接口"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    @log_api_access(api_name="API使用统计查询")
    def get(self, request):
        """获取当前用户的API使用统计"""
        try:
            # 获取查询参数
            days = int(request.GET.get('days', 7))  # 默认查询最近7天
            api_name = request.GET.get('api_name', '')
            
            # 计算日期范围
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=days-1)
            
            # 构建查询条件
            queryset = APIUsageStatistics.objects.filter(
                user=request.user,
                date__range=[start_date, end_date]
            )
            
            if api_name:
                queryset = queryset.filter(api_name__icontains=api_name)
            
            # 获取统计数据
            statistics = queryset.order_by('date')
            
            # 格式化数据
            stats_list = []
            for stat in statistics:
                stats_list.append({
                    'date': stat.date.strftime('%Y-%m-%d'),
                    'api_name': stat.api_name,
                    'total_requests': stat.total_requests,
                    'successful_requests': stat.successful_requests,
                    'failed_requests': stat.failed_requests,
                    'success_rate': stat.success_rate,
                    'avg_execution_time': stat.avg_execution_time,
                    'total_request_size_mb': round(stat.total_request_size / (1024 * 1024), 2),
                    'total_response_size_mb': round(stat.total_response_size / (1024 * 1024), 2),
                })
            
            # 计算总体统计
            total_stats = queryset.aggregate(
                total_requests=Sum('total_requests'),
                successful_requests=Sum('successful_requests'),
                failed_requests=Sum('failed_requests'),
                total_execution_time=Sum('total_execution_time'),
                total_request_size=Sum('total_request_size'),
                total_response_size=Sum('total_response_size'),
            )
            
            overall_stats = {
                'total_requests': total_stats['total_requests'] or 0,
                'successful_requests': total_stats['successful_requests'] or 0,
                'failed_requests': total_stats['failed_requests'] or 0,
                'overall_success_rate': round(
                    (total_stats['successful_requests'] or 0) / (total_stats['total_requests'] or 1) * 100, 2
                ),
                'avg_execution_time': round(
                    (total_stats['total_execution_time'] or 0) / (total_stats['total_requests'] or 1), 3
                ),
                'total_request_size_mb': round((total_stats['total_request_size'] or 0) / (1024 * 1024), 2),
                'total_response_size_mb': round((total_stats['total_response_size'] or 0) / (1024 * 1024), 2),
            }
            
            return APIResponse.success(
                msg="获取API使用统计成功",
                data={
                    'statistics': stats_list,
                    'overall_stats': overall_stats,
                    'date_range': {
                        'start_date': start_date.strftime('%Y-%m-%d'),
                        'end_date': end_date.strftime('%Y-%m-%d'),
                        'days': days
                    }
                }
            )
            
        except Exception as e:
            return APIResponse.fail(msg=f"获取API使用统计失败: {str(e)}", code="4009")

