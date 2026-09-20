# 🐾 AI Agent Table Pets — 人工智能代理桌宠

一个运行在 Windows 桌面的 AI 桌宠程序。它不只是个 GIF 动画，而是真正能"看"、能"听"、能"说话"、还能"动手"的智能体：

- 🎤 **语音对话**：你说它听，用 Whisper 本地识别 + DeepSeek 理解回复
- 👁️ **视觉感知**：看摄像头、截屏幕，用通义万相多模态理解
- 🖥️ **电脑操作**：让它"打开微信"、"搜一下天气"，它会自己写 Python 代码执行
- 🗣️ **情感配音**：GPT-SoVITS 本地合成语音，多种感情腔
- 🐕 **桌宠 GUI**：PyQt5 做的桌面悬浮窗，支持拖拽、右键菜单

---

## 架构一览

```
┌─────────────────────────────────────────────────────┐
│                     deepseek2.py                     │
│  ┌───────────┐  ┌───────────┐  ┌─────────────────┐  │
│  │ 录音 +     │  │ AI 对话   │  │ GUI 桌宠 / 托盘  │  │
│  │ VAD +      │→│ + Function │→│ PyQt5 悬浮窗    │  │
│  │ Whisper    │  │ Calling   │  │ 多进程通信      │  │
│  └───────────┘  └─────┬─────┘  └─────────────────┘  │
│                       │ 动态加载                      │
│                       ▼                              │
│  ┌─────────────────────────────────────────────────┐ │
│  │                   mods/                         │ │
│  │  see_camera │ see_screen │ do_computer │ search │ │
│  │  每个工具 = tool.json + handler.py               │ │
│  └─────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
         │                    │
         ▼                    ▼
  GPT-SoVITS 本地服务    DeepSeek / 通义万相 API
  (语音合成)             (LLM + 视觉理解)
```

**核心设计**：Function Calling 模块化。每个工具是 `mods/` 下的一个文件夹，包含：
- `tool.json` — AI 看到的工具描述（name、description、parameters）
- `handler.py` — `execute(args, context)` 实现

加新工具 = 新建文件夹 + 写两个文件，主程序不用改一行代码。

---

## 目录结构

```
正式版/
├── deepseek2.py           # 主程序入口
├── init.json              # 配置文件（API keys 等，自行填入）
├── petinit.json           # 桌宠配置（感情、GIF 映射等）
├── pet.gif                # 桌宠动画
├── test_vad.py            # 独立的 VAD 录音测试脚本
├── mods/                  # 模块化 Function Calling 工具
│   ├── __init__.py        # 自动加载器
│   ├── see_camera/        # 摄像头拍照分析
│   ├── see_screen/        # 屏幕截图分析
│   ├── do_computer/       # AI 写 Python 操作电脑
│   └── search/            # 外部信息搜索
└── fufu/
    ├── petinit.json       # 桌宠配置（fufu 角色专用）
    └── 音频=参考/         # 10 个情感参考音频（开心/悲伤/生气/骄傲...）
```

---

## 安装

### 1. 克隆仓库

```bash
git clone https://github.com/troy-git-hub/ai-agent-table-pets.git
cd ai-agent-table-pets
```

### 2. 安装 Python 依赖

项目用 Python 3.11，建议用 conda 或 venv：

```bash
pip install openai pyaudio numpy pyautogui opencv-python sounddevice soundfile whisper opencc PyQt5 Pillow oss2 requests
```

> `pyaudio` 如果安装报错，Windows 下可以先去 [PyAudio 的 Unofficial Windows Binaries](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio) 下对应版本的 `.whl`，然后 `pip install`。

### 3. 安装 GPT-SoVITS（语音合成）

下载 GPT-SoVITS v2 版本，解压到项目根目录，**文件夹名保持 `GPT-SoVITS-v2-240821`**（和 init.json 里配置一致）。你需要：
- GPT-SoVITS 代码本体
- 训练好的 `.ckpt` + `.pth` 模型权重
- `runtime/python.exe`（它自带的便携 Python 环境）

下载完成后目录结构应该是：

```
GPT-SoVITS-v2-240821/
├── runtime/python.exe
├── api.py
└── GPT_SoVITS_Inference.ipynb (不需要，主要要 api.py 和模型)
```

### 4. 配置 init.json

打开 `init.json`，把空的 API key 填上：

```json
{
  "oss": {
    "access_key_id": "你的阿里云 OSS AccessKey ID",
    "access_key_secret": "你的阿里云 OSS AccessKey Secret",
    "endpoint": "oss-cn-beijing.aliyuncs.com",
    "bucket_name": "你的 bucket 名"
  },
  "apikey": {
    "qwen_lv_api_key": "你的通义万相 API Key",
    "deepseek_api_key": "你的 DeepSeek API Key"
  }
}
```

**为什么需要 OSS？** 摄像头/屏幕截图需要上传到阿里云 OSS，拿到 URL 后通义万相的多模态 API 才能接收图片。如果不需要视觉功能，可以不配 OSS。

### 5. 配置桌宠 petinit.json

`petinit.json` 里定义了：
- `Emotions` — 支持的情感列表（如 `["开心", "悲伤", "生气", ...]`）
- `Emotionspath` — 每种情感对应的 GPT-SoVITS 参考音频路径
- `Emotionstext` — 每种情感参考音频的文本
- `gifs` — 桌宠各种状态对应的 GIF 动画路径

