<script setup lang="ts">
import { computed, ref } from 'vue';
import { NButton, NCard, NForm, NFormItem, NIcon, NInput, NSelect, useMessage } from 'naive-ui';
import { translateTextFull } from '@/service/api/translate';
import { type SpeechRecognitionResult, speechRecognition } from '@/service/api/speech';
import { useModelConfigStore } from '@/store/modules/model-config';

const modelConfigStore = useModelConfigStore();
const message = useMessage();

// 语音识别相关状态
const isRecording = ref(false);
const isPlaying = ref(false);
const audioBlob = ref<Blob | null>(null);
const audioUrl = ref<string>('');
const recordingTime = ref(0);
const recordingTimer = ref<number | null>(null);

// 识别和翻译结果
const recognizedText = ref('');
const detectedLanguage = ref('');
const translatedText = ref('');
const loading = ref(false);
const recognizing = ref(false);

// 目标语言选项
const targetLanguageOptions = ref([
  { label: '中文', value: 'zh' },
  { label: '英语', value: 'en' },
  { label: '日语', value: 'ja' },
  { label: '韩语', value: 'ko' },
  { label: '法语', value: 'fr' },
  { label: '德语', value: 'de' },
  { label: '俄语', value: 'ru' },
  { label: '西班牙语', value: 'es' },
  { label: '意大利语', value: 'it' }
]);

// 语言代码映射
const languageMap: Record<string, string> = {
  zh: 'zh_cn',
  en: 'en_us',
  ja: 'ja_jp',
  ko: 'ko_kr',
  fr: 'fr_fr',
  de: 'de_de',
  ru: 'ru_ru',
  es: 'es_es',
  it: 'it_it'
};

const form = ref({
  target_language: 'zh',
  model_provider: modelConfigStore.config.provider || 'deepseek',
  api_key: modelConfigStore.config.translationApiKey || '',
  model_name: modelConfigStore.config.model || 'deepseek-chat',
  prompt_content: modelConfigStore.config.prompt || '',
  use_json_format: false,
  custom_base_url: '',
  rpm_limit_translation: 0
});

// 计算录音时长显示
const recordingTimeDisplay = computed(() => {
  const minutes = Math.floor(recordingTime.value / 60);
  const seconds = recordingTime.value % 60;
  return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
});

// 清理录音资源
function cleanupRecording() {
  if (recordingTimer.value) {
    clearInterval(recordingTimer.value);
    recordingTimer.value = null;
  }
  if (audioUrl.value) {
    URL.revokeObjectURL(audioUrl.value);
    audioUrl.value = '';
  }
}

let audioContext: AudioContext | null = null;
let mediaStream: MediaStream | null = null;
let source: MediaStreamAudioSourceNode | null = null;
let processor: ScriptProcessorNode | null = null;
let pcmData: number[] = [];

async function startRecording() {
  try {
    mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
    console.log('mediaStream.getAudioTracks()', mediaStream.getAudioTracks());
    audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
    source = audioContext.createMediaStreamSource(mediaStream);
    processor = audioContext.createScriptProcessor(4096, 1, 1);

    processor.onaudioprocess = e => {
      const channelData = e.inputBuffer.getChannelData(0);
      for (let i = 0; i < channelData.length; i += 1) {
        pcmData.push(channelData[i]);
      }
    };

    source.connect(processor);
    processor.connect(audioContext.destination);

    console.log('mediaStream', mediaStream);
    console.log('audioContext', audioContext);

    isRecording.value = true;
    recordingTime.value = 0;
    recordingTimer.value = window.setInterval(() => {
      recordingTime.value += 1;
    }, 1000);

    message.success('开始录音');
  } catch (error) {
    message.error('无法访问麦克风，请检查权限设置');
    console.error('录音失败:', error);
  }
}

