import subprocess
import os
import time
import queue
from tkinter import messagebox
from openai import OpenAI
import json
import pyaudio
import numpy as np
import re
import oss2
from datetime import datetime
import uuid
import pyautogui
import random
import cv2
import subprocess
import time
import requests
import sounddevice as sd
import soundfile as sf
import threading 
import whisper 
import opencc
import collections
from datetime import datetime, timedelta
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QMenu, QAction, QDialog, QPushButton, QLineEdit, QVBoxLayout, QGraphicsDropShadowEffect, QSystemTrayIcon, QStyle, QSlider, QHBoxLayout, QTextEdit
from PyQt5.QtGui import QPixmap, QFont, QIcon
from PyQt5.QtCore import Qt, QTimer
from PIL import Image, ImageSequence
from io import BytesIO
import tempfile
import sys
from multiprocessing import Process, Manager
import pickle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mods

#=======================================================#


# 读取配置文件
with open('init.json', 'r',encoding='utf-8') as file:
    config = json.load(file)

# 使用配置
ACCESS_KEY_ID = config['oss']['access_key_id']
ACCESS_KEY_SECRET = config['oss']['access_key_secret']
ENDPOINT = config['oss']['endpoint']
BUCKET_NAME = config['oss']['bucket_name']
qwenLVapikey = config['apikey']['qwen_lv_api_key']
deepseekapikey= config['apikey']['deepseek_api_key']
petjson=config['petjson']

#=======================================================#
with open(petjson, 'r',encoding='utf-8') as file:
    configpet = json.load(file)

Emotions=configpet["Emotions"]
Emotionspath=configpet["Emotionspath"]
Emotionstext=configpet["Emotionstext"]
gifs=configpet['gifs']
systemEmotions=configpet['systemEmotions']
deepseekagentairead=configpet['deepseekagentai']


#=======================================================#
aiagentsystem="不要回复太多字，不要使用特殊字符。用户使用的是语音识别，避免不了一些奇怪的问题，所以你回答时要仔细理解问题，回答中不要提语音识别有识别错误和有问题的地方，用户问题的语言还可能是繁体中文，你会的用户的一定是简体中文。你可以使用以下工具函数来完成某些操作：\n- see_camera: 调用摄像头拍照片并分析，了解主人当前状态\n- see_screen: 截取屏幕画面并分析，了解主人在做什么\n- do_computer: 执行电脑操作，如打开软件、搜索文件等\n- search: 搜索外部信息，如天气、新闻等\n\n当你需要使用这些工具时，请直接调用对应的函数，系统会将结果返回给你，你再根据结果回答主人。在你回答中，你需要在每句话前加入你认为朗读时需要的感情，你有这些感情："+systemEmotions+"。你只能用前面的感情，不能再创造一个出来,这更重要，不能违反。感情加在对应的那句话前面，用[]包裹，回答中至少一个感情，一到两个逗号或句号前面的话算一个句子，每个句子都要有一个感情。使用示例：[开心]今天我吃到了美味的小蛋糕。[伤心]可明天就要考试了，我还没复习，[伤心]又要被老师骂了。"
deepseekagentai=deepseekagentairead+aiagentsystem
deepseekcodeai="你是一个写代码的AI，用户的电脑是windows11，你的要求就是按照用户的需求写出python语言，代码中不要有假设的信息，代码一定要套在```python和```中间。你要在代码的前面加一些代码的解释，不是代码里，就是你用的重要的函数函数，不要超过40字，代码后面就不要加文字，每次你的代码运行后我都会告诉你运行的结果，你要根据运行的结果更改代码，所以你可以在不知道用户代码要用到的重要信息时可以通过写代码来获取信息，假如用户让你打开Edge游览器，你不知道Edge浏览器装在哪时，你可以先扫描桌面快捷方式，再打开主程序，你每一次写完代码后都要先检查一下任务是否完成，就是检测一下Edge游览器是否在任务管理器中有进程，防止多次打开，如果你的程序设么也没输出，有可能Edge已经打开了，每次判断要考虑极端情况。如果你觉得你写的这个你写的代码已经达到用户的目的，你就在你前面介绍的字符中末尾加上[成功]，[成功]不要第一次就加上，你多试几次，真正成功了在加上[成功]，不要一直在那试，如果你这次成功了，你也不要总结代码；这个如果你经过多次尝试，觉得做不到用户的请求，先尽力解决问题，实在做不到你就在你前面介绍的字符中末尾加上[失败]。[成功]和[失败]都是在介绍里加的，不是在你的python代码里的注释里加的，千万不要加在注释代码中，代码中也不要加注释，你注释中说的都放到前面的解释中"
qwenLVcameraai="你是一个分析图片的AI，我发给你的图片图片是用户摄像头拍的一张照片，你要描述这张图片中的人物的心情以及一些关键的东西，尽量说详细一点，你的识别结果会发给另一个ai，相当于你当一个眼睛，另一个ai当嘴巴,数据库直接传给另一个ai你不要去问他一些奇怪的问题不然另一个ai会报错"
qwenLVscreenai="你是一个分析图片的AI，我发给你的图片是一台windows11电脑的屏幕截图，你要描述这张图片中的主人在干嘛和屏幕上比较重要的东西，尽量说详细一点你的识别结果会发给另一个ai，相当于你当一个眼睛，另一个ai当嘴巴,数据库直接传给另一个ai你不要去问他一些奇怪的问题不然另一个ai会报错"

