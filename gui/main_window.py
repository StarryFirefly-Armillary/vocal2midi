# -*- coding: utf-8 -*-
"""
主窗口界面
"""

import os
import sys
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QGroupBox, QSlider, QCheckBox,
    QFileDialog, QProgressBar, QTextEdit, QSplitter,
    QFrame, QComboBox, QSpinBox, QDoubleSpinBox, QMessageBox,
    QScrollArea
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QIcon, QColor

from gui.style import AppStyle
from gui.waveform_widget import WaveformWidget
from core.audio_processor import AudioProcessor
from core.pitch_detector import PitchDetector
from core.vibrato_detector import VibratoDetector
from core.midi_generator import MIDIGenerator
from config import SUPPORTED_FORMATS, GUIConfig
import librosa


class ProcessingThread(QThread):
    """处理线程"""
    progress = pyqtSignal(str, int)  # 状态信息, 进度百分比
    finished = pyqtSignal(bool, str)  # 是否成功, 消息

    def __init__(self, audio_path: str, output_path: str, params: dict):
        super().__init__()
        self.audio_path = audio_path
        self.output_path = output_path
        self.params = params

    def run(self):
        try:
            # 1. 加载音频
            self.progress.emit("正在加载音频文件...", 10)
            audio_processor = AudioProcessor()
            audio_data, sr = audio_processor.load_audio(self.audio_path)

            # 2. 加载RMVPE模型
            self.progress.emit("正在加载RMVPE模型...", 20)
            pitch_detector = PitchDetector()
            if not pitch_detector.load_model():
                self.finished.emit(False, "RMVPE模型加载失败")
                return

            # 3. 音高检测
            self.progress.emit("正在进行音高检测...", 30)
            rmvpe_input, rmvpe_sr = audio_processor.get_rmvpe_input()
            time_axis, f0_sequence = pitch_detector.detect_pitch(
                rmvpe_input,
                rmvpe_sr,
                progress_callback=self._pitch_progress_callback
            )

            # 4. 颤音检测
            self.progress.emit("正在检测颤音...", 60)
            vibrato_detector = VibratoDetector()
            vibrato_events = vibrato_detector.detect(
                f0_sequence,
                time_axis,
                sr,
                512
            )

            # 5. 生成MIDI
            self.progress.emit("正在生成MIDI文件...", 80)
            rms_energy = audio_processor.get_rms_energy()
            midi_generator = MIDIGenerator()
            midi = midi_generator.generate(
                f0_sequence,
                time_axis,
                vibrato_events,
                rms_energy,
                tempo=self.params.get('tempo', 120),
                pitch_bend_range=self.params.get('pitch_bend_range', 2)
            )

            # 6. 保存文件
            self.progress.emit("正在保存MIDI文件...", 90)
            midi_generator.save(self.output_path)

            self.progress.emit("完成！", 100)
            self.finished.emit(True, f"MIDI文件已保存到:\n{self.output_path}")

        except Exception as e:
            self.finished.emit(False, f"处理失败:\n{str(e)}")

    def _pitch_progress_callback(self, progress):
        """音高检测进度回调"""
        self.progress.emit(
            f"正在检测音高... {int(progress * 100)}%",
            30 + int(progress * 30)
        )


