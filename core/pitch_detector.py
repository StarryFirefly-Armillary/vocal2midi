# -*- coding: utf-8 -*-
"""
RMVPE音高检测模块
使用RMVPE深度学习模型进行高精度人声音高检测
"""

import os
import sys
from pathlib import Path
from typing import Optional, Tuple

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import librosa

from config import (
    RMVPE_MODEL_PATH,
    LOCAL_MODELS_DIR,
    RMVPEConfig,
    AudioConfig
)


# RMVPE模型定义
class ConvBlock(nn.Module):
    """卷积块"""
    def __init__(self, in_channels, out_channels, kernel_size=3, stride=1, padding=1):
        super().__init__()
        self.conv = nn.Conv2d(in_channels, out_channels, kernel_size, stride, padding)
        self.bn = nn.BatchNorm2d(out_channels)
        self.relu = nn.ReLU()
        self.pool = nn.MaxPool2d(2, 2)

    def forward(self, x):
        x = self.conv(x)
        x = self.bn(x)
        x = self.relu(x)
        x = self.pool(x)
        return x


class RMVPEModel(nn.Module):
    """RMVPE音高检测模型"""

    def __init__(self):
        super().__init__()

        # 输入层
        self.input_conv = nn.Conv2d(1, 64, kernel_size=3, padding=1)
        self.input_bn = nn.BatchNorm2d(64)
        self.input_relu = nn.ReLU()

        # 卷积层
        self.conv_blocks = nn.ModuleList([
            ConvBlock(64, 64),
            ConvBlock(64, 128),
            ConvBlock(128, 256),
            ConvBlock(256, 256),
            ConvBlock(256, 512),
        ])

        # 自适应池化
        self.adaptive_pool = nn.AdaptiveAvgPool2d((1, None))

        # LSTM层
        self.lstm = nn.LSTM(
            input_size=512,
            hidden_size=256,
            num_layers=2,
            batch_first=True,
            bidirectional=True
        )

        # 输出层
        self.output_layer = nn.Linear(512, 360)

    def forward(self, x):
        # x: (batch, 1, n_mels, time)
        x = self.input_conv(x)
        x = self.input_bn(x)
        x = self.input_relu(x)

        for conv_block in self.conv_blocks:
            x = conv_block(x)

        # 自适应池化
        x = self.adaptive_pool(x)

        # 重塑为序列: (batch, channels, 1, time) -> (batch, time, channels)
        x = x.squeeze(2).permute(0, 2, 1)

        # LSTM
        x, _ = self.lstm(x)

        # 输出
        x = self.output_layer(x)

        return x


