<script lang="ts" setup>
import { computed, ref } from 'vue';
import { translateImage } from '@/service/api/translate';
import { useModelConfigStore } from '@/store/modules/model-config';

const imageUpload = ref<HTMLInputElement | null>(null);
const errorMessage = ref('');
const loading = ref(false);
const thumbnails = ref<string[]>([]); // 缩略图dataURL
const images = ref<string[]>([]); // 纯base64
const translatedImages = ref<string[]>([]); // 翻译后图片dataURL
const translatedTexts = ref<string[][]>([]); // 每张图片的翻译文本数组
const currentImageIndex = ref(0);
const showPreview = ref(false);
const previewImageSrc = ref('');

const modelConfigStore = useModelConfigStore();

const langNameMap: Record<string, string> = {
  zh: '中文',
  en: '英语',
  ja: '日语',
  ko: '韩语',
  fr: '法语',
  de: '德语',
  ru: '俄语',
  es: '西班牙语',
  it: '意大利语'
  // 如有其它语言可继续补充
};

function onSelectFile() {
  imageUpload.value?.click();
}
function onFileChange(e: Event) {
  const files = (e.target as HTMLInputElement).files;
  if (!files || files.length === 0) return;
  for (let i = 0; i < files.length; i += 1) {
    const file = files[i];
      const reader = new FileReader();
    reader.onload = ev => {
        const base64 = ev.target?.result as string;
        const pureBase64 = base64.replace(/^data:image\/\w+;base64,/, '');
        thumbnails.value.push(base64);
        images.value.push(pureBase64);
      translatedImages.value.push('');
      translatedTexts.value.push([]);
      };
    reader.readAsDataURL(file);
  }
}
function onDrop(e: DragEvent) {
  if (e.dataTransfer?.files) {
    onFileChange({ target: { files: e.dataTransfer.files } } as any);
  }
}
function selectImage(idx: number) {
  currentImageIndex.value = idx;
  previewImageSrc.value = thumbnails.value[idx];
  showPreview.value = true;
}

const currentTranslatedImage = computed(() => translatedImages.value[currentImageIndex.value] || '');
const currentBubbleTexts = computed(() => translatedTexts.value[currentImageIndex.value] || []);

async function handleTranslate(idx: number) {
  if (!images.value[idx]) return;
  try {
    loading.value = true;
    const config = modelConfigStore.config as any;
    const params = {
      image: images.value[idx],
      ...getModelParams(config),
      ...getFontParams(config),
      ...getOcrParams(config),
      ...getOtherParams(config)
    };
    const res = await translateImage(params);
    if (res && res.data) {
      if (res.data.translated_image) {
        translatedImages.value[idx] = `data:image/png;base64,${res.data.translated_image}`;
      }
      if (Array.isArray(res.data.bubble_texts)) {
        translatedTexts.value[idx] = res.data.bubble_texts;
      } else if (Array.isArray(res.data.textbox_texts)) {
        translatedTexts.value[idx] = res.data.textbox_texts;
      } else if (typeof res.data.bubble_texts === 'string') {
        translatedTexts.value[idx] = [res.data.bubble_texts];
      } else if (typeof res.data.textbox_texts === 'string') {
        translatedTexts.value[idx] = [res.data.textbox_texts];
      } else {
        translatedTexts.value[idx] = [];
}
    }
  } catch {
    errorMessage.value = '图片翻译失败';
  } finally {
    loading.value = false;
}
}

async function translateOne(idx: number, img: string) {
  const config = modelConfigStore.config as any;
  const params = {
    image: img,
    ...getModelParams(config),
    ...getFontParams(config),
    ...getOcrParams(config),
    ...getOtherParams(config)
  };
  // eslint-disable-next-line no-await-in-loop
  const res = await translateImage(params);
  if (res && res.data) {
    if (res.data.translated_image) {
      translatedImages.value[idx] = `data:image/png;base64,${res.data.translated_image}`;
    }
    let texts = [];
    if (Array.isArray(res.data.bubble_texts)) {
      texts = res.data.bubble_texts;
    } else if (typeof res.data.bubble_texts === 'string') {
      texts = [res.data.bubble_texts];
    }
    translatedTexts.value[idx] = texts;
  }
}

async function translateAll() {
  if (images.value.length === 0) return;
  loading.value = true;
  try {
    await Promise.all(
      images.value.map((img, idx) => {
        if (!translatedImages.value[idx]) {
          return translateOne(idx, img);
        }
        return Promise.resolve();
      })
    );
    } catch {
    errorMessage.value = '批量翻译失败';
  } finally {
    loading.value = false;
    }
}