#=======================================================#

client = OpenAI(api_key=deepseekapikey
                , base_url="https://api.deepseek.com")
messages=[{"role": "system", "content": deepseekagentai}]#talk 

client_talt1 = OpenAI(api_key=deepseekapikey,
                       base_url="https://api.deepseek.com")
messagestalk1=[{"role": "system", "content":deepseekcodeai}]#talt1

#=======================================================#
# 频谱 VAD —— 基于频谱特征区分人声与音乐/噪声
# 核心原理：人声能量集中在 300-3400Hz，音乐频谱更宽
# 通过频带能量比 + 频谱质心 + 自适应阈值 综合判断

class SpectralVAD:
    """基于频谱特征的语音活动检测（比 webrtcvad 更精准区分人声/音乐）"""

    SPEECH_LOW = 300
    SPEECH_HIGH = 3400
    MUSIC_HIGH = 6000

    def __init__(self, sampling_rate=16000):
        self.sampling_rate = sampling_rate
        self.window_size = 512
        self.eps = 1e-10
        self.energy_floor = 0.002
        self.alpha = 0.1
        self.noise_floor = 0.01
        self.speech_strength = 0.0
        self.smoothing_window = []
        self.smoothing_max = 5

    def reset(self):
        self.noise_floor = 0.01
        self.speech_strength = 0.0
        self.smoothing_window = []

    def _compute_features(self, audio_float):
        """计算频谱特征： speech_band_ratio + spectral_centroid + rms"""
        n = len(audio_float)
        if n < 64:
            return 0.0, 0.0, 0.0
        windowed = audio_float * np.hanning(n).astype(np.float32)
        spectrum = np.abs(np.fft.rfft(windowed))
        freqs = np.fft.rfftfreq(n, d=1.0 / self.sampling_rate)

        total_energy = np.sum(spectrum ** 2) + self.eps
        speech_mask = (freqs >= self.SPEECH_LOW) & (freqs <= self.SPEECH_HIGH)
        speech_energy = np.sum((spectrum[speech_mask]) ** 2)
        speech_ratio = speech_energy / total_energy

        weighted_sum = np.sum(freqs * (spectrum ** 2))
        spectral_centroid = weighted_sum / total_energy

        rms = np.sqrt(np.mean(audio_float ** 2))
        return speech_ratio, spectral_centroid, rms

    def is_speech(self, audio_bytes, sample_rate=None):
        if sample_rate is None:
            sample_rate = self.sampling_rate
        audio = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
        if len(audio) < 64:
            return False, {}
        audio = audio[:self.window_size]

        speech_ratio, centroid, rms = self._compute_features(audio)

        self.noise_floor = self.alpha * rms + (1 - self.alpha) * self.noise_floor
        snr = rms / (self.noise_floor + self.eps)

        speech_score = 0.0
        if snr > 1.5:
            speech_score += 0.3
        if snr > 3.0:
            speech_score += 0.2

        if speech_ratio > 0.5:
            speech_score += 0.3
        elif speech_ratio > 0.4:
            speech_score += 0.15

        if centroid < 2500:
            speech_score += 0.2
        elif centroid < 3500:
            speech_score += 0.1

        self.smoothing_window.append(speech_score)
        if len(self.smoothing_window) > self.smoothing_max:
            self.smoothing_window.pop(0)
        smoothed = sum(self.smoothing_window) / len(self.smoothing_window)

        self.speech_strength = 0.7 * self.speech_strength + 0.3 * smoothed
        strength = self.speech_strength

        features = {
            'rms': rms,
            'sr': speech_ratio,
            'centroid': centroid,
            'snr': snr,
            'score': speech_score,
            'smoothed': smoothed,
            'strength': strength,
        }
        return strength > 0.45, features

#=======================================================#
# Function Calling 模块化工具
TOOLS = []
MAX_TOOL_ITERATIONS = 5

def init_mod_tools(context):
    """初始化模块化工具，返回 TOOLS 列表"""
    global TOOLS
    tool_defs, dispatch = mods.load_tools(context=context)
    TOOLS = tool_defs
    return TOOLS

#=======================================================#

