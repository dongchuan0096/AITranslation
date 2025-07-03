<script setup lang="ts">
import { onMounted, ref, watch } from 'vue';
import { useMessage } from 'naive-ui';
import { useModelConfigStore } from '@/store/modules/model-config';

const message = useMessage();

// 折叠状态
const collapsedKeys = ref<string[]>([]);

// 新增配置选项
const sourceLanguageOptions = ref([
  { label: '日语', value: 'ja' },
  { label: '英语', value: 'en' },
  { label: '韩语', value: 'ko' },
  { label: '繁体中文', value: 'zh-tw' },
  { label: '法文', value: 'fr' },
  { label: '德文', value: 'de' },
  { label: '俄文', value: 'ru' },
  { label: '意大利文', value: 'it' },
  { label: '西班牙文', value: 'es' }
]);

const ocrEngineOptions = ref([
  { label: '自动选择', value: 'auto' },
  { label: 'MangaOCR', value: 'manga_ocr' },
  { label: 'PaddleOCR', value: 'paddle_ocr' },
  { label: '百度OCR', value: 'baidu_ocr' },
  { label: 'AI视觉OCR', value: 'ai_vision_ocr' }
]);

const baiduOcrVersionOptions = ref([
  { label: '标准版', value: 'standard' },
  { label: '高精度版', value: 'high_accuracy' }
]);

const aiVisionOcrProviderOptions = ref([
  { label: 'SiliconFlow', value: 'siliconflow' },
  { label: '火山引擎', value: 'volcengine' },
  { label: 'Google Gemini', value: 'google_gemini' },
  { label: '自定义OpenAI兼容视觉服务', value: 'custom_openai' }
]);

const translationProviderOptions = ref([
  { label: 'SiliconFlow', value: 'siliconflow' },
  { label: 'DeepSeek', value: 'deepseek' },
  { label: '火山引擎', value: 'volcengine' },
  { label: '彩云小译', value: 'caiyun' },
  { label: '百度翻译', value: 'baidu' },
  { label: '有道翻译', value: 'youdao' },
  { label: 'Google Gemini', value: 'google_gemini' },
  { label: 'Ollama', value: 'ollama' },
  { label: 'Sakura', value: 'sakura' },
  { label: '自定义OpenAI兼容服务', value: 'custom_openai' }
]);

const promptFormatOptions = ref([
  { label: '普通提示词', value: 'normal' },
  { label: 'JSON提示词', value: 'json' }
]);

const layoutOptions = ref([
  { label: '竖向排版', value: 'vertical' },
  { label: '横向排版', value: 'horizontal' }
]);

const bubbleFillOptions = ref([
  { label: '纯色填充', value: 'solid' },
  { label: 'LAMA修复', value: 'lama' }
]);

const downloadFormatOptions = ref([
  { label: 'ZIP压缩包', value: 'zip' },
  { label: 'PDF文件', value: 'pdf' },
  { label: 'CBZ漫画格式', value: 'cbz' }
]);

const aiProviderOptions = ref([
  { label: 'SiliconFlow', value: 'siliconflow' },
  { label: 'DeepSeek', value: 'deepseek' },
  { label: '火山引擎', value: 'volcengine' },
  { label: 'Google Gemini', value: 'google_gemini' },
  { label: '自定义OpenAI兼容服务', value: 'custom_openai' }
]);

const fontList = [
  'msyh.ttc',
  'msyhbd.ttc',
  'NotoSans-Medium.ttf',
  'simfang.ttf',
  'simhei.ttf',
  'simkai.ttf',
  'SIMLI.TTF',
  'SIMYOU.TTF',
  'STCAIYUN.TTF',
  'STFANGSO.TTF',
  'STHUPO.TTF',
  'STKAITI.TTF',
  'STLITI.TTF',
  'STSONG.TTF',
  'STXIHEI.TTF',
  'STXINGKA.TTF',
  'STXINWEI.TTF',
  'STZHONGS.TTF'
];
const fontOptions = fontList.map(f => ({ label: f, value: f }));

