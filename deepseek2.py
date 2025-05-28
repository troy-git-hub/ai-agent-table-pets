import subprocess
import os
import time
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
import webrtcvad
import opencc
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
# 打印配置（用于验证）
print(f"ACCESS_KEY_ID: {ACCESS_KEY_ID}")
print(f"ACCESS_KEY_SECRET: {ACCESS_KEY_SECRET}")
print(f"ENDPOINT: {ENDPOINT}")
print(f"BUCKET_NAME: {BUCKET_NAME}")
print(f"QWEN_LV_API_KEY: {qwenLVapikey}")
print(f"DEEPEEK_API_KEY: {deepseekapikey}")
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
aiagentsystem="不要回复太多字，不要使用特殊字符。用户有使用的是语音识别，避免不了一些奇怪的问题，所以你回答时要仔细理解问题，回答中不要提语音识别有识别错误和有问题的地方，用户问题的语言还可能是繁体中文，你会的用户的一定是简体中文。如果我的问题前加了屏幕截图描述：就代表这是主人屏幕的描述，你根据描述和你的人设回答主人。如果我的问题前加了摄像头照片描述：就代表这是主人摄像头的描述，你根据描述和你的人设回答主人；当你觉得要需要操作电脑时在回答结尾追加[do_computer/具体操作命令]（如：[do_computer/打开微信]）但不要自己写代码让用户来执行。环境检查指令：摄像头检查：[see_camera]（无参数）屏幕检查：[see_screen]（无参数），我会告诉你图中有什么，你再回答主人。附加项后面不能有文字，而且每次回答只能加一个附加项，不能违反！在你回答中，你需要在每句话前加入你认为朗读时需要的感情，你有这些感情："+systemEmotions+"。你只能用前面的感情，不能再创造一个出来,这更重要，不能违反。感情加在对应的那句话前面，用[]包裹，回答中至少一个感情，一到两个逗号或句号前面的话算一个句子，每个句子都要有一个感情。使用示例：[开心]今天我吃到了美味的小蛋糕。[伤心]可明天就要考试了，我还没复习，[伤心]又要被老师骂了。"
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
            self.offset = event.pos()
        elif event.button() == Qt.RightButton:
            self.contextMenuEvent(event)
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.locked or not self.draggable or self.offset is None:
            return
        self.move(self.pos() + event.pos() - self.offset)

    def mouseReleaseEvent(self, event):
        if self.locked or not self.draggable or event.button() != Qt.LeftButton:
            return
        self.offset = None

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
    
def text_to_speech(i,text,REFERENCE_WAV,PROMPT_TEXT):
    """合成并播放语音"""
    params = {
        "refer_wav_path": REFERENCE_WAV,
        "prompt_text": PROMPT_TEXT,
        "prompt_language": "zh",
        "text": text,
        "text_language": "zh"
    }

    try:
        response = requests.get('http://127.0.0.1:9880/', params=params, timeout=60)
        response.raise_for_status()
        filename='tempwav\\temp'+str(i)+'.wav'
        with open(filename, 'wb') as f:
            f.write(response.content)
    except Exception as e:
        print(f"发生错误: {str(e)}")

import re

def parse_ai_response(response: str) -> tuple:
    """
    返回三元组: (清理文本, 操作类型, 参数)
    返回值示例:
    ("请创建文件", "do_computer", "touch 数据.txt") 
    ("环境检查", "see_camera", None)
    ("普通回复", None, None)
    """
    # 匹配带参数和无参数指令
    pattern = re.compile(
        r'(.*?)(?:\[(search|do_computer)/(.+?)\]'    # 带参数指令（修改：使用斜杠/而非反斜杠\）
        r'|\[(see_camera|see_screen)\])\s*$'         # 无参数指令
    )
    
    match = pattern.search(response)
    if not match:
        return (response.strip(), None, None)
    
    clean_text = match.group(1).strip()
    
    if match.group(2):  # 处理带参数指令
        return (clean_text, match.group(2), match.group(3))
    else:  # 处理无参数指令
        return (clean_text, match.group(4), None)
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
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cv2.imwrite("image\\"+filename, frame)
    cap.release()
    return "image\\"+filename
def image_screen():
    timestamp = datetime.now().strftime("%Y%m%d%H%M")
    filename = f"screen_{timestamp}.png"
    screenshot = pyautogui.screenshot()
    screenshot.save('image\\'+filename)  
    return 'image\\'+filename