# GPT-SoVITS服务启动配置
GPT_SOVITS_PATH = config['GPT-SOVITS']["GPT_SOVITS_PATH"]
PYTHON_EXE = config['GPT-SOVITS']["PYTHON_EXE"]
CKPT_PATH = configpet["CKPT_PATH"]
PTH_PATH = configpet["PTH_PATH"]
#开心，生气，伤心，正常，骄傲
Emotions=configpet['Emotions']
Emotionspath=configpet['Emotionspath']
Emotionstext=configpet['Emotionstext']
gifs=configpet['gifs']

#=======================================================#
class TextInputDialog(QDialog):
    def __init__(self, shared_vars, parent=None):
        super().__init__(parent)
        self.setWindowTitle("文字输入")
        self.shared_vars = shared_vars

        layout = QVBoxLayout(self)

        self.input_box = QLineEdit(self)
        self.send_button = QPushButton("发送", self)
        self.send_button.clicked.connect(self.on_send_click)

        layout.addWidget(self.input_box)
        layout.addWidget(self.send_button)

        self.setLayout(layout)

    def on_send_click(self):
        current_text = self.input_box.text()
        if self.shared_vars.text_input is None and current_text.strip():
            # 更新共享变量
            self.shared_vars.text_input = current_text
            # 清空输入框
            self.input_box.clear()
        else:
            # 如果共享变量已有内容或输入为空，则不执行任何操作
            pass


class DesktopPetApp(QWidget):
    def __init__(self, gifs, shared_vars):
        super().__init__()
        self.setWindowTitle('会动的小宠物')
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowOpacity(1.0)

        # 共享变量引用
        self.shared_vars = shared_vars

        self.draggable = True
        self.locked = False
        self.offset = None

        self.resize(300, 350)  # 增加高度以容纳输入框和按钮
        self.move(300, 300)

        self._ensure_on_screen()

        self.frames = []
        self.current_frame = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.next_frame)

        self.label = QLabel(self)
        layout = QVBoxLayout()
        layout.addWidget(self.label)

        self.setLayout(layout)

        # 角色轮播相关
        self.gifs = gifs
        self.current_gif_index = 0
        self.role_timer = QTimer(self)
        self.role_timer.timeout.connect(self.play_next_gif)

        if self.gifs:
            self.switch_gif(self.gifs[0], speed_factor=0.4)

        self.role_timer.start(50000)

        self.create_tray_icon()

    def switch_gif(self, gif_path, speed_factor=0.4):
        if not os.path.exists(gif_path):
            print(f"❌ 文件不存在: {gif_path}")
            return

        self.timer.stop()
        self.frames.clear()

        try:
            gif = Image.open(gif_path)
            for frame in ImageSequence.Iterator(gif):
                with BytesIO() as output:
                    frame.save(output, format="PNG")
                    data = output.getvalue()
                tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
                tmp_file.write(data)
                tmp_file.close()
                self.frames.append(tmp_file.name)

            duration = gif.info.get('duration', 100)
            adjusted_duration = max(1, int(duration / speed_factor))
            self.timer.start(adjusted_duration)

        except Exception as e:
            print(f"❌ 加载 GIF 失败: {e}")

    def next_frame(self):
        if not self.frames or not self.isVisible():
            return

        self.current_frame = self.current_frame % len(self.frames)
        pixmap = QPixmap(self.frames[self.current_frame])
        self.label.setPixmap(pixmap)
        self.current_frame += 1

    def play_next_gif(self):
        self.current_gif_index = (self.current_gif_index + 1) % len(self.gifs)
        self.switch_gif(self.gifs[self.current_gif_index], speed_factor=0.4)

    def contextMenuEvent(self, event):
        if self.locked:
            return
        menu = self.create_main_menu()
        menu.exec_(event.globalPos())

    def create_main_menu(self):
        menu = QMenu(self)
        menu.setFont(QFont("微软雅黑", 10))
        shadow = QGraphicsDropShadowEffect(menu)
        shadow.setBlurRadius(15)
        shadow.setColor(Qt.black)
        shadow.setOffset(0, 4)
        menu.setGraphicsEffect(shadow)
        menu.setStyleSheet("""
            QMenu {
                background-color: #ffffff;
                border-radius: 12px;
                padding: 6px;
                margin: 0px;
            }
            QMenu::item {
                padding: 8px 24px;
                border-radius: 8px;
                margin: 2px 0;
            }
            QMenu::item:selected {
                background-color: #e0e0e0;
            }
        """)

        opacity_action = QAction("透明度设置", self)
        move_check = QAction("可否移动", self)
        lock_or_unlock_action = QAction("解除锁定" if self.locked else "锁定", self)
        sep1 = QAction(self)
        sep1.setSeparator(True)
        mic_action = QAction("开始录音" if not self.shared_vars.recording else "停止录音", self)
        text_input_action = QAction("文字输入", self)
        text_input_action.triggered.connect(self.show_text_input_dialog)
        sep2 = QAction(self)
        sep2.setSeparator(True)
        exit_action = QAction("退出", self)

        move_check.setCheckable(True)
        move_check.setChecked(self.draggable)
        move_check.triggered.connect(lambda checked: setattr(self, 'draggable', checked))

        lock_or_unlock_action.triggered.connect(self.toggle_locked)
        mic_action.triggered.connect(self.toggle_recording)
        opacity_action.triggered.connect(self.show_opacity_settings)
        exit_action.triggered.connect(self.on_exit)

        menu.addAction(opacity_action)
        menu.addAction(move_check)
        menu.addAction(lock_or_unlock_action)
        menu.addAction(sep1)
        menu.addAction(mic_action)
        menu.addAction(text_input_action)
        menu.addAction(sep2)
        menu.addAction(exit_action)

        return menu

    def show_text_input_dialog(self):
        dialog = TextInputDialog(self.shared_vars, self)
        dialog.exec_()

    def toggle_locked(self):
        self.locked = not self.locked
        self.create_tray_icon()

    def show_opacity_settings(self):
        dialog = OpacityDialog(self.windowOpacity(), self)
        if dialog.exec_():
            opacity = dialog.get_value()
            self.setWindowOpacity(opacity)

    def toggle_recording(self):
        self.shared_vars.recording = not self.shared_vars.recording

    def on_exit(self):
        self.tray_icon.hide()
        self.close()
        QApplication.quit()

    def mousePressEvent(self, event):
        if self.locked:
            return

        if event.button() == Qt.LeftButton and self.draggable:
            self._drag_start_pos = event.globalPos()
            self._drag_start_widget_pos = self.pos()
            self.offset = event.pos()
        elif event.button() == Qt.RightButton:
            self.contextMenuEvent(event)
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.locked or not self.draggable or self.offset is None:
            return
        if not (event.buttons() & Qt.LeftButton):
            self.offset = None
            return
        screen = self.screen() or QApplication.primaryScreen()
        if screen:
            geo = screen.availableGeometry()
            gpos = event.globalPos()
            dx = gpos.x() - self._drag_start_pos.x()
            dy = gpos.y() - self._drag_start_pos.y()
            new_x = self._drag_start_widget_pos.x() + dx
            new_y = self._drag_start_widget_pos.y() + dy
            w, h = self.width(), self.height()
            new_x = max(geo.left() - w + 50, min(new_x, geo.right() - 50))
            new_y = max(geo.top() - h + 50, min(new_y, geo.bottom() - 50))
            self.move(new_x, new_y)

    def mouseReleaseEvent(self, event):
        if self.locked or not self.draggable or event.button() != Qt.LeftButton:
            return
        self.offset = None
        self._ensure_on_screen()

    def showEvent(self, event):
        super().showEvent(event)
        self._ensure_on_screen()

    def leaveEvent(self, event):
        self._ensure_on_screen()

    def _ensure_on_screen(self):
        screen = self.screen() or QApplication.primaryScreen()
        if not screen:
            return
        geo = screen.availableGeometry()
        frame = self.frameGeometry()
        if geo.intersects(frame.adjusted(-30, -30, 30, 30)):
            return
        self.move(geo.center() - self.rect().center())

    def create_tray_icon(self):
        if not hasattr(self, 'tray_icon') or self.tray_icon is None:
            self.tray_icon = QSystemTrayIcon(self)
            icon = self.style().standardIcon(QStyle.SP_ComputerIcon)
            self.tray_icon.setIcon(QIcon(icon))

        tray_menu = self.create_main_menu()
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.setVisible(True)
        self.tray_icon.activated.connect(self.on_tray_icon_activated)

    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.showNormal()
            self.activateWindow()


