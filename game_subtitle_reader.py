"""
游戏字幕朗读工具 V2 - 使用全模态 API
为小孩子提供游戏对话的语音阅读功能
"""
import os
import sys
import base64
import time
import threading
import io
import tkinter as tk
from tkinter import ttk, scrolledtext
import mss
from PIL import Image, ImageDraw
from pynput import keyboard
import numpy as np
from openai import OpenAI

from config import Config
from i18n import I18n, t


class FloatingWindow:
    """悬浮窗口 - 小巧的可拖动窗口（优化拖动体验）"""

    def __init__(self, parent_app):
        """初始化悬浮窗口"""
        self.parent_app = parent_app
        self.window = tk.Toplevel()
        self.window.title(t("floating_title"))

        # 窗口设置
        self.window.geometry("100x120+100+100")
        self.window.attributes('-topmost', True)  # 始终置顶
        self.window.attributes('-alpha', 0.9)  # 半透明
        self.window.overrideredirect(True)  # 无边框

        # 拖动相关变量
        self.offset_x = 0
        self.offset_y = 0
        self.is_dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0

        # 创建主框架
        main_frame = tk.Frame(
            self.window,
            bg="#2196F3",
            relief=tk.RAISED,
            borderwidth=2
        )
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 标题栏（用于拖动）
        self.title_bar = tk.Label(
            main_frame,
            text=f"⋮⋮ {t('floating_title')} ⋮⋮",
            font=("Arial", 8),
            bg="#1976D2",
            fg="white",
            cursor="fleur"  # 拖动光标
        )
        self.title_bar.pack(fill=tk.X)

        # 绑定标题栏拖动事件
        self.title_bar.bind('<Button-1>', self.start_drag)
        self.title_bar.bind('<B1-Motion>', self.do_drag)
        self.title_bar.bind('<ButtonRelease-1>', self.end_drag)

        # 按钮容器
        button_frame = tk.Frame(main_frame, bg="#2196F3")
        button_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=(5, 5))

        # 截图按钮（使用 Label 模拟，避免 Button 的 command 冲突）
        self.capture_btn = tk.Label(
            button_frame,
            text=t("floating_capture"),
            font=("Arial", 12, "bold"),
            bg="#4CAF50",
            fg="white",
            relief=tk.RAISED,
            cursor="hand2",
            borderwidth=2
        )
        self.capture_btn.pack(fill=tk.BOTH, expand=True)

        # 按钮交互效果
        self.capture_btn.bind('<Button-1>', self.on_button_press)
        self.capture_btn.bind('<ButtonRelease-1>', self.on_button_release)
        self.capture_btn.bind('<Enter>', lambda e: self.capture_btn.config(relief=tk.RAISED, borderwidth=3))
        self.capture_btn.bind('<Leave>', lambda e: self.capture_btn.config(relief=tk.RAISED, borderwidth=2))

        # 双击返回主窗口
        self.capture_btn.bind('<Double-Button-1>', self.on_double_click)

        # 右键菜单
        self.menu = tk.Menu(self.window, tearoff=0)
        self.menu.add_command(label=t("menu_show_main"), command=self.show_main_window)
        self.menu.add_separator()
        self.menu.add_command(label=t("menu_exit"), command=self.parent_app.on_exit)

        self.window.bind('<Button-3>', self.show_menu)
        self.title_bar.bind('<Button-3>', self.show_menu)
        self.capture_btn.bind('<Button-3>', self.show_menu)

        # 状态指示器
        self.status_indicator = tk.Label(
            main_frame,
            text="●",
            font=("Arial", 10),
            bg="#2196F3",
            fg="#4CAF50"
        )
        self.status_indicator.place(relx=0.95, rely=0.15, anchor='ne')

    def start_drag(self, event):
        """开始拖动"""
        self.offset_x = event.x_root - self.window.winfo_x()
        self.offset_y = event.y_root - self.window.winfo_y()
        self.drag_start_x = event.x_root
        self.drag_start_y = event.y_root
        self.is_dragging = False

    def do_drag(self, event):
        """执行拖动"""
        # 计算移动距离
        dx = abs(event.x_root - self.drag_start_x)
        dy = abs(event.y_root - self.drag_start_y)

        # 如果移动超过 5 像素，认为是拖动
        if dx > 5 or dy > 5:
            self.is_dragging = True

        x = event.x_root - self.offset_x
        y = event.y_root - self.offset_y
        self.window.geometry(f"+{x}+{y}")

    def end_drag(self, event):
        """结束拖动"""
        # 重置拖动标志
        self.is_dragging = False

    def on_button_press(self, event):
        """按钮按下"""
        self.capture_btn.config(relief=tk.SUNKEN)
        self.drag_start_x = event.x_root
        self.drag_start_y = event.y_root

    def on_button_release(self, event):
        """按钮释放"""
        self.capture_btn.config(relief=tk.RAISED)

        # 计算移动距离
        dx = abs(event.x_root - self.drag_start_x)
        dy = abs(event.y_root - self.drag_start_y)

        # 只有移动距离小于 5 像素才算点击
        if dx < 5 and dy < 5:
            self.on_capture()

    def on_capture(self):
        """截图按钮点击"""
        self.set_processing(True)
        threading.Thread(
            target=self.parent_app.process_screenshot,
            daemon=True
        ).start()

    def on_double_click(self, event):
        """双击返回主窗口"""
        self.show_main_window()

    def show_main_window(self):
        """显示主窗口"""
        self.window.withdraw()
        self.parent_app.root.deiconify()
        self.parent_app.is_floating = False

    def show_menu(self, event):
        """显示右键菜单"""
        try:
            self.menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu.grab_release()

    def set_processing(self, is_processing):
        """设置处理状态指示"""
        if is_processing:
            self.status_indicator.config(fg="orange")
            self.capture_btn.config(bg="#FF9800")  # 处理中变橙色
        else:
            self.status_indicator.config(fg="#4CAF50")
            self.capture_btn.config(bg="#4CAF50")  # 恢复绿色

    def update_language(self):
        """更新语言"""
        self.window.title(t("floating_title"))
        self.title_bar.config(text=f"⋮⋮ {t('floating_title')} ⋮⋮")
        self.capture_btn.config(text=t("floating_capture"))
        # 更新菜单
        self.menu.entryconfig(0, label=t("menu_show_main"))
        self.menu.entryconfig(2, label=t("menu_exit"))

    def close(self):
        """关闭悬浮窗口"""
        self.window.destroy()