def extract_code_and_text(response_text):
    #被 ```python 和 ``` 包裹的代码块
    code_pattern = re.compile(r'```python(.*?)```', re.DOTALL)
    code_blocks = code_pattern.findall(response_text)
    codes = [code.strip() for code in code_blocks]
    text = code_pattern.sub('', response_text).strip()
    return [codes if len(codes) > 0 else '', text]
def talk(say):
    messages.append({"role": "user", "content": say})
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages
    )
    assistant_response = response.choices[0].message  # 获取完整响应对象
    messages.append(assistant_response)  # 依然存储完整响应对象以保证上下文连贯
    return assistant_response.content
    #text_to_speech(assistant_response.content)

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
    print(aisaylist)
    while ex:
        if '[成功]' in aisaylist[1]:
            with open("airunpy.py", 'w',encoding='utf-8') as f:
                f.write(aisaylist[0][0].strip())  # 去除首尾空白
            pr=subprocess.run("python.exe airunpy.py",shell=True,capture_output=True,text=True).stdout
            print('aicodeprint:'+str(pr))
            print('yes')
            ex=False
        elif '[失败]' in aisaylist[1]:
            ex=False
            print('not')
        else:
            with open("airunpy.py", 'w',encoding='utf-8') as f:
                f.write(aisaylist[0][0].strip())  # 去除首尾空白
            pr=subprocess.run("python.exe airunpy.py",shell=True,capture_output=True,text=True).stdout
            ursay='程序返回：'+str(pr)
            print('aicodeprint:'+str(pr))
            aisay=talk1(ursay)
            aisaylist=extract_code_and_text(aisay)
            print(aisaylist)
def deepseektalkhandle(say,tf=False):
    aisay,aiwant,parameter=parse_ai_response(say)
    if aiwant=='do_computer':
        print(say)
        deepseekgptsovitshandle(aisay)
        deepseekcodeaihandle(parameter)
    elif aiwant=='search':
        print(say)
        print("search",parameter)
    elif aiwant=='see_camera':
        print(say)
        deepseekgptsovitshandle(aisay)
        qwen=qwenLV(image_to_oss(image_camera()),airenshe=qwenLVcameraai) 
        print(qwen)
        aisay=talk('摄像头照片描述：'+qwen)
        deepseektalkhandle(aisay,False)
    elif aiwant=='see_screen':
        print(say)
        deepseekgptsovitshandle(aisay)
        qwen=qwenLV(image_to_oss(image_screen()),airenshe=qwenLVscreenai) 
        print(qwen)
        aisay=talk('屏幕截图描述：'+qwen)
        
        deepseektalkhandle(aisay,False)
    else:
        if not tf:
            print(say)
            deepseekgptsovitshandle(aisay)


def deepseekgptsovitshandle(say):
    threads = []
    aisayEmotions,say=extract_emotion_text(say,Emotions)
    for i in range(len(aisayEmotions)):
        """print(i)
        print(say)
        print(Emotionspath[Emotions.index(aisayEmotions[i])])
        print(Emotionstext[Emotions.index(aisayEmotions[i])])
        text_to_speech(say[i],Emotionspath[Emotions.index(aisayEmotions[i])],Emotionstext[Emotions.index(aisayEmotions[i])])"""
        t=threading.Thread(target=text_to_speech,args=(i,say[i],Emotionspath[Emotions.index(aisayEmotions[i])],Emotionstext[Emotions.index(aisayEmotions[i])]))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
        
    for i in range(len(aisayEmotions)):
        filename='tempwav\\temp'+str(i)+'.wav'
        data, samplerate = sf.read(filename)
        sd.play(data, samplerate)
        sd.wait()
        print("播放"+'temp'+str(i)+'.wav'+'完成')
        os.remove(filename)
 
def run_qt_app(gifs, shared_vars):
    app = QApplication(sys.argv)
    pet = DesktopPetApp(gifs, shared_vars)
    pet.show()
    sys.exit(app.exec_())
