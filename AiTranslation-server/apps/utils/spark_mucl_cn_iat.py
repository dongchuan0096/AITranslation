# -*- coding:utf-8 -*-
#
#   author: iflytek
#
#  本demo测试时运行的环境为：Windows + Python3.7
#  本demo测试成功运行时所安装的第三方库及其版本如下，您可自行逐一或者复制到一个新的txt文件利用pip一次性安装：
#   cffi==1.12.3
#   gevent==1.4.0
#   greenlet==0.4.15
#   pycparser==2.19
#   six==1.12.0
#   websocket==0.2.1
#   websocket-client==0.56.0
#
#  语音听写流式 WebAPI 接口调用示例 接口文档（必看）：https://doc.xfyun.cn/rest_api/语音听写（流式版）.html
#  webapi 听写服务参考帖子（必看）：http://bbs.xfyun.cn/forum.php?mod=viewthread&tid=38947&extra=
#  语音听写流式WebAPI 服务，热词使用方式：登陆开放平台https://www.xfyun.cn/后，找到控制台--我的应用---语音听写（流式）---服务管理--个性化热词，
#  设置热词
#  注意：热词只能在识别的时候会增加热词的识别权重，需要注意的是增加相应词条的识别率，但并不是绝对的，具体效果以您测试为准。
#  语音听写流式WebAPI 服务，方言试用方法：登陆开放平台https://www.xfyun.cn/后，找到控制台--我的应用---语音听写（流式）---服务管理--识别语种列表
#  可添加语种或方言，添加后会显示该方言的参数值
#  错误码链接：https://www.xfyun.cn/document/error-code （code返回错误码时必看）
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
import _thread as thread
import time
from time import mktime
import websocket
import base64
import datetime
import hashlib
import hmac
import json
import ssl
import threading
from datetime import datetime
from urllib.parse import urlencode
from wsgiref.handlers import format_date_time
from apps.utils.xunfei_config import XUNFEI_CONFIG

STATUS_FIRST_FRAME = 0  # 第一帧的标识
STATUS_CONTINUE_FRAME = 1  # 中间帧标识
STATUS_LAST_FRAME = 2  # 最后一帧的标识


class Ws_Param(object):
    # 初始化
    def __init__(self, APPID=None, APIKey=None, APISecret=None, AudioFile=None):
        # 使用配置文件中的默认值
        self.APPID = APPID or XUNFEI_CONFIG['APP_ID']
        self.APIKey = APIKey or XUNFEI_CONFIG['API_KEY']
        self.APISecret = APISecret or XUNFEI_CONFIG['API_SECRET']
        self.AudioFile = AudioFile
        self.iat_params = {
            "domain": "slm", 
            "language": "mul_cn", 
            "accent": "mandarin",
            "result": {
                "encoding": "utf8",
                "compress": "raw",
                "format": "json"
            }
        }

    # 生成url
    def create_url(self):
        url = 'wss://iat.cn-huabei-1.xf-yun.com/v1'
        # 生成RFC1123格式的时间戳
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        # 拼接字符串
        signature_origin = "host: " + "iat.cn-huabei-1.xf-yun.com" + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + "/v1 " + "HTTP/1.1"
        # 进行hmac-sha256进行加密
        signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()
        signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')

        authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
            self.APIKey, "hmac-sha256", "host date request-line", signature_sha)

        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
        # 将请求的鉴权参数组合为字典
        v = {
            "authorization": authorization,
            "date": date,
            "host": "iat.cn-huabei-1.xf-yun.com"
        }
        # 拼接鉴权参数，生成url
        url = url + '?' + urlencode(v)

        # 此处打印出建立连接时候的url,参考本demo的时候可取消上方打印的注释，比对相同参数时生成的url与自己代码生成的url是否一致
        print('websocket url :', url)
        return url


