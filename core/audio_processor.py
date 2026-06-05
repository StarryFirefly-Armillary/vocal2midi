# -*- coding: utf-8 -*-
"""
音频处理模块
负责音频文件的加载、预处理和格式转换
"""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Tuple

import numpy as np
import librosa
import soundfile as sf

from config import (
    FFMPEG_EXE,
    SUPPORTED_FORMATS,
    AudioConfig
)


class AudioProcessor:
    """音频处理器"""

    def __init__(self):
        self.audio_data: Optional[np.ndarray] = None
        self.sample_rate: int = AudioConfig.SAMPLE_RATE
        self.duration: float = 0.0
        self.file_path: Optional[Path] = None

    def load_audio(self, file_path: str) -> Tuple[np.ndarray, int]:
        """
        加载音频文件

        Args:
            file_path: 音频文件路径

        Returns:
            (音频数据, 采样率)

        Raises:
            ValueError: 不支持的格式
            FileNotFoundError: 文件不存在
        """
        file_path = Path(file_path)

        # 检查文件是否存在
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        # 检查格式是否支持
        if file_path.suffix.lower() not in SUPPORTED_FORMATS:
            raise ValueError(f"不支持的音频格式: {file_path.suffix}")

        self.file_path = file_path

        # 使用librosa加载音频
        try:
            audio_data, sr = librosa.load(
                str(file_path),
                sr=AudioConfig.SAMPLE_RATE,
                mono=True
            )
        except Exception as e:
            # 如果librosa加载失败，尝试使用ffmpeg转换后加载
            audio_data, sr = self._load_with_ffmpeg(file_path)

        # 预处理
        audio_data = self._preprocess(audio_data)

        self.audio_data = audio_data
        self.sample_rate = sr
        self.duration = len(audio_data) / sr

        return audio_data, sr

    def _load_with_ffmpeg(self, file_path: Path) -> Tuple[np.ndarray, int]:
        """
        使用ffmpeg加载音频（备用方案）

        Args:
            file_path: 音频文件路径

        Returns:
            (音频数据, 采样率)
        """
        if not FFMPEG_EXE.exists():
            raise RuntimeError(
                f"FFmpeg未找到: {FFMPEG_EXE}\n"
                "请运行install.bat安装FFmpeg"
            )

        # 创建临时文件
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            # 使用ffmpeg转换
            cmd = [
                str(FFMPEG_EXE),
                "-i", str(file_path),
                "-ar", str(AudioConfig.SAMPLE_RATE),
                "-ac", "1",
                "-y",
                tmp_path
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                raise RuntimeError(f"FFmpeg转换失败: {result.stderr}")

            # 加载转换后的文件
            audio_data, sr = librosa.load(tmp_path, sr=None, mono=True)

            return audio_data, sr

        finally:
            # 清理临时文件
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def _preprocess(self, audio_data: np.ndarray) -> np.ndarray:
        """
        音频预处理

        Args:
            audio_data: 原始音频数据

        Returns:
            处理后的音频数据
        """
        # 移除直流偏移
        audio_data = audio_data - np.mean(audio_data)

        # 归一化
        max_val = np.max(np.abs(audio_data))
        if max_val > 0:
            audio_data = audio_data / max_val * 0.95

        return audio_data

    def get_rmvpe_input(self) -> Tuple[np.ndarray, int]:
        """
        获取RMVPE模型的输入格式

        Returns:
            (重采样后的音频数据, 16000)
        """
        if self.audio_data is None:
            raise RuntimeError("请先加载音频文件")

        # 重采样到16kHz
        if self.sample_rate != AudioConfig.RMVPE_SAMPLE_RATE:
            audio_16k = librosa.resample(
                self.audio_data,
                orig_sr=self.sample_rate,
                target_sr=AudioConfig.RMVPE_SAMPLE_RATE
            )
        else:
            audio_16k = self.audio_data.copy()

        return audio_16k, AudioConfig.RMVPE_SAMPLE_RATE

    def get_waveform_data(self, num_points: int = 1000) -> np.ndarray:
        """
        获取波形显示数据（降采样）

        Args:
            num_points: 显示点数

        Returns:
            降采样后的波形数据
        """
        if self.audio_data is None:
            return np.array([])

        # 降采样
        indices = np.linspace(0, len(self.audio_data) - 1, num_points, dtype=int)
        return self.audio_data[indices]

    def get_time_axis(self, num_points: int = 1000) -> np.ndarray:
        """
        获取时间轴

        Args:
            num_points: 显示点数

        Returns:
            时间轴数组（秒）
        """
        if self.audio_data is None:
            return np.array([])

        return np.linspace(0, self.duration, num_points)

    def get_rms_energy(self, frame_length: int = 2048, hop_length: int = 512) -> np.ndarray:
        """
        计算RMS能量（用于力度映射）

        Args:
            frame_length: 帧长
            hop_length: 帧移

        Returns:
            RMS能量数组
        """
        if self.audio_data is None:
            return np.array([])

        return librosa.feature.rms(
            y=self.audio_data,
            frame_length=frame_length,
            hop_length=hop_length
        )[0]

    def get_duration(self) -> float:
        """获取音频时长（秒）"""
        return self.duration

    def is_loaded(self) -> bool:
        """检查是否已加载音频"""
        return self.audio_data is not None