async function stopRecording() {
  if (!audioContext || !processor || !mediaStream) return;
  processor.disconnect();
  source?.disconnect();
  mediaStream.getTracks().forEach(track => track.stop());

  // 合并PCM数据
  console.log('pcmData 数组长度', pcmData.length);
  const flatPCM = Float32Array.from(pcmData);
  console.log('flatPCM 长度', flatPCM.length, '前10个值', flatPCM.slice(0, 10));
  // 重采样到16kHz
  const offlineCtx = new OfflineAudioContext(1, (flatPCM.length * 16000) / audioContext.sampleRate, 16000);
  const buffer = offlineCtx.createBuffer(1, flatPCM.length, audioContext.sampleRate);
  buffer.copyToChannel(flatPCM, 0);
  const src = offlineCtx.createBufferSource();
  src.buffer = buffer;
  src.connect(offlineCtx.destination);
  src.start();
  const rendered = await offlineCtx.startRendering();
  const resampled = rendered.getChannelData(0);

  // 转为WAV
  const wavBlob = encodeWAV(resampled, 16000);
  console.log('wavBlob 大小', wavBlob.size);
  audioBlob.value = wavBlob;
  audioUrl.value = URL.createObjectURL(wavBlob);

  // 清理
  audioContext.close();
  audioContext = null;
  processor = null;
  source = null;
  mediaStream = null;
  pcmData = [];
  isRecording.value = false;
  cleanupRecording();
  message.success('录音完成');
}

// PCM转WAV
function encodeWAV(samples: Float32Array, sampleRate: number) {
  const buffer = new ArrayBuffer(44 + samples.length * 2);
  const dataView = new DataView(buffer);

  function writeString(view: DataView, offset: number, str: string) {
    for (let i = 0; i < str.length; i += 1) {
      view.setUint8(offset + i, str.charCodeAt(i));
    }
  }

  writeString(dataView, 0, 'RIFF');
  dataView.setUint32(4, 36 + samples.length * 2, true);
  writeString(dataView, 8, 'WAVE');
  writeString(dataView, 12, 'fmt ');
  dataView.setUint32(16, 16, true);
  dataView.setUint16(20, 1, true);
  dataView.setUint16(22, 1, true);
  dataView.setUint32(24, sampleRate, true);
  dataView.setUint32(28, sampleRate * 2, true);
  dataView.setUint16(32, 2, true);
  dataView.setUint16(34, 16, true);
  writeString(dataView, 36, 'data');
  dataView.setUint32(40, samples.length * 2, true);

  // PCM数据写入
  let offset = 44;
  for (let i = 0; i < samples.length; i += 1, offset += 2) {
    const s = Math.max(-1, Math.min(1, samples[i]));
    dataView.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7fff, true);
  }
  return new Blob([dataView], { type: 'audio/wav' });
}

// 播放录音
function playRecording() {
  if (audioUrl.value && !isPlaying.value) {
    const audio = new Audio(audioUrl.value);
    isPlaying.value = true;

    audio.onended = () => {
      isPlaying.value = false;
    };

    audio.onerror = () => {
      isPlaying.value = false;
      message.error('播放失败');
    };

    audio.play();
  }
}

// 语音识别
async function recognizeSpeech() {
  if (!audioBlob.value) {
    message.warning('请先录制语音');
    return;
  }

  recognizing.value = true;
  try {
    console.log('音频数据大小:', audioBlob.value.size, 'bytes');
    console.log('音频数据类型:', audioBlob.value.type);

    const response = await speechRecognition({
      audio: audioBlob.value,
      language: languageMap[form.value.target_language] || 'zh_cn',
      engine_type: 'sms16k'
    });

    const result = response.data as SpeechRecognitionResult;
    recognizedText.value = result.text || '识别失败';
    detectedLanguage.value = result.language || 'unknown';

    message.success('语音识别完成');
  } catch (error) {
    message.error('语音识别失败');
    console.error('语音识别错误:', error);
    recognizedText.value = '语音识别服务暂时不可用，请稍后重试。';
    detectedLanguage.value = 'zh';
  } finally {
    recognizing.value = false;
  }
}

// 处理翻译结果
function processTranslationResult(result: any): { translation: string; detected: string } {
  if (typeof result === 'object' && result !== null && 'translation' in result && 'detected' in result) {
    return {
      translation: result.translation || '翻译失败',
      detected: result.detected || detectedLanguage.value
    };
  }

  if (typeof result === 'string') {
    const detectedMatch = result.match(/"detected"\s*:\s*"([^"]+)"/);
    const translationMatch = result.match(/"translation"\s*:\s*"([^"]+)"/);
    if (detectedMatch && translationMatch) {
      return {
        detected: detectedMatch[1],
        translation: translationMatch[1]
      };
    }
    return { translation: result || '翻译失败', detected: detectedLanguage.value };
  }

  return { translation: result || '翻译失败', detected: detectedLanguage.value };
}