class XunfeiSpeechRecognition:
    """讯飞语音识别客户端 - 基于官方接口"""
    
    def __init__(self, app_id=None, api_key=None, api_secret=None):
        self.ws_param = Ws_Param(APPID=app_id, APIKey=api_key, APISecret=api_secret)
        self.ws = None
        self.result_text = ""
        self.is_finished = False
        self.error_message = None
        self.connection_established = False
        
    def on_message(self, ws, message):
        """收到websocket消息的处理"""
        try:
            message = json.loads(message)
            code = message["header"]["code"]
            status = message["header"]["status"]
            
            if code != 0:
                self.error_message = f"请求错误：{code}"
                print(f"请求错误：{code}")
                ws.close()
            else:
                payload = message.get("payload")
                if payload:
                    text = payload["result"]["text"]
                    text = json.loads(str(base64.b64decode(text), "utf8"))
                    text_ws = text['ws']
                    result = ''
                    for i in text_ws:
                        for j in i["cw"]:
                            w = j["w"]
                            result += w
                    self.result_text += result
                    print(f"识别结果: {result}")
                    
                if status == 2:
                    print("语音识别完成")
                    self.is_finished = True
                    ws.close()
                    
        except Exception as e:
            self.error_message = f"解析响应失败: {str(e)}"
            print(f"解析响应失败: {str(e)}")
            self.is_finished = True
            ws.close()

    def on_error(self, ws, error):
        """收到websocket错误的处理"""
        self.error_message = f"WebSocket错误: {str(error)}"
        print("### error:", error)

    def on_close(self, ws, close_status_code, close_msg):
        """收到websocket关闭的处理"""
        print("### closed ###")

    def on_open(self, ws):
        """收到websocket连接建立的处理"""
        print("WebSocket连接已建立")
        self.connection_established = True
        
        def run(*args):
            frameSize = 1280  # 每一帧的音频大小
            intervel = 0.04  # 发送音频间隔(单位:s)
            status = STATUS_FIRST_FRAME  # 音频的状态信息，标识音频是第一帧，还是中间帧、最后一帧

            with open(self.ws_param.AudioFile, "rb") as fp:
                while True:
                    buf = fp.read(frameSize)
                    audio = str(base64.b64encode(buf), 'utf-8')

                    # 文件结束
                    if not buf:
                        status = STATUS_LAST_FRAME
                        
                    # 第一帧处理
                    if status == STATUS_FIRST_FRAME:
                        d = {"header": {
                                "status": 0,
                                "app_id": self.ws_param.APPID
                            },
                            "parameter": {
                                "iat": self.ws_param.iat_params
                            },
                            "payload": {
                                "audio": {
                                    "audio": audio, "sample_rate": 16000, "encoding": "raw"
                                }
                            }}
                        d = json.dumps(d)
                        ws.send(d)
                        status = STATUS_CONTINUE_FRAME
                        
                    # 中间帧处理
                    elif status == STATUS_CONTINUE_FRAME:
                        d = {"header": {"status": 1,
                                        "app_id": self.ws_param.APPID},
                             "payload": {
                                 "audio": {
                                     "audio": audio, "sample_rate": 16000, "encoding": "raw"
                                 }}}
                        ws.send(json.dumps(d))
                        
                    # 最后一帧处理
                    elif status == STATUS_LAST_FRAME:
                        d = {"header": {"status": 2,
                                        "app_id": self.ws_param.APPID
                                        },
                             "payload": {
                                 "audio": {
                                     "audio": audio, "sample_rate": 16000, "encoding": "raw"
                                 }}}
                        ws.send(json.dumps(d))
                        break

                    # 模拟音频采样间隔
                    time.sleep(intervel)

        thread.start_new_thread(run, ())

    def recognize_audio_file(self, audio_file_path):
        """识别音频文件"""
        try:
            self.ws_param.AudioFile = audio_file_path
            self.result_text = ""
            self.is_finished = False
            self.error_message = None
            self.connection_established = False
            
            websocket.enableTrace(False)
            wsUrl = self.ws_param.create_url()
            self.ws = websocket.WebSocketApp(
                wsUrl, 
                on_message=self.on_message, 
                on_error=self.on_error, 
                on_close=self.on_close
            )
            self.ws.on_open = self.on_open
            
            # 在新线程中运行WebSocket
            ws_thread = threading.Thread(target=self.ws.run_forever, kwargs={"sslopt": {"cert_reqs": ssl.CERT_NONE}})
            ws_thread.daemon = True
            ws_thread.start()
            
            # 等待识别完成
            print("等待识别结果...")
            timeout = 60  # 60秒识别超时
            start_time = time.time()
            while not self.is_finished and time.time() - start_time < timeout:
                time.sleep(0.1)
            
            if not self.is_finished:
                self.error_message = "识别超时"
                print("识别超时")
                if self.ws:
                    self.ws.close()
            
            return {
                'success': self.error_message is None,
                'text': self.result_text,
                'error': self.error_message
            }
            
        except Exception as e:
            error_msg = f"识别失败: {str(e)}"
            print(error_msg)
            return {
                'success': False,
                'text': '',
                'error': error_msg
            }
        finally:
            if self.ws:
                self.ws.close()