function getModelParams(config: any) {
  return {
    api_key: config.apiKey || '',
    model_name: config.model || '',
    model_provider: config.provider || '',
    prompt_content: config.prompt || ''
  };
}
function getFontParams(config: any) {
  return {
    fontSize: config.fontSize ?? 16,
    autoFontSize: config.autoFontSize ?? true,
    fontFamily: config.textFont || '',
    textDirection: config.layout || 'vertical',
    rotation_angle: config.bubbleRotationAngle ?? 0,
    enableTextStroke: config.enableTextStroke ?? false,
    textStrokeColor: config.strokeColor || '#000000',
    textStrokeWidth: config.strokeWidth ?? 2
  };
}
function getOcrParams(config: any) {
  return {
    ocr_engine: config.ocrEngine || '',
    baidu_api_key: config.baiduOcrApiKey || '',
    baidu_secret_key: config.baiduOcrSecretKey || '',
    baidu_version: config.baiduOcrVersion || '',
    ai_vision_provider: config.aiVisionOcrProvider || '',
    ai_vision_api_key: config.aiVisionOcrApiKey || '',
    ai_vision_model_name: config.aiVisionOcrModelName || '',
    ai_vision_ocr_prompt: config.aiVisionOcrPrompt || '',
    custom_ai_vision_base_url: config.aiVisionOcrBaseUrl || '',
    use_json_format_ai_vision_ocr: config.use_json_format_ai_vision_ocr ?? false,
    rpm_limit_ai_vision_ocr: config.aiVisionOcrRpmLimit ?? 0
  };
}
function getOtherParams(config: any) {
  return {
    fill_color: config.fillColor || '#ffffff',
    text_color: config.textColor || '#000000',
    use_inpainting: config.use_inpainting ?? false,
    blend_edges: config.edgeBlending ?? false,
    inpainting_strength: config.repairStrength ?? 50,
    use_lama: config.use_lama ?? false,
    skip_translation: config.skip_translation ?? false,
    skip_ocr: config.skip_ocr ?? false,
    remove_only: config.remove_only ?? false,
    use_textbox_prompt: config.enableIndependentTextPrompt ?? false,
    textbox_prompt_content: config.textBoxPrompt || '',
    use_json_format_translation: config.use_json_format_translation ?? false,
    rpm_limit_translation: config.rpm_limit_translation ?? 0,
    bubble_coords: [],
    target_language: config.target_language || 'zh',
    source_language: config.sourceLanguage || '',
    custom_base_url: config.translationBaseUrl || ''
  };
}

function openPreview() {
  previewImageSrc.value = currentTranslatedImage.value;
  showPreview.value = true;
  }
function closePreview() {
  console.log('closePreview called');
  showPreview.value = false;
}

function deleteImage(idx: number) {
  thumbnails.value.splice(idx, 1);
  images.value.splice(idx, 1);
  translatedImages.value.splice(idx, 1);
  translatedTexts.value.splice(idx, 1);
  // 如果删除的是当前选中，重置currentImageIndex
  if (currentImageIndex.value === idx) {
    currentImageIndex.value = 0;
  } else if (currentImageIndex.value > idx) {
    currentImageIndex.value -= 1;
  }
}
</script>

<template>
  <div class="comic-translate-layout">
    <!-- 左侧卡片：上传与图片队列 -->
    <section class="left-panel card">
      <div id="drop-area" @dragover.prevent @drop.prevent="onDrop" @click="onSelectFile">
        <p>
          拖拽图片到这里，或
          <span class="select-file-link">点击选择文件</span>
        </p>
        <input
          id="imageUpload"
          ref="imageUpload"
          type="file"
          accept="image/*"
          multiple
          style="display: none"
          @change="onFileChange"
        />
      </div>
      <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>
      <div v-if="loading" class="loading-animation"><div class="spinner"></div></div>
      <div class="thumbnails-queue-horizontal">
        <div
          v-for="(thumb, idx) in thumbnails"
          :key="idx"
          class="thumbnail-wrapper"
          :class="{ selected: idx === currentImageIndex }"
        >
          <div class="thumb-img-box">
            <img :src="thumb" class="thumbnail-img" @click="selectImage(idx)" />
            <button class="delete-thumb-btn" @click.stop="deleteImage(idx)">×</button>
          </div>
          <button v-if="!translatedImages[idx] && !loading" class="translate-btn" @click="handleTranslate(idx)">
            翻译
          </button>
        </div>
      </div>
    </section>

    <!-- 右侧卡片：翻译结果 -->
    <section class="right-panel card">
      <div class="result-image-area">
        <button class="translate-all-btn" :disabled="loading || images.length === 0" @click="translateAll">
          一键翻译
        </button>
        <div v-if="currentTranslatedImage">
          <img :src="currentTranslatedImage" class="result-image clickable" @click="openPreview" />
        </div>
        <div v-else class="result-placeholder">请上传并选择图片</div>
      </div>
      <div class="result-text-area">
        <ul>
          <li v-for="(item, idx) in currentBubbleTexts" :key="idx">
            <span class="lang-tag">{{ langNameMap[item.detected] || item.detected }}</span>
            {{ item.translation }}
          </li>
        </ul>
      </div>
      <!-- 放大预览弹窗 -->
      <Teleport to="body">
        <Transition name="fade">
          <div v-if="showPreview" class="preview-modal" @click.self="closePreview">
            <img :src="previewImageSrc" class="preview-image" @click.stop />
          </div>
        </Transition>
      </Teleport>
    </section>
  </div>
</template>