const modelConfigStore = useModelConfigStore();

// 默认翻译提示词
const DEFAULT_TRANSLATION_PROMPT = `你是一个语言识别与翻译助手。请完成以下两件事：（1）判断我提供的原文属于哪种语言，输出该语言的 ISO 639-1 两位语言代码（如 zh 表示中文，en 表示英文，ja 表示日文；（2）将该段原文翻译为我指定的目标语言，翻译时请尽量保持含义准确、语言自然，并控制在不超过原文长度的范围内。请按以下格式输出："detected": "<原文语言代码>","translation": "<翻译后的文本>"`;

const form = ref({
  provider: modelConfigStore.config.provider || '',
  providerInput: false,
  apiKey: modelConfigStore.config.apiKey || '',
  model: modelConfigStore.config.model || '',
  modelInput: false,
  prompt: modelConfigStore.config.prompt || '',

  // 文字设置
  sourceLanguage: modelConfigStore.config.sourceLanguage || 'ja',
  ocrEngine: modelConfigStore.config.ocrEngine || 'auto',
  baiduOcrApiKey: modelConfigStore.config.baiduOcrApiKey || '',
  baiduOcrSecretKey: modelConfigStore.config.baiduOcrSecretKey || '',
  baiduOcrVersion: modelConfigStore.config.baiduOcrVersion || 'standard',
  aiVisionOcrProvider: modelConfigStore.config.aiVisionOcrProvider || 'siliconflow',
  aiVisionOcrBaseUrl: modelConfigStore.config.aiVisionOcrBaseUrl || '',
  aiVisionOcrApiKey: modelConfigStore.config.aiVisionOcrApiKey || '',
  aiVisionOcrModelName: modelConfigStore.config.aiVisionOcrModelName || '',
  aiVisionOcrPrompt: modelConfigStore.config.aiVisionOcrPrompt || '',
  aiVisionOcrPromptFormat: modelConfigStore.config.aiVisionOcrPromptFormat || 'normal',
  aiVisionOcrRpmLimit: modelConfigStore.config.aiVisionOcrRpmLimit || 0,
  fontSize: modelConfigStore.config.fontSize || 16,
  autoFontSize: modelConfigStore.config.autoFontSize !== undefined ? modelConfigStore.config.autoFontSize : true,
  textFont: modelConfigStore.config.textFont || 'msyh.ttc',
  layout: modelConfigStore.config.layout || 'vertical',
  textColor: modelConfigStore.config.textColor || '#000000',
  enableTextStroke:
    modelConfigStore.config.enableTextStroke !== undefined ? modelConfigStore.config.enableTextStroke : false,
  strokeColor: modelConfigStore.config.strokeColor || '#ffffff',
  strokeWidth: modelConfigStore.config.strokeWidth || 2,
  bubbleFillMethod: modelConfigStore.config.bubbleFillMethod || 'solid',
  fillColor: modelConfigStore.config.fillColor || '#ffffff',
  repairStrength: modelConfigStore.config.repairStrength || 50,
  edgeBlending: modelConfigStore.config.edgeBlending !== undefined ? modelConfigStore.config.edgeBlending : true,

  // AI模型设置
  translationProvider: modelConfigStore.config.translationProvider || 'deepseek',
  translationApiKey: modelConfigStore.config.translationApiKey || '',
  translationBaseUrl: modelConfigStore.config.translationBaseUrl || '',
  translationModel: modelConfigStore.config.translationModel || '',
  translationRpmLimit: modelConfigStore.config.translationRpmLimit || 0,

  // 提示词设置
  mangaTranslationPrompt: modelConfigStore.config.mangaTranslationPrompt || DEFAULT_TRANSLATION_PROMPT,
  promptFormat: modelConfigStore.config.promptFormat || 'normal',
  rememberPrompt: modelConfigStore.config.rememberPrompt !== undefined ? modelConfigStore.config.rememberPrompt : false,
  promptName: modelConfigStore.config.promptName || '',
  enableIndependentTextPrompt:
    modelConfigStore.config.enableIndependentTextPrompt !== undefined
      ? modelConfigStore.config.enableIndependentTextPrompt
      : false,
  textBoxPrompt: modelConfigStore.config.textBoxPrompt || '',
  rememberTextBoxPrompt:
    modelConfigStore.config.rememberTextBoxPrompt !== undefined ? modelConfigStore.config.rememberTextBoxPrompt : false,
  textBoxPromptName: modelConfigStore.config.textBoxPromptName || '',

  // 高质量翻译模式设置
  highQualityAiProvider: modelConfigStore.config.highQualityAiProvider || 'deepseek',
  highQualityApiKey: modelConfigStore.config.highQualityApiKey || '',
  highQualityModel: modelConfigStore.config.highQualityModel || '',
  highQualityBaseUrl: modelConfigStore.config.highQualityBaseUrl || '',
  batchImageCount: modelConfigStore.config.batchImageCount || 1,
  sessionResetFrequency: modelConfigStore.config.sessionResetFrequency || 10,
  highQualityRpmLimit: modelConfigStore.config.highQualityRpmLimit || 0,
  disableThinking:
    modelConfigStore.config.disableThinking !== undefined ? modelConfigStore.config.disableThinking : false,
  forceJsonOutput:
    modelConfigStore.config.forceJsonOutput !== undefined ? modelConfigStore.config.forceJsonOutput : false,
  translationPrompt: modelConfigStore.config.translationPrompt || '',

  // 气泡编辑设置
  bubbleFontSize: modelConfigStore.config.bubbleFontSize || 16,
  bubbleAutoFontSize:
    modelConfigStore.config.bubbleAutoFontSize !== undefined ? modelConfigStore.config.bubbleAutoFontSize : true,
  bubbleTextFont: modelConfigStore.config.bubbleTextFont || '',
  bubbleLayout: modelConfigStore.config.bubbleLayout || 'vertical',
  bubbleTextColor: modelConfigStore.config.bubbleTextColor || '#000000',
  bubbleRotationAngle: modelConfigStore.config.bubbleRotationAngle || 0,
  bubbleFillColor: modelConfigStore.config.bubbleFillColor || '#ffffff',
  bubbleEnableTextStroke:
    modelConfigStore.config.bubbleEnableTextStroke !== undefined
      ? modelConfigStore.config.bubbleEnableTextStroke
      : false,
  bubbleStrokeColor: modelConfigStore.config.bubbleStrokeColor || '#ffffff',
  bubbleStrokeWidth: modelConfigStore.config.bubbleStrokeWidth || 2,

  // 图片控制设置
  imageSize: modelConfigStore.config.imageSize || 100,
  downloadFormat: modelConfigStore.config.downloadFormat || 'zip',

  // 其他设置
  positionOffsetX: modelConfigStore.config.positionOffsetX || 0,
  positionOffsetY: modelConfigStore.config.positionOffsetY || 0
});

