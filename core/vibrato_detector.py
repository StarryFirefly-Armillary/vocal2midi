# -*- coding: utf-8 -*-
"""
颤音检测模块
检测和量化人声中的颤音特征
"""

import numpy as np
from scipy import signal
from typing import List, Tuple, Optional
from dataclasses import dataclass

from config import VibratoConfig


@dataclass
class VibratoEvent:
    """颤音事件"""
    start_time: float  # 开始时间（秒）
    end_time: float  # 结束时间（秒）
    rate: float  # 颤音频率（Hz）
    depth: float  # 颤音深度（音分）
    center_f0: float  # 中心频率（Hz）


class VibratoDetector:
    """颤音检测器"""

    def __init__(self):
        self.config = VibratoConfig()
        self.vibrato_events: List[VibratoEvent] = []

    def detect(
        self,
        f0_sequence: np.ndarray,
        time_axis: np.ndarray,
        sample_rate: int = 44100,
        hop_length: int = 512
    ) -> List[VibratoEvent]:
        """
        检测颤音

        Args:
            f0_sequence: F0频率序列
            time_axis: 时间轴
            sample_rate: 采样率
            hop_length: 帧移

        Returns:
            颤音事件列表
        """
        self.vibrato_events = []

        # 计算帧率
        frame_rate = sample_rate / hop_length

        # 应用带通滤波器提取颤音成分
        vibrato_signal = self._apply_bandpass_filter(f0_sequence, frame_rate)

        # 检测颤音区间
        vibrato_segments = self._find_vibrato_segments(vibrato_signal, frame_rate)

        # 分析每个颤音区间
        for start_frame, end_frame in vibrato_segments:
            event = self._analyze_vibrato_segment(
                f0_sequence,
                time_axis,
                vibrato_signal,
                start_frame,
                end_frame,
                frame_rate
            )

            if event is not None:
                self.vibrato_events.append(event)

        return self.vibrato_events

    def _apply_bandpass_filter(
        self,
        f0_sequence: np.ndarray,
        frame_rate: float
    ) -> np.ndarray:
        """
        应用带通滤波器提取颤音成分

        Args:
            f0_sequence: F0频率序列
            frame_rate: 帧率

        Returns:
            颤音信号
        """
        # 设计带通滤波器（4-8Hz）
        nyquist = frame_rate / 2
        low = self.config.MIN_RATE / nyquist
        high = self.config.MAX_RATE / nyquist

        # 确保频率在有效范围内
        if high >= 1.0:
            high = 0.99
        if low <= 0:
            low = 0.01

        try:
            b, a = signal.butter(4, [low, high], btype='band')
            vibrato_signal = signal.filtfilt(b, a, f0_sequence)
        except Exception:
            # 如果滤波失败，返回零信号
            vibrato_signal = np.zeros_like(f0_sequence)

        return vibrato_signal

    def _find_vibrato_segments(
        self,
        vibrato_signal: np.ndarray,
        frame_rate: float
    ) -> List[Tuple[int, int]]:
        """
        查找颤音区间

        Args:
            vibrato_signal: 颤音信号
            frame_rate: 帧率

        Returns:
            颤音区间列表 [(start, end), ...]
        """
        # 计算信号包络
        envelope = np.abs(vibrato_signal)

        # 应用平滑滤波
        window_size = int(frame_rate * 0.05)  # 50ms窗口
        if window_size > 0:
            envelope = np.convolve(
                envelope,
                np.ones(window_size) / window_size,
                mode='same'
            )

        # 计算阈值（基于信号标准差）
        threshold = self.config.MIN_DEPTH / 1200  # 转换为半音

        # 找到超过阈值的区间
        above_threshold = envelope > threshold

        # 查找连续区间
        segments = []
        in_segment = False
        start = 0

        for i in range(len(above_threshold)):
            if above_threshold[i] and not in_segment:
                start = i
                in_segment = True
            elif not above_threshold[i] and in_segment:
                # 检查区间长度是否足够
                duration = (i - start) / frame_rate
                if duration >= 0.1:  # 最少100ms
                    segments.append((start, i))
                in_segment = False

        # 处理最后一个区间
        if in_segment:
            duration = (len(above_threshold) - start) / frame_rate
            if duration >= 0.1:
                segments.append((start, len(above_threshold)))

        return segments

    def _analyze_vibrato_segment(
        self,
        f0_sequence: np.ndarray,
        time_axis: np.ndarray,
        vibrato_signal: np.ndarray,
        start_frame: int,
        end_frame: int,
        frame_rate: float
    ) -> Optional[VibratoEvent]:
        """
        分析颤音区间

        Args:
            f0_sequence: F0频率序列
            time_axis: 时间轴
            vibrato_signal: 颤音信号
            start_frame: 开始帧
            end_frame: 结束帧
            frame_rate: 帧率

        Returns:
            颤音事件或None
        """
        # 提取区间内的信号
        segment = vibrato_signal[start_frame:end_frame]
        f0_segment = f0_sequence[start_frame:end_frame]

        # 检查是否有足够的有效数据
        if len(segment) < 10 or np.std(f0_segment) == 0:
            return None

        # 计算颤音频率（通过过零率）
        zero_crossings = np.where(np.diff(np.sign(segment)))[0]
        if len(zero_crossings) < 2:
            return None

        # 颤音频率 = 过零次数 / 2 / 时长
        duration = len(segment) / frame_rate
        rate = len(zero_crossings) / 2 / duration

        # 检查频率是否在合理范围内
        if rate < self.config.MIN_RATE or rate > self.config.MAX_RATE:
            return None

        # 计算颤音深度
        depth_cents = np.std(segment) * 1200  # 转换为音分

        # 检查深度是否在合理范围内
        if depth_cents < self.config.MIN_DEPTH:
            return None

        # 限制最大深度
        if depth_cents > self.config.MAX_DEPTH:
            depth_cents = self.config.MAX_DEPTH

        # 计算中心频率
        center_f0 = np.mean(f0_segment[f0_segment > 0])
        if np.isnan(center_f0) or center_f0 <= 0:
            return None

        # 创建颤音事件
        start_time = time_axis[start_frame] if start_frame < len(time_axis) else 0
        end_time = time_axis[end_frame] if end_frame < len(time_axis) else 0

        return VibratoEvent(
            start_time=start_time,
            end_time=end_time,
            rate=rate,
            depth=depth_cents,
            center_f0=center_f0
        )

    def get_vibrato_events(self) -> List[VibratoEvent]:
        """获取检测到的颤音事件"""
        return self.vibrato_events

    def get_vibrato_count(self) -> int:
        """获取颤音数量"""
        return len(self.vibrato_events)

    def get_vibrato_density(self, total_duration: float) -> float:
        """
        计算颤音密度（每秒颤音数）

        Args:
            total_duration: 总时长（秒）

        Returns:
            颤音密度
        """
        if total_duration <= 0:
            return 0.0

        return len(self.vibrato_events) / total_duration

    def get_average_vibrato_rate(self) -> float:
        """获取平均颤音频率"""
        if not self.vibrato_events:
            return 0.0

        return np.mean([e.rate for e in self.vibrato_events])

    def get_average_vibrato_depth(self) -> float:
        """获取平均颤音深度（音分）"""
        if not self.vibrato_events:
            return 0.0

        return np.mean([e.depth for e in self.vibrato_events])

    def generate_pitch_bend_events(
        self,
        events: List[VibratoEvent],
        pitch_bend_range: int = 2
    ) -> List[Tuple[float, int]]:
        """
        生成MIDI Pitch Bend事件

        Args:
            events: 颤音事件列表
            pitch_bend_range: 弯音范围（半音）

        Returns:
            [(时间, 弯音值), ...]
        """
        pitch_bend_events = []

        for event in events:
            # 计算时间点
            start = event.start_time
            end = event.end_time
            duration = end - start

            # 生成正弦波形的弯音事件
            num_cycles = event.rate * duration
            num_points = int(num_cycles * 20)  # 每个周期20个点

            for i in range(num_points):
                t = start + i * duration / num_points

                # 正弦波形
                angle = 2 * np.pi * event.rate * (t - start)
                value = np.sin(angle)

                # 转换为弯音值（±8192）
                max_bend = 8192 * event.depth / (pitch_bend_range * 100)
                bend_value = int(value * max_bend)

                # 限制范围
                bend_value = max(-8192, min(8191, bend_value))

                pitch_bend_events.append((t, bend_value + 8192))  # 偏移到0-16383

        # 按时间排序
        pitch_bend_events.sort(key=lambda x: x[0])

        return pitch_bend_events
