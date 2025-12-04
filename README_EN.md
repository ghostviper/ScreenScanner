# Game Subtitle Reader (ScreenScanner)

A real-time game subtitle reader designed for children, which recognizes in-game dialogue through screenshots and reads it aloud, helping kids in the literacy stage understand game storylines.

## Features

- **Smart Recognition**: Uses Alibaba Cloud Qwen3-Omni multimodal AI to automatically extract dialogue content from game screens
- **Voice Reading**: Uses child-friendly Cherry voice to clearly read character dialogues
- **Floating Window Mode**: Lightweight floating button that doesn't obstruct the game screen
- **Global Hotkey**: Supports F9 hotkey trigger (works even in fullscreen games)
- **Multi-language Support**: Supports Chinese and English interface switching
- **Flexible Configuration**: Customizable voice, prompts, and other parameters
- **Real-time Feedback**: Displays recognized text and processing status

## Installation

### 1. Clone the Project

```bash
git clone <repository-url>
cd ScreenScanner
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure API Key

Create a `.env` file in the project root directory and add your Alibaba Cloud API Key:

```
DASHSCOPE_API_KEY=your_api_key_here
```

**How to Get API Key (Qwen-Omini Setup):**

1. Visit [Alibaba Cloud DashScope Console](https://dashscope.console.aliyun.com/)
2. Sign up or log in with your Alibaba Cloud account
3. Navigate to API-KEY management page
4. Click "Create API Key" and copy the generated key
5. Enable the Qwen3-Omni model in the model gallery
6. Ensure your account has sufficient balance (pay-as-you-go or prepaid)

## Usage

### Launch the Application

```bash
python game_subtitle_reader.py
```

### Two Usage Modes

#### 1. Main Window Mode
- Click the "Capture Screen" button to trigger recognition
- View recognition results and configuration options in the main window

#### 2. Floating Window Mode (Recommended)
- Click "Toggle Floating Mode" to enter floating mode
- The small window can be dragged to any position
- Drag: Hold the title bar (⋮⋮ Subtitle Reader ⋮⋮) and move
- Trigger recognition: Click the floating button or press F9 hotkey

### Operation Workflow

1. Open your game and enter a scene with dialogue
2. Launch the subtitle reader tool and switch to floating window mode
3. When dialogue appears in the game, click the floating button or press F9
4. Wait for AI recognition and voice reading of the dialogue content

## Configuration

### Voice Selection

Choose different voices in the main window:
- **Cherry** (Recommended): Child-friendly, clear and soft
- **Chelsie**: Female voice, mature and steady
- **Stella**: Female voice, lively and bright
- **Luna**: Female voice, gentle and kind

### Custom Prompts

Default prompt:
```
Please extract the dialogue content of the characters in the screen and output it in the format "Character name says: dialogue content".
If there is no dialogue in the screen, please reply "No dialogue detected".
```

You can modify the prompt to optimize recognition accuracy.

## Technology Stack

- **AI Model**: Alibaba Cloud Qwen3-Omni Flash (Multimodal Large Model)
- **Image Processing**: Pillow, MSS (High-performance screenshots)
- **Audio Playback**: PyAudio, NumPy, SoundFile
- **UI Framework**: Tkinter
- **Global Hotkey**: pynput
- **API Communication**: OpenAI SDK (Compatibility mode)

## Project Structure

```
ScreenScanner/
├── game_subtitle_reader.py    # Main program
├── config.py                   # Configuration management
├── i18n.py                     # Internationalization module
├── requirements.txt            # Dependencies list
├── qwen_omini_api.py          # API usage example
├── .env                        # API Key configuration (create manually)
├── README.md                   # Project documentation (Chinese)
└── README_EN.md                # Project documentation (English)
```

## Troubleshooting

### 1. Recognition Not Accurate?

- Ensure game dialogue text is clearly visible
- Avoid capturing too much irrelevant content in screenshots
- Try adjusting prompts to improve recognition accuracy

### 2. Hotkey Not Working?

- Confirm the application is running and not minimized to tray
- Check for conflicts with other software hotkeys
- Try running with administrator privileges (required for some games)

### 3. API Call Failed?

- Check if the API Key in `.env` file is correct
- Confirm network connection is normal
- Check if your Alibaba Cloud account has sufficient balance

## Notes

- This tool requires internet connection (calls cloud API)
- API calls will incur costs, please control usage frequency
- For personal learning and family use only, not for commercial purposes

## License

MIT License

## Feedback and Contribution

If you have any questions or suggestions, feel free to submit an Issue or Pull Request.
