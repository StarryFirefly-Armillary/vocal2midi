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


# RMVPE模型定义（简化版，用于加载权重）
class RMVPEModel(nn.Module):
    """RMVPE音高检测模型"""

    def __init__(self):
        super().__init__()
        # 模型架构（这里使用简化的表示）
        # 实际实现需要完整的RMVPE网络结构
        self.conv_layers = nn.ModuleList()
        self.lstm_layers = nn.ModuleList()

        # 输入层
        self.input_conv = nn.Conv2d(1, 64, kernel_size=3, padding=1)

        # 卷积层
        for i in range(6):
            self.conv_layers.append(
                nn.Sequential(
                    nn.Conv2d(64 * (2 ** min(i, 3)), 64 * (2 ** min(i + 1, 3)),
                              kernel_size=3, padding=1),
                    nn.BatchNorm2d(64 * (2 ** min(i + 1, 3))),
                    nn.ReLU(),
                    nn.MaxPool2d(2, 2)
                )
            )

        # LSTM层
        self.lstm = nn.LSTM(
            input_size=64 * 8,
            hidden_size=256,
            num_layers=2,
            batch_first=True,
            bidirectional=True
        )

        # 输出层
        self.output_layer = nn.Linear(512, 360)  # 360个音高类别

    def forward(self, x):
        # x: (batch, 1, n_mels, time)
        x = self.input_conv(x)

        for conv in self.conv_layers:
            x = conv(x)

        # 重塑为序列
        batch, channels, height, width = x.shape
        x = x.permute(0, 3, 1, 2).reshape(batch, width, -1)

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

        # 音高类别对应的频率
        self._init_frequency_bins()

    def _init_frequency_bins(self):
        """初始化频率分箱"""
        # 从C1到B7，共360个半音（30个八度）
        # MIDI音符范围：24-108（C1-C8）
        self.f0_bin = 360
        self.f0_max = 1046.50  # C6
        self.f0_min = 32.70  # C1

        # 创建频率分箱
        self.cent_bins = np.linspace(
            self.f0_to_cent(self.f0_min),
            self.f0_to_cent(self.f0_max),
            self.f0_bin + 1
        )
        self.freq_bins = self.cent_to_f0(self.cent_bins)

    def f0_to_cent(self, f0: float) -> float:
        """频率转换为音分"""
        return 1200 * np.log2(f0 / self.f0_min)

    def cent_to_f0(self, cent: np.ndarray) -> np.ndarray:
        """音分转换为频率"""
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
            print("请运行install.bat下载模型，或手动下载模型到以下位置之一：")
            print(f"  1. {RMVPE_MODEL_PATH}")
            print(f"  2. {LOCAL_MODELS_DIR / 'rmvpe.pt'}")
            return False

        try:
            print(f"正在加载RMVPE模型: {model_path}")

            # 创建模型
            self.model = RMVPEModel()

            # 加载权重
            state_dict = torch.load(model_path, map_location=self.device)
            self.model.load_state_dict(state_dict, strict=False)

            # 移动到设备
            self.model = self.model.to(self.device)
            self.model.eval()

            self.is_model_loaded = True
            print(f"模型加载成功，使用设备: {self.device}")

            return True

        except Exception as e:
            print(f"模型加载失败: {e}")
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
            raise RuntimeError("请先调用 load_model() 加载模型")

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
            n_fft=RMVPEConfig.N_MELS * 20,
            hop_length=hop_length,
            n_mels=RMVPEConfig.N_MELS,
            fmin=50,
            fmax=8000
        )

        # 转换为对数刻度
        mel_spec = np.log(np.maximum(mel_spec, 1e-5))

        # 转换为张量
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
            probs = F.softmax(output, dim=-1)

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
        f0_sequence = self.cent_bins[bin_indices]

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