class OpacityDialog(QDialog):
    def __init__(self, current_opacity, parent=None):
        super().__init__(parent)
        self.setWindowTitle("透明度设置")
        self.setFixedSize(250, 100)

        layout = QVBoxLayout(self)
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(1)
        self.slider.setMaximum(100)
        self.slider.setValue(int(current_opacity * 100))

        layout.addWidget(self.slider)

        confirm_btn = QPushButton("确认")
        confirm_btn.clicked.connect(self.accept)
        layout.addWidget(confirm_btn)

        self.slider.valueChanged.connect(lambda v: parent.setWindowOpacity(v / 100.0))

    def accept(self):
        super().accept()

    def get_value(self):
        return self.slider.value() / 100.0


def start_gpt_sovits():
    """启动服务核心函数"""
    subprocess.Popen(
        [PYTHON_EXE, 'api.py', '-g',CKPT_PATH, '-s', PTH_PATH],
        cwd=GPT_SOVITS_PATH,
        creationflags=subprocess.CREATE_NEW_CONSOLE
        
    )
    def warmup():
        print("预热 GPT-SoVITS...")
        for attempt in range(10):
            try:
                resp = requests.get('http://127.0.0.1:9880/', params={
                    "refer_wav_path": Emotionspath[0],
                    "prompt_text": Emotionstext[0],
                    "prompt_language": "zh",
                    "text": "预热",
                    "text_language": "zh"
                }, timeout=30)
                if resp.status_code == 200:
                    print("GPT-SoVITS 预热完成")
                    return
            except Exception:
                pass
            time.sleep(2)
        print("GPT-SoVITS 预热超时")
    threading.Thread(target=warmup, daemon=True).start()
    
