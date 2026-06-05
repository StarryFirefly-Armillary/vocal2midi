# -*- coding: utf-8 -*-
"""
波形和音高可视化组件
"""

import numpy as np
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import QPainter, QPen, QColor, QLinearGradient, QPainterPath

from gui.style import AppStyle


class WaveformWidget(QWidget):
    """波形和音高可视化组件"""

    def __init__(self, parent=None):
        super().__init__(parent)

        # 数据
        self.waveform_data: np.ndarray = np.array([])
        self.time_axis: np.ndarray = np.array([])
        self.pitch_data: np.ndarray = np.array([])
        self.pitch_time: np.ndarray = np.array([])
        self.vibrato_regions: list = []

        # 显示设置
        self.show_waveform = True
        self.show_pitch = True
        self.show_vibrato = True

        # 颜色
        self.colors = AppStyle.COLORS

        # 设置最小尺寸
        self.setMinimumHeight(200)
        self.setMinimumWidth(400)

    def set_waveform_data(self, data: np.ndarray, time_axis: np.ndarray):
        """设置波形数据"""
        self.waveform_data = data
        self.time_axis = time_axis
        self.update()

    def set_pitch_data(self, pitch: np.ndarray, time_axis: np.ndarray):
        """设置音高数据"""
        self.pitch_data = pitch
        self.pitch_time = time_axis
        self.update()

    def set_vibrato_regions(self, regions: list):
        """设置颤音区域"""
        self.vibrato_regions = regions
        self.update()

    def clear(self):
        """清除所有数据"""
        self.waveform_data = np.array([])
        self.time_axis = np.array([])
        self.pitch_data = np.array([])
        self.pitch_time = np.array([])
        self.vibrato_regions = []
        self.update()

    def paintEvent(self, event):
        """绘制事件"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 获取绘制区域
        rect = self.rect()
        width = rect.width()
        height = rect.height()

        # 绘制背景
        self._draw_background(painter, rect)

        # 绘制网格
        self._draw_grid(painter, rect)

        # 绘制波形
        if self.show_waveform and len(self.waveform_data) > 0:
            self._draw_waveform(painter, rect)

        # 绘制音高曲线
        if self.show_pitch and len(self.pitch_data) > 0:
            self._draw_pitch_curve(painter, rect)

        # 绘制颤音区域
        if self.show_vibrato and len(self.vibrato_regions) > 0:
            self._draw_vibrato_regions(painter, rect)

        painter.end()

    def _draw_background(self, painter: QPainter, rect: QRectF):
        """绘制背景"""
        painter.fillRect(rect, QColor(self.colors['bg_dark']))

        # 绘制边框
        painter.setPen(QPen(QColor(self.colors['border']), 1))
        painter.drawRect(rect.adjusted(1, 1, -1, -1))

    def _draw_grid(self, painter: QPainter, rect: QRectF):
        """绘制网格"""
        painter.setPen(QPen(QColor(self.colors['border']), 0.5, Qt.PenStyle.DotLine))

        # 垂直网格线（时间）
        margin = 60
        num_vertical = 10
        for i in range(num_vertical + 1):
            x = margin + i * (rect.width() - 2 * margin) / num_vertical
            painter.drawLine(int(x), int(margin), int(x), int(rect.height() - margin))

        # 水平网格线
        num_horizontal = 6
        for i in range(num_horizontal + 1):
            y = margin + i * (rect.height() - 2 * margin) / num_horizontal
            painter.drawLine(int(margin), int(y), int(rect.width() - margin), int(y))

    def _draw_waveform(self, painter: QPainter, rect: QRectF):
        """绘制波形"""
        if len(self.waveform_data) == 0:
            return

        margin = 60
        draw_rect = rect.adjusted(margin, margin, -margin, -margin)

        # 创建波形路径
        path = QPainterPath()
        n = len(self.waveform_data)

        # 计算采样点
        x_scale = draw_rect.width() / n
        y_center = draw_rect.center().y()
        y_scale = draw_rect.height() / 2 * 0.8

        # 绘制上半部分
        path.moveTo(draw_rect.left(), y_center)
        for i in range(n):
            x = draw_rect.left() + i * x_scale
            y = y_center - self.waveform_data[i] * y_scale
            path.lineTo(x, y)

        # 绘制下半部分（镜像）
        for i in range(n - 1, -1, -1):
            x = draw_rect.left() + i * x_scale
            y = y_center + self.waveform_data[i] * y_scale
            path.lineTo(x, y)

        path.closeSubpath()

        # 创建渐变
        gradient = QLinearGradient(0, draw_rect.top(), 0, draw_rect.bottom())
        gradient.setColorAt(0, QColor(129, 140, 248, 100))  # 紫色，半透明
        gradient.setColorAt(0.5, QColor(129, 140, 248, 200))
        gradient.setColorAt(1, QColor(129, 140, 248, 100))

        # 填充波形
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(gradient)
        painter.drawPath(path)

        # 绘制波形边框
        painter.setPen(QPen(QColor(self.colors['waveform']), 1.5))
        painter.setBrush(Qt.BrushStyle.NoBrush)

        # 上边框
        border_path = QPainterPath()
        border_path.moveTo(draw_rect.left(), y_center)
        for i in range(n):
            x = draw_rect.left() + i * x_scale
            y = y_center - self.waveform_data[i] * y_scale
            border_path.lineTo(x, y)
        painter.drawPath(border_path)

        # 下边框
        border_path = QPainterPath()
        border_path.moveTo(draw_rect.left(), y_center)
        for i in range(n):
            x = draw_rect.left() + i * x_scale
            y = y_center + self.waveform_data[i] * y_scale
            border_path.lineTo(x, y)
        painter.drawPath(border_path)

    def _draw_pitch_curve(self, painter: QPainter, rect: QRectF):
        """绘制音高曲线"""
        if len(self.pitch_data) == 0:
            return

        margin = 60
        draw_rect = rect.adjusted(margin, margin, -margin, -margin)

        # 过滤有效音高
        valid_mask = self.pitch_data > 0
        if not np.any(valid_mask):
            return

        valid_pitch = self.pitch_data[valid_mask]
        valid_time = self.pitch_time[valid_mask] if len(self.pitch_time) == len(self.pitch_data) else np.where(valid_mask)[0]

        # 计算音高范围
        min_pitch = np.min(valid_pitch)
        max_pitch = np.max(valid_pitch)
        pitch_range = max_pitch - min_pitch

        if pitch_range == 0:
            pitch_range = 1

        # 创建路径
        path = QPainterPath()
        n = len(valid_pitch)

        # 计算坐标
        if len(self.pitch_time) == len(self.pitch_data):
            time_range = self.pitch_time[-1] - self.pitch_time[0]
            if time_range == 0:
                time_range = 1

        for i in range(n):
            # X坐标（时间）
            if len(self.pitch_time) == len(self.pitch_data):
                x = draw_rect.left() + (valid_time[i] - self.pitch_time[0]) / time_range * draw_rect.width()
            else:
                x = draw_rect.left() + i / n * draw_rect.width()

            # Y坐标（音高，反转）
            y = draw_rect.bottom() - (valid_pitch[i] - min_pitch) / pitch_range * draw_rect.height()

            if i == 0:
                path.moveTo(x, y)
            else:
                path.lineTo(x, y)

        # 绘制音高曲线
        painter.setPen(QPen(QColor(self.colors['pitch_curve']), 2))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path)

    def _draw_vibrato_regions(self, painter: QPainter, rect: QRectF):
        """绘制颤音区域"""
        if not self.vibrato_regions:
            return

        margin = 60
        draw_rect = rect.adjusted(margin, margin, -margin, -margin)

        # 计算时间范围
        if len(self.time_axis) == 0:
            return

        time_range = self.time_axis[-1] - self.time_axis[0]
        if time_range == 0:
            return

        # 设置半透明画刷
        vibrato_color = QColor(self.colors['vibrato'])
        vibrato_color.setAlpha(40)

        for region in self.vibrato_regions:
            start_time, end_time = region

            # 计算X坐标
            x1 = draw_rect.left() + (start_time - self.time_axis[0]) / time_range * draw_rect.width()
            x2 = draw_rect.left() + (end_time - self.time_axis[0]) / time_range * draw_rect.width()

            # 绘制半透明矩形
            painter.fillRect(
                QRectF(x1, draw_rect.top(), x2 - x1, draw_rect.height()),
                vibrato_color
            )

            # 绘制边框
            painter.setPen(QPen(QColor(self.colors['vibrato']), 1, Qt.PenStyle.DashLine))
            painter.drawRect(QRectF(x1, draw_rect.top(), x2 - x1, draw_rect.height()))

    def toggle_waveform(self, show: bool):
        """切换波形显示"""
        self.show_waveform = show
        self.update()

    def toggle_pitch(self, show: bool):
        """切换音高曲线显示"""
        self.show_pitch = show
        self.update()

    def toggle_vibrato(self, show: bool):
        """切换颤音区域显示"""
        self.show_vibrato = show
        self.update()
