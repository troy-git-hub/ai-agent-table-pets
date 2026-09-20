"""
独立 VAD 测试脚本 - 调试语音检测
运行: python test_vad.py
按 Ctrl+C 退出

MODE 1: 原始VAD数据打印 (调试分数)
MODE 2: 模拟录音起止 + Whisper识别
"""

import numpy as np
import pyaudio
import time
import collections

RATE = 16000
CHUNK = 512
FORMAT = pyaudio.paInt16
CHANNELS = 1

MODE = 2

print("=" * 60)
print("频谱 VAD 测试")
print(f"模式: {'原始数据' if MODE == 1 else '录音模拟 + Whisper识别'}")
print("按 Ctrl+C 退出")
print("=" * 60)


class SpectralVAD:
    SPEECH_LOW = 300
    SPEECH_HIGH = 3400

    def __init__(self, sampling_rate=16000):
        self.sampling_rate = sampling_rate
        self.window_size = 512
        self.eps = 1e-10
        self.alpha = 0.1
        self.noise_floor = 0.01
        self.speech_strength = 0.0
        self.smoothing_window = []
        self.smoothing_max = 5

    def reset(self):
        self.noise_floor = 0.01
        self.speech_strength = 0.0
        self.smoothing_window = []

    def is_speech(self, audio_bytes):
        audio = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
        if len(audio) < 64:
            return False, {}
        audio = audio[:self.window_size]

        n = len(audio)
        windowed = audio * np.hanning(n).astype(np.float32)
        spectrum = np.abs(np.fft.rfft(windowed))
        freqs = np.fft.rfftfreq(n, d=1.0 / self.sampling_rate)

        total_energy = np.sum(spectrum ** 2) + self.eps
        speech_mask = (freqs >= self.SPEECH_LOW) & (freqs <= self.SPEECH_HIGH)
        speech_energy = np.sum((spectrum[speech_mask]) ** 2)
        speech_ratio = speech_energy / total_energy

        weighted_sum = np.sum(freqs * (spectrum ** 2))
        spectral_centroid = weighted_sum / total_energy
        rms = np.sqrt(np.mean(audio ** 2))

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
        if spectral_centroid < 2500:
            speech_score += 0.2
        elif spectral_centroid < 3500:
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
            'centroid': spectral_centroid,
            'snr': snr,
            'score': speech_score,
            'smoothed': smoothed,
            'strength': strength,
        }
        return strength > 0.45, features


vad = SpectralVAD(RATE)
p = pyaudio.PyAudio()
stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

if MODE == 1:
    print("\n原始VAD数据模式 - 打印每帧特征值 (每0.15s输出一次)")
    print("-" * 90)
    print(f"{'RMS':>8} {'SR':>6} {'CENT':>8} {'SNR':>6} {'SCORE':>7} {'SMOOTH':>7} {'STRENGTH':>9} {'VAD':>6}")
    print("-" * 90)

    last_print = 0
    try:
        while True:
            data = stream.read(CHUNK, exception_on_overflow=False)
            is_speech, feat = vad.is_speech(data)
            now = time.time()
            if now - last_print >= 0.15:
                print(f"{feat['rms']:8.4f} {feat['sr']:6.3f} {feat['centroid']:7.0f}Hz "
                      f"{feat['snr']:6.2f} {feat['score']:7.2f} {feat['smoothed']:7.2f} "
                      f"{feat['strength']:9.3f} {'SPEECH' if is_speech else 'SILENT'}")
                last_print = now
    except KeyboardInterrupt:
        print("\n测试结束")
        stream.stop_stream()
        stream.close()
        p.terminate()


elif MODE == 2:
    import soundfile as sf
    import sounddevice as sd
    import whisper
    import opencc

    print("\n录音模拟 + Whisper识别模式")
    print("说话开始，停下后自动停止录音并识别")
    print("-" * 60)
    print("预缓存: 保留说话前 0.32s 的音频，防止首字丢失")
    print("-" * 60)

    SILENCE_LIMIT = 1.0
    speech_start_trigger = 2
    SILENCE_END_FRAMES = 5 + int(SILENCE_LIMIT * RATE / CHUNK)
    PRE_BUFFER_FRAMES = 10

    print("\n加载 Whisper 模型...")
    whisper_model = whisper.load_model("small")
    cc = opencc.OpenCC("t2s")
    print("Whisper 加载完成")

    try:
        while True:
            vad.reset()
            pre_buffer = collections.deque(maxlen=PRE_BUFFER_FRAMES)
            frames = []
            silence_frames = 0
            speech_counter = 0
            in_speech = False
            start_time = None

            print("  [等待中...] ", end="", flush=True)

            while True:
                data = stream.read(CHUNK, exception_on_overflow=False)
                is_speech, feat = vad.is_speech(data)

                pre_buffer.append(data)

                if is_speech:
                    if not in_speech:
                        speech_counter += 1
                        if speech_counter >= speech_start_trigger:
                            print("\r  [录音中...]          ", end="", flush=True)
                            in_speech = True
                            start_time = time.time()
                            frames.extend(pre_buffer)
                    if in_speech:
                        frames.append(data)
                    silence_frames = 0
                else:
                    speech_counter = 0
                    if in_speech:
                        silence_frames += 1
                        if silence_frames >= SILENCE_END_FRAMES:
                            dur = time.time() - start_time
                            print(f"\r  [停止] 录了 {len(frames)} 帧, {dur:.1f}s     ")
                            break

            if len(frames) > 0:
                raw_audio = np.frombuffer(b''.join(frames), dtype=np.int16)
                audio_data = raw_audio.astype(np.float32) / 32768.0
                filename = f"test_capture_{int(time.time())}.wav"
                sf.write(filename, audio_data, RATE)
                print(f"  保存: {filename} ({len(frames)} 帧)")

                print("  识别中... ", end="", flush=True)
                try:
                    result = whisper_model.transcribe(audio_data, language="zh")
                    text = cc.convert(result['text'])
                    print(f"\n  识别结果: {text}")
                except Exception as e:
                    print(f"\n  识别失败: {e}")

                print("  播放中... ", end="", flush=True)
                try:
                    sd.play(audio_data, RATE)
                    sd.wait()
                    print("完成")
                except Exception as e:
                    print(f"播放失败: {e}")

            print("  继续等待下一轮...")
            time.sleep(0.3)

    except KeyboardInterrupt:
        print("\n测试结束")
        stream.stop_stream()
        stream.close()
        p.terminate()