def text_to_speech(i, text, REFERENCE_WAV, PROMPT_TEXT, session_id="", max_retries=2):
    """合成语音，支持重试"""
    params = {
        "refer_wav_path": REFERENCE_WAV,
        "prompt_text": PROMPT_TEXT,
        "prompt_language": "zh",
        "text": text,
        "text_language": "zh"
    }
    filename = f'tempwav/{session_id}_temp{i}.wav'
    os.makedirs('tempwav', exist_ok=True)
    for attempt in range(max_retries):
        try:
            response = requests.get('http://127.0.0.1:9880/', params=params, timeout=120)
            response.raise_for_status()
            with open(filename, 'wb') as f:
                f.write(response.content)
            if os.path.getsize(filename) > 100:
                return filename
            else:
                print(f"TTS合成文件过小 [{filename}]: {os.path.getsize(filename)} bytes, 重试 {attempt+1}")
                os.remove(filename)
        except requests.exceptions.Timeout:
            print(f"TTS合成超时 [{filename}], 重试 {attempt+1}/{max_retries}")
            if attempt < max_retries - 1:
                time.sleep(1)
        except Exception as e:
            print(f"TTS合成失败 [{filename}]: {str(e)}, 重试 {attempt+1}/{max_retries}")
            if attempt < max_retries - 1:
                time.sleep(1)
    return None

import re

def trim_conversation(max_pairs=10):
    """裁剪对话历史，防止上下文无限增长"""
    global messages
    non_system = messages[1:]
    pairs = []
    current_user = None
    current_assistant = None
    tool_results = []
    i = 0
    while i < len(non_system):
        msg = non_system[i]
        if msg['role'] == 'user':
            if current_user is not None:
                if current_assistant is not None or tool_results:
                    pairs.append((current_user, current_assistant, tool_results))
                else:
                    pairs.append((current_user, None, tool_results))
            current_user = msg
            current_assistant = None
            tool_results = []
        elif msg['role'] == 'assistant':
            current_assistant = msg
        elif msg['role'] == 'tool':
            tool_results.append(msg)
        i += 1
    if current_user is not None:
        pairs.append((current_user, current_assistant, tool_results))
    if len(pairs) > max_pairs:
        keep = pairs[-max_pairs:]
        new_messages = [messages[0]]
        for user_msg, assistant_msg, tool_msgs in keep:
            new_messages.append(user_msg)
            if assistant_msg:
                new_messages.append(assistant_msg)
            new_messages.extend(tool_msgs)
        messages = new_messages


def execute_tool_call(tool_call):
    """执行单个工具调用（模块化版本）"""
    func_name = tool_call.function.name
    try:
        args = json.loads(tool_call.function.arguments or '{}')
        return mods.execute_tool(func_name, args)
    except Exception as e:
        return f"工具执行失败 [{func_name}]: {str(e)}"


def chat_with_tools(user_text):
    """
    发送消息给AI并完整处理 Function Calling 循环：
    AI响应 → 检测工具调用 → 执行工具 → 回传结果 → 再次调用 → 直到无工具调用
    返回最终AI的文本响应
    """
    trim_conversation(max_pairs=10)

    messages.append({"role": "user", "content": user_text})

    for iteration in range(MAX_TOOL_ITERATIONS):
        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                tools=TOOLS,
                tool_choice="auto"
            )
        except Exception as e:
            print(f"❌ AI API调用失败: {e}")
            return f"抱歉，AI调用出了点问题: {str(e)}"

        message = response.choices[0].message

        if not message.tool_calls:
            if message.content and message.content.strip():
                print("AI回复:", message.content)
                try:
                    deepseekgptsovitshandle(message.content)
                except Exception as e:
                    print(f"语音合成失败: {e}")
            return message.content or ""

        msg_dict = message.to_dict() if hasattr(message, 'to_dict') else {
            "role": message.role,
            "content": message.content,
            "tool_calls": message.tool_calls
        }
        messages.append(msg_dict)

        for tool_call in message.tool_calls:
            print(f"  → 执行工具: {tool_call.function.name}({tool_call.function.arguments})")
            result = execute_tool_call(tool_call)
            print(f"  ← 工具结果: {result[:200] if len(result) > 200 else result}")

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": tool_call.function.name,
                "content": result
            })

    return "对话轮数已达上限，AI无法继续调用工具"
