<template>
<!-- 复制自 index.html 的 <body> 部分 -->
<div>
    <!-- 页面头部横幅 -->
    <header class="app-header">
        <div class="header-content">
            <div class="logo-container">
                <a href="https://github.com/MashiroSaber03/Saber-Translator" target="_blank" title="访问项目仓库">
                    <img :src="logoUrl" alt="Saber-Translator Logo" class="app-logo">
                    <span class="app-name">Saber-Translator</span>
                </a>
            </div>
            <div class="header-links">
                <span class="open-source-notice">本项目完全开源免费，请勿上当受骗</span>
                <a href="http://www.mashirosaber.top" target="_blank" class="tutorial-link">使用教程</a>
                <a href="javascript:void(0)" class="donate-link" id="donateButton">
                    <img :src="donateIconUrl" alt="赞助" class="donate-icon" @error="onDonateIconError">
                    <span>请作者喝奶茶</span>
                </a>
                <a href="https://github.com/MashiroSaber03" target="_blank" class="github-link">
                    <img :src="githubIconUrl" alt="GitHub" class="github-icon">
                </a>
                <button id="themeToggle" class="theme-toggle" title="切换亮暗模式" @click="toggleTheme">
                    <span class="theme-icon light-icon">☀️</span>
                    <span class="theme-icon dark-icon">🌙</span>
                </button>
            </div>
        </div>
    </header>
    <!-- ... 其余内容保持原结构 ... -->
    <!-- 由于内容较多，建议后续分割为多个子组件 -->
    <div class="container">
        <!-- ... 省略，后续补全 ... -->
    </div>
    <!-- 赞助弹出层、插件管理弹出层、会话管理弹出层、AI校对设置弹窗等同理迁移 ... -->
</div>
</template>

<script setup>
import { ref } from 'vue'
// 静态资源路径可根据实际部署调整
const logoUrl = '/static/pic/logo.png'
const donateIconUrl = '/static/pic/donate-icon.png'
const githubIconUrl = '/static/pic/github.jpg'

function onDonateIconError(event) {
  event.target.src = 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#f06292"><path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/></svg>'
}

function toggleTheme() {
  // 主题切换逻辑，后续可完善
}
</script>

<style scoped>
@import url('/static/css/style.css');
</style> 