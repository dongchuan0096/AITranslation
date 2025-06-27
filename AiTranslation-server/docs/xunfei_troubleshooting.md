# 讯飞API问题解决指南

## 问题描述

当前遇到讯飞API错误：`illegal access|no appid info` (错误码: 10105)

## 错误分析

错误码10105表示：
- APP_ID不存在或无效
- API_KEY与APP_ID不匹配
- 应用未激活或未通过审核
- 应用没有语音识别权限
- 应用已过期或被禁用

## 解决步骤

### 1. 检查讯飞开放平台账号

1. 访问 [讯飞开放平台](https://www.xfyun.cn/)
2. 登录您的账号
3. 确认账号已激活

### 2. 检查应用状态

1. 进入 [应用管理](https://console.xfyun.cn/app/myapp)
2. 确认应用已创建
3. 检查应用状态是否为"已激活"
4. 确认应用已通过审核

### 3. 检查API权限

1. 在应用详情页面查看API权限
2. 确认已开通"语音识别"服务
3. 检查服务状态是否正常

### 4. 重新生成API密钥

1. 在应用详情页面找到"API密钥"部分
2. 点击"重新生成"按钮
3. 复制新的API_KEY和API_SECRET

### 5. 更新配置文件

编辑 `apps/utils/xunfei_config.py` 文件：

```python
XUNFEI_CONFIG = {
    'APP_ID': 'your_new_app_id',      # 替换为新的APP_ID
    'API_KEY': 'your_new_api_key',    # 替换为新的API_KEY
    'API_SECRET': 'your_new_secret',  # 替换为新的API_SECRET
}
```

### 6. 测试配置

运行诊断脚本：
```bash
python fix_xunfei_config.py
```

## 临时解决方案

在讯飞API配置问题解决期间，可以使用测试接口：

### 测试接口
- **URL**: `/api/speech-recognition-test/`
- **方法**: POST
- **功能**: 模拟语音识别，用于测试系统功能

### 使用测试接口
```bash
# 文件上传方式
curl -X POST http://localhost:8000/api/speech-recognition-test/ \
  -F "audio_data=@recording.wav" \
  -F "language=zh_cn" \
  -F "engine_type=sms16k"
```

## 常见问题

### Q: 为什么会出现10105错误？
A: 通常是因为API配置不正确或应用权限不足。

### Q: 如何确认API配置正确？
A: 使用诊断脚本 `fix_xunfei_config.py` 进行测试。

### Q: 应用审核需要多长时间？
A: 通常1-3个工作日，具体时间请查看讯飞开放平台通知。

### Q: 可以同时使用多个应用吗？
A: 可以，但每个应用需要独立的API密钥。

## 帮助资源

- [讯飞开放平台](https://www.xfyun.cn/)
- [语音识别API文档](https://www.xfyun.cn/doc/asr/voicedictation/API.html)
- [应用管理](https://console.xfyun.cn/app/myapp)
- [错误码说明](https://www.xfyun.cn/doc/asr/voicedictation/API.html#错误码)

## 联系支持

如果问题仍然存在，请联系：
- 讯飞开放平台客服
- 技术支持邮箱
- 开发者社区

## 注意事项

1. **API密钥安全**: 请妥善保管API密钥，不要泄露给他人
2. **调用限制**: 注意API调用次数限制
3. **网络要求**: 确保网络连接稳定
4. **音频格式**: 使用支持的音频格式（WAV、MP3、M4A、AMR、PCM） 