class MainWindow(QMainWindow):
    """主窗口"""

    def __init__(self):
        super().__init__()

        # 处理器
        self.audio_processor = AudioProcessor()
        self.pitch_detector = PitchDetector()
        self.vibrato_detector = VibratoDetector()
        self.midi_generator = MIDIGenerator()

        # 处理线程
        self.processing_thread: Optional[ProcessingThread] = None

        # 初始化UI
        self._init_ui()

        # 应用样式
        self.setStyleSheet(AppStyle.get_stylesheet())

        # 检查GPU状态并提示
        self._check_gpu_status()

    def _init_ui(self):
        """初始化UI"""
        self.setWindowTitle(GUIConfig.WINDOW_TITLE)
        self.setMinimumSize(GUIConfig.WINDOW_WIDTH, GUIConfig.WINDOW_HEIGHT)

        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # 标题栏
        title_bar = self._create_title_bar()
        main_layout.addWidget(title_bar)

        # 工具栏
        toolbar = self._create_toolbar()
        main_layout.addWidget(toolbar)

        # 主内容区域（使用分割器）
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # 左侧：可视化区域
        visualization_group = self._create_visualization_group()
        splitter.addWidget(visualization_group)

        # 右侧：控制面板
        control_panel = self._create_control_panel()
        splitter.addWidget(control_panel)

        # 设置分割比例
        splitter.setSizes([700, 300])

        main_layout.addWidget(splitter)

        # 底部状态栏
        status_bar = self._create_status_bar()
        main_layout.addWidget(status_bar)

    def _create_title_bar(self) -> QWidget:
        """创建标题栏"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # 图标和标题
        title_label = QLabel("🎤 Vocal2MIDI")
        title_label.setObjectName("titleLabel")
        title_label.setFont(QFont("Microsoft YaHei", 20, QFont.Weight.Bold))
        layout.addWidget(title_label)

        # 副标题
        subtitle_label = QLabel("高精度人声转MIDI转换器")
        subtitle_label.setObjectName("subtitleLabel")
        layout.addWidget(subtitle_label)

        layout.addStretch()

        return widget

    def _create_toolbar(self) -> QWidget:
        """创建工具栏"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # 导入按钮
        self.btn_import = QPushButton("📁 导入音频")
        self.btn_import.setObjectName("primaryButton")
        self.btn_import.clicked.connect(self._on_import)
        layout.addWidget(self.btn_import)

        # 导出按钮
        self.btn_export = QPushButton("💾 导出MIDI")
        self.btn_export.setObjectName("successButton")
        self.btn_export.clicked.connect(self._on_export)
        self.btn_export.setEnabled(False)
        layout.addWidget(self.btn_export)

        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.Shape.VLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)

        # 文件路径显示
        self.lbl_file_path = QLabel("未选择文件")
        self.lbl_file_path.setObjectName("statusLabel")
        layout.addWidget(self.lbl_file_path, 1)

        return widget

    def _create_visualization_group(self) -> QWidget:
        """创建可视化区域"""
        group = QGroupBox("📊 音频可视化")
        layout = QVBoxLayout(group)

        # 波形显示组件
        self.waveform_widget = WaveformWidget()
        layout.addWidget(self.waveform_widget)

        # 显示控制
        controls_layout = QHBoxLayout()

        self.chk_waveform = QCheckBox("显示波形")
        self.chk_waveform.setChecked(True)
        self.chk_waveform.stateChanged.connect(
            lambda state: self.waveform_widget.toggle_waveform(state == Qt.CheckState.Checked.value)
        )
        controls_layout.addWidget(self.chk_waveform)

        self.chk_pitch = QCheckBox("显示音高")
        self.chk_pitch.setChecked(True)
        self.chk_pitch.stateChanged.connect(
            lambda state: self.waveform_widget.toggle_pitch(state == Qt.CheckState.Checked.value)
        )
        controls_layout.addWidget(self.chk_pitch)

        self.chk_vibrato = QCheckBox("显示颤音")
        self.chk_vibrato.setChecked(True)
        self.chk_vibrato.stateChanged.connect(
            lambda state: self.waveform_widget.toggle_vibrato(state == Qt.CheckState.Checked.value)
        )
        controls_layout.addWidget(self.chk_vibrato)

        controls_layout.addStretch()

        layout.addLayout(controls_layout)

        return group

    def _create_control_panel(self) -> QWidget:
        """创建控制面板"""
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # 创建内容容器
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setSpacing(12)
        layout.setContentsMargins(8, 8, 8, 8)

        # === 快速预设 ===
        preset_label = QLabel("🎯 快速预设")
        preset_label.setFont(QFont("Microsoft YaHei", 11, QFont.Weight.Bold))
        layout.addWidget(preset_label)

        preset_btn_layout = QHBoxLayout()
        preset_btn_layout.setSpacing(6)

        self.btn_preset_default = QPushButton("默认")
        self.btn_preset_default.setToolTip("通用设置")
        self.btn_preset_default.clicked.connect(lambda: self._apply_preset("default"))
        preset_btn_layout.addWidget(self.btn_preset_default)

        self.btn_preset_ballad = QPushButton("抒情歌")
        self.btn_preset_ballad.setToolTip("慢歌，颤音更丰富")
        self.btn_preset_ballad.clicked.connect(lambda: self._apply_preset("ballad"))
        preset_btn_layout.addWidget(self.btn_preset_ballad)

        self.btn_preset_pop = QPushButton("流行歌")
        self.btn_preset_pop.setToolTip("快歌，节奏感强")
        self.btn_preset_pop.clicked.connect(lambda: self._apply_preset("pop"))
        preset_btn_layout.addWidget(self.btn_preset_pop)

        layout.addLayout(preset_btn_layout)

        # === 歌曲速度 ===
        bpm_label = QLabel("🎵 歌曲速度 (BPM)")
        bpm_label.setFont(QFont("Microsoft YaHei", 10, QFont.Weight.Bold))
        layout.addWidget(bpm_label)

        bpm_input_layout = QHBoxLayout()
        bpm_input_layout.setSpacing(6)

        self.spin_bpm = QSpinBox()
        self.spin_bpm.setRange(20, 300)
        self.spin_bpm.setValue(120)
        self.spin_bpm.setSuffix(" BPM")
        self.spin_bpm.setToolTip("慢歌60-80 | 中速100-130 | 快歌140-180")
        bpm_input_layout.addWidget(self.spin_bpm, 1)

        self.btn_detect_bpm = QPushButton("🔍 自动识别")
        self.btn_detect_bpm.setToolTip("自动检测歌曲速度")
        self.btn_detect_bpm.clicked.connect(self._on_detect_bpm)
        self.btn_detect_bpm.setEnabled(False)
        self.btn_detect_bpm.setMinimumWidth(90)
        bpm_input_layout.addWidget(self.btn_detect_bpm)

        layout.addLayout(bpm_input_layout)

        # === 颤音检测 ===
        self.chk_vibrato_detect = QCheckBox("🎤 保留颤音效果")
        self.chk_vibrato_detect.setChecked(True)
        self.chk_vibrato_detect.setToolTip("让虚拟歌手演唱更自然")
        layout.addWidget(self.chk_vibrato_detect)

        # === 力度映射 ===
        self.chk_velocity = QCheckBox("🔊 智能力度调整")
        self.chk_velocity.setChecked(True)
        self.chk_velocity.setToolTip("根据音量自动调整强弱")
        layout.addWidget(self.chk_velocity)

        # 颤音幅度（使用默认值2半音，无需用户设置）
        self.spin_bend_range = QSpinBox()
        self.spin_bend_range.setValue(2)
        self.spin_bend_range.setVisible(False)

        # === 开始转换按钮 ===
        self.btn_process = QPushButton("🚀 开始转换")
        self.btn_process.setObjectName("primaryButton")
        self.btn_process.setFont(QFont("Microsoft YaHei", 13, QFont.Weight.Bold))
        self.btn_process.setMinimumHeight(45)
        self.btn_process.clicked.connect(self._on_process)
        self.btn_process.setEnabled(False)
        layout.addWidget(self.btn_process)

        # === 进度条 ===
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setMinimumHeight(20)
        layout.addWidget(self.progress_bar)

        # === 状态标签 ===
        self.lbl_status = QLabel("就绪")
        self.lbl_status.setObjectName("statusLabel")
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_status)

        # === 检测结果 ===
        result_label = QLabel("📋 检测结果")
        result_label.setFont(QFont("Microsoft YaHei", 10, QFont.Weight.Bold))
        layout.addWidget(result_label)

        self.lbl_note_count = QLabel("音符数量: -")
        layout.addWidget(self.lbl_note_count)

        self.lbl_duration = QLabel("时长: -")
        layout.addWidget(self.lbl_duration)

        self.lbl_vibrato_count = QLabel("颤音区间: -")
        layout.addWidget(self.lbl_vibrato_count)

        layout.addStretch()

        # 设置滚动区域
        scroll_area.setWidget(content_widget)

        return scroll_area

    def _create_status_bar(self) -> QWidget:
        """创建状态栏"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 8, 0, 0)

        # 版本信息
        version_label = QLabel("v1.0.0 | RMVPE引擎")
        version_label.setObjectName("subtitleLabel")
        layout.addWidget(version_label)

        layout.addStretch()

        # 设备信息
        if self.pitch_detector.device.type == "cuda":
            device_text = "🚀 GPU加速"
            device_tip = "使用NVIDIA显卡加速处理"
        else:
            device_text = "💻 CPU模式"
            device_tip = "使用CPU处理，速度较慢\n如需加速请安装NVIDIA显卡驱动"

        self.lbl_device_info = QLabel(device_text)
        self.lbl_device_info.setObjectName("subtitleLabel")
        self.lbl_device_info.setToolTip(device_tip)
        layout.addWidget(self.lbl_device_info)

        return widget

    def _apply_preset(self, preset: str):
        """应用预设"""
        presets = {
            "default": {
                "bpm": 120,
                "vibrato": True,
                "velocity": True,
                "bend_range": 2
            },
            "ballad": {
                "bpm": 70,
                "vibrato": True,
                "velocity": True,
                "bend_range": 3
            },
            "pop": {
                "bpm": 130,
                "vibrato": True,
                "velocity": True,
                "bend_range": 2
            }
        }

        if preset in presets:
            p = presets[preset]
            self.spin_bpm.setValue(p["bpm"])
            self.chk_vibrato_detect.setChecked(p["vibrato"])
            self.chk_velocity.setChecked(p["velocity"])
            self.spin_bend_range.setValue(p["bend_range"])

    def _check_gpu_status(self):
        """检查GPU状态并显示提示"""
        try:
            import torch
            if torch.cuda.is_available():
                gpu_name = torch.cuda.get_device_name(0)
                self.lbl_status.setText(f"🚀 GPU就绪: {gpu_name}")
            else:
                self.lbl_status.setText("💻 CPU模式 (如需加速请安装CUDA版PyTorch)")
        except Exception:
            pass

    def _on_detect_bpm(self):
        """自动检测BPM"""
        if not self.audio_processor.is_loaded():
            return

        try:
            self.btn_detect_bpm.setEnabled(False)
            self.btn_detect_bpm.setText("🔄 识别中...")
            self.lbl_status.setText("正在分析歌曲节奏...")

            # 使用librosa检测BPM
            audio_data = self.audio_processor.audio_data
            sr = self.audio_processor.sample_rate

            # 检测节拍
            tempo, _ = librosa.beat.beat_track(y=audio_data, sr=sr)

            # 处理返回值（可能是数组或标量）
            if hasattr(tempo, '__len__'):
                bpm = int(round(float(tempo[0])))
            else:
                bpm = int(round(float(tempo)))

            # 限制范围
            if bpm < 20:
                bpm = 20
            elif bpm > 300:
                bpm = 300

            # 更新UI
            self.spin_bpm.setValue(bpm)
            self.btn_detect_bpm.setText("✅ 识别完成")
            self.lbl_status.setText(f"BPM已识别: {bpm}")

            # 3秒后恢复按钮
            QTimer.singleShot(3000, lambda: self.btn_detect_bpm.setText("🔍 自动识别"))
            QTimer.singleShot(3000, lambda: self.btn_detect_bpm.setEnabled(True))

        except Exception as e:
            self.btn_detect_bpm.setText("❌ 失败")
            self.lbl_status.setText(f"BPM识别失败，请手动输入")
            QTimer.singleShot(3000, lambda: self.btn_detect_bpm.setText("🔍 自动识别"))
            QTimer.singleShot(3000, lambda: self.btn_detect_bpm.setEnabled(True))

    def _on_import(self):
        """导入音频文件"""
        # 构建文件过滤器
        formats = " ".join(f"*{ext}" for ext in SUPPORTED_FORMATS)
        filter_str = f"音频文件 ({formats});;所有文件 (*.*)"

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择音频文件",
            "",
            filter_str
        )

        if file_path:
            self._load_audio(file_path)

    def _load_audio(self, file_path: str):
        """加载音频文件"""
        try:
            self.lbl_file_path.setText(file_path)
            self.lbl_status.setText("正在加载音频...")

            # 加载音频
            self.audio_processor.load_audio(file_path)

            # 更新波形显示
            waveform_data = self.audio_processor.get_waveform_data(1000)
            time_axis = self.audio_processor.get_time_axis(1000)
            self.waveform_widget.set_waveform_data(waveform_data, time_axis)

            # 更新状态
            duration = self.audio_processor.get_duration()
            self.lbl_duration.setText(f"时长: {duration:.2f}秒")
            self.lbl_status.setText("音频加载成功")

            # 启用处理按钮和BPM检测按钮
            self.btn_process.setEnabled(True)
            self.btn_detect_bpm.setEnabled(True)

        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载音频失败:\n{str(e)}")
            self.lbl_status.setText("加载失败")

    def _on_export(self):
        """导出MIDI文件"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存MIDI文件",
            "",
            "MIDI文件 (*.mid);;所有文件 (*.*)"
        )

        if file_path:
            # 确保有.mid扩展名
            if not file_path.endswith('.mid'):
                file_path += '.mid'

            # 保存文件（如果已经生成了MIDI）
            if self.midi_generator.midi is not None:
                if self.midi_generator.save(file_path):
                    QMessageBox.information(
                        self,
                        "成功",
                        f"MIDI文件已保存到:\n{file_path}"
                    )

    def _on_process(self):
        """开始处理"""
        if self.processing_thread and self.processing_thread.isRunning():
            return

        # 检查是否已加载音频
        if not self.audio_processor.is_loaded():
            QMessageBox.warning(self, "警告", "请先导入音频文件")
            return

        # 获取输出路径
        input_path = self.audio_processor.file_path
        output_path = input_path.with_suffix('.mid')

        # 获取参数
        params = {
            'tempo': self.spin_bpm.value(),
            'pitch_bend_range': self.spin_bend_range.value(),
            'vibrato_detect': self.chk_vibrato_detect.isChecked(),
            'velocity_mapping': self.chk_velocity.isChecked()
        }

        # 创建并启动处理线程
        self.processing_thread = ProcessingThread(
            str(input_path),
            str(output_path),
            params
        )
        self.processing_thread.progress.connect(self._on_progress)
        self.processing_thread.finished.connect(self._on_finished)

        # 禁用按钮
        self.btn_process.setEnabled(False)
        self.btn_import.setEnabled(False)

        # 启动处理
        self.processing_thread.start()

    def _on_progress(self, status: str, progress: int):
        """更新进度"""
        self.lbl_status.setText(status)
        self.progress_bar.setValue(progress)

    def _on_finished(self, success: bool, message: str):
        """处理完成"""
        # 启用按钮
        self.btn_process.setEnabled(True)
        self.btn_import.setEnabled(True)

        if success:
            self.btn_export.setEnabled(True)
            self.lbl_status.setText("转换完成")

            # 更新结果信息
            self.lbl_note_count.setText(f"音符数量: {self.midi_generator.get_note_count()}")
            self.lbl_vibrato_count.setText(f"颤音区间: {self.vibrato_detector.get_vibrato_count()}")

            # 更新音高曲线显示
            if hasattr(self.processing_thread, 'f0_sequence'):
                self.waveform_widget.set_pitch_data(
                    self.processing_thread.f0_sequence,
                    self.processing_thread.time_axis
                )

            QMessageBox.information(self, "成功", message)
        else:
            self.lbl_status.setText("转换失败")
            QMessageBox.critical(self, "错误", message)
