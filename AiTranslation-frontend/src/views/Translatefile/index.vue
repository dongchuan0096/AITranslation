<script setup lang="ts">
import { ref } from 'vue';

const messages = ref<string[]>(['欢迎使用文件翻译！']);

function handleFileUpload(event: Event) {
  const input = event.target as HTMLInputElement;
  if (input.files && input.files[0]) {
    messages.value.push(`已上传文件：${input.files[0].name}`);
  }
}
</script>

<template>
  <div class="translatefile-container">
    <div class="card left-card">
      <h2>上传文件</h2>
      <input type="file" @change="handleFileUpload" />
    </div>
    <div class="card right-card">
      <h2>对话框</h2>
      <div class="chat-box">
        <div v-for="(msg, idx) in messages" :key="idx" class="chat-message">
          {{ msg }}
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.translatefile-container {
  display: flex;
  gap: 24px;
  padding: 24px;
}
.card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  padding: 24px;
  flex: 1;
  min-height: 300px;
}
.left-card {
  max-width: 320px;
}
.right-card {
  flex: 2;
  display: flex;
  flex-direction: column;
}
.chat-box {
  flex: 1;
  margin-top: 16px;
  background: #f7f7f7;
  border-radius: 4px;
  padding: 16px;
  min-height: 200px;
  overflow-y: auto;
}
.chat-message {
  margin-bottom: 8px;
  color: #333;
}
</style>