def image_to_oss(image_panth):
    
    import os

    def upload_to_oss(file_path, object_prefix="uploads/"):
        """
        上传文件到阿里云OSS，返回用于Qwen-VL模型的访问URL
        :param file_path: 本地文件路径
        :param object_prefix: OSS存储路径前缀，默认uploads/
        :return: 文件URL 或 None（上传失败时）
        """
        # OSS配置（替换为您的实际信息）
        OSS_CFG = {
            "ACCESS_KEY_ID": ACCESS_KEY_ID,
            "ACCESS_KEY_SECRET": ACCESS_KEY_SECRET,
            "ENDPOINT": ENDPOINT,
            "BUCKET_NAME": BUCKET_NAME
        }

        try:
            # 验证文件存在
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"文件不存在: {file_path}")

            # 生成唯一对象名称（保留原始扩展名）
            ext = os.path.splitext(file_path)[-1]
            object_name = f"{object_prefix}{datetime.now().strftime('%Y%m%d')}_{str(uuid.uuid4().hex)}{ext}"

            # 创建OSS客户端
            auth = oss2.Auth(OSS_CFG["ACCESS_KEY_ID"], OSS_CFG["ACCESS_KEY_SECRET"])
            bucket = oss2.Bucket(auth, OSS_CFG["ENDPOINT"], OSS_CFG["BUCKET_NAME"])

            # 执行上传
            with open(file_path, 'rb') as f:
                result = bucket.put_object(object_name, f)
            
            if result.status == 200:
                # 构建Qwen-VL需要的URL格式
                file_url = f"https://{OSS_CFG['BUCKET_NAME']}.{OSS_CFG['ENDPOINT']}/{object_name}"
                return file_url
            return None

        except Exception as e:
            print(f"OSS上传失败: {str(e)}")
            return None

    # 使用示例
    
        # 上传测试文件
    url = upload_to_oss(image_panth)
    if url:
        print(f"上传成功，URL: {url}")
        return url
    else:
        print("上传失败")
        return None


def qwenLV(image_ossurl,airenshe=''):
    from openai import OpenAI
    client = OpenAI(
        # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
        api_key=qwenLVapikey,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )

    completion = client.chat.completions.create(
        model="qwen-vl-plus",  # 此处以qwen-vl-plus为例，可按需更换模型名称。模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
        messages=[{"role": "user","content": [
                {"type": "text","text": airenshe},
                {"type": "image_url",
                "image_url": {"url": image_ossurl}}
                ]}]
        )
    return completion.choices[0].message.content
def image_camera():
    timestamp = datetime.now().strftime("%Y%m%d%H%M")
    filename = f"camera_{timestamp}.png"
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("❌ 摄像头无法打开")
            return None
        ret, frame = cap.read()
        if not ret:
            print("❌ 摄像头读取失败")
            cap.release()
            return None
        cv2.imwrite("image\\"+filename, frame)
        cap.release()
        return "image\\"+filename
    except Exception as e:
        print(f"❌ 摄像头异常: {e}")
        return None
def image_screen():
    timestamp = datetime.now().strftime("%Y%m%d%H%M")
    filename = f"screen_{timestamp}.png"
    screenshot = pyautogui.screenshot()
    screenshot.save('image\\'+filename)  
    return 'image\\'+filename
def extract_code_and_text(response_text):
    code_pattern = re.compile(r'```python(.*?)```', re.DOTALL)
    code_blocks = code_pattern.findall(response_text)
    codes = [code.strip() for code in code_blocks]
    text = code_pattern.sub('', response_text).strip()
    return [codes, text]

def talk1(say):
    while True:    
        messagestalk1.append({"role": "user", "content": say})
        response = client_talt1.chat.completions.create(
            model="deepseek-chat",
            messages=messagestalk1
        )

        assistant_response = response.choices[0].message  # 获取完整响应对象
        messagestalk1.append(assistant_response)  # 依然存储完整响应对象以保证上下文连贯
        print(assistant_response.content) 
        return assistant_response.content
     

def extract_emotion_text(text, valid_emotions):
    emotions = []
    texts = []
    segments = text.split("[")
    for segment in segments[1:]:
        parts = segment.split("]")
        if len(parts) == 2:
            emotion = parts[0]
            text_part = parts[1].strip()
            if emotion in valid_emotions and text_part:
                emotions.append(emotion)
                texts.append(text_part)
    return emotions, texts