默认带了一套芙宁娜的参考音频，如果你想换角色，替换 `fufu/音频=参考/` 里的 wav 并更新 petinit.json 里的路径和文本即可。

---

## 运行

```bash
python deepseek2.py
```

启动后会自动：
1. 加载 Whisper `small` 模型（首次需要联网下载 ~460MB）
2. 加载频谱 VAD（无需外部模型）
3. 启动 GPT-SoVITS 本地服务（占一个新控制台窗口），并发一个"预热"请求让模型热起来
4. 弹出桌宠 GUI 悬浮窗

右键桌宠有菜单，可以调透明度、退出等。

对着麦克风说话，停顿 1 秒后自动触发识别 → AI 思考 → 语音合成 → 播放回复。

---

## Function Calling 工具开发

想加新工具？比如"查天气"：

### 第 1 步：建文件夹

```
mods/check_weather/
├── tool.json
└── handler.py
```

### 第 2 步：写 tool.json

```json
{
  "name": "check_weather",
  "description": "查询指定城市的天气",
  "parameters": {
    "type": "object",
    "properties": {
      "city": {
        "type": "string",
        "description": "城市名，如 北京、上海"
      }
    },
    "required": ["city"]
  }
}
```

### 第 3 步：写 handler.py

```python
def execute(args, context):
    city = args.get("city", "")
    # 用 context 里注入的依赖，或者自己 import
    import requests
    resp = requests.get(f"https://wttr.in/{city}?format=%C+%t").text
    return f"{city} 当前天气：{resp}"
```

### 第 4 步：在主程序注册

在 `deepseek2.py` 的 `mod_context` 字典里，如果 handler 需要用到主程序里的函数（比如截图函数、OSS 上传），就把它们作为 key-value 注入。纯自包含的工具不需要改主程序。

主程序启动时 `mods.load_tools(context=...)` 会自动扫描所有子目录，加载新工具到 TOOLS 列表。

---

## 已做的优化

| 优化 | 效果 |
|------|------|
| 跳过 Function Calling 中间回复的 TTS | 省掉工具调用期间的无效合成 |
| 流水线式 TTS（合成完一个立刻播） | 不等全部合成完再开始播，首音延迟明显缩短 |
| GPT-SoVITS 预热（启动时发一次合成请求） | 让模型常驻内存，后续合成直接用缓存 |
| Whisper 参数优化（temperature=0, fp16=False） | 更确定性，减少推理抖动 |
| 对话历史裁剪（最多保留 10 轮） | 防止上下文膨胀拖慢 API 响应 |
| 频谱 VAD（本地 FFT，不依赖外部模型） | 抗音乐干扰，区分语音/环境音 |

---

## 依赖清单

| 组件 | 用途 | 来源 |
|------|------|------|
| Python 3.11 | 运行环境 | [python.org](https://www.python.org/) |
| DeepSeek API | 主 AI 对话 + 代码 AI | [platform.deepseek.com](https://platform.deepseek.com/) |
| 通义万相 API | 图片理解（摄像头/屏幕） | [阿里云百炼](https://bailian.console.aliyun.com/) |
| 阿里云 OSS | 图片上传 | [阿里云 OSS](https://oss.console.aliyun.com/) |
| GPT-SoVITS v2 | 本地语音合成 | [GitHub 自行下载](https://github.com/RVC-Boss/GPT-SoVITS) |
| Whisper small | 本地语音识别 | `pip install whisper`，首次运行自动下载模型 |
| PyQt5 | 桌宠 GUI | `pip install PyQt5` |
| PyAudio + sounddevice | 录音/播放 | `pip install pyaudio sounddevice` |
| OpenCV + pyautogui | 摄像头/截图/电脑操作 | `pip install opencv-python pyautogui` |

---

## 常见问题

**Q: 启动后 Whisper 下载慢？**
首次会从 OpenAI CDN 下载 small 模型 ~460MB。网络差可以提前手动下载放到 `~/.cache/whisper/`。

**Q: GPT-SoVITS 启动失败？**
确认 `init.json` 里 `GPT_SOVITS_PATH` 指向的目录下有 `runtime/python.exe` 和 `api.py`。模型权重 `.ckpt` 和 `.pth` 也要放对位置。

**Q: 桌宠 GUI 拖太快消失？**
代码里已经加了窗口边界约束，如果还是有问题，检查显卡驱动或者降低拖拽速度。

**Q: `do_computer` 工具报 `string index out of range`？**
修好了。原来是 AI 没返回 Python 代码块时 `extract_code_and_text` 返回空字符串导致的，现在已经做了空列表防护。

**Q: 语音识别把音乐当说话？**
频谱 VAD 用了 300-3400Hz 语音带能量比 + 频谱质心来区分，比单纯响度判断好很多。如果电脑放的是人声歌唱，仍可能触发，这时候可以手动关掉。

---

## 项目说明

这是我花了很久时间做出来的个人桌宠项目，从硬编码的正则解析一路进化到 Function Calling 模块化。目标是让它能真正"帮我干活"——不只是聊天，而是能看、能操作、能自己写代码解决问题。

代码写得不算优雅，但每一行都是跑起来过的。有问题欢迎提 Issue，也可以自己 fork 改。

Enjoy。