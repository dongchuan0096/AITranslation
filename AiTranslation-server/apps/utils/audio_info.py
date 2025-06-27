import sys
import os
import wave
import contextlib

try:
    import soundfile as sf
except ImportError:
    sf = None

def print_wav_info(filepath):
    with contextlib.closing(wave.open(filepath, 'rb')) as wf:
        channels = wf.getnchannels()
        sample_width = wf.getsampwidth()
        framerate = wf.getframerate()
        nframes = wf.getnframes()
        duration = nframes / float(framerate)
        print(f"文件: {filepath}")
        print(f"格式: WAV")
        print(f"声道数: {channels}")
        print(f"采样率: {framerate} Hz")
        print(f"采样位数: {sample_width * 8} bit")
        print(f"时长: {duration:.2f} 秒")

def print_audio_info(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    if ext == '.wav':
        try:
            print_wav_info(filepath)
        except Exception as e:
            print(f"读取WAV失败: {e}")
    elif sf is not None:
        try:
            info = sf.info(filepath)
            print(f"文件: {filepath}")
            print(f"格式: {info.format}")
            print(f"声道数: {info.channels}")
            print(f"采样率: {info.samplerate} Hz")
            print(f"采样位数: {info.subtype}")
            print(f"时长: {info.duration:.2f} 秒")
        except Exception as e:
            print(f"读取音频失败: {e}")
    else:
        print("请先安装 soundfile 库: pip install soundfile")
        print("暂不支持此格式的检测")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python audio_info.py 文件路径")
        sys.exit(1)
    filepath = sys.argv[1]
    if not os.path.isfile(filepath):
        print(f"文件不存在: {filepath}")
        sys.exit(1)
    print_audio_info(filepath) 