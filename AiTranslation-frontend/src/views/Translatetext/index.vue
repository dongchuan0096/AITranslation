<script setup lang="ts">
import { ref } from 'vue';
import { NButton, NCard, NIcon, NInput, NSelect, useMessage } from 'naive-ui';
import { translateTextFull } from '@/service/api/translate';
import { useModelConfigStore } from '@/store/modules/model-config';

const modelConfigStore = useModelConfigStore();
const message = useMessage();

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

const form = ref({
  text: '',
  source_language: '',
  target_language: 'zh',
  model_provider: modelConfigStore.config.provider || 'deepseek',
  api_key: modelConfigStore.config.translationApiKey || '',
  model_name: modelConfigStore.config.model || 'deepseek-chat',
  prompt_content: modelConfigStore.config.prompt || '',
  use_json_format: false,
  custom_base_url: '',
  rpm_limit_translation: 0
});
const translatedText = ref('');
const loading = ref(false);

async function copyToClipboard(text: string) {
  try {
    await navigator.clipboard.writeText(text);
    message.success('复制成功！');
  } catch {
    message.error('复制失败，请手动复制');
  }
}

async function handleTranslate() {
  if (!form.value.text) {
    message.warning('请输入要翻译的内容');
    return;
  }
  if (!form.value.api_key) {
    message.warning('请前往配置页面配置API Key');
    return;
  }
  loading.value = true;
  translatedText.value = '翻译中...';
  try {
    const res = await translateTextFull({ ...form.value });
    const result = res.data.translated_text;
    if (typeof result === 'object' && result !== null && 'translation' in result && 'detected' in result) {
      translatedText.value = result.translation || '翻译失败';
      form.value.source_language = result.detected || '';
    } else if (typeof result === 'string') {
      // 尝试用正则提取 detected 和 translation
      const detectedMatch = result.match(/"detected"\s*:\s*"([^"]+)"/);
      const translationMatch = result.match(/"translation"\s*:\s*"([^"]+)"/);
      if (detectedMatch && translationMatch) {
        form.value.source_language = detectedMatch[1];
        translatedText.value = translationMatch[1];
      } else {
        translatedText.value = result || '翻译失败';
      }
    } else {
      translatedText.value = result || '翻译失败';
    }
    message.success('翻译完成');
  } catch (e) {
    translatedText.value = (e as any)?.message || '翻译失败';
    message.error('翻译失败');
  } finally {
    loading.value = false;
  }
}

// 清空所有内容
function clearAll() {
  form.value.text = '';
  form.value.source_language = '';
  translatedText.value = '';
}
</script>

<template>
  <div class="text-translate-container">
    <!--
 <div class="page-header">
      <div class="page-title">
        <NIcon size="24" class="title-icon">
          <i-mdi-translate />
        </NIcon>
        <span>文本翻译</span>
      </div>
    </div> 
-->

    <div class="main-content">
      <!-- 左侧：输入区域 -->
      <div class="left-panel">
        <NCard :bordered="false" class="panel-card">
          <div class="panel-header header-with-btn">
            <h3>输入内容</h3>
            <NButton
              type="primary"
              size="large"
              :loading="loading"
              :disabled="!form.text"
              class="translate-btn-header"
              @click="handleTranslate"
            >
              <template #icon>
                <NIcon size="20"><IMdiArrowRightBold /></NIcon>
              </template>
              翻译
            </NButton>
          </div>

          <div class="left-content">
            <!-- 输入区域 -->
            <NCard class="input-card" size="small">
              <div class="input-header-row">
                <div class="input-header-title">
                  <NSelect
                    :value="form.source_language || null"
                    :options="targetLanguageOptions"
                    class="lang-select"
                    placeholder="自动检测"
                    disabled
                    style="width: 100px"
                  />
                </div>
              </div>
              <div class="input-content-flex">
                <NInput
                  v-model:value="form.text"
                  type="textarea"
                  placeholder="请输入要翻译的内容"
                  :autosize="{ minRows: 12, maxRows: 15 }"
                  class="text-input"
                >
                  <template #suffix>
                    <NButton
                      quaternary
                      size="small"
                      class="copy-icon-btn"
                      :disabled="!form.text"
                      style="padding: 0 4px"
                      title="复制"
                      @click.stop="copyToClipboard(form.text)"
                    >
                      <NIcon size="18"><IMdiContentCopy /></NIcon>
                    </NButton>
                  </template>
                </NInput>
              </div>
            </NCard>
          </div>
        </NCard>
      </div>

      <!-- 右侧：翻译结果区域 -->
      <div class="right-panel">
        <NCard :bordered="false" class="panel-card">
          <div class="panel-header">
            <h3>翻译结果</h3>
          </div>

          <div class="right-content">
            <div class="right-header-actions">
              <NSelect
                v-model:value="form.target_language"
                :options="targetLanguageOptions"
                class="lang-select"
                placeholder="目标语言"
              />
            </div>
            <div v-if="translatedText" class="translation-result">
              <NInput
                v-model:value="translatedText"
                type="textarea"
                placeholder="翻译结果将显示在这里"
                :autosize="{ minRows: 12, maxRows: 25 }"
                readonly
              />
              <div class="copy-btn-row">
                <NButton size="small" class="copy-button" @click="copyToClipboard(translatedText)">复制</NButton>
              </div>
            </div>
            <div v-else class="empty-state">
              <NIcon size="64" color="#d9d9d9">
                <IMdiTranslate />
              </NIcon>
              <p>翻译结果将显示在这里</p>
              <p class="hint">请输入要翻译的内容，然后点击翻译按钮</p>
            </div>
            <!-- 清空按钮 -->
            <div class="clear-section">
              <NButton type="default" size="medium" @click="clearAll">清空所有内容</NButton>
            </div>
          </div>
        </NCard>
      </div>
    </div>
  </div>
