import { request } from '../request';

/** 创建专门处理 FormData 的请求函数 */
function createFormDataRequest() {
  return {
    ...request,
    async post(url: string, data: FormData, config: any = {}) {
      return request({
        url,
        method: 'post',
        data,
        ...config,
        // 确保不设置 Content-Type，让浏览器自动设置
        headers: {
          ...config.headers,
          // 移除可能存在的 Content-Type
          'Content-Type': undefined
        }
      });
    }
  };
}

const formDataRequest = createFormDataRequest();

/**
 * 语音识别接口（实时录音）
 *
 * @param data 语音识别参数
 * @returns 识别结果
 */
export function speechRecognition(data: { audio: Blob; language?: string; engine_type?: string }) {
  const formData = new FormData();

  // 将音频数据转换为File对象，确保正确的MIME类型
  const audioFile = new File([data.audio], 'recording.wav', { type: 'audio/wav' });
  formData.append('audio_data', audioFile);

  // 添加其他参数
  formData.append('audio_format', 'wav');
  formData.append('language', data.language || 'zh_cn');
  formData.append('engine_type', data.engine_type || 'sms16k');

  return request({
    url: '/api/speech-recognition/',
    method: 'post',
    data: formData,
    timeout: 30000,
    // 不设置Content-Type，让浏览器自动处理multipart边界
    headers: {
      'Content-Type': undefined
    }
  });
}

/**
 * 语音识别接口（文件上传）
 *
 * @param data 语音识别参数
 * @returns 识别结果
 */
export function speechRecognitionFile(data: { audio_file: File; language?: string; engine_type?: string }) {
  const formData = new FormData();
  formData.append('audio_file', data.audio_file, data.audio_file.name);
  formData.append('language', data.language || 'zh_cn');
  formData.append('engine_type', data.engine_type || 'sms16k');

  return formDataRequest.post('/api/speech-recognition-file/', formData, {
    timeout: 60000
  });
}

/**
 * 获取语音识别信息接口
 *
 * @returns 语音识别服务信息
 */
export function getSpeechRecognitionInfo() {
  return request({
    url: '/api/speech-recognition-info/',
    method: 'get',
    timeout: 10000
  });
}

/** 语音识别结果类型定义 */
export interface SpeechRecognitionResult {
  text: string; // 识别出的文字内容
  language: string; // 检测到的语言代码
  confidence?: number; // 识别置信度
  duration?: number; // 音频时长（秒）
  timestamp?: string; // 识别时间戳
}

/** 语音识别服务信息类型定义 */
export interface SpeechRecognitionInfo {
  available_models: string[]; // 可用的识别模型
  supported_languages: string[]; // 支持的语言列表
  max_file_size: number; // 最大文件大小（MB）
  max_duration: number; // 最大音频时长（秒）
  service_status: string; // 服务状态
}