<style scoped>
.comic-translate-layout {
  display: flex;
  gap: 24px;
  min-height: 70vh;
}
.left-panel {
  flex: 0 0 280px;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  min-width: 220px;
  max-width: 340px;
  margin-right: 0;
}
.right-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  padding-left: 0;
}
.card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px #eee;
  padding: 20px;
  margin-bottom: 0;
}
#drop-area {
  border: 2px dashed #bbb;
  padding: 30px 10px;
  text-align: center;
  cursor: pointer;
  margin-bottom: 18px;
}
.select-file-link {
  color: #3498db;
  cursor: pointer;
}
.error-message {
  color: #e74c3c;
  margin: 10px 0;
}
.loading-animation .spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #eee;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto;
}
@keyframes spin {
  100% {
    transform: rotate(360deg);
  }
}
.thumbnails-queue-horizontal {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-top: 0;
  margin-bottom: 0;
  padding: 0;
  max-height: 400px;
  overflow-y: auto;
}
.thumbnail-wrapper {
  width: 100%;
  margin: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.thumb-img-box {
  position: relative;
  width: 100%;
  height: 0;
  padding-bottom: 100%;
}
.thumbnail-img {
  width: 100%;
  height: 100%;
  position: absolute;
  left: 0;
  top: 0;
  object-fit: cover;
  border-radius: 4px;
  display: block;
  margin: 0;
}
.delete-thumb-btn {
  position: absolute;
  top: 2px;
  right: 2px;
  width: 20px;
  height: 20px;
  border: none;
  background: rgba(0, 0, 0, 0.5);
  color: #fff;
  border-radius: 50%;
  font-size: 16px;
  line-height: 20px;
  cursor: pointer;
  z-index: 2;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  transition: background 0.2s;
}
.delete-thumb-btn:hover {
  background: #e74c3c;
}
.translate-btn {
  width: 60px;
  margin: 0;
  padding: 2px 0;
  font-size: 13px;
  border: none;
  background: #3498db;
  color: #fff;
  border-radius: 0 0 4px 4px;
  cursor: pointer;
  transition: background 0.2s;
}
.translate-btn:hover {
  background: #2176bd;
}
.right-panel {
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  min-width: 0;
}
.result-image-area {
  flex: 0 0 auto;
  min-height: 320px;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  justify-content: flex-start;
  border-bottom: 1px solid #f0f0f0;
  margin-bottom: 16px;
  min-width: 0;
  position: relative;
}
.translate-all-btn {
  position: absolute;
  top: 16px;
  right: 16px;
  z-index: 2;
  padding: 6px 18px;
  font-size: 15px;
  background: #3498db;
  color: #fff;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  box-shadow: 0 2px 8px #eee;
  transition: background 0.2s;
}
.translate-all-btn:disabled {
  background: #b0c4d8;
  cursor: not-allowed;
}
.translate-all-btn:hover:not(:disabled) {
  background: #2176bd;
}
.result-image {
  max-width: 100%;
  max-height: 360px;
  border-radius: 8px;
  box-shadow: 0 2px 8px #eee;
  background: #fafbfc;
  cursor: zoom-in;
}
.result-placeholder {
  color: #aaa;
  text-align: center;
  width: 100%;
}
.result-text-area {
  flex: 1;
  padding: 12px 0 0 0;
  overflow-y: auto;
}
.result-text-area h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
  color: #333;
}
.result-text-area ul {
  padding-left: 18px;
  margin: 0;
}
.result-text-area li {
  margin-bottom: 6px;
  color: #444;
  font-size: 15px;
}
/* 放大预览弹窗样式 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
.preview-modal {
  position: fixed;
  left: 0;
  top: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  z-index: 99999;
  display: flex;
  align-items: center;
  justify-content: center;
}
.preview-image {
  max-width: 90vw;
  max-height: 90vh;
  border-radius: 10px;
  box-shadow: 0 4px 24px #0008;
  background: #fff;
  display: block;
}
.lang-tag {
  display: inline-block;
  background: #e6f0fa;
  color: #2176bd;
  border-radius: 4px;
  padding: 0 6px;
  margin-right: 6px;
  font-size: 12px;
}
@media (max-width: 900px) {
  .comic-translate-layout {
    flex-direction: column;
  }
  .left-panel {
    flex-direction: row;
    max-width: 100%;
    min-width: 0;
    margin-bottom: 18px;
  }
  .thumbnails-queue-horizontal {
    grid-template-columns: repeat(2, 1fr);
  }
  .thumbnail-wrapper,
  .thumbnail-img {
    width: 48px;
    height: 48px;
  }
  .translate-btn {
    width: 48px;
  }
}
@media (max-width: 600px) {
  .thumbnails-queue-horizontal {
    grid-template-columns: 1fr;
  }
}
</style>

<style>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
.preview-modal {
  position: fixed;
  left: 0;
  top: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  z-index: 99999;
  display: flex;
  align-items: center;
  justify-content: center;
}
.preview-image {
  max-width: 90vw;
  max-height: 90vh;
  border-radius: 10px;
  box-shadow: 0 4px 24px #0008;
  background: #fff;
  display: block;
}
</style>