</template>

<style scoped>
.text-translate-container {
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
  align-items: stretch;
}

.left-panel {
  flex: 1;
  min-width: 0;
  display: flex;
}

.right-panel {
  flex: 1;
  min-width: 0;
  display: flex;
}

.panel-card {
  width: 100%;
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

.translate-settings-card,
.input-card {
  margin-bottom: 20px;
  border-radius: 12px;
  border: 1px solid #e8eaed;
}

.input-card {
  flex: 1;
  margin-bottom: 16px;
  border: none !important;
  box-shadow: none !important;
}

/* 深度穿透 Naive UI 内部的卡片内容和伪元素 */
:deep(.input-card .n-card) {
  border: none !important;
  box-shadow: none !important;
  background: transparent;
}
:deep(.input-card .n-card__content) {
  border: none !important;
  box-shadow: none !important;
}
:deep(.input-card .n-card__border) {
  display: none !important;
}

.translate-settings-card {
  flex-shrink: 0;
  margin-bottom: 0;
}

.translate-settings-card h4,
.input-header h4 {
  margin: 0 0 16px 0;
  color: #2c3e50;
  font-size: 16px;
  font-weight: bold;
}

.input-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.language-badge {
  background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
  color: white;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: bold;
}

.input-content {
  position: relative;
}

.input-content-flex {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  justify-content: stretch;
}

.text-input {
  flex: 1;
  min-height: 0;
  resize: none;
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
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  justify-content: stretch;
}

.translation-result .n-input {
  flex: 1;
  min-height: 0;
  resize: none;
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
  min-height: 0;
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
  flex-shrink: 0;
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

  .text-translate-container {
    height: auto;
    min-height: 100vh;
  }
}

@media (max-width: 768px) {
  .text-translate-container {
    padding: 16px;
  }

  .page-title {
    font-size: 24px;
  }

  .translate-button {
    padding: 10px 24px;
    font-size: 14px;
  }

  .main-content {
    gap: 16px;
  }
}

.left-content {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
}

.right-content {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
}

.input-row-flex {
  display: flex;
  flex-direction: row;
  gap: 24px;
  align-items: flex-start;
}

.input-side-bar {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: 16px;
  min-width: 140px;
  max-width: 180px;
  background: rgba(245, 247, 255, 0.7);
  border-radius: 18px;
  box-shadow: 0 2px 12px #b3c6ff22;
  padding: 18px 12px 18px 12px;
  margin-top: 4px;
}

.lang-select {
  min-width: 90px;
  max-width: 120px;
  border-radius: 8px;
  background: #fff;
  box-shadow: 0 1px 6px #e0e7ff44;
}

.translate-btn {
  min-width: 72px;
  padding: 0 18px;
  margin-top: 0;
  border-radius: 20px;
  font-weight: bold;
  letter-spacing: 2px;
  background: linear-gradient(90deg, #7f9cf5 0%, #a78bfa 100%);
  box-shadow: 0 2px 8px #a78bfa33;
  transition: background 0.2s;
  height: 36px;
  line-height: 36px;
  font-size: 15px;
}

.translate-btn:hover {
  background: linear-gradient(90deg, #6c63ff 0%, #b993ff 100%);
}

.input-header-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.input-header-title {
  display: flex;
  align-items: center;
  font-size: 16px;
  font-weight: bold;
  color: #2c3e50;
}

.input-header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.copy-btn-row {
  display: flex;
  justify-content: flex-end;
  margin-top: 8px;
}

.panel-header.header-with-btn {
  display: flex;
  align-items: center;
  gap: 18px;
}

.panel-header.header-with-btn h3 {
  margin: 0;
  font-size: 20px;
  font-weight: bold;
  color: #2c3e50;
  margin-right: 280px;
}

.copy-icon-btn {
  position: absolute;
  top: 6px;
  right: 8px;
  z-index: 2;
  background: transparent;
  box-shadow: none;
}

.translate-btn-header {
  height: 30px;
  line-height: 36px;
  font-size: 15px;
}
</style>
