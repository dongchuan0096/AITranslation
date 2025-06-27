<script setup lang="ts">
import { ref } from 'vue';
const inputText = ref('');
const translatedText = ref('');

function handleTranslate() {
  // 这里只做简单演示，实际可接入翻译API
  translatedText.value = inputText.value ? `【模拟翻译】${inputText.value}` : '';
}
</script>

<template>
  <NCard :bordered="false" class="card-wrapper">
    <div class="translate-title">文本翻译</div>
    <NInput v-model="inputText" placeholder="请输入要翻译的内容" class="translate-input" />
    <NButton type="primary" @click="handleTranslate">翻译</NButton>
    <div v-if="translatedText" class="translate-result">翻译结果：{{ translatedText }}</div>
  </NCard>
</template>

<style scoped>
.translate-title {
  font-size: 20px;
  margin-bottom: 12px;
}
.translate-input {
  margin-bottom: 12px;
}
.translate-result {
  margin-top: 16px;
  color: #18a058;
}
</style>
