from flask import Blueprint, request, jsonify
from src.shared.request_logger import log_request
from src.core.translation import translate_single_text
from src.app.api.config_api import save_model_info_api
from src.shared import constants
import logging
import os
import threading

logger = logging.getLogger("TextTranslateAPI")

text_translate_bp = Blueprint('text_translate_api', __name__, url_prefix='/api')

@text_translate_bp.route('/text-translate/', methods=['POST'])
@log_request
def text_translate():
    """
    文本翻译接口，POST /api/text-translate/
    请求体: { "text": "待翻译内容", "target_language": "en", ... }
    返回: { "translated_text": "..." }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '请求体不能为空'}), 400

        original_text = data.get('text')
        target_language = data.get('target_language')
        api_key = data.get('api_key')
        model_name = data.get('model_name')
        model_provider = data.get('model_provider')
        prompt_content = data.get('prompt_content')
        use_json_format = data.get('use_json_format', False)
        custom_base_url = data.get('custom_base_url')
        rpm_limit_translation = data.get('rpm_limit_translation', constants.DEFAULT_rpm_TRANSLATION)
        try:
            rpm_limit_translation = int(rpm_limit_translation)
            if rpm_limit_translation < 0: rpm_limit_translation = 0
        except (ValueError, TypeError):
            rpm_limit_translation = constants.DEFAULT_rpm_TRANSLATION

        if not all([original_text, target_language, model_provider]):
            return jsonify({'error': '缺少必要的参数 (text, target_language, model_provider)'}), 400

        # 权限校验逻辑已放开

        try:
            logger.info(f"开始调用translate_single_text函数进行翻译... JSON模式: {use_json_format}, 自定义BaseURL: {custom_base_url if custom_base_url else '无'}, rpm: {rpm_limit_translation}")
            translated = translate_single_text(
                original_text,
                target_language,
                model_provider,
                api_key=api_key,
                model_name=model_name,
                prompt_content=prompt_content,
                use_json_format=use_json_format,
                custom_base_url=custom_base_url,
                rpm_limit_translation=rpm_limit_translation
            )
            try:
                save_model_info_api(model_provider, model_name)
            except Exception as e:
                logger.warning(f"保存模型历史时出错: {e}")
            return jsonify({
                'code': '0000',
                'msg': '翻译成功',
                'data': {
                    'translated_text': translated
                }
            })
        except Exception as e:
            logger.error(f"翻译文本时出错: {e}")
            return jsonify({'error': f'翻译失败: {str(e)}'}), 500
    except Exception as e:
        logger.error(f"处理文本翻译请求时出错: {e}")
        return jsonify({'error': f'请求处理失败: {str(e)}'}), 500

if __name__ == '__main__':
    # 只在不是重载进程时打开浏览器
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        pass  # 这是重载进程，不打开浏览器
    else:
        threading.Timer(1, open_browser).start()
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=True) 