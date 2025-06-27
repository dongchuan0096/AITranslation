import { request } from '../request';

/**
 * 文本翻译接口
 *
 * @param data 翻译参数
 * @returns 翻译结果
 */
export function translateSingleText(data: {
  original_text: string;
  target_language: string;
  model_provider: string;
  api_key: string;
  model_name: string;
}) {
  return request({
    url: '/api/translate_single_text/',
    method: 'post',
    data
  });
}

/**
 * 文本翻译（完整参数）接口
 *
 * @param data 翻译参数
 * @returns 翻译结果
 */
export function translateTextFull(data: {
  text: string;
  target_language: string;
  model_provider: string;
  api_key: string;
  model_name: string;
  prompt_content: string;
  use_json_format: boolean;
  custom_base_url: string;
  rpm_limit_translation: number;
}) {
  return request({
    url: '/api/text-translate/',
    method: 'post',
    timeout: 30000,
    data
  });
}


/**
 * 图片翻译接口
 * @param data 翻译参数
 * @returns 翻译结果
 */
export function translateImage(data: {
  image: string;
  target_language: string;
  source_language: string;
  fontSize: number | string;
  autoFontSize: boolean;
  api_key: string;
  model_name: string;
  model_provider: string;
  fontFamily: string;
  textDirection: string;
  prompt_content: string;
  use_textbox_prompt: boolean;
  textbox_prompt_content: string;
  use_inpainting: boolean;
  blend_edges: boolean;
  inpainting_strength: number;
  use_lama: boolean;
  skip_translation: boolean;
  skip_ocr: boolean;
  remove_only: boolean;
  fill_color: string;
  text_color: string;
  rotation_angle: number;
  ocr_engine: string;
  baidu_api_key: string;
  baidu_secret_key: string;
  baidu_version: string;
  ai_vision_provider: string;
  ai_vision_api_key: string;
  ai_vision_model_name: string;
  ai_vision_ocr_prompt: string;
  custom_ai_vision_base_url: string;
  custom_base_url: string;
  use_json_format_translation: boolean;
  use_json_format_ai_vision_ocr: boolean;
  rpm_limit_translation: number;
  rpm_limit_ai_vision_ocr: number;
  enableTextStroke: boolean;
  textStrokeColor: string;
  textStrokeWidth: number;
  bubble_coords: number[][];
}) {
  return request({
    url: '/api/translate_image/',
    method: 'post',
    timeout: 60000,
    data
  });
}

/**
 * 重新渲染图片接口
 * @param data 渲染参数
 * @returns 渲染结果
 */
export function reRenderImage(data: {
  image: string;
  clean_image: string;
  bubble_texts: string[];
  bubble_coords: number[][];
  fontSize: number | string;
  autoFontSize: boolean;
  fontFamily: string;
  textDirection: string;
  use_inpainting: boolean;
  use_lama: boolean;
  blend_edges: boolean;
  inpainting_strength: number;
  is_font_style_change: boolean;
  all_bubble_styles: any[];
  textColor: string;
  rotationAngle: number;
  enableTextStroke: boolean;
  textStrokeColor: string;
  textStrokeWidth: number;
  fill_color: string;
  use_individual_styles: boolean;
}) {
  return request({
    url: '/api/re_render_image/',
    method: 'post',
    timeout: 30000,
    data
  });
}

/**
 * 重新渲染单个气泡接口
 * @param data 单气泡渲染参数
 * @returns 渲染结果
 */
export function reRenderSingleBubble(data: {
  bubble_index: number;
  all_texts: string[];
  fontSize: number | string;
  autoFontSize: boolean;
  fontFamily: string;
  text_direction: string;
  position_offset: { x: number; y: number };
  bubble_coords: number[][];
  image: string;
  clean_image: string;
  use_inpainting: boolean;
  use_lama: boolean;
  is_single_bubble_style: boolean;
  text_color: string;
  rotation_angle: number;
  enableTextStroke: boolean;
  textStrokeColor: string;
  textStrokeWidth: number;
  all_bubble_styles: any[];
  fill_color: string;
}) {
  return request({
    url: '/api/re_render_single_bubble/',
    method: 'post',
    timeout: 30000,
    data
  });
}

/**
 * 应用设置到所有图片接口
 * @param data 设置参数
 * @returns 处理结果
 */
export function applySettingsToAllImages(data: {
  fontSize: number | string;
  autoFontSize: boolean;
  fontFamily: string;
  textDirection: string;
  textColor: string;
  rotationAngle: number;
  enableTextStroke: boolean;
  textStrokeColor: string;
  textStrokeWidth: number;
  all_images: string[];
  all_clean_images: string[];
  all_texts: string[][];
  all_bubble_coords: number[][][];
  use_inpainting: boolean;
  use_lama: boolean;
  fill_color: string;
}) {
  return request({
    url: '/api/apply_settings_to_all_images/',
    method: 'post',
    timeout: 120000,
    data
  });
}
