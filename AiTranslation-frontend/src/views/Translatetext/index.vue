<script setup lang="ts">
import { ref } from 'vue';
import { NButton, NCard, NForm, NFormItem, NInput, useMessage } from 'naive-ui';
import { translateTextFull } from '@/service/api/translate';
import { useModelConfigStore } from '@/store/modules/model-config';

const modelConfigStore = useModelConfigStore();
const message = useMessage();

const form = ref({
  text: '',
  source_language: '',
  target_language: 'zh',
  model_provider: modelConfigStore.config.provider || 'deepseek',
  api_key: modelConfigStore.config.apiKey || '',
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
    translatedText.value = '请输入要翻译的内容';
    return;
  }
  if (!form.value.api_key) {
    translatedText.value = '请前往配置页面配置API Key';
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
  } catch (e) {
    translatedText.value = (e as any)?.message || '翻译失败';
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <NCard :bordered="false" class="card-wrapper">
    <div class="translate-title">文本翻译</div>
    <NForm :model="form" label-width="100" class="translate-form">
      <NFormItem label="待翻译内容">
        <NInput
          v-model:value="form.text"
          type="textarea"
          placeholder="请输入要翻译的内容"
          class="translate-input"
          :autosize="{ minRows: 3, maxRows: 10 }"
        />
      </NFormItem>
      <NFormItem>
        <div class="lang-row">
          <div class="lang-item">
            <span class="lang-label">当前语言</span>
            <NInput v-model:value="form.source_language" placeholder="自动识别" disabled style="width: 100px" />
          </div>
          <span class="lang-arrow">→</span>
          <div class="lang-item">
            <span class="lang-label">目标语言</span>
            <NInput v-model:value="form.target_language" placeholder="如 zh、en" style="width: 100px" />
          </div>
        </div>
      </NFormItem>
      <NFormItem label="模型服务商">
        <NInput v-model:value="form.model_provider" placeholder="如 OpenAI" style="width: 180px" />
      </NFormItem>
      <NFormItem label="模型型号">
        <NInput v-model:value="form.model_name" placeholder="如 gpt-3.5-turbo" style="width: 180px" />
      </NFormItem>
      <NFormItem>
        <div style="width: 100%; text-align: center">
          <NButton type="primary" :loading="loading" size="large" style="min-width: 120px" @click="handleTranslate">
            {{ loading ? '翻译中...' : '翻译' }}
          </NButton>
        </div>
      </NFormItem>
    </NForm>
    <NCard v-if="translatedText" class="translate-result-card" size="small" style="margin-top: 18px">
      <div class="translate-result-header">
        <div class="translate-result-title">翻译结果：</div>
        <NButton size="small" @click="copyToClipboard(translatedText)">复制</NButton>
      </div>
      <div class="translate-result-content">{{ translatedText }}</div>
    </NCard>
  </NCard>
</template>

<style scoped>
.card-wrapper {
  max-width: 600px;
  margin: 32px auto;
  box-shadow: 0 2px 12px #0001;
  border-radius: 12px;
  padding: 24px 18px 18px 18px;
}
.translate-title {
  font-size: 22px;
  font-weight: bold;
  margin-bottom: 18px;
  text-align: center;
  letter-spacing: 2px;
}
.translate-form {
  margin-bottom: 0;
}
.translate-input {
  /* 移除固定高度，让autosize生效 */
}
.lang-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 0;
}
.lang-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}
.lang-label {
  font-size: 13px;
  color: #888;
  margin-bottom: 2px;
}
.lang-arrow {
  font-size: 20px;
  color: #aaa;
  margin: 0 8px;
}
.translate-result-card {
  background: #f6fff6;
  border: 1px solid #e6f4ea;
  border-radius: 8px;
}
.translate-result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}
.translate-result-title {
  font-weight: bold;
  color: #18a058;
}
.translate-result-content {
  color: #222;
  font-size: 16px;
  word-break: break-all;
}
</style>