onMounted(() => {
  // 回显配置
  Object.assign(form.value, modelConfigStore.config);

  // 如果没有设置提示词，使用默认提示词
  if (!form.value.mangaTranslationPrompt) {
    form.value.mangaTranslationPrompt = DEFAULT_TRANSLATION_PROMPT;
  }
});

function handleSave() {
  // 确保 apiKey 和 translationApiKey 保持同步
  const configToSave = {
    ...form.value,
    apiKey: form.value.translationApiKey // 同步到 apiKey 字段
  };

  modelConfigStore.setConfig(configToSave);
  message.success('保存成功！');
}

// 表单变动时自动同步到 store（可选）
watch(
  () => form.value,
  () => {
    modelConfigStore.setConfig({
      ...form.value
    });
  },
  { deep: true }
);
</script>

<template>
  <div class="config-container">
    <NCollapse v-model:expanded-names="collapsedKeys" accordion>
      <!-- 文字设置 -->
      <NCollapseItem name="text-settings" title="文字设置">
        <NForm :model="form" label-width="140">
          <!-- <NFormItem label="源语言">
            <NSelect v-model:value="form.sourceLanguage" :options="sourceLanguageOptions" />
          </NFormItem>
          <NFormItem label="OCR引擎">
            <NSelect v-model:value="form.ocrEngine" :options="ocrEngineOptions" />
          </NFormItem>
          <NFormItem label="百度OCR API Key">
            <NInput v-model:value="form.baiduOcrApiKey" placeholder="请输入百度OCR API Key" />
          </NFormItem>
          <NFormItem label="百度OCR Secret Key">
            <NInput v-model:value="form.baiduOcrSecretKey" placeholder="请输入百度OCR Secret Key" />
          </NFormItem>
          <NFormItem label="百度OCR识别版本">
            <NSelect v-model:value="form.baiduOcrVersion" :options="baiduOcrVersionOptions" />
          </NFormItem>
          <NFormItem label="AI视觉OCR服务商">
            <NSelect v-model:value="form.aiVisionOcrProvider" :options="aiVisionOcrProviderOptions" />
          </NFormItem>
          <NFormItem label="AI视觉OCR Base URL">
            <NInput v-model:value="form.aiVisionOcrBaseUrl" placeholder="请输入Base URL" />
          </NFormItem>
          <NFormItem label="AI视觉OCR API Key">
            <NInput v-model:value="form.aiVisionOcrApiKey" placeholder="请输入API Key" />
          </NFormItem>
          <NFormItem label="AI视觉OCR模型名称">
            <NInput v-model:value="form.aiVisionOcrModelName" placeholder="请输入模型名称" />
          </NFormItem>
          <NFormItem label="AI视觉OCR提示词">
            <NInput
              v-model:value="form.aiVisionOcrPrompt"
              type="textarea"
              placeholder="请输入提示词"
              :autosize="{ minRows: 2, maxRows: 8 }"
            />
          </NFormItem>
          <NFormItem label="AI视觉OCR提示词格式">
            <NSelect v-model:value="form.aiVisionOcrPromptFormat" :options="promptFormatOptions" />
          </NFormItem>
          <NFormItem label="AI视觉OCR rpm限制">
            <NInputNumber v-model:value="form.aiVisionOcrRpmLimit" placeholder="0表示无限制" />
          </NFormItem> -->
          <NFormItem label="字号大小">
            <NInputNumber v-model:value="form.fontSize" :min="8" :max="72" />
          </NFormItem>
          <!-- <NFormItem label="自动字号">
            <NSwitch v-model:value="form.autoFontSize" />
          </NFormItem> -->
          <NFormItem label="文本字体">
            <NSelect v-model:value="form.textFont" :options="fontOptions" placeholder="选择字体" />
          </NFormItem>
          <NFormItem label="排版设置">
            <NSelect v-model:value="form.layout" :options="layoutOptions" />
          </NFormItem>
          <NFormItem label="文字颜色">
            <NColorPicker v-model:value="form.textColor" />
          </NFormItem>
          <NFormItem label="启用文本描边">
            <NSwitch v-model:value="form.enableTextStroke" />
          </NFormItem>
          <NFormItem label="描边颜色">
            <NColorPicker v-model:value="form.strokeColor" />
          </NFormItem>
          <NFormItem label="描边宽度">
            <NInputNumber v-model:value="form.strokeWidth" :min="1" :max="10" />
          </NFormItem>
          <!-- <NFormItem label="气泡填充方式">
            <NSelect v-model:value="form.bubbleFillMethod" :options="bubbleFillOptions" />
          </NFormItem> -->
          <NFormItem label="填充颜色">
            <NColorPicker v-model:value="form.fillColor" />
          </NFormItem>
          <!-- <NFormItem label="修复强度">
            <NSlider v-model:value="form.repairStrength" :min="0" :max="100" />
          </NFormItem> -->
          <!-- <NFormItem label="边缘融合">
            <NSwitch v-model:value="form.edgeBlending" />
          </NFormItem> -->
        </NForm>
      </NCollapseItem>

      <!-- AI模型设置 -->
      <NCollapseItem name="ai-model-settings" title="AI模型设置">
        <NForm :model="form" label-width="140">
          <NFormItem label="翻译服务商">
            <NSelect v-model:value="form.translationProvider" :options="translationProviderOptions" />
          </NFormItem>
          <NFormItem label="API Key">
            <NInput v-model:value="form.translationApiKey" placeholder="请输入API Key" />
          </NFormItem>
          <NFormItem label="Base URL">
            <NInput v-model:value="form.translationBaseUrl" placeholder="请输入Base URL" />
          </NFormItem>
          <NFormItem label="大模型型号">
            <NInput v-model:value="form.translationModel" placeholder="请输入模型型号" />
          </NFormItem>
          <NFormItem label="翻译服务rpm限制">
            <NInputNumber v-model:value="form.translationRpmLimit" placeholder="0表示无限制" />
          </NFormItem>
        </NForm>
      </NCollapseItem>

      <!-- 提示词设置
      <NCollapseItem name="prompt-settings" title="提示词设置">
        <NForm :model="form" label-width="140">
          <NFormItem label="漫画翻译提示词">
            <NInput
              v-model:value="form.mangaTranslationPrompt"
              type="textarea"
              placeholder="请输入翻译提示词"
              :autosize="{ minRows: 3, maxRows: 10 }"
            />
          </NFormItem>
          <NFormItem label="提示词格式">
            <NSelect v-model:value="form.promptFormat" :options="promptFormatOptions" />
          </NFormItem>
          <NFormItem label="记住提示词">
            <NSwitch v-model:value="form.rememberPrompt" />
          </NFormItem>
          <NFormItem label="提示词名称">
            <NInput v-model:value="form.promptName" placeholder="请输入提示词名称" />
          </NFormItem>
          <NFormItem label="启用独立文本框提示词">
            <NSwitch v-model:value="form.enableIndependentTextPrompt" />
          </NFormItem>
          <NFormItem label="文本框提示词">
            <NInput
              v-model:value="form.textBoxPrompt"
              type="textarea"
              placeholder="请输入文本框提示词"
              :autosize="{ minRows: 2, maxRows: 8 }"
            />
          </NFormItem>
          <NFormItem label="记住文本框提示词">
            <NSwitch v-model:value="form.rememberTextBoxPrompt" />
          </NFormItem>
          <NFormItem label="文本框提示词名称">
            <NInput v-model:value="form.textBoxPromptName" placeholder="请输入文本框提示词名称" />
          </NFormItem>
        </NForm>
      </NCollapseItem> -->

      <!-- 高质量翻译模式设置
      <NCollapseItem name="high-quality-settings" title="高质量翻译模式设置">
        <NForm :model="form" label-width="140">
          <NFormItem label="AI服务商">
            <NSelect v-model:value="form.highQualityAiProvider" :options="aiProviderOptions" />
          </NFormItem>
          <NFormItem label="API Key">
            <NInput v-model:value="form.highQualityApiKey" placeholder="请输入API Key" />
          </NFormItem>
          <NFormItem label="模型名称">
            <NInput v-model:value="form.highQualityModel" placeholder="请输入模型名称" />
          </NFormItem>
          <NFormItem label="Base URL">
            <NInput v-model:value="form.highQualityBaseUrl" placeholder="请输入Base URL" />
          </NFormItem>
          <NFormItem label="每批次图片数">
            <NInputNumber v-model:value="form.batchImageCount" :min="1" :max="10" />
          </NFormItem>
          <NFormItem label="会话重置频率">
            <NInputNumber v-model:value="form.sessionResetFrequency" :min="1" :max="100" />
          </NFormItem>
          <NFormItem label="RPM限制">
            <NInputNumber v-model:value="form.highQualityRpmLimit" placeholder="0表示无限制" />
          </NFormItem>
          <NFormItem label="关闭思考功能">
            <NSwitch v-model:value="form.disableThinking" />
          </NFormItem>
          <NFormItem label="强制JSON输出">
            <NSwitch v-model:value="form.forceJsonOutput" />
          </NFormItem>
          <NFormItem label="翻译提示词">
            <NInput v-model:value="form.translationPrompt" type="textarea" placeholder="请输入翻译提示词" />
          </NFormItem>
        </NForm>
      </NCollapseItem> -->

      <!-- 气泡编辑设置 -->
      <!-- <NCollapseItem name="bubble-settings" title="气泡编辑设置">
        <NForm :model="form" label-width="140">
          <NFormItem label="气泡字号大小">
            <NInputNumber v-model:value="form.bubbleFontSize" :min="8" :max="72" />
          </NFormItem>
          <NFormItem label="气泡自动字号">
            <NSwitch v-model:value="form.bubbleAutoFontSize" />
          </NFormItem>
          <NFormItem label="气泡文本字体">
            <NSelect v-model:value="form.bubbleTextFont" :options="fontOptions" placeholder="选择字体" />
          </NFormItem>
          <NFormItem label="气泡排版设置">
            <NSelect v-model:value="form.bubbleLayout" :options="layoutOptions" />
          </NFormItem>
          <NFormItem label="气泡文字颜色">
            <NColorPicker v-model:value="form.bubbleTextColor" />
          </NFormItem>
          <NFormItem label="气泡旋转角度">
            <NSlider v-model:value="form.bubbleRotationAngle" :min="-180" :max="180" />
          </NFormItem>
          <NFormItem label="气泡填充颜色">
            <NColorPicker v-model:value="form.bubbleFillColor" />
          </NFormItem>
          <NFormItem label="气泡启用文本描边">
            <NSwitch v-model:value="form.bubbleEnableTextStroke" />
          </NFormItem>
          <NFormItem label="气泡描边颜色">
            <NColorPicker v-model:value="form.bubbleStrokeColor" />
          </NFormItem>
          <NFormItem label="气泡描边宽度">
            <NInputNumber v-model:value="form.bubbleStrokeWidth" :min="1" :max="10" />
          </NFormItem>
        </NForm>
      </NCollapseItem> -->

      <!-- 图片控制设置 -->
      <!-- <NCollapseItem name="image-settings" title="图片控制设置">
        <NForm :model="form" label-width="140">
          <NFormItem label="图片大小">
            <NSlider v-model:value="form.imageSize" :min="50" :max="200" />
          </NFormItem>
          <NFormItem label="下载格式">
            <NSelect v-model:value="form.downloadFormat" :options="downloadFormatOptions" />
          </NFormItem>
        </NForm>
      </NCollapseItem> -->

      <!-- 其他设置 -->
      <!-- <NCollapseItem name="other-settings" title="其他设置">
        <NForm :model="form" label-width="140">
          <NFormItem label="位置偏移X" style="display: none">
            <NInputNumber v-model:value="form.positionOffsetX" />
          </NFormItem>
          <NFormItem label="位置偏移Y" style="display: none">
            <NInputNumber v-model:value="form.positionOffsetY" />
          </NFormItem>
        </NForm>
      </NCollapseItem> -->
    </NCollapse>

    <!-- 保存按钮 -->
    <NCard class="config-card">
      <NButton type="primary" size="large" @click="handleSave">保存所有配置</NButton>
    </NCard>
  </div>
</template>

<style scoped>
.config-container {
  width: 100%;
  margin: 0;
  padding: 20px;
}

.config-card {
  margin-top: 20px;
}

.config-card :deep(.n-card__content) {
  padding: 20px;
}
</style>