// 翻译文本
async function translateText() {
  if (!recognizedText.value) {
    message.warning('请先进行语音识别');
    return;
  }

  if (!form.value.api_key) {
    message.warning('请前往配置页面配置API Key');
    return;
  }

  loading.value = true;
  translatedText.value = '翻译中...';

  try {
    const res = await translateTextFull({
      ...form.value,
      text: recognizedText.value,
    });

    const { translation, detected } = processTranslationResult(res.data.translated_text);
    translatedText.value = translation;
    detectedLanguage.value = detected;

    message.success('翻译完成');
  } catch (e) {
    translatedText.value = (e as any)?.message || '翻译失败';
    message.error('翻译失败');
  } finally {
    loading.value = false;
  }
}

// 复制文本到剪贴板
async function copyToClipboard(text: string) {
  try {
    await navigator.clipboard.writeText(text);
    message.success('复制成功！');
  } catch {
    message.error('复制失败，请手动复制');
  }
}

// 清空所有内容
function clearAll() {
  recognizedText.value = '';
  detectedLanguage.value = '';
  translatedText.value = '';
  audioBlob.value = null;
  cleanupRecording();
  recordingTime.value = 0;
  isRecording.value = false;
  isPlaying.value = false;
}
</script>

<template>
  <div class="voice-translate-container">
    <div class="page-header">
      <div class="page-title">
        <NIcon size="24" class="title-icon">
          <IMdiVolumeHigh />
        </NIcon>
        <span>语音识别与翻译</span>
      </div>
    </div>

    <div class="main-content">
      <!-- 左侧：语音识别区域 -->
      <div class="left-panel">
        <NCard :bordered="false" class="panel-card">
          <div class="panel-header">
            <h3>语音识别</h3>
          </div>

          <!-- 录音控制区域 -->
          <NCard class="recording-card" size="small">
            <div class="recording-header">
              <h4>语音录制</h4>
              <div v-if="isRecording" class="recording-time">
                <NIcon size="16" color="#ff4d4f">
                  <IMdiMicrophone />
                </NIcon>
                <span>{{ recordingTimeDisplay }}</span>
              </div>
            </div>

            <!-- 横向按钮组 -->
            <div class="recording-btn-row">
              <NButton
                v-if="!isRecording"
                type="primary"
                size="large"
                :disabled="recognizing || loading"
                class="record-btn"
                @click="startRecording"
              >
                <template #icon>
                  <NIcon size="20">
                    <IMdiMicrophone />
                  </NIcon>
                </template>
                录音
              </NButton>

              <NButton v-else type="error" size="large" class="record-btn" @click="stopRecording">
                <template #icon>
                  <NIcon size="20">
                    <IMdiMicrophoneOff />
                  </NIcon>
                </template>
                停止
              </NButton>

              <NButton
                v-if="audioUrl"
                type="info"
                size="large"
                :disabled="isPlaying || recognizing || loading"
                class="record-btn"
                @click="playRecording"
              >
                <template #icon>
                  <NIcon size="20">
                    <IMdiPlay />
                  </NIcon>
                </template>
                播放
              </NButton>

              <NButton
                v-if="audioBlob"
                type="success"
                size="large"
                :loading="recognizing"
                :disabled="loading"
                class="record-btn"
                @click="recognizeSpeech"
              >
                <template #icon>
                  <NIcon size="20">
                    <IMdiCheck />
                  </NIcon>
                </template>
                识别
              </NButton>
            </div>
          </NCard>

          <!-- 识别结果区域 -->
          <NCard v-if="recognizedText" class="result-card" size="small">
            <div class="result-header">
              <h4>识别结果</h4>
              <div v-if="detectedLanguage" class="language-badge">检测语言: {{ detectedLanguage }}</div>
            </div>

            <div class="result-content">
              <NInput
                v-model:value="recognizedText"
                type="textarea"
                placeholder="识别结果将显示在这里"
                :autosize="{ minRows: 6, maxRows: 12 }"
                readonly
              />
              <NButton size="small" class="copy-button" @click="copyToClipboard(recognizedText)">复制</NButton>
            </div>
          </NCard>
        </NCard>
      </div>

      <!-- 右侧：翻译结果区域 -->
      <div class="right-panel">
        <NCard :bordered="false" class="panel-card">
          <div class="panel-header">
            <h3>翻译结果</h3>
          </div>

          <!-- 翻译设置 -->
          <NCard v-if="recognizedText" class="translate-settings-card" size="small">
            <h4>翻译设置</h4>
            <NForm :model="form" label-width="80" class="translate-form">
              <NFormItem label="目标语言">
                <NSelect v-model:value="form.target_language" :options="targetLanguageOptions" style="width: 100%" />
              </NFormItem>
            </NForm>

            <NButton
              type="primary"
              size="large"
              :loading="loading"
              :disabled="!recognizedText"
              class="translate-button"
              @click="translateText"
            >
              {{ loading ? '翻译中...' : '开始翻译' }}
            </NButton>
          </NCard>

          <div v-if="translatedText" class="translation-result">
            <NInput
              v-model:value="translatedText"
              type="textarea"
              placeholder="翻译结果将显示在这里"
              :autosize="{ minRows: 8, maxRows: 20 }"
              readonly
            />
            <NButton size="small" class="copy-button" @click="copyToClipboard(translatedText)">复制</NButton>
          </div>

          <div v-else-if="!recognizedText" class="empty-state">
            <NIcon size="64" color="#d9d9d9">
              <IMdiTranslate />
            </NIcon>
            <p>翻译结果将显示在这里</p>
            <p class="hint">请先进行语音识别，然后点击翻译按钮</p>
          </div>

          <!-- 清空按钮 -->
          <div class="clear-section">
            <NButton type="default" size="medium" @click="clearAll">清空所有内容</NButton>
          </div>
        </NCard>
      </div>
    </div>
  </div>
