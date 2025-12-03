"""
音频播放器模块
从 qwen_omini_api.py 提取并优化的音频播放器
"""
import base64
import queue
import threading
import contextlib
import pyaudio


class AudioPlayer:
    """Base64 PCM 音频播放器

    支持流式接收 Base64 编码的 PCM 音频数据并实时播放
    使用双线程 + 双队列架构实现解码和播放的异步处理
    """

    def __init__(self, sample_rate=24000, chunk_size_ms=100):
        """初始化音频播放器

        Args:
            sample_rate: 采样率（Hz），默认 24000
            chunk_size_ms: 音频块大小（毫秒），默认 100
        """
        self.pya = pyaudio.PyAudio()
        self.sample_rate = sample_rate
        self.chunk_size_bytes = chunk_size_ms * sample_rate * 2 // 1000

        # 初始化播放流
        self.player_stream = self.pya.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=sample_rate,
            output=True
        )

        # 双队列缓冲
        self.raw_audio_buffer: queue.Queue = queue.Queue()
        self.b64_audio_buffer: queue.Queue = queue.Queue()

        # 状态控制
        self.status_lock = threading.Lock()
        self.status = 'playing'

        # 启动处理线程
        self.decoder_thread = threading.Thread(target=self.decoder_loop, daemon=True)
        self.player_thread = threading.Thread(target=self.player_loop, daemon=True)
        self.decoder_thread.start()
        self.player_thread.start()

        # 完成事件
        self.complete_event: threading.Event = None

    def decoder_loop(self):
        """解码器循环 - 将 Base64 音频解码为原始 PCM 数据"""
        while self.status != 'stop':
            recv_audio_b64 = None
            with contextlib.suppress(queue.Empty):
                recv_audio_b64 = self.b64_audio_buffer.get(timeout=0.1)

            if recv_audio_b64 is None:
                continue

            # 解码 Base64
            recv_audio_raw = base64.b64decode(recv_audio_b64)

            # 将原始音频数据按块推入队列
            for i in range(0, len(recv_audio_raw), self.chunk_size_bytes):
                chunk = recv_audio_raw[i:i + self.chunk_size_bytes]
                self.raw_audio_buffer.put(chunk)

    def player_loop(self):
        """播放器循环 - 从队列读取 PCM 数据并播放"""
        while self.status != 'stop':
            recv_audio_raw = None
            with contextlib.suppress(queue.Empty):
                recv_audio_raw = self.raw_audio_buffer.get(timeout=0.1)

            if recv_audio_raw is None:
                # 队列为空，检查是否需要触发完成事件
                if self.complete_event:
                    self.complete_event.set()
                continue

            # 播放音频块
            self.player_stream.write(recv_audio_raw)

    def cancel_playing(self):
        """取消当前播放，清空缓冲队列"""
        self.b64_audio_buffer.queue.clear()
        self.raw_audio_buffer.queue.clear()

    def add_data(self, audio_b64: str):
        """添加 Base64 音频数据到播放队列

        Args:
            audio_b64: Base64 编码的音频数据
        """
        self.b64_audio_buffer.put(audio_b64)

    def wait_for_complete(self):
        """等待当前音频播放完成"""
        self.complete_event = threading.Event()
        self.complete_event.wait()
        self.complete_event = None

    def shutdown(self):
        """关闭音频播放器，释放资源"""
        self.status = 'stop'
        self.decoder_thread.join()
        self.player_thread.join()
        self.player_stream.close()
        self.pya.terminate()