class ScreenshotHandler:
    """处理屏幕截图"""

    @staticmethod
    def capture_screen(max_size=1280, quality=85) -> bytes:
        """截取屏幕并返回压缩后的 JPEG 字节"""
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            screenshot = sct.grab(monitor)
            img = Image.frombytes('RGB', screenshot.size, screenshot.rgb)

            # 压缩图像
            width, height = img.size
            if max(width, height) > max_size:
                if width > height:
                    new_width = max_size
                    new_height = int(height * (max_size / width))
                else:
                    new_height = max_size
                    new_width = int(width * (max_size / height))
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            img_bytes = io.BytesIO()
            img.save(img_bytes, format='JPEG', quality=quality, optimize=True)
            return img_bytes.getvalue()

    @staticmethod
    def image_to_base64(image_bytes: bytes) -> str:
        """图像字节转 Base64"""
        return base64.b64encode(image_bytes).decode('ascii')


class AudioPlayer:
    """音频播放器 - 实时播放 WAV 格式音频"""

    def __init__(self):
        """初始化音频播放器"""
        import pyaudio
        self.pya = pyaudio.PyAudio()
        self.sample_rate = 24000  # Qwen 输出 24kHz
        self.audio_buffer = []
        self.is_playing = False

    def play_wav_audio(self, wav_bytes: bytes):
        """播放 WAV 格式音频"""
        try:
            # 解码 WAV 字节为 PCM 数据
            audio_np = np.frombuffer(wav_bytes, dtype=np.int16)

            # 打开播放流
            stream = self.pya.open(
                format=self.pya.get_format_from_width(2),  # 16-bit
                channels=1,
                rate=self.sample_rate,
                output=True
            )

            # 播放音频
            self.is_playing = True
            stream.write(audio_np.tobytes())
            stream.stop_stream()
            stream.close()
            self.is_playing = False

        except Exception as e:
            print(t("log_play_failed", e))

    def shutdown(self):
        """关闭音频播放器"""
        if self.pya:
            self.pya.terminate()


