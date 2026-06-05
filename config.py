# -*- coding: utf-8 -*-
"""
Vocal2MIDI 配置管理
"""

import os
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent

# 外部工具目录（统一安装到E:\DevTools）
DEVTOOLS_DIR = Path("E:/DevTools")

# FFmpeg路径
FFMPEG_DIR = DEVTOOLS_DIR / "ffmpeg"
FFMPEG_EXE = FFMPEG_DIR / "bin" / "ffmpeg.exe"

# 模型目录
MODELS_DIR = DEVTOOLS_DIR / "models"
RMVPE_MODEL_PATH = MODELS_DIR / "rmvpe" / "rmvpe.pt"

# 本地模型目录（备用）
LOCAL_MODELS_DIR = PROJECT_ROOT / "models"

# 支持的音频格式
SUPPORTED_FORMATS = [".wav", ".mp3", ".flac", ".ogg", ".m4a"]

# 音频处理参数
class AudioConfig:
    """音频处理配置"""
    SAMPLE_RATE = 44100  # 采样率
    RMVPE_SAMPLE_RATE = 16000  # RMVPE模型采样率
    HOP_LENGTH = 512  # 帧移
    N_FFT = 2048  # FFT窗口大小
    N_MELS = 128  # 梅尔频谱维度

# RMVPE模型参数
class RMVPEConfig:
    """RMVPE模型配置"""
    MODEL_URL = "https://huggingface.co/lj1995/VoiceConversionWebUI/resolve/main/rmvpe.pt"
    MODEL_URL_BACKUP = "https://github.com/yxlllc/RMVPE/releases/download/v1.0/rmvpe.pt"
    HOP_LENGTH = 160  # 模型帧移
    SAMPLE_RATE = 16000  # 模型采样率
    N_MELS = 128  # 梅尔频谱维度

# 颤音检测参数
class VibratoConfig:
    """颤音检测配置"""
    MIN_RATE = 4.0  # 最小颤音频率 (Hz)
    MAX_RATE = 8.0  # 最大颤音频率 (Hz)
    MIN_DEPTH = 50  # 最小颤音深度 (cents)
    MAX_DEPTH = 200  # 最大颤音深度 (cents)
    WINDOW_SIZE = 0.2  # 分析窗口大小 (秒)
    OVERLAP = 0.5  # 窗口重叠比例

# MIDI生成参数
class MIDIConfig:
    """MIDI生成配置"""
    PPQ = 480  # 每拍tick数
    TEMPO = 120  # 默认BPM
    VELOCITY_MIN = 30  # 最小力度
    VELOCITY_MAX = 127  # 最大力度
    PITCH_BEND_RANGE = 2  # 弯音范围（半音）
    MIN_NOTE_DURATION = 0.05  # 最小音符时长（秒）
    SILENCE_THRESHOLD_DB = -40  # 静音阈值（dB）

# GUI配置
class GUIConfig:
    """GUI配置"""
    WINDOW_TITLE = "Vocal2MIDI - 人声转MIDI转换器"
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 800
    THEME = "dark"  # 深色主题

# 确保目录存在
def ensure_dirs():
    """确保必要的目录存在"""
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    (MODELS_DIR / "rmvpe").mkdir(parents=True, exist_ok=True)
    LOCAL_MODELS_DIR.mkdir(parents=True, exist_ok=True)
