import { request } from '../request';

/**
 * 上传PDF文件接口
 *
 * @param formData PDF文件数据
 * @returns 提取的图片数据
 */
export function uploadPdf(formData: FormData) {
  return request({
    url: '/api/upload_pdf',
    method: 'post',
    timeout: 60000,
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
}

/**
 * 清理调试文件接口
 *
 * @returns 清理结果
 */
export function cleanDebugFiles() {
  return request({
    url: '/api/clean_debug_files',
    method: 'post',
    timeout: 30000
  });
}

/**
 * 测试Ollama连接接口
 *
 * @returns 连接状态
 */
export function testOllamaConnection() {
  return request({
    url: '/api/test_ollama_connection',
    method: 'get',
    timeout: 10000
  });
}

/**
 * 测试Sakura连接接口
 *
 * @param forceRefresh 是否强制刷新
 * @returns 连接状态
 */
export function testSakuraConnection(forceRefresh: boolean = false) {
  return request({
    url: '/api/test_sakura_connection',
    method: 'get',
    timeout: 10000,
    params: { force: forceRefresh }
  });
}

/**
 * 测试LAMA修复接口
 *
 * @returns 测试结果
 */
export function testLamaRepair() {
  return request({
    url: '/api/test_lama_repair',
    method: 'get',
    timeout: 30000
  });
}

/**
 * 测试参数解析接口
 *
 * @param data 测试参数
 * @returns 解析结果
 */
export function testParams(data: { use_inpainting: boolean; use_lama: boolean }) {
  return request({
    url: '/api/test_params',
    method: 'post',
    timeout: 10000,
    data
  });
}

/**
 * 测试百度OCR连接接口
 *
 * @param data OCR参数
 * @returns 连接状态
 */
export function testBaiduOcrConnection(data: { api_key: string; secret_key: string }) {
  return request({
    url: '/api/test_baidu_ocr_connection',
    method: 'post',
    timeout: 15000,
    data
  });
}

/**
 * 测试AI视觉OCR接口
 *
 * @param data AI视觉OCR参数
 * @returns 测试结果
 */
export function testAiVisionOcr(data: {
  provider: string;
  api_key: string;
  model_name: string;
  prompt: string;
  custom_ai_vision_base_url: string;
}) {
  return request({
    url: '/api/test_ai_vision_ocr',
    method: 'post',
    timeout: 30000,
    data
  });
}

/**
 * 测试百度翻译接口
 *
 * @param data 翻译参数
 * @returns 测试结果
 */
export function testBaiduTranslate(data: { app_id: string; app_key: string }) {
  return request({
    url: '/api/test_baidu_translate_connection',
    method: 'post',
    timeout: 15000,
    data
  });
}

/**
 * 测试有道翻译接口
 *
 * @param data 翻译参数
 * @returns 测试结果
 */
export function testYoudaoTranslate(data: { appKey: string; appSecret: string }) {
  return request({
    url: '/api/test_youdao_translate',
    method: 'post',
    timeout: 15000,
    data
  });
}

/**
 * 获取字体列表接口
 *
 * @returns 字体列表
 */
export function getFontList() {
  return request({
    url: '/api/get_font_list',
    method: 'get',
    timeout: 10000
  });
}

/**
 * 上传字体文件接口
 *
 * @param formData 字体文件数据
 * @returns 上传结果
 */
export function uploadFont(formData: FormData) {
  return request({
    url: '/api/upload_font',
    method: 'post',
    timeout: 30000,
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
}

/**
 * 批量下载图片接口
 *
 * @param data 下载参数
 * @returns 下载信息
 */
export function downloadAllImages(data: { format: 'zip' | 'pdf' | 'cbz'; images: string[] }) {
  return request({
    url: '/api/download_all_images',
    method: 'post',
    timeout: 120000,
    data
  });
}

/**
 * 下载处理好的文件接口
 *
 * @param fileId 文件ID
 * @param format 文件格式
 * @returns 文件流
 */
export function downloadProcessedFile(fileId: string, format: string) {
  return request({
    url: `/api/download_file/${fileId}`,
    method: 'get',
    timeout: 60000,
    params: { format },
    responseType: 'blob'
  });
}

/**
 * 清理临时文件接口
 *
 * @returns 清理结果
 */
export function cleanTempFiles() {
  return request({
    url: '/api/clean_temp_files',
    method: 'post',
    timeout: 30000
  });
}

/**
 * 检测文本框接口
 *
 * @param data 检测参数
 * @returns 检测结果
 */
export function detectBoxes(data: { image: string; conf_threshold: number }) {
  return request({
    url: '/api/detect_boxes',
    method: 'post',
    timeout: 30000,
    data
  });
}