class QwenMultimodalHandler:
    """处理 Qwen 全模态 API 调用"""

    def __init__(self, config: Config, log_callback=None):
        """初始化 API 处理器"""
        self.config = config
        self.log_callback = log_callback
        self.client = OpenAI(
            api_key=config.DASHSCOPE_API_KEY,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        self.recognized_text = ""

    def log(self, message: str):
        """记录日志"""
        if self.log_callback:
            self.log_callback(message)
        else:
            print(f"[QwenAPI] {message}")

    def log_t(self, key: str, *args):
        """记录翻译后的日志"""
        message = t(key, *args)
        self.log(message)

    def process_image_and_prompt(self, image_b64: str, prompt: str):
        """处理图像和提示词，返回文本和音频

        Args:
            image_b64: Base64 编码的图像
            prompt: 文本提示词

        Returns:
            (recognized_text, audio_bytes): 识别的文本和音频字节
        """
        try:
            self.log_t("log_sending_request")

            # 构建消息
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_b64}"
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]

            # 发起流式请求
            completion = self.client.chat.completions.create(
                model="qwen3-omni-flash",
                messages=messages,
                modalities=["text", "audio"],  # 输出文本和音频
                audio={"voice": self.config.VOICE, "format": "wav"},
                stream=True,
                stream_options={"include_usage": True},
            )

            # 处理流式响应
            self.log_t("log_receiving")
            text_parts = []
            audio_base64_string = ""

            for chunk in completion:
                # 处理文本部分
                if chunk.choices and chunk.choices[0].delta.content:
                    text_part = chunk.choices[0].delta.content
                    text_parts.append(text_part)
                    self.log_t("log_recognized", text_part)

                # 收集音频部分
                if (chunk.choices and
                    hasattr(chunk.choices[0].delta, "audio") and
                    chunk.choices[0].delta.audio):
                    audio_data = chunk.choices[0].delta.audio.get("data", "")
                    if audio_data:
                        audio_base64_string += audio_data

            # 合并文本
            recognized_text = "".join(text_parts)
            self.recognized_text = recognized_text

            # 解码音频
            audio_bytes = None
            if audio_base64_string:
                audio_bytes = base64.b64decode(audio_base64_string)
                self.log_t("log_audio_size", len(audio_bytes))
            else:
                self.log_t("log_no_audio")

            return recognized_text, audio_bytes

        except Exception as e:
            self.log_t("log_api_failed", e)
            raise