def deepseekcodeaihandle(ursay):
    aisay=talk1(ursay)
    aisaylist=extract_code_and_text(aisay)
    ex=True
    result = "操作未完成"
    max_retries = 10
    retries = 0
    print(aisaylist)
    while ex and retries < max_retries:
        retries += 1
        codes = aisaylist[0] if aisaylist[0] else []
        if not codes:
            result = "AI未返回可执行的代码"
            ex=False
            break
        code_text = codes[0].strip() if codes else ''
        if '[成功]' in aisaylist[1]:
            with open("airunpy.py", 'w',encoding='utf-8') as f:
                f.write(code_text)
            pr=subprocess.run("python.exe airunpy.py",shell=True,capture_output=True,text=True).stdout
            print('aicodeprint:'+str(pr))
            print('yes')
            result = f"操作成功，程序输出：{str(pr)}"
            ex=False
        elif '[失败]' in aisaylist[1]:
            result = "操作失败，AI判断无法完成"
            ex=False
            print('not')
        else:
            with open("airunpy.py", 'w',encoding='utf-8') as f:
                f.write(code_text)
            pr=subprocess.run("python.exe airunpy.py",shell=True,capture_output=True,text=True).stdout
            ursay='程序返回：'+str(pr)
            print('aicodeprint:'+str(pr))
            aisay=talk1(ursay)
            aisaylist=extract_code_and_text(aisay)
            print(aisaylist)
    if retries >= max_retries and ex:
        result = "操作失败：已达到最大重试次数"
    return result
def deepseektalkhandle(say, tf=False):
    """
    旧版文本指令解析入口（保留兼容）。
    现在主要使用 chat_with_tools() 进行 Function Calling。
    此函数仅作为文本转语音的简单通道。
    """
    print("AI回复:", say)
    deepseekgptsovitshandle(say)


def deepseekgptsovitshandle(say):
    aisayEmotions, say = extract_emotion_text(say, Emotions)
    if not aisayEmotions:
        return
    session_id = datetime.now().strftime("%H%M%S_") + str(uuid.uuid4())[:8]
    total = len(aisayEmotions)
    result_queue = queue.Queue()
    done_event = threading.Event()
    completed_count = [0]
    lock = threading.Lock()

    def synth_worker(idx, text, ref_path, prompt_text):
        try:
            result = text_to_speech(idx, text, ref_path, prompt_text, session_id)
            result_queue.put((idx, result))
        except Exception as e:
            print(f"TTS线程异常: {e}")
            result_queue.put((idx, None))
        with lock:
            completed_count[0] += 1
            if completed_count[0] >= total:
                done_event.set()

    for i in range(total):
        t = threading.Thread(
            target=synth_worker,
            args=(i, say[i], Emotionspath[Emotions.index(aisayEmotions[i])], Emotionstext[Emotions.index(aisayEmotions[i])])
        )
        t.daemon = True
        t.start()

    results = {}
    played = set()
    stop_playback = threading.Event()

    def playback_loop():
        while not stop_playback.is_set():
            try:
                idx, fname = result_queue.get(timeout=0.2)
                if idx == -1:
                    break
                results[idx] = fname
            except queue.Empty:
                if done_event.is_set() and len(results) == len(played):
                    break
                continue

            while True:
                next_idx = None
                for i in range(total):
                    if i not in played:
                        next_idx = i
                        break
                if next_idx is None or next_idx not in results:
                    break
                fname = results.pop(next_idx)
                played.add(next_idx)
                if fname is None or not os.path.exists(fname):
                    print(f"跳过缺失的音频文件 [{next_idx}]: {fname}")
                else:
                    try:
                        data, samplerate = sf.read(fname)
                        sd.play(data, samplerate)
                        sd.wait()
                        print(f"播放 {fname} 完成")
                    except Exception as e:
                        print(f"播放失败 [{fname}]: {e}")
                    finally:
                        try:
                            os.remove(fname)
                        except Exception:
                            pass

    play_thread = threading.Thread(target=playback_loop)
    play_thread.daemon = True
    play_thread.start()

    done_event.wait()
    result_queue.put((-1, None))
    stop_playback.set()
    play_thread.join(timeout=30)

    for fname in results.values():
        if fname and os.path.exists(fname):
            try:
                os.remove(fname)
            except Exception:
                pass
 
def run_qt_app(gifs, shared_vars):
    app = QApplication(sys.argv)
    pet = DesktopPetApp(gifs, shared_vars)
    pet.show()
    sys.exit(app.exec_())
