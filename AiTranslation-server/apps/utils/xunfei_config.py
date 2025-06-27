# 讯飞语音识别配置
# 请在此处配置您的讯飞开放平台API密钥

# 讯飞开放平台应用配置
XUNFEI_CONFIG = {
    'APP_ID': 'e511513e',  # 请替换为您的讯飞APP_ID
    'API_KEY': '782ad2efbcd02fc90f42f64255cb8009',  # 请替换为您的讯飞API_KEY
    'API_SECRET': 'MzI0OWExNTVkMWZhYzBmZGQ5ZjZhYmYy',  # 请替换为您的讯飞API_SECRET
}

# 讯飞语音识别API地址
XUNFEI_ASR_URL = "https://api.xfyun.cn/v1/service/v1/iat"

# 支持的音频格式
SUPPORTED_AUDIO_FORMATS = {
    'wav': 'audio/wav',
    'mp3': 'audio/mp3', 
    'm4a': 'audio/m4a',
    'amr': 'audio/amr',
    'pcm': 'audio/pcm',
}

# 支持的语言
SUPPORTED_LANGUAGES = {
    'zh_cn': '中文普通话',
    'en_us': '英文',
    'ja_jp': '日文',
    'ko_kr': '韩文',
    'fr_fr': '法文',
    'es_es': '西班牙文',
    'ru_ru': '俄文',
    'pt_pt': '葡萄牙文',
    'de_de': '德文',
    'it_it': '意大利文',
}

# 引擎类型配置
ENGINE_TYPES = {
    'sms16k': {
        'name': '16k采样率普通话音频',
        'rate': '16000',
        'language': 'zh_cn'
    },
    'sms8k': {
        'name': '8k采样率普通话音频', 
        'rate': '8000',
        'language': 'zh_cn'
    },
    'iat': {
        'name': '16k采样率多语言音频',
        'rate': '16000',
        'language': 'auto'
    }
} 