def main():
    
    manager = Manager()
    shared_vars = manager.Namespace()
    shared_vars.recording = False  # 原有的录音状态共享变量
    shared_vars.text_input = None

    start_gpt_sovits()
    print('开始加载，请耐心等待')   
    p = Process(target=run_qt_app, args=(gifs, shared_vars))
    p.start()
    time.sleep(25)
    # 启动 Qt 子进程
    print('加载成功')
        
    while True:
        
        nexttime=random.randint(config['nexttime'][0],config['nexttime'][1])

        print('对话时间：',nexttime)
        last_activity_time = datetime.now() 
        while True:
            FORMAT = pyaudio.paInt16  # 16位整数格式
            CHANNELS = 1              # 单声道
            RATE = 16000              # 采样率（必须为8000、16000、32000、48000）
            CHUNK = 160               # 每次读取的音频块大小（160个采样点，约10ms）
            VOLUME_BOOST = 1.2        # 音量增强倍数
            SILENCE_LIMIT = 1     # 静音超过多少秒后停止录音
            VAD_MODE = 2             # VAD 模式（0-3，3最敏感）

            # 初始化 PyAudio
            p = pyaudio.PyAudio()
            stream = p.open(format=FORMAT,
                            channels=CHANNELS,
                            rate=RATE,
                            input=True,
                            frames_per_buffer=CHUNK)

            # 初始化 VAD（语音活动检测器）
            vad = webrtcvad.Vad()
            vad.set_mode(VAD_MODE)  # 设置检测灵敏度



            # 存储音频数据
            frames = []
            silence_counter = 0  # 静音计数器（单位：CHUNK）
            in_speech = False    # 是否正在录音
            
            ex=False
            try:
                while True:
                    data = stream.read(CHUNK)  # 读取音频块
                    is_speech = vad.is_speech(data, RATE)  # 判断是否为语音

                    if is_speech:
                        if not in_speech and shared_vars.recording==True:
                            print("检测到声音，开始录音")
                            
                            in_speech = True
                        silence_counter = 0
                        # 音量增强
                        audio = np.frombuffer(data, dtype=np.int16)
                        boosted = (audio * VOLUME_BOOST).astype(np.int16)
                        frames.append(boosted.tobytes())
                    elif in_speech:
                        # 已经开始录音，但现在静音
                        silence_counter += 1
                        if silence_counter >= SILENCE_LIMIT * (RATE / CHUNK):
                            print("检测到静音，停止录音")
                            break
                    
                    
                    if datetime.now() - last_activity_time > timedelta(minutes=nexttime) and is_speech==False:
                        action = random.randint(1, 2)
                        
                        if action == 1:
                            print("ai see_camera")
                            img_path = image_camera()
                            qwen = qwenLV(image_to_oss(img_path), qwenLVcameraai)
                            print('qwen:', qwen)
                            b=talk('摄像头照片描述：' + qwen)
                            deepseektalkhandle(b)
                        elif action == 2:
                            print("ai see_screen")
                            img_path = image_screen()
                            qwen = qwenLV(image_to_oss(img_path), qwenLVscreenai)
                            print('qwen:', qwen)
                            b=talk('屏幕截图描述：' + qwen)
                            deepseektalkhandle(b)
                            
                        # 更新最后活动时间为当前时间
                        last_activity_time = datetime.now()
                    if shared_vars.text_input != None:
                        res=shared_vars.text_input
                        ex=True
                        last_activity_time = datetime.now()
                        break


            except KeyboardInterrupt:
                print("\n录音手动中断")
            
            # 结束音频流
            
            stream.stop_stream()
            stream.close()
            p.terminate()
            if ex==True:
                print('文字输入:',res)
                break
            else:

            # 判断是否检测到有效语音
                if not frames:
                    print("未检测到有效语音输入。")
                else:
                    # 合并所有音频片段
                    raw_audio = np.frombuffer(b''.join(frames), dtype=np.int16)
                    normalized_audio = raw_audio.astype(np.float32) / 32768.0  # 归一化

                    # 使用 Whisper 进行语音识别
                    print("正在识别...")
                    model = whisper.load_model("base")
                    result = model.transcribe(normalized_audio, language="zh")  # 中文识别
                    cc = opencc.OpenCC("t2s")
                    res = cc.convert(result['text'])
                    if res!='':

                        print("识别结果：", res)
                        last_activity_time = datetime.now()
                        break
                        
                    else:
                        print('无内容，跳过识别')
        
        
        a=talk(res)
        deepseektalkhandle(a)
        
        
        shared_vars.text_input=None 

if __name__=='__main__':
    
    main()
       
        