def main():
    
    manager = Manager()
    shared_vars = manager.Namespace()
    shared_vars.recording = False
    shared_vars.text_input = None

    for dir_path in ['image', 'tempwav']:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            print(f'创建目录: {dir_path}')
        else:
            for f in os.listdir(dir_path):
                fpath = os.path.join(dir_path, f)
                try:
                    os.remove(fpath)
                except Exception:
                    pass

    print("桌宠json:",petjson)
    print("情感：",Emotionstext)
    print("gifs:",gifs)
    print("python路径:",PYTHON_EXE)
    print("ckpt:",CKPT_PATH)
    print("pth",PTH_PATH)
    print("加载频谱 VAD...")
    try:
        vad_instance = SpectralVAD(sampling_rate=16000)
        print("频谱 VAD 加载完成")
    except Exception as e:
        print(f"频谱 VAD 加载失败: {e}")
        vad_instance = None

    print("加载 Whisper 语音识别模型 (small)...")
    try:
        whisper_model = whisper.load_model("medium")
        cc_converter = opencc.OpenCC("t2s")
        print("Whisper 加载完成")
    except Exception as e:
        print(f"Whisper 加载失败: {e}")
        whisper_model = None
        cc_converter = None

    print("加载模块化工具...")
    mod_context = {
        'image_camera': image_camera,
        'image_screen': image_screen,
        'image_to_oss': image_to_oss,
        'qwenLV': qwenLV,
        'qwenLVcameraai': qwenLVcameraai,
        'qwenLVscreenai': qwenLVscreenai,
        'deepseekcodeaihandle': deepseekcodeaihandle,
    }
    global TOOLS
    TOOLS = init_mod_tools(mod_context)
    print(f"已加载 {len(TOOLS)} 个工具")

    start_gpt_sovits()
    print('开始加载，请耐心等待')   
    p = Process(target=run_qt_app, args=(gifs, shared_vars))
    p.start()
    time.sleep(25)
    print('加载成功')
        
    while True:
        
        nexttime=random.randint(config['nexttime'][0],config['nexttime'][1])

        print('对话时间：',nexttime)
        last_activity_time = datetime.now() 
        while True:
            FORMAT = pyaudio.paInt16
            CHANNELS = 1
            RATE = 16000
            CHUNK = 512
            SILENCE_LIMIT = 1.0
            PRE_BUFFER_FRAMES = 10

            p_audio = pyaudio.PyAudio()
            stream = p_audio.open(format=FORMAT,
                            channels=CHANNELS,
                            rate=RATE,
                            input=True,
                            frames_per_buffer=CHUNK)

            vad = vad_instance
            if vad is not None and hasattr(vad, 'reset'):
                vad.reset()

            frames = []
            pre_buffer = collections.deque(maxlen=PRE_BUFFER_FRAMES)
            silence_frames = 0
            speech_counter = 0
            in_speech = False
            speech_start_trigger = 2
            SILENCE_END_FRAMES = 5 + int(SILENCE_LIMIT * RATE / CHUNK)
            
            ex=False
            res=""
            try:
                while True:
                    
                    data = stream.read(CHUNK, exception_on_overflow=False)
                    
                    if vad is not None:
                        is_speech, _ = vad.is_speech(data)
                    else:
                        audio_data = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
                        rms = np.sqrt(np.mean(audio_data ** 2))
                        is_speech = rms > 0.015
                    
                    pre_buffer.append(data)

                    if is_speech:
                        if not in_speech and shared_vars.recording==True:
                            speech_counter += 1
                            if speech_counter >= speech_start_trigger:
                                print("检测到语音，开始录音")
                                in_speech = True
                                frames.extend(pre_buffer)
                        if in_speech:
                            frames.append(data)
                        silence_frames = 0
                    else:
                        speech_counter = 0
                        if in_speech:
                            silence_frames += 1
                            if silence_frames >= SILENCE_END_FRAMES:
                                print("检测到静音，停止录音")
                                in_speech = False
                                break
                    
                    
                    if datetime.now() - last_activity_time > timedelta(minutes=nexttime) and not in_speech:
                        try:
                            auto_prompt = "主人好久没说话了，你可以主动观察一下主人在做什么，并和主人打招呼"
                            chat_with_tools(auto_prompt)
                        except Exception as e:
                            print(f"自动行为异常: {e}")
                        last_activity_time = datetime.now()
                    if shared_vars.text_input != None:
                        res=shared_vars.text_input
                        ex=True
                        last_activity_time = datetime.now()
                        break


            except KeyboardInterrupt:
                print("\n录音手动中断")
            
            in_speech=False
            stream.stop_stream()
            stream.close()
            p_audio.terminate()
            if ex==True:
                print('文字输入:',res)
                break
            else:

                if not frames:
                    print("未检测到有效语音输入。")
                else:
                    raw_audio = np.frombuffer(b''.join(frames), dtype=np.int16)
                    normalized_audio = raw_audio.astype(np.float32) / 32768.0

                    MAX_DURATION = 30
                    max_samples = int(MAX_DURATION * RATE)
                    if len(normalized_audio) > max_samples:
                        normalized_audio = normalized_audio[:max_samples]

                    print("正在识别...")
                    if whisper_model is not None:
                        result = whisper_model.transcribe(
                            normalized_audio,
                            language="zh",
                            fp16=False,
                            temperature=0.0,
                            condition_on_previous_text=False
                        )
                        if cc_converter is not None:
                            res = cc_converter.convert(result['text'])
                        else:
                            res = result['text']
                    else:
                        res = ""

                    if res!='':
                        print("识别结果：", res)
                        last_activity_time = datetime.now()
                        break
                    else:
                        print('无内容，跳过识别')
        
        
        chat_with_tools(res)
        
        
        shared_vars.text_input=None 

if __name__=='__main__':
    start_gpt_sovits()
    #main()
