<script lang="ts" setup>
import { computed, ref } from 'vue';
import { downloadAllImages, uploadPdf } from '@/service/api/system';
import { translateImage } from '@/service/api/translate';
import { useModelConfigStore } from '@/store/modules/model-config';

const imageUpload = ref<HTMLInputElement | null>(null);
const importTextFileInput = ref<HTMLInputElement | null>(null);

const errorMessage = ref('');
const loading = ref(false);
const thumbnails = ref<string[]>([]);
const images = ref<string[]>([]); // images 只存储纯 base64 字符串（不带 data:image/png;base64, 前缀）
const translatedImages = ref<string[]>([]); // base64翻译图
const showProgress = ref(false);
const progress = ref({ current: 0, total: 0 });
const showResult = ref(false);
const canToggleImage = ref(false);
const showTranslatedImage = ref(true);
const displayImage = ref('');
const editMode = ref(false);
const imageSize = ref(100);
const bubbles = ref<{ text: string }[]>([]);
const currentBubble = ref<number | null>(null);
const downloadFormat = ref<'zip' | 'pdf' | 'cbz'>('zip');
const lastResponseKeys = ref<string[]>([]);
const lastResponseData = ref<any>(null);

const modelConfigStore = useModelConfigStore();

const progressPercent = computed(() =>
  progress.value.total ? (progress.value.current / progress.value.total) * 100 : 0
);

