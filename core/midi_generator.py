# -*- coding: utf-8 -*-
"""
MIDI生成模块
将音高检测结果转换为高质量MIDI文件
"""

import numpy as np
import pretty_midi
from typing import List, Optional, Tuple
from pathlib import Path

from config import MIDIConfig
from .vibrato_detector import VibratoEvent


class MIDIGenerator:
    """MIDI生成器"""

    def __init__(self):
        self.midi: Optional[pretty_midi.PrettyMIDI] = None
        self.config = MIDIConfig()

    def generate(
        self,
        f0_sequence: np.ndarray,
        time_axis: np.ndarray,
        vibrato_events: List[VibratoEvent],
        rms_energy: Optional[np.ndarray] = None,
        tempo: float = 120.0,
        pitch_bend_range: int = 2
    ) -> pretty_midi.PrettyMIDI:
        """
        生成MIDI文件

        Args:
            f0_sequence: F0频率序列
            time_axis: 时间轴
            vibrato_events: 颤音事件列表
            rms_energy: RMS能量（用于力度映射）
            tempo: BPM
            pitch_bend_range: 弯音范围（半音）

        Returns:
            PrettyMIDI对象
        """
        # 创建MIDI对象
        self.midi = pretty_midi.PrettyMIDI(
            initial_tempo=tempo,
            resolution=self.config.PPQ
        )

        # 创建乐器（人声）
        instrument = pretty_midi.Instrument(
            program=0,  # 钢琴音色（虚拟歌手通常使用这个）
            name="Vocal",
            is_drum=False
        )

        # 提取音符序列
        notes = self._extract_notes(f0_sequence, time_axis, rms_energy)

        # 添加音符到乐器
        for note in notes:
            instrument.notes.append(note)

        # 添加Pitch Bend事件（颤音）
        pitch_bends = self._generate_pitch_bends(
            vibrato_events,
            time_axis,
            pitch_bend_range
        )
        for pb in pitch_bends:
            instrument.pitch_bends.append(pb)

        # 添加乐器到MIDI
        self.midi.instruments.append(instrument)

        return self.midi

    def _extract_notes(
        self,
        f0_sequence: np.ndarray,
        time_axis: np.ndarray,
        rms_energy: Optional[np.ndarray] = None
    ) -> List[pretty_midi.Note]:
        """
        提取音符序列

        Args:
            f0序列: F0频率序列
            time_axis: 时间轴
            rms_energy: RMS能量

        Returns:
            音符列表
        """
        notes = []

        # 状态变量
        current_note = None
        current_start = 0
        current_pitch = 0
        note_pitches = []

        for i in range(len(f0_sequence)):
            f0 = f0_sequence[i]
            time = time_axis[i]

            # 检查是否是有效音高
            if f0 > 0:
                midi_note = self._f0_to_midi_note(f0)

                if current_note is None:
                    # 开始新音符
                    current_note = midi_note
                    current_start = time
                    current_pitch = f0
                    note_pitches = [f0]
                elif self._is_same_note(midi_note, current_note):
                    # 继续当前音符
                    note_pitches.append(f0)
                else:
                    # 结束当前音符，开始新音符
                    if len(note_pitches) > 0:
                        note = self._create_note(
                            current_note,
                            current_start,
                            time,
                            note_pitches,
                            rms_energy,
                            i
                        )
                        if note is not None:
                            notes.append(note)

                    # 开始新音符
                    current_note = midi_note
                    current_start = time
                    current_pitch = f0
                    note_pitches = [f0]
            else:
                # 静音帧
                if current_note is not None:
                    # 结束当前音符
                    if len(note_pitches) > 0:
                        note = self._create_note(
                            current_note,
                            current_start,
                            time,
                            note_pitches,
                            rms_energy,
                            i
                        )
                        if note is not None:
                            notes.append(note)

                    current_note = None
                    note_pitches = []

        # 处理最后一个音符
        if current_note is not None and len(note_pitches) > 0:
            note = self._create_note(
                current_note,
                current_start,
                time_axis[-1],
                note_pitches,
                rms_energy,
                len(f0_sequence) - 1
            )
            if note is not None:
                notes.append(note)

        return notes

    def _f0_to_midi_note(self, f0: float) -> int:
        """
        将频率转换为MIDI音符编号

        Args:
            f0: 频率（Hz）

        Returns:
            MIDI音符编号
        """
        if f0 <= 0:
            return 0

        # MIDI音符 = 12 * log2(f0/440) + 69
        midi_note = 12 * np.log2(f0 / 440) + 69

        return int(round(midi_note))

    def _is_same_note(self, note1: int, note2: int) -> bool:
        """
        检查是否是同一个音符（允许微小偏差）

        Args:
            note1: 音符1
            note2: 音符2

        Returns:
            是否是同一个音符
        """
        return abs(note1 - note2) < 0.5

    def _create_note(
        self,
        pitch: int,
        start_time: float,
        end_time: float,
        pitch_values: List[float],
        rms_energy: Optional[np.ndarray],
        frame_index: int
    ) -> Optional[pretty_midi.Note]:
        """
        创建音符对象

        Args:
            pitch: MIDI音符编号
            start_time: 开始时间
            end_time: 结束时间
            pitch_values: 音高值列表
            rms_energy: RMS能量
            frame_index: 帧索引

        Returns:
            音符对象或None
        """
        # 检查音符时长
        duration = end_time - start_time
        if duration < self.config.MIN_NOTE_DURATION:
            return None

        # 计算力度
        velocity = self._calculate_velocity(
            pitch_values,
            rms_energy,
            frame_index
        )

        # 创建音符
        note = pretty_midi.Note(
            velocity=velocity,
            pitch=pitch,
            start=start_time,
            end=end_time
        )

        return note

    def _calculate_velocity(
        self,
        pitch_values: List[float],
        rms_energy: Optional[np.ndarray],
        frame_index: int
    ) -> int:
        """
        计算音符力度

        Args:
            pitch_values: 音高值列表
            rms_energy: RMS能量
            frame_index: 帧索引

        Returns:
            力度值（0-127）
        """
        if rms_energy is not None and len(rms_energy) > 0:
            # 使用RMS能量计算力度
            if frame_index < len(rms_energy):
                energy = rms_energy[frame_index]
            else:
                energy = rms_energy[-1]

            # 归一化到力度范围
            max_energy = np.max(rms_energy)
            if max_energy > 0:
                normalized = energy / max_energy
            else:
                normalized = 0.5

            velocity = int(
                self.config.VELOCITY_MIN +
                normalized * (self.config.VELOCITY_MAX - self.config.VELOCITY_MIN)
            )
        else:
            # 默认中等力度
            velocity = 80

        # 限制范围
        velocity = max(self.config.VELOCITY_MIN,
                       min(self.config.VELOCITY_MAX, velocity))

        return velocity

    def _generate_pitch_bends(
        self,
        vibrato_events: List[VibratoEvent],
        time_axis: np.ndarray,
        pitch_bend_range: int
    ) -> List[pretty_midi.PitchBend]:
        """
        生成Pitch Bend事件

        Args:
            vibrato_events: 颤音事件列表
            time_axis: 时间轴
            pitch_bend_range: 弯音范围（半音）

        Returns:
            Pitch Bend事件列表
        """
        pitch_bends = []

        for event in vibrato_events:
            # 生成正弦波形的弯音
            start = event.start_time
            end = event.end_time
            duration = end - start

            # 计算点数
            num_points = int(duration * 100)  # 100点/秒
            if num_points < 2:
                num_points = 2

            for i in range(num_points):
                t = start + i * duration / (num_points - 1)

                # 正弦波形
                angle = 2 * np.pi * event.rate * (t - start)
                value = np.sin(angle)

                # 转换为弯音值（±8192）
                max_bend = 8192 * event.depth / (pitch_bend_range * 100)
                bend_value = int(value * max_bend)

                # 限制范围
                bend_value = max(-8192, min(8191, bend_value))

                # 创建Pitch Bend事件
                pb = pretty_midi.PitchBend(
                    pitch=bend_value,
                    time=t
                )
                pitch_bends.append(pb)

        return pitch_bends

    def save(self, file_path: str) -> bool:
        """
        保存MIDI文件

        Args:
            file_path: 文件路径

        Returns:
            是否保存成功
        """
        if self.midi is None:
            print("错误：没有可保存的MIDI数据")
            return False

        try:
            # 确保目录存在
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)

            # 保存文件
            self.midi.write(str(path))
            print(f"MIDI文件已保存: {file_path}")

            return True

        except Exception as e:
            print(f"保存MIDI文件失败: {e}")
            return False

    def get_note_count(self) -> int:
        """获取音符数量"""
        if self.midi is None:
            return 0

        return sum(len(inst.notes) for inst in self.midi.instruments)

    def get_duration(self) -> float:
        """获取MIDI时长"""
        if self.midi is None:
            return 0.0

        return self.midi.get_end_time()

    def get_pitch_bend_count(self) -> int:
        """获取Pitch Bend事件数量"""
        if self.midi is None:
            return 0

        return sum(len(inst.pitch_bends) for inst in self.midi.instruments)
