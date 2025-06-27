<template>
  <NCard :bordered="false" class="card-wrapper">
    <div style="font-size: 20px; margin-bottom: 12px;">文本翻译</div>
    <n-input v-model="inputText" placeholder="请输入要翻译的内容" style="margin-bottom: 12px;" />
    <n-button type="primary" @click="handleTranslate">翻译</n-button>
    <div v-if="translatedText" style="margin-top: 16px; color: #18a058;">翻译结果：{{ translatedText }}</div>
  </NCard>
</template>

<script setup lang="ts">
import { ref } from 'vue';
const inputText = ref('');
const translatedText = ref('');

function handleTranslate() {
  // 这里只做简单演示，实际可接入翻译API
  translatedText.value = inputText.value ? `【模拟翻译】${inputText.value}` : '';
}
</script>

<style scoped></style> 