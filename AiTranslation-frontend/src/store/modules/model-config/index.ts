import { ref, watch } from 'vue';
import { defineStore } from 'pinia';

const LOCAL_KEY = 'modelConfig';

export interface ModelConfig {
  provider: string;
  apiKey: string;
  model: string;
  prompt: string;

  // 文字设置
  sourceLanguage?: string;
  ocrEngine?: string;
  baiduOcrApiKey?: string;
  baiduOcrSecretKey?: string;
  baiduOcrVersion?: string;
  aiVisionOcrProvider?: string;
  aiVisionOcrBaseUrl?: string;
  aiVisionOcrApiKey?: string;
  aiVisionOcrModelName?: string;
  aiVisionOcrPrompt?: string;
  aiVisionOcrPromptFormat?: string;
  aiVisionOcrRpmLimit?: number;
  fontSize?: number;
  autoFontSize?: boolean;
  textFont?: string;
  layout?: string;
  textColor?: string;
  enableTextStroke?: boolean;
  strokeColor?: string;
  strokeWidth?: number;
  bubbleFillMethod?: string;
  fillColor?: string;
  repairStrength?: number;
  edgeBlending?: boolean;

  // AI模型设置
  translationProvider?: string;
  translationApiKey?: string;
  translationBaseUrl?: string;
  translationModel?: string;
  translationRpmLimit?: number;

  // 提示词设置
  mangaTranslationPrompt?: string;
  promptFormat?: string;
  rememberPrompt?: boolean;
  promptName?: string;
  enableIndependentTextPrompt?: boolean;
  textBoxPrompt?: string;
  rememberTextBoxPrompt?: boolean;
  textBoxPromptName?: string;

  // 高质量翻译模式设置
  highQualityAiProvider?: string;
  highQualityApiKey?: string;
  highQualityModel?: string;
  highQualityBaseUrl?: string;
  batchImageCount?: number;
  sessionResetFrequency?: number;
  highQualityRpmLimit?: number;
  disableThinking?: boolean;
  forceJsonOutput?: boolean;
  translationPrompt?: string;

  // 气泡编辑设置
  bubbleFontSize?: number;
  bubbleAutoFontSize?: boolean;
  bubbleTextFont?: string;
  bubbleLayout?: string;
  bubbleTextColor?: string;
  bubbleRotationAngle?: number;
  bubbleFillColor?: string;
  bubbleEnableTextStroke?: boolean;
  bubbleStrokeColor?: string;
  bubbleStrokeWidth?: number;

  // 图片控制设置
  imageSize?: number;
  downloadFormat?: string;

  // 其他设置
  positionOffsetX?: number;
  positionOffsetY?: number;
}

function getDefaultConfig(): ModelConfig {
  const local = localStorage.getItem(LOCAL_KEY);
  if (local) {
    try {
      return JSON.parse(local);
    } catch {
      // ignore
    }
  }
  return {
    provider: '',
    apiKey: '',
    model: '',
    prompt: ''
  };
}

export const useModelConfigStore = defineStore('model-config', () => {
  const config = ref<ModelConfig>(getDefaultConfig());

  watch(
    config,
    val => {
      localStorage.setItem(LOCAL_KEY, JSON.stringify(val));
    },
    { deep: true }
  );

  function setConfig(newConfig: Partial<ModelConfig>) {
    config.value = { ...config.value, ...newConfig };
  }

  return {
    config,
    setConfig
  };
});