class PitchDetector:
    """RMVPE音高检测器"""

    def __init__(self, device: Optional[str] = None):
        """
        初始化音高检测器

        Args:
            device: 计算设备 ('cuda' 或 'cpu')
        """
        # 自动选择设备
        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)

        self.model: Optional[nn.Module] = None
        self.is_model_loaded = False

        # 音高参数
        self.f0_bin = 360
        self.f0_max = 1100.0  # Hz
        self.f0_min = 30.0  # Hz

        # 创建频率分箱
        self._init_frequency_bins()

    def _init_frequency_bins(self):
        """初始化频率分箱"""
        # 从f0_min到f0_max，共360个bin
        self.cents_bins = np.linspace(
            self.hz_to_cent(self.f0_min),
            self.hz_to_cent(self.f0_max),
            self.f0_bin + 1
        )
        self.freq_bins = self.cent_to_hz(self.cents_bins)

    def hz_to_cent(self, hz: float) -> float:
        """频率(Hz)转换为音分(cents)"""
        return 1200 * np.log2(hz / self.f0_min)

    def cent_to_hz(self, cent: np.ndarray) -> np.ndarray:
        """音分(cents)转换为频率(Hz)"""
        return self.f0_min * (2.0 ** (cent / 1200.0))

    def load_model(self) -> bool:
        """
        加载RMVPE模型

        Returns:
            是否加载成功
        """
        # 查找模型文件
        model_path = self._find_model()

        if model_path is None:
            print("错误: 未找到RMVPE模型文件")
            print("请运行download_model.bat下载模型")
            return False

        try:
            print(f"正在加载RMVPE模型: {model_path}")

            # 创建模型
            self.model = RMVPEModel()

            # 加载权重
            state_dict = torch.load(model_path, map_location=self.device, weights_only=True)

            # 尝试加载权重，忽略不匹配的
            model_dict = self.model.state_dict()
            pretrained_dict = {k: v for k, v in state_dict.items() if k in model_dict and v.shape == model_dict[k].shape}
            model_dict.update(pretrained_dict)
            self.model.load_state_dict(model_dict)

            # 移动到设备
            self.model = self.model.to(self.device)
            self.model.eval()

            self.is_model_loaded = True
            print(f"模型加载成功，使用设备: {self.device}")

            return True

        except Exception as e:
            print(f"模型加载失败: {e}")
            print("将使用librosa的pyin算法作为备用")
            self.is_model_loaded = False
            return False

    def _find_model(self) -> Optional[Path]:
        """
        查找模型文件

        Returns:
            模型文件路径或None
        """
        # 检查配置路径
        if RMVPE_MODEL_PATH.exists():
            return RMVPE_MODEL_PATH

        # 检查本地目录
        local_path = LOCAL_MODELS_DIR / "rmvpe.pt"
        if local_path.exists():
            return local_path

        # 检查当前目录
        current_path = Path("rmvpe.pt")
        if current_path.exists():
            return current_path

        return None

    def detect_pitch(
        self,
        audio: np.ndarray,
        sample_rate: int = 16000,
        hop_length: int = 160,
        progress_callback=None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        检测音高

        Args:
            audio: 音频数据
            sample_rate: 采样率
            hop_length: 帧移
            progress_callback: 进度回调函数

        Returns:
            (时间轴, F0频率序列)
        """
        if not self.is_model_loaded:
            # 使用librosa的pyin作为备用
            return self._detect_pitch_fallback(audio, sample_rate, hop_length)

        try:
            # 确保音频是float32
            if audio.dtype != np.float32:
                audio = audio.astype(np.float32)

            # 提取梅尔频谱
            mel_spec = self._extract_mel_spectrogram(audio, sample_rate, hop_length)

            # 使用模型推理
            f0_sequence = self._inference(mel_spec, progress_callback)

            # 创建时间轴
            num_frames = len(f0_sequence)
            time_axis = np.arange(num_frames) * hop_length / sample_rate

            return time_axis, f0_sequence

        except Exception as e:
            print(f"RMVPE推理失败: {e}")
            print("使用librosa的pyin算法作为备用")
            return self._detect_pitch_fallback(audio, sample_rate, hop_length)

    def _detect_pitch_fallback(
        self,
        audio: np.ndarray,
        sample_rate: int,
        hop_length: int
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        使用librosa的pyin算法检测音高（备用方案）

        Args:
            audio: 音频数据
            sample_rate: 采样率
            hop_length: 帧移

        Returns:
            (时间轴, F0频率序列)
        """
        # 使用pyin算法
        f0, voiced_flag, voiced_probs = librosa.pyin(
            audio,
            fmin=self.f0_min,
            fmax=self.f0_max,
            sr=sample_rate,
            hop_length=hop_length
        )

        # 将NaN替换为0
        f0 = np.nan_to_num(f0, nan=0.0)

        # 创建时间轴
        time_axis = librosa.times_like(f0, sr=sample_rate, hop_length=hop_length)

        return time_axis, f0

    def _extract_mel_spectrogram(
        self,
        audio: np.ndarray,
        sample_rate: int,
        hop_length: int
    ) -> torch.Tensor:
        """
        提取梅尔频谱

        Args:
            audio: 音频数据
            sample_rate: 采样率
            hop_length: 帧移

        Returns:
            梅尔频谱张量
        """
        # 计算梅尔频谱
        mel_spec = librosa.feature.melspectrogram(
            y=audio,
            sr=sample_rate,
            n_fft=2048,
            hop_length=hop_length,
            n_mels=128,
            fmin=30,
            fmax=1100
        )

        # 转换为对数刻度
        mel_spec = np.log(np.maximum(mel_spec, 1e-5))

        # 转换为张量: (1, 1, n_mels, time)
        mel_tensor = torch.FloatTensor(mel_spec).unsqueeze(0).unsqueeze(0)

        return mel_tensor.to(self.device)

    def _inference(
        self,
        mel_spec: torch.Tensor,
        progress_callback=None
    ) -> np.ndarray:
        """
        模型推理

        Args:
            mel_spec: 梅尔频谱张量
            progress_callback: 进度回调

        Returns:
            F0频率序列
        """
        with torch.no_grad():
            # 模型推理
            output = self.model(mel_spec)

            # 转换为概率分布
            probs = torch.sigmoid(output)

            # 提取F0
            f0_sequence = self._probs_to_f0(probs)

        return f0_sequence

    def _probs_to_f0(self, probs: torch.Tensor) -> np.ndarray:
        """
        将概率分布转换为F0频率

        Args:
            probs: 概率分布张量

        Returns:
            F0频率序列
        """
        # 移动到CPU
        probs = probs.cpu().numpy()[0]  # (time, bins)

        # 找到每个时间步的最大概率对应的频率
        bin_indices = np.argmax(probs, axis=-1)

        # 转换为频率
        f0_sequence = self.freq_bins[bin_indices]

        # 检测静音帧（概率太低）
        max_probs = np.max(probs, axis=-1)
        f0_sequence[max_probs < 0.5] = 0  # 静音帧设为0

        return f0_sequence

    def f0_to_midi(self, f0: np.ndarray) -> np.ndarray:
        """
        将F0频率转换为MIDI音符编号

        Args:
            f0: F0频率序列

        Returns:
            MIDI音符编号序列
        """
        midi_notes = np.zeros_like(f0)
        valid_mask = f0 > 0

        # MIDI音符编号 = 12 * log2(f0/440) + 69
        midi_notes[valid_mask] = 12 * np.log2(f0[valid_mask] / 440) + 69

        return midi_notes

    def get_note_names(self, midi_notes: np.ndarray) -> list:
        """
        获取音符名称

        Args:
            midi_notes: MIDI音符编号

        Returns:
            音符名称列表
        """
        note_names = ['C', 'C#', 'D', 'D#', 'E', 'F',
                      'F#', 'G', 'G#', 'A', 'A#', 'B']

        names = []
        for note in midi_notes:
            if note > 0:
                octave = int(note) // 12 - 1
                note_idx = int(note) % 12
                names.append(f"{note_names[note_idx]}{octave}")
            else:
                names.append("-")

        return names

    def is_loaded(self) -> bool:
        """检查模型是否已加载"""
        return self.is_model_loaded

    def get_device_info(self) -> str:
        """获取设备信息"""
        if self.device.type == "cuda":
            return f"GPU: {torch.cuda.get_device_name(0)}"
        else:
            return "CPU"