def create_xunfei_speech_recognition(app_id=None, api_key=None, api_secret=None):
    """创建讯飞语音识别客户端"""
    return XunfeiSpeechRecognition(app_id, api_key, api_secret)


# 保持原有的函数接口，用于向后兼容
def on_message(ws, message):
    """收到websocket消息的处理 - 兼容原有接口"""
    message = json.loads(message)
    code = message["header"]["code"]
    status = message["header"]["status"]
    if code != 0:
        print(f"请求错误：{code}")
        ws.close()
    else:
        payload = message.get("payload")
        if payload:
            text = payload["result"]["text"]
            text = json.loads(str(base64.b64decode(text), "utf8"))
            text_ws = text['ws']
            result = ''
            for i in text_ws:
                for j in i["cw"]:
                    w = j["w"]
                    result += w
            print(result)
        if status == 2:
            ws.close()


def on_error(ws, error):
    """收到websocket错误的处理 - 兼容原有接口"""
    print("### error:", error)


def on_close(ws, close_status_code, close_msg):
    """收到websocket关闭的处理 - 兼容原有接口"""
    print("### closed ###")


def on_open(ws):
    """收到websocket连接建立的处理 - 兼容原有接口"""
    def run(*args):
        frameSize = 1280  # 每一帧的音频大小
        intervel = 0.04  # 发送音频间隔(单位:s)
        status = STATUS_FIRST_FRAME  # 音频的状态信息，标识音频是第一帧，还是中间帧、最后一帧

        with open(wsParam.AudioFile, "rb") as fp:
            while True:
                buf = fp.read(frameSize)
                audio = str(base64.b64encode(buf), 'utf-8')

                # 文件结束
                if not buf:
                    status = STATUS_LAST_FRAME
                # 第一帧处理
                if status == STATUS_FIRST_FRAME:
                    d = {"header": {
                            "status": 0,
                            "app_id": wsParam.APPID
                        },
                        "parameter": {
                            "iat": wsParam.iat_params
                        },
                        "payload": {
                            "audio": {
                                "audio": audio, "sample_rate": 16000, "encoding": "raw"
                            }
                        }}
                    d = json.dumps(d)
                    ws.send(d)
                    status = STATUS_CONTINUE_FRAME
                # 中间帧处理
                elif status == STATUS_CONTINUE_FRAME:
                    d = {"header": {"status": 1,
                                    "app_id": wsParam.APPID},
                         "payload": {
                             "audio": {
                                 "audio": audio, "sample_rate": 16000, "encoding": "raw"
                             }}}
                    ws.send(json.dumps(d))
                # 最后一帧处理
                elif status == STATUS_LAST_FRAME:
                    d = {"header": {"status": 2,
                                    "app_id": wsParam.APPID
                                    },
                         "payload": {
                             "audio": {
                                 "audio": audio, "sample_rate": 16000, "encoding": "raw"
                             }}}
                    ws.send(json.dumps(d))
                    break

                # 模拟音频采样间隔
                time.sleep(intervel)

    thread.start_new_thread(run, ())


if __name__ == "__main__":
    # 测试时候在此处正确填写相关信息即可运行
    wsParam = Ws_Param(APPID='', APISecret='',
                       APIKey='',
                       AudioFile=r'')
    websocket.enableTrace(False)
    wsUrl = wsParam.create_url()
    ws = websocket.WebSocketApp(wsUrl, on_message=on_message, on_error=on_error, on_close=on_close)
    ws.on_open = on_open
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