function onSelectFile() {
  imageUpload.value?.click();
}
function onFileChange(e: Event) {
  const files = (e.target as HTMLInputElement).files;
  if (!files || files.length === 0) return;
  let hasPdf = false;
  for (let i = 0; i < files.length; i += 1) {
    const file = files[i];
    if (file.type === 'application/pdf') {
      hasPdf = true;
      const formData = new FormData();
      formData.append('file', file);
      uploadPdf(formData).then(res => {
        console.log('PDF上传返回：', res);
      });
      // 只处理第一个PDF
      break;
    }
  }
  if (!hasPdf) {
    for (let i = 0; i < files.length; i += 1) {
      const reader = new FileReader();
      reader.onload = async ev => {
        const base64 = ev.target?.result as string;
        const pureBase64 = base64.replace(/^data:image\/\w+;base64,/, '');
        thumbnails.value.push(base64);
        images.value.push(pureBase64);

        // 自动调用图片翻译接口
        try {
          // 组装参数
          const config = modelConfigStore.config as any;
          const params = {
            image: pureBase64,
            ...getModelParams(config),
            ...getFontParams(config),
            ...getOcrParams(config),
            ...getOtherParams(config)
          };
          const res = await translateImage(params);
          console.log('图片上传后接口返回：', res);
          if (res && res.data) {
            lastResponseKeys.value = Object.keys(res.data);
            lastResponseData.value = res.data;
          } else {
            lastResponseKeys.value = [];
            lastResponseData.value = null;
          }
        } catch (err) {
          console.error('图片上传后接口请求失败：', err);
        }
      };
      reader.readAsDataURL(files[i]);
    }
    showResult.value = true;
  }
}
function onDrop(e: DragEvent) {
  if (e.dataTransfer?.files) {
    onFileChange({ target: { files: e.dataTransfer.files } } as any);
  }
}
function selectImage(idx: number) {
  displayImage.value = translatedImages.value[idx] || images.value[idx];
  // 可同步气泡数据
}
function toggleImage() {
  showTranslatedImage.value = !showTranslatedImage.value;
}
function toggleEditMode() {
  editMode.value = !editMode.value;
}
function onImageSizeChange() {
  // 仅前端缩放
}
function selectBubble(idx: number) {
  currentBubble.value = idx;
}
function applyBubbleEdit() {
  // 可调用 reRenderSingleBubble
}
function resetBubbleEdit() {
  // 恢复原始内容
}
function downloadCurrent() {
  // 直接下载当前图片
  const a = document.createElement('a');
  a.href = displayImage.value;
  a.download = 'translated.png';
  a.click();
}
async function downloadAll() {
  // 调用 downloadAllImages 接口
  const res = (await downloadAllImages({
    format: downloadFormat.value,
    images: translatedImages.value
  })) as any;
  // 获取下载链接并下载
  if (res.success && res.file_id) {
    const url = `/api/download_file/${res.file_id}?format=${downloadFormat.value}`;
    window.open(url, '_blank');
  }
}
function exportText() {
  // 导出所有气泡文本
  const data = JSON.stringify(bubbles.value.map(b => b.text));
  const blob = new Blob([data], { type: 'application/json' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'bubbles.json';
  a.click();
}
function importText() {
  importTextFileInput.value?.click();
}
function onImportTextFile(e: Event) {
  const files = (e.target as HTMLInputElement).files;
  if (!files || files.length === 0) return;
  const reader = new FileReader();
  reader.onload = ev => {
    try {
      const arr = JSON.parse(ev.target?.result as string);
      if (Array.isArray(arr)) {
        arr.forEach((text, idx) => {
          if (bubbles.value[idx]) bubbles.value[idx].text = text;
        });
      }
    } catch {
      errorMessage.value = '导入文本格式错误';
    }
  };
  reader.readAsText(files[0]);
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

function getTranslateParams() {
  const config = modelConfigStore.config as any;
  // displayImage.value 可能是 DataURL，也可能是纯base64
  let imageData = displayImage.value;
  if (imageData.startsWith('data:image/')) {
    imageData = imageData.replace(/^data:image\/\w+;base64,/, '');
  }
  return {
    image: imageData,
    ...getModelParams(config),
    ...getFontParams(config),
    ...getOcrParams(config),
    ...getOtherParams(config)
  };
}
async function handleTranslate() {
  if (!displayImage.value) {
    errorMessage.value = '请先选择图片';
    return;
  }
  const params = getTranslateParams();
  try {
    loading.value = true;
    const res = await translateImage(params);
    console.log('图片翻译返回：', res);
  } catch {
    errorMessage.value = '图片翻译失败';
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="main-comic-translator">
    <!-- 上传区 -->
    <section class="card upload-card">
      <div id="drop-area" @dragover.prevent @drop.prevent="onDrop" @click="onSelectFile">
        <p>
          拖拽图片或PDF文件到这里，或
          <span class="select-file-link">点击选择文件</span>
        </p>
        <input
          id="imageUpload"
          ref="imageUpload"
          type="file"
          accept="image/*,application/pdf"
          multiple
          style="display: none"
          @change="onFileChange"
        />
      </div>
      <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>
      <div v-if="loading" class="loading-animation"><div class="spinner"></div></div>
      <div class="thumbnails">
        <img
          v-for="(thumb, idx) in thumbnails"
          :key="idx"
          :src="thumb"
          class="thumbnail-img"
          @click="selectImage(idx)"
        />
      </div>
      <div v-if="showProgress" class="progress-bar-label">
        进度:
        <span>{{ progress.current }}/{{ progress.total }}</span>
        <div class="progress-bar"><div class="progress" :style="{ width: progressPercent + '%' }"></div></div>
      </div>
    </section>

    <!-- 结果区 -->
    <section v-if="showResult" class="card result-card">
      <div class="image-controls">
        <button v-if="canToggleImage" @click="toggleImage">切换原图/翻译图</button>
        <button @click="toggleEditMode">切换编辑模式</button>
        <div class="image-size-control">
          <label for="imageSize">图片大小:</label>
          <input id="imageSize" v-model="imageSize" type="range" min="50" max="200" @input="onImageSizeChange" />
          <span>{{ imageSize }}%</span>
        </div>
      </div>
      <div class="content-container">
        <div class="image-container">
          <img v-show="showTranslatedImage" :src="displayImage" alt="翻译后图片" :style="{ width: imageSize + '%' }" />
        </div>
        <div v-if="editMode" class="edit-mode-container">
          <h3>气泡编辑模式</h3>
          <div class="bubble-list-container">
            <div class="bubble-list-header">
              <h4>气泡列表</h4>
              <span class="bubble-count">
                共
                <span>{{ bubbles.length }}</span>
                个气泡
              </span>
            </div>
            <div class="bubble-list">
              <div v-for="(bubble, idx) in bubbles" :key="idx" class="bubble-item" @click="selectBubble(idx)">
                #{{ idx + 1 }} {{ bubble.text }}
              </div>
            </div>
          </div>
          <div v-if="currentBubble !== null" class="bubble-edit-container">
            <h4>编辑气泡 #{{ currentBubble + 1 }}</h4>
            <textarea v-model="bubbles[currentBubble].text" placeholder="气泡文字内容"></textarea>
            <!-- 其他气泡属性设置可扩展 -->
            <button @click="applyBubbleEdit">应用更改</button>
            <button @click="resetBubbleEdit">重置</button>
          </div>
        </div>
      </div>
      <div class="download-buttons">
        <button @click="downloadCurrent">下载当前图片</button>
        <button @click="downloadAll">下载所有图片</button>
        <select v-model="downloadFormat">
          <option value="zip">ZIP压缩包</option>
          <option value="pdf">PDF文件</option>
          <option value="cbz">CBZ漫画格式</option>
        </select>
        <button @click="exportText">导出文本</button>
        <button @click="importText">导入文本</button>
        <button @click="handleTranslate">翻译</button>
        <input ref="importTextFileInput" type="file" style="display: none" accept=".json" @change="onImportTextFile" />
      </div>
      <div v-if="lastResponseKeys.length" class="response-keys">
        <strong>后端返回字段：</strong>
        <span v-for="key in lastResponseKeys" :key="key" class="response-key">{{ key }}</span>
      </div>
      <div v-if="lastResponseData">
        <div v-if="lastResponseData.translated_image">
          <strong>翻译后图片：</strong>
          <img
            :src="'data:image/png;base64,' + lastResponseData.translated_image"
            style="max-width: 100%; display: block; margin-bottom: 10px"
          />
        </div>
        <div v-if="lastResponseData.clean_image">
          <strong>消除文字后图片：</strong>
          <img
            :src="'data:image/png;base64,' + lastResponseData.clean_image"
            style="max-width: 100%; display: block; margin-bottom: 10px"
          />
        </div>
        <div v-if="lastResponseData.textbox_texts && lastResponseData.textbox_texts.length">
          <strong>文本框内容：</strong>
          <ul>
            <li v-for="(text, idx) in lastResponseData.textbox_texts" :key="idx">{{ text }}</li>
          </ul>
        </div>
      </div>
    </section>

    <!-- 右侧缩略图栏 -->
    <aside id="thumbnail-sidebar">
      <div class="card thumbnail-card">
        <h2>图片概览</h2>
        <ul id="thumbnailList">
          <li v-for="(thumb, idx) in thumbnails" :key="idx" @click="selectImage(idx)">
            <img :src="thumb" class="thumbnail-img" />
          </li>
        </ul>
      </div>
    </aside>
  </div>
</template>

<style scoped>
.main-comic-translator {
  display: flex;
}
.card {
  background: #fff;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px #eee;
}
.upload-card,
.result-card {
  padding: 20px;
  flex: 1;
}
#drop-area {
  border: 2px dashed #bbb;
  padding: 30px;
  text-align: center;
  cursor: pointer;
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
.thumbnails {
  display: flex;
  gap: 10px;
  margin: 10px 0;
}
.thumbnail-img {
  width: 60px;
  height: 60px;
  object-fit: cover;
  border-radius: 4px;
}
.progress-bar {
  width: 100%;
  height: 8px;
  background: #f0f0f0;
  border-radius: 4px;
  margin-top: 5px;
}
.progress {
  height: 100%;
  background: #4cae4c;
  border-radius: 4px;
}
.image-controls {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}
.image-size-control {
  display: flex;
  align-items: center;
  gap: 5px;
}
.download-buttons {
  margin-top: 20px;
  display: flex;
  gap: 10px;
  align-items: center;
}
#thumbnail-sidebar {
  width: 200px;
  background: #f8fafc;
  border-left: 1px solid #eee;
  padding: 10px;
}
.thumbnail-card {
  padding: 10px;
}
#thumbnailList {
  list-style: none;
  padding: 0;
  margin: 0;
}
#thumbnailList li {
  margin-bottom: 10px;
  cursor: pointer;
}
.response-keys {
  margin: 10px 0;
  font-size: 14px;
  color: #333;
}
.response-key {
  display: inline-block;
  background: #f0f0f0;
  border-radius: 4px;
  padding: 2px 8px;
  margin-right: 8px;
}
</style>
