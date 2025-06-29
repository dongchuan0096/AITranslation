import os
import time
import hashlib
import mimetypes
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
import oss2
from django.conf import settings
from .oss_config import (
    OSS_CONFIG, CDN_CONFIG, UPLOAD_CONFIG, 
    SECURITY_CONFIG, PERFORMANCE_CONFIG, 
    ACCESS_CONTROL_CONFIG
)

class OSSUploader:
    """阿里云OSS文件上传工具类"""
    
    def __init__(self):
        """初始化OSS客户端"""
        self.access_key_id = OSS_CONFIG['ACCESS_KEY_ID']
        self.access_key_secret = OSS_CONFIG['ACCESS_KEY_SECRET']
        self.endpoint = OSS_CONFIG['ENDPOINT']
        self.bucket_name = OSS_CONFIG['BUCKET_NAME']
        self.region = OSS_CONFIG['REGION']
        
        # 初始化OSS客户端
        self.auth = oss2.Auth(self.access_key_id, self.access_key_secret)
        self.bucket = oss2.Bucket(self.auth, self.endpoint, self.bucket_name)
        
        # 配置信息
        self.max_file_size = UPLOAD_CONFIG['MAX_FILE_SIZE']
        self.allowed_extensions = UPLOAD_CONFIG['ALLOWED_EXTENSIONS']
        self.allowed_mime_types = UPLOAD_CONFIG['ALLOWED_MIME_TYPES']
        self.upload_paths = UPLOAD_CONFIG['UPLOAD_PATH']
        self.file_name_pattern = UPLOAD_CONFIG['FILE_NAME_PATTERN']
        
    def validate_file(self, file_obj, original_filename: str) -> Tuple[bool, str]:
        """
        验证文件
        
        Args:
            file_obj: 文件对象
            original_filename: 原始文件名
            
        Returns:
            (是否有效, 错误信息)
        """
        try:
            # 检查文件大小
            if SECURITY_CONFIG['ENABLE_SIZE_LIMIT']:
                file_obj.seek(0, os.SEEK_END)
                file_size = file_obj.tell()
                file_obj.seek(0)
                
                if file_size > self.max_file_size:
                    return False, f"文件大小超过限制：{file_size} > {self.max_file_size}"
            
            # 检查文件扩展名
            if SECURITY_CONFIG['ENABLE_FILE_TYPE_CHECK']:
                file_extension = os.path.splitext(original_filename)[1].lower()
                allowed_extensions = []
                for extensions in self.allowed_extensions.values():
                    allowed_extensions.extend(extensions)
                
                if file_extension not in allowed_extensions:
                    return False, f"不支持的文件类型：{file_extension}"
            
            # 检查MIME类型
            content_type, _ = mimetypes.guess_type(original_filename)
            if content_type and content_type not in self.allowed_mime_types:
                return False, f"不支持的内容类型：{content_type}"
            
            return True, ""
            
        except Exception as e:
            return False, f"文件验证失败：{str(e)}"
    
    def generate_file_path(self, original_filename: str, file_type: str = 'other') -> str:
        """
        生成文件存储路径
        
        Args:
            original_filename: 原始文件名
            file_type: 文件类型
            
        Returns:
            文件存储路径
        """
        # 获取当前时间
        now = datetime.now()
        year = str(now.year)
        month = str(now.month).zfill(2)
        day = str(now.day).zfill(2)
        
        # 获取文件扩展名
        file_extension = os.path.splitext(original_filename)[1].lower()
        
        # 生成基础路径
        base_path = self.upload_paths.get(file_type, self.upload_paths['other'])
        base_path = base_path.format(year=year, month=month, day=day)
        
        # 生成文件名
        timestamp = str(int(time.time()))
        random_str = str(uuid.uuid4())[:8]
        safe_filename = self._sanitize_filename(original_filename)
        
        filename = self.file_name_pattern.format(
            timestamp=timestamp,
            random=random_str,
            original_name=safe_filename
        )
        
        return os.path.join(base_path, filename).replace('\\', '/')
    
    def _sanitize_filename(self, filename: str) -> str:
        """清理文件名，移除特殊字符"""
        # 移除路径分隔符和特殊字符
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename
    
    def calculate_md5(self, file_obj) -> str:
        """计算文件MD5值"""
        md5_hash = hashlib.md5()
        file_obj.seek(0)
        
        chunk_size = 8192
        while True:
            chunk = file_obj.read(chunk_size)
            if not chunk:
                break
            md5_hash.update(chunk)
        
        file_obj.seek(0)
        return md5_hash.hexdigest()
    
    def upload_file(self, file_obj, original_filename: str, user=None) -> Dict[str, Any]:
        """
        上传文件到OSS
        
        Args:
            file_obj: 文件对象
            original_filename: 原始文件名
            user: 用户对象（可选）
            
        Returns:
            上传结果字典
        """
        start_time = time.time()
        
        try:
            # 验证文件
            is_valid, error_msg = self.validate_file(file_obj, original_filename)
            if not is_valid:
                return {
                    'success': False,
                    'error': error_msg,
                    'upload_time': time.time() - start_time
                }
            
            # 确定文件类型
            file_extension = os.path.splitext(original_filename)[1].lower()
            file_type = 'other'
            for type_name, extensions in self.allowed_extensions.items():
                if file_extension in extensions:
                    file_type = type_name
                    break
            
            # 生成存储路径
            oss_key = self.generate_file_path(original_filename, file_type)
            
            # 获取文件大小和内容类型
            file_obj.seek(0, os.SEEK_END)
            file_size = file_obj.tell()
            file_obj.seek(0)
            
            content_type, _ = mimetypes.guess_type(original_filename)
            if not content_type:
                content_type = 'application/octet-stream'
            
            # 计算MD5（可选）
            md5_hash = None
            if SECURITY_CONFIG['ENABLE_MD5_CHECK']:
                md5_hash = self.calculate_md5(file_obj)
            
            # 上传到OSS
            headers = {
                'Content-Type': content_type,
            }
            
            if md5_hash:
                headers['Content-MD5'] = md5_hash
            
            # 设置访问权限
            if ACCESS_CONTROL_CONFIG['DEFAULT_ACL'] != 'private':
                headers['x-oss-object-acl'] = ACCESS_CONTROL_CONFIG['DEFAULT_ACL']
            
            # 执行上传
            result = self.bucket.put_object(oss_key, file_obj, headers=headers)
            
            # 生成访问URL
            oss_url = f"https://{self.bucket_name}.{self.endpoint.replace('https://', '')}/{oss_key}"
            
            # 生成CDN URL（如果启用）
            cdn_url = None
            if CDN_CONFIG['ENABLED']:
                cdn_url = f"{CDN_CONFIG['DOMAIN']}/{oss_key}"
            
            upload_time = time.time() - start_time
            
            # 保存到数据库
            from apps.api.models import FileUploadRecord
            
            file_record = FileUploadRecord.objects.create(
                user=user,
                original_filename=original_filename,
                file_size=file_size,
                file_type=content_type,
                file_extension=file_extension,
                oss_bucket=self.bucket_name,
                oss_key=oss_key,
                oss_url=oss_url,
                cdn_url=cdn_url,
                upload_status='success',
                upload_time=upload_time,
                content_type=content_type,
                md5_hash=md5_hash
            )
            
            return {
                'success': True,
                'file_record_id': file_record.id,
                'original_filename': original_filename,
                'file_size': file_size,
                'file_type': content_type,
                'oss_key': oss_key,
                'oss_url': oss_url,
                'cdn_url': cdn_url,
                'upload_time': upload_time,
                'md5_hash': md5_hash
            }
            
        except Exception as e:
            upload_time = time.time() - start_time
            error_msg = f"文件上传失败：{str(e)}"
            
            # 记录错误到数据库
            try:
                from apps.api.models import FileUploadRecord
                FileUploadRecord.objects.create(
                    user=user,
                    original_filename=original_filename,
                    file_size=0,
                    file_type='unknown',
                    file_extension='',
                    oss_bucket=self.bucket_name,
                    oss_key='',
                    oss_url='',
                    upload_status='failed',
                    upload_time=upload_time,
                    error_message=error_msg
                )
            except:
                pass
            
            return {
                'success': False,
                'error': error_msg,
                'upload_time': upload_time
            }
    
    def delete_file(self, oss_key: str) -> Dict[str, Any]:
        """
        删除OSS文件
        
        Args:
            oss_key: OSS对象键
            
        Returns:
            删除结果
        """
        try:
            self.bucket.delete_object(oss_key)
            return {'success': True, 'message': '文件删除成功'}
        except Exception as e:
            return {'success': False, 'error': f'文件删除失败：{str(e)}'}
    
    def get_signed_url(self, oss_key: str, expire: int = None) -> str:
        """
        获取签名URL
        
        Args:
            oss_key: OSS对象键
            expire: 过期时间（秒）
            
        Returns:
            签名URL
        """
        if not expire:
            expire = ACCESS_CONTROL_CONFIG['SIGNED_URL_EXPIRE']
        
        try:
            url = self.bucket.sign_url('GET', oss_key, expire)
            return url
        except Exception as e:
            return f"签名URL生成失败：{str(e)}"
    
    def get_file_info(self, oss_key: str) -> Dict[str, Any]:
        """
        获取文件信息
        
        Args:
            oss_key: OSS对象键
            
        Returns:
            文件信息
        """
        try:
            info = self.bucket.head_object(oss_key)
            return {
                'success': True,
                'size': info.content_length,
                'content_type': info.content_type,
                'last_modified': info.last_modified,
                'etag': info.etag,
                'content_md5': getattr(info, 'content_md5', None)
            }
        except Exception as e:
            return {'success': False, 'error': f'获取文件信息失败：{str(e)}'}

# 创建全局实例
oss_uploader = OSSUploader() 