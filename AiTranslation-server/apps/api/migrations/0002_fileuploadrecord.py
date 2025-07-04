# Generated by Django 4.2.14 on 2025-06-28 09:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("api", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="FileUploadRecord",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "original_filename",
                    models.CharField(max_length=255, verbose_name="原始文件名"),
                ),
                ("file_size", models.BigIntegerField(verbose_name="文件大小(字节)")),
                ("file_type", models.CharField(max_length=50, verbose_name="文件类型")),
                (
                    "file_extension",
                    models.CharField(max_length=20, verbose_name="文件扩展名"),
                ),
                (
                    "oss_bucket",
                    models.CharField(max_length=100, verbose_name="OSS存储桶"),
                ),
                ("oss_key", models.CharField(max_length=500, verbose_name="OSS对象键")),
                (
                    "oss_url",
                    models.URLField(max_length=1000, verbose_name="OSS访问URL"),
                ),
                (
                    "cdn_url",
                    models.URLField(
                        blank=True,
                        max_length=1000,
                        null=True,
                        verbose_name="CDN加速URL",
                    ),
                ),
                (
                    "upload_status",
                    models.CharField(
                        default="success", max_length=20, verbose_name="上传状态"
                    ),
                ),
                (
                    "upload_time",
                    models.FloatField(
                        blank=True, null=True, verbose_name="上传耗时(秒)"
                    ),
                ),
                (
                    "error_message",
                    models.TextField(blank=True, null=True, verbose_name="错误信息"),
                ),
                (
                    "content_type",
                    models.CharField(
                        blank=True, max_length=100, null=True, verbose_name="内容类型"
                    ),
                ),
                (
                    "md5_hash",
                    models.CharField(
                        blank=True, max_length=32, null=True, verbose_name="MD5哈希值"
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="创建时间"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="更新时间"),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="用户",
                    ),
                ),
            ],
            options={
                "verbose_name": "文件上传记录",
                "verbose_name_plural": "文件上传记录",
                "db_table": "file_upload_record",
                "ordering": ["-created_at"],
                "indexes": [
                    models.Index(
                        fields=["user", "created_at"],
                        name="file_upload_user_id_9da94f_idx",
                    ),
                    models.Index(
                        fields=["file_type", "created_at"],
                        name="file_upload_file_ty_11470c_idx",
                    ),
                    models.Index(
                        fields=["upload_status", "created_at"],
                        name="file_upload_upload__618188_idx",
                    ),
                    models.Index(
                        fields=["oss_key"], name="file_upload_oss_key_d5bd76_idx"
                    ),
                ],
            },
        ),
    ]
