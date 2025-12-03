"""
配置管理模块
"""
import os
from dotenv import load_dotenv
import dashscope
from dashscope.audio.qwen_omni import AudioFormat

# 加载环境变量
load_dotenv()


class Config:
    """应用配置类"""

    # ============ API 配置 ============
    DASHSCOPE_API_KEY = os.getenv('DASHSCOPE_API_KEY')

    # 设置全局 API Key（dashscope SDK 要求）
    if DASHSCOPE_API_KEY:
        dashscope.api_key = DASHSCOPE_API_KEY

    API_URL = "wss://dashscope.aliyuncs.com/api-ws/v1/realtime"
    MODEL = "qwen3-omni-flash-realtime"

    # ============ 快捷键配置 ============
    SCREENSHOT_HOTKEY = "<f9>"  # pynput 格式

    # ============ 语音配置 ============
    VOICE = "Cherry"  # 童音（女童）
    # 可选语音列表
    AVAILABLE_VOICES = ["Cherry", "Chelsie", "Stella", "Luna"]

    # 音频格式
    OUTPUT_AUDIO_FORMAT = AudioFormat.PCM_24000HZ_MONO_16BIT

    # ============ 提示词配置 ============
    PROMPT_TEMPLATE = (
        "你是一位实时翻译的游戏声优，你负责对画面中的对话信息进行提取和识别，请帮我提取画面中角色的对话内容，然后使用童声和中文念出对话，你只需要使用中文念出对话，不需要说额外的文字。"
        "你必须以旁白的身份念出来比如：'xxx说：xxxxx'"
    )

    # ============ 其他配置 ============
    ENABLE_LOG = True  # 是否启用日志
    LOG_LEVEL = "INFO"  # 日志级别

    @classmethod
    def validate(cls):
        """验证配置是否有效"""
        if not cls.DASHSCOPE_API_KEY:
            raise ValueError(
                "未找到 DASHSCOPE_API_KEY！\n"
                "请在 .env 文件中设置您的 API Key：\n"
                "DASHSCOPE_API_KEY=your-api-key-here"
            )

        # 确保全局 API key 已设置
        if not dashscope.api_key:
            dashscope.api_key = cls.DASHSCOPE_API_KEY

        print(f"[Config] API Key 已加载: {cls.DASHSCOPE_API_KEY[:10]}...")
        return True