</template>

<style scoped>
.voice-translate-container {
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
  padding: 20px;
  box-sizing: border-box;
}

.page-header {
  margin-bottom: 24px;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 28px;
  font-weight: bold;
  color: #2c3e50;
}

.title-icon {
  color: #3498db;
}

.main-content {
  display: flex;
  gap: 24px;
  flex: 1;
  min-height: 0;
}

.left-panel {
  flex: 1;
  min-width: 0;
}

.right-panel {
  flex: 1;
  min-width: 0;
}

.panel-card {
  height: 100%;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  border-radius: 16px;
}

.panel-header {
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 2px solid #f0f0f0;
}

.panel-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 20px;
  font-weight: bold;
}

.recording-card,
.result-card,
.translate-settings-card {
  margin-bottom: 20px;
  border-radius: 12px;
  border: 1px solid #e8eaed;
}

.recording-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.recording-header h4 {
  margin: 0;
  color: #2c3e50;
  font-size: 16px;
  font-weight: bold;
}

.recording-time {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #ff4d4f;
  font-weight: bold;
  font-size: 14px;
}

.recording-btn-row {
  display: flex;
  justify-content: center;
  gap: 16px;
}

.record-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 50px;
  padding: 12px 32px;
  font-size: 16px;
  font-weight: bold;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.result-header h4 {
  margin: 0;
  color: #2c3e50;
  font-size: 16px;
  font-weight: bold;
}

.language-badge {
  background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
  color: white;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: bold;
}

.result-content {
  position: relative;
}

.copy-button {
  position: absolute;
  top: 8px;
  right: 8px;
  background: rgba(52, 152, 219, 0.9);
  color: white;
  border: none;
  border-radius: 6px;
}

.copy-button:hover {
  background: rgba(52, 152, 219, 1);
}

.translate-form {
  margin-bottom: 20px;
}

.translate-button {
  background: linear-gradient(135deg, #9b59b6 0%, #8e44ad 100%);
  border: none;
  border-radius: 50px;
  padding: 12px 32px;
  font-size: 16px;
  font-weight: bold;
  box-shadow: 0 4px 15px rgba(155, 89, 182, 0.4);
  width: 100%;
}

.translation-result {
  position: relative;
  flex: 1;
  display: flex;
  flex-direction: column;
  margin-top: 20px;
}

.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  color: #999;
  padding: 60px 20px;
}

.empty-state p {
  margin: 16px 0 8px 0;
  font-size: 16px;
  color: #666;
}

.empty-state .hint {
  font-size: 14px;
  color: #999;
  margin: 0;
}

.clear-section {
  display: flex;
  justify-content: center;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #f0f0f0;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .main-content {
    flex-direction: column;
    gap: 20px;
  }

  .left-panel,
  .right-panel {
    flex: none;
  }

  .voice-translate-container {
    height: auto;
    min-height: 100vh;
  }
}

@media (max-width: 768px) {
  .voice-translate-container {
    padding: 16px;
  }

  .page-title {
    font-size: 24px;
  }

  .record-btn,
  .translate-button {
    padding: 10px 24px;
    font-size: 14px;
  }

  .main-content {
    gap: 16px;
  }
}
</style>