class GameSubtitleReaderApp:
    """主应用程序"""

    def __init__(self):
        """初始化应用"""
        self.config = Config()

        # 验证配置
        try:
            self.config.validate()
        except ValueError as e:
            print(f"配置错误: {e}")
            sys.exit(1)

        # 初始化组件
        self.audio_player = AudioPlayer()
        self.api_handler = QwenMultimodalHandler(self.config, self.log)
        self.screenshot_handler = ScreenshotHandler()

        # 状态
        self.is_processing = False
        self.is_floating = False  # 是否处于悬浮模式

        # GUI 组件
        self.root = None
        self.status_label = None
        self.log_text = None
        self.result_text = None
        self.prompt_text = None
        self.floating_window = None  # 悬浮窗口

        # 快捷键监听器
        self.hotkey_listener = None

        # 保存最后的结果
        self.last_screenshot = None
        self.last_recognized_text = ""

    # ============ 核心处理流程 ============

    def process_screenshot(self):
        """主处理流程：截图 → API → 播放"""
        if self.is_processing:
            self.log(t("log_processing"))
            return

        self.is_processing = True
        self.update_status(t("status_processing"))

        try:
            # 1. 截图
            self.log(t("log_capturing"))
            image_bytes = self.screenshot_handler.capture_screen()
            image_b64 = self.screenshot_handler.image_to_base64(image_bytes)
            self.log(t("log_capture_done", len(image_bytes)))
            self.last_screenshot = image_bytes

            # 2. 发送到 API 并获取结果
            prompt = self.prompt_text.get('1.0', tk.END).strip()
            recognized_text, audio_bytes = self.api_handler.process_image_and_prompt(
                image_b64, prompt
            )

            # 3. 显示识别结果
            if recognized_text:
                self.last_recognized_text = recognized_text
                self.display_result(recognized_text)
                self.log(t("log_complete"))
            else:
                self.log(t("log_no_text"))

            # 4. 播放音频
            if audio_bytes:
                self.log(t("log_playing"))
                self.audio_player.play_wav_audio(audio_bytes)
                self.log(t("log_play_done"))
            else:
                self.log(t("log_no_audio_play"))

            self.update_status(t("status_waiting"))

        except Exception as e:
            self.log(t("log_error", e))
            self.update_status(t("status_error"))

        finally:
            self.is_processing = False
            # 更新悬浮窗口状态
            if self.floating_window:
                self.floating_window.set_processing(False)

    def display_result(self, text: str):
        """在结果区域显示识别文本"""
        if self.result_text:
            self.result_text.config(state=tk.NORMAL)
            self.result_text.delete('1.0', tk.END)
            self.result_text.insert('1.0', text)
            self.result_text.config(state=tk.DISABLED)

    def save_results(self):
        """保存截图和识别结果"""
        if not self.last_screenshot and not self.last_recognized_text:
            self.log(t("log_no_save_data"))
            return

        try:
            save_dir = "saved_results"
            os.makedirs(save_dir, exist_ok=True)
            timestamp = time.strftime("%Y%m%d_%H%M%S")

            if self.last_screenshot:
                image_path = os.path.join(save_dir, f"screenshot_{timestamp}.png")
                with open(image_path, 'wb') as f:
                    f.write(self.last_screenshot)
                self.log(t("log_screenshot_saved", image_path))

            if self.last_recognized_text:
                text_path = os.path.join(save_dir, f"text_{timestamp}.txt")
                with open(text_path, 'w', encoding='utf-8') as f:
                    f.write(self.last_recognized_text)
                self.log(t("log_text_saved", text_path))

            self.log(t("log_save_success"))

        except Exception as e:
            self.log(t("log_save_failed", e))

    def toggle_floating_mode(self):
        """切换悬浮模式"""
        if self.is_floating:
            # 退出悬浮模式
            if self.floating_window:
                self.floating_window.close()
                self.floating_window = None
            self.root.deiconify()
            self.is_floating = False
            self.log(t("log_floating_exit"))
        else:
            # 进入悬浮模式
            self.root.withdraw()  # 隐藏主窗口
            self.floating_window = FloatingWindow(self)
            self.is_floating = True
            self.log(t("log_floating_enter"))

    def setup_hotkey(self):
        """设置全局快捷键"""
        if self.hotkey_listener:
            return  # 已经设置

        try:
            hotkey_str = self.config.SCREENSHOT_HOTKEY

            def on_activate():
                """快捷键触发回调"""
                self.log(t("log_hotkey_trigger", hotkey_str))
                threading.Thread(target=self.process_screenshot, daemon=True).start()

            # 解析快捷键
            hotkey_combo = keyboard.HotKey(
                keyboard.HotKey.parse(hotkey_str),
                on_activate
            )

            # 创建监听器
            self.hotkey_listener = keyboard.Listener(
                on_press=lambda key: hotkey_combo.press(self.hotkey_listener.canonical(key)),
                on_release=lambda key: hotkey_combo.release(self.hotkey_listener.canonical(key))
            )
            self.hotkey_listener.start()
            self.log(t("log_hotkey_enabled", hotkey_str))

        except Exception as e:
            self.log(t("log_hotkey_failed", e))

    def stop_hotkey(self):
        """停止快捷键监听"""
        if self.hotkey_listener:
            self.hotkey_listener.stop()
            self.hotkey_listener = None
            self.log(t("log_hotkey_disabled"))

    # ============ GUI 相关 ============

    def create_gui(self):
        """创建 tkinter GUI"""
        self.root = tk.Tk()
        self.root.title(t("app_title"))
        self.root.geometry("550x700")

        # 状态显示
        status_frame = tk.Frame(self.root, bg="#f0f0f0", pady=10)
        status_frame.pack(fill=tk.X)

        self.status_text_label = tk.Label(
            status_frame,
            text=t("status"),
            font=("Arial", 12),
            bg="#f0f0f0"
        )
        self.status_text_label.pack(side=tk.LEFT, padx=(20, 5))

        self.status_label = tk.Label(
            status_frame,
            text=t("status_ready"),
            font=("Arial", 12, "bold"),
            fg="green",
            bg="#f0f0f0"
        )
        self.status_label.pack(side=tk.LEFT)

        # 语言切换按钮（右侧）
        self.language_btn = tk.Button(
            status_frame,
            text=t("btn_language"),
            command=self.toggle_language,
            font=("Arial", 9),
            bg="#9C27B0",
            fg="white",
            cursor="hand2"
        )
        self.language_btn.pack(side=tk.RIGHT, padx=(5, 20))

        # 配置区
        self.config_frame = tk.LabelFrame(
            self.root,
            text=t("config_settings"),
            font=("Arial", 11, "bold"),
            padx=15,
            pady=10
        )
        self.config_frame.pack(padx=15, pady=10, fill=tk.BOTH)

        # 语音选择
        voice_frame = tk.Frame(self.config_frame)
        voice_frame.pack(fill=tk.X, pady=5)
        self.voice_label = tk.Label(voice_frame, text=t("voice"), width=8, anchor='w')
        self.voice_label.pack(side=tk.LEFT)
        voice_var = tk.StringVar(value=self.config.VOICE)
        voice_combo = ttk.Combobox(
            voice_frame,
            textvariable=voice_var,
            values=self.config.AVAILABLE_VOICES,
            width=12,
            state='readonly'
        )
        voice_combo.pack(side=tk.LEFT, padx=5)

        # 提示词编辑
        self.prompt_frame = tk.LabelFrame(
            self.config_frame,
            text=t("prompt_label"),
            font=("Arial", 9),
            padx=5,
            pady=5
        )
        self.prompt_frame.pack(fill=tk.BOTH, pady=10)

        self.prompt_text = tk.Text(self.prompt_frame, height=4, wrap=tk.WORD, font=("Arial", 9))
        self.prompt_text.insert('1.0', self.config.PROMPT_TEMPLATE)
        self.prompt_text.pack(fill=tk.BOTH)

        # 按钮区域
        button_row1 = tk.Frame(self.root)
        button_row1.pack(pady=10, padx=20, fill=tk.X)

        # 手动触发按钮
        self.capture_btn_main = tk.Button(
            button_row1,
            text=t("btn_capture"),
            command=self.on_manual_trigger,
            font=("Arial", 11, "bold"),
            bg="#4CAF50",
            fg="white",
            height=2
        )
        self.capture_btn_main.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=(0, 5))

        # 悬浮模式按钮
        self.floating_btn = tk.Button(
            button_row1,
            text=t("btn_floating"),
            command=self.toggle_floating_mode,
            font=("Arial", 11, "bold"),
            bg="#FF9800",
            fg="white",
            height=2
        )
        self.floating_btn.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=(5, 0))

        # 识别结果显示区
        self.result_frame = tk.LabelFrame(
            self.root,
            text=t("result_title"),
            font=("Arial", 11, "bold"),
            padx=5,
            pady=5
        )
        self.result_frame.pack(padx=15, pady=10, fill=tk.BOTH)

        self.result_text = scrolledtext.ScrolledText(
            self.result_frame,
            height=4,
            state=tk.DISABLED,
            font=("Microsoft YaHei", 11),
            wrap=tk.WORD,
            bg="#f9f9f9"
        )
        self.result_text.pack(fill=tk.BOTH)

        # 保存按钮
        self.save_btn = tk.Button(
            self.root,
            text=t("btn_save"),
            command=self.save_results,
            font=("Arial", 10),
            bg="#2196F3",
            fg="white"
        )
        self.save_btn.pack(pady=5, padx=20, fill=tk.X)

        # 日志输出区
        self.log_frame = tk.LabelFrame(
            self.root,
            text=t("log_title"),
            font=("Arial", 11, "bold"),
            padx=5,
            pady=5
        )
        self.log_frame.pack(padx=15, pady=10, fill=tk.BOTH, expand=True)

        self.log_text = scrolledtext.ScrolledText(
            self.log_frame,
            height=8,
            state=tk.DISABLED,
            font=("Consolas", 9),
            wrap=tk.WORD
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # 控制按钮
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        self.exit_btn = tk.Button(
            button_frame,
            text=t("btn_exit"),
            command=self.on_exit,
            width=12,
            font=("Arial", 10),
            bg="#f44336",
            fg="white"
        )
        self.exit_btn.pack(side=tk.LEFT, padx=5)

        # 初始日志
        self.log("=" * 50)
        self.log(t("log_loaded"))
        self.log(t("log_api_model"))
        self.log(f"{t('log_voice')} {self.config.VOICE}")
        self.log(f"{t('log_hotkey')} {self.config.SCREENSHOT_HOTKEY}")
        self.log(t("log_hint"))
        self.log("=" * 50)

        # 自动启用快捷键
        self.setup_hotkey()

    # ============ 事件处理 ============

    def on_manual_trigger(self):
        """手动触发按钮"""
        self.log(t("log_manual_trigger"))
        threading.Thread(target=self.process_screenshot, daemon=True).start()

    def toggle_language(self):
        """切换语言"""
        # 切换语言
        current = I18n.get_current_language()
        new_lang = "en_US" if current == "zh_CN" else "zh_CN"
        I18n.set_language(new_lang)

        # 更新所有界面文本
        self.update_ui_language()

        # 记录日志
        lang_name = I18n.get_language_name()
        self.log(t("log_language_changed", lang_name))

    def update_ui_language(self):
        """更新界面语言"""
        # 更新窗口标题
        self.root.title(t("app_title"))

        # 更新状态区
        self.status_text_label.config(text=t("status"))
        status_text = self.status_label.cget("text")
        if "就绪" in status_text or "Ready" in status_text:
            self.status_label.config(text=t("status_ready"))
        elif "处理" in status_text or "Processing" in status_text:
            self.status_label.config(text=t("status_processing"))
        elif "等待" in status_text or "Waiting" in status_text:
            self.status_label.config(text=t("status_waiting"))
        elif "错误" in status_text or "Error" in status_text:
            self.status_label.config(text=t("status_error"))

        # 更新语言按钮
        self.language_btn.config(text=t("btn_language"))

        # 更新配置区
        self.config_frame.config(text=t("config_settings"))
        self.voice_label.config(text=t("voice"))
        self.prompt_frame.config(text=t("prompt_label"))

        # 更新按钮
        self.capture_btn_main.config(text=t("btn_capture"))
        self.floating_btn.config(text=t("btn_floating"))
        self.save_btn.config(text=t("btn_save"))
        self.exit_btn.config(text=t("btn_exit"))

        # 更新结果和日志区
        self.result_frame.config(text=t("result_title"))
        self.log_frame.config(text=t("log_title"))

        # 更新悬浮窗口（如果存在）
        if self.floating_window:
            self.floating_window.update_language()

    def on_exit(self):
        """退出按钮"""
        try:
            # 停止快捷键
            self.stop_hotkey()

            # 关闭悬浮窗口
            if self.floating_window:
                self.floating_window.close()

            # 关闭音频播放器
            self.audio_player.shutdown()

            self.log(t("log_exiting"))
            self.root.quit()
            self.root.destroy()
        except Exception as e:
            print(f"Exit error: {e}")
            sys.exit(0)

    # ============ 辅助方法 ============

    def update_status(self, status: str):
        """更新状态显示"""
        if self.status_label:
            self.status_label.config(text=status)
            # 根据状态内容判断颜色
            if "Processing" in status or "处理" in status:
                self.status_label.config(fg="orange")
            elif "Error" in status or "错误" in status:
                self.status_label.config(fg="red")
            else:
                self.status_label.config(fg="green")

    def log(self, message: str):
        """添加日志"""
        if self.log_text:
            self.log_text.config(state=tk.NORMAL)
            timestamp = time.strftime("%H:%M:%S")
            self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
            self.log_text.see(tk.END)
            self.log_text.config(state=tk.DISABLED)

        # 输出到控制台
        try:
            print(f"[{time.strftime('%H:%M:%S')}] {message}")
        except UnicodeEncodeError:
            safe_message = message.encode('ascii', 'replace').decode('ascii')
            print(f"[{time.strftime('%H:%M:%S')}] {safe_message}")

    # ============ 运行 ============

    def run(self):
        """启动应用"""
        self.create_gui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_exit)
        self.root.mainloop()


# ============ 入口 ============
if __name__ == '__main__':
    # 设置控制台编码为 UTF-8（Windows）
    if sys.platform == 'win32':
        try:
            import codecs
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'ignore')
            sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'ignore')
        except:
            pass

    print("=" * 50)
    print("游戏字幕朗读工具 V2")
    print("使用 Qwen 全模态 API")
    print("=" * 50)

    app = GameSubtitleReaderApp()
    app.run()
