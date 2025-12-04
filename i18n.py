"""
Internationalization (i18n) module for Game Subtitle Reader
多语言国际化模块
"""

class I18n:
    """多语言管理类"""

    # 当前语言
    current_language = "zh_CN"  # 默认中文

    # 翻译字典
    translations = {
        "zh_CN": {
            # 窗口标题
            "app_title": "游戏字幕朗读工具 V2",
            "floating_title": "字幕朗读",

            # 状态
            "status": "状态:",
            "status_ready": "就绪",
            "status_processing": "处理中...",
            "status_error": "错误",
            "status_waiting": "等待中",

            # 配置区
            "config_settings": "配置设置",
            "voice": "语音:",
            "prompt_label": "提示词",

            # 按钮
            "btn_capture": "📸 截图并朗读",
            "btn_floating": "🎯 悬浮模式",
            "btn_save": "💾 保存截图和识别结果",
            "btn_exit": "❌ 退出",
            "btn_show_main": "📱 显示主窗口",
            "btn_language": "🌐 Language",

            # 悬浮窗
            "floating_capture": "📸\n截图",

            # 结果区
            "result_title": "📝 识别结果",
            "log_title": "📋 日志输出",

            # 日志消息
            "log_loaded": "游戏字幕朗读工具 V2 已加载",
            "log_api_model": "使用 Qwen 全模态 API (qwen3-omni-flash)",
            "log_voice": "语音:",
            "log_hotkey": "快捷键:",
            "log_hint": "提示: 点击'悬浮模式'可最小化窗口",
            "log_hotkey_enabled": "快捷键 {} 已启用",
            "log_hotkey_disabled": "快捷键已停用",
            "log_hotkey_trigger": "快捷键触发: {}",
            "log_processing": "正在处理中,请稍候...",
            "log_capturing": "截取屏幕...",
            "log_capture_done": "截图完成,大小: {} 字节",
            "log_sending_request": "发送请求到 Qwen 全模态 API...",
            "log_receiving": "接收响应...",
            "log_recognized": "识别文本: {}",
            "log_audio_size": "音频大小: {} 字节",
            "log_no_audio": "⚠️ 未接收到音频数据",
            "log_complete": "✅ 识别完成",
            "log_no_text": "⚠️ 未识别到文本内容",
            "log_playing": "播放语音...",
            "log_play_done": "播放完成！",
            "log_no_audio_play": "⚠️ 无音频数据可播放",
            "log_error": "错误: {}",
            "log_manual_trigger": "手动触发截图...",
            "log_exiting": "正在退出...",
            "log_floating_enter": "进入悬浮模式 - 双击悬浮窗返回",
            "log_floating_exit": "退出悬浮模式",
            "log_no_save_data": "没有可保存的数据",
            "log_screenshot_saved": "截图已保存: {}",
            "log_text_saved": "文本已保存: {}",
            "log_save_success": "✅ 保存成功！",
            "log_save_failed": "保存失败: {}",
            "log_api_failed": "API 请求失败: {}",
            "log_hotkey_failed": "设置快捷键失败: {}",
            "log_play_failed": "播放音频失败: {}",
            "log_language_changed": "语言已切换为: {}",

            # 提示词
            "default_prompt": "请帮我提取画面中角色的对话内容，并以角色名说：对话内容的格式输出。\n如果画面中没有对话，请回复‘未检测到对话’。",

            # 菜单
            "menu_show_main": "📱 显示主窗口",
            "menu_exit": "❌ 退出",
        },

        "en_US": {
            # Window titles
            "app_title": "Game Subtitle Reader V2",
            "floating_title": "Subtitle Reader",

            # Status
            "status": "Status:",
            "status_ready": "Ready",
            "status_processing": "Processing...",
            "status_error": "Error",
            "status_waiting": "Waiting",

            # Configuration
            "config_settings": "Configuration Settings",
            "voice": "Voice:",
            "prompt_label": "Prompt",

            # Buttons
            "btn_capture": "📸 Capture & Read",
            "btn_floating": "🎯 Floating Mode",
            "btn_save": "💾 Save Screenshot & Result",
            "btn_exit": "❌ Exit",
            "btn_show_main": "📱 Show Main Window",
            "btn_language": "🌐 语言",

            # Floating window
            "floating_capture": "📸\nCapture",

            # Result area
            "result_title": "📝 Recognition Result",
            "log_title": "📋 Log Output",

            # Log messages
            "log_loaded": "Game Subtitle Reader V2 Loaded",
            "log_api_model": "Using Qwen Multimodal API (qwen3-omni-flash)",
            "log_voice": "Voice:",
            "log_hotkey": "Hotkey:",
            "log_hint": "Tip: Click 'Floating Mode' to minimize window",
            "log_hotkey_enabled": "Hotkey {} enabled",
            "log_hotkey_disabled": "Hotkey disabled",
            "log_hotkey_trigger": "Hotkey triggered: {}",
            "log_processing": "Processing, please wait...",
            "log_capturing": "Capturing screen...",
            "log_capture_done": "Capture completed, size: {} bytes",
            "log_sending_request": "Sending request to Qwen Multimodal API...",
            "log_receiving": "Receiving response...",
            "log_recognized": "Recognized text: {}",
            "log_audio_size": "Audio size: {} bytes",
            "log_no_audio": "⚠️ No audio data received",
            "log_complete": "✅ Recognition completed",
            "log_no_text": "⚠️ No text content recognized",
            "log_playing": "Playing audio...",
            "log_play_done": "Playback completed!",
            "log_no_audio_play": "⚠️ No audio data to play",
            "log_error": "Error: {}",
            "log_manual_trigger": "Manual trigger capture...",
            "log_exiting": "Exiting...",
            "log_floating_enter": "Entered floating mode - Double click to return",
            "log_floating_exit": "Exited floating mode",
            "log_no_save_data": "No data to save",
            "log_screenshot_saved": "Screenshot saved: {}",
            "log_text_saved": "Text saved: {}",
            "log_save_success": "✅ Save successful!",
            "log_save_failed": "Save failed: {}",
            "log_api_failed": "API request failed: {}",
            "log_hotkey_failed": "Failed to setup hotkey: {}",
            "log_play_failed": "Failed to play audio: {}",
            "log_language_changed": "Language changed to: {}",

            # Default prompt
            "default_prompt": "Please extract the dialogue content of the characters in the screen and output it in the format \"Character name says: dialogue content\".\nIf there is no dialogue in the screen, please reply \"No dialogue detected\".",

            # Menu
            "menu_show_main": "📱 Show Main Window",
            "menu_exit": "❌ Exit",
        }
    }

    @classmethod
    def set_language(cls, lang_code: str):
        """设置当前语言

        Args:
            lang_code: 语言代码 ("zh_CN" 或 "en_US")
        """
        if lang_code in cls.translations:
            cls.current_language = lang_code
            return True
        return False

    @classmethod
    def get_text(cls, key: str, *args) -> str:
        """获取翻译文本

        Args:
            key: 文本键
            *args: 格式化参数

        Returns:
            翻译后的文本
        """
        lang_dict = cls.translations.get(cls.current_language, cls.translations["zh_CN"])
        text = lang_dict.get(key, key)

        # 如果有格式化参数，进行格式化
        if args:
            try:
                text = text.format(*args)
            except:
                pass

        return text

    @classmethod
    def get_current_language(cls) -> str:
        """获取当前语言代码"""
        return cls.current_language

    @classmethod
    def get_language_name(cls) -> str:
        """获取当前语言名称"""
        return "中文" if cls.current_language == "zh_CN" else "English"


# 便捷函数
def t(key: str, *args) -> str:
    """获取翻译文本的便捷函数

    Args:
        key: 文本键
        *args: 格式化参数

    Returns:
        翻译后的文本
    """
    return I18n.get_text(key, *args)
