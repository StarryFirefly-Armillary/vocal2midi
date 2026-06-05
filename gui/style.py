# -*- coding: utf-8 -*-
"""
GUI样式定义
深色主题，现代化设计
"""


class AppStyle:
    """应用程序样式"""

    # 颜色定义
    COLORS = {
        # 主色调
        'primary': '#6366f1',        # 紫色
        'primary_hover': '#818cf8',
        'primary_pressed': '#4f46e5',

        # 背景色
        'bg_dark': '#0f0f23',        # 最深背景
        'bg_medium': '#1a1a2e',      # 中等背景
        'bg_light': '#252542',       # 浅背景
        'bg_card': '#1e1e3f',        # 卡片背景

        # 文本色
        'text_primary': '#e2e8f0',   # 主文本
        'text_secondary': '#94a3b8', # 次要文本
        'text_muted': '#64748b',     # 暗淡文本

        # 强调色
        'accent_green': '#10b981',   # 成功/播放
        'accent_red': '#ef4444',     # 错误/停止
        'accent_yellow': '#f59e0b',  # 警告
        'accent_blue': '#3b82f6',    # 信息

        # 波形颜色
        'waveform': '#818cf8',       # 波形
        'pitch_curve': '#f472b6',    # 音高曲线
        'vibrato': '#fbbf24',        # 颤音标记

        # 边框
        'border': '#2d2d5e',
        'border_light': '#3d3d7e',
    }

    @staticmethod
    def get_stylesheet() -> str:
        """获取主样式表"""
        colors = AppStyle.COLORS

        return f"""
        /* 主窗口 */
        QMainWindow {{
            background-color: {colors['bg_dark']};
            color: {colors['text_primary']};
        }}

        /* 通用QWidget */
        QWidget {{
            background-color: transparent;
            color: {colors['text_primary']};
            font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
            font-size: 13px;
        }}

        /* 按钮基础样式 */
        QPushButton {{
            background-color: {colors['bg_light']};
            border: 1px solid {colors['border']};
            border-radius: 6px;
            padding: 8px 14px;
            color: {colors['text_primary']};
            font-weight: 500;
            min-height: 18px;
        }}

        QPushButton:hover {{
            background-color: {colors['border']};
            border-color: {colors['border_light']};
        }}

        QPushButton:pressed {{
            background-color: {colors['bg_medium']};
        }}

        QPushButton:disabled {{
            background-color: {colors['bg_dark']};
            color: {colors['text_muted']};
            border-color: {colors['bg_medium']};
        }}

        /* 主要按钮 */
        QPushButton#primaryButton {{
            background-color: {colors['primary']};
            border-color: {colors['primary']};
            color: white;
        }}

        QPushButton#primaryButton:hover {{
            background-color: {colors['primary_hover']};
            border-color: {colors['primary_hover']};
        }}

        QPushButton#primaryButton:pressed {{
            background-color: {colors['primary_pressed']};
        }}

        /* 成功按钮 */
        QPushButton#successButton {{
            background-color: {colors['accent_green']};
            border-color: {colors['accent_green']};
            color: white;
        }}

        QPushButton#successButton:hover {{
            background-color: #059669;
        }}

        /* 危险按钮 */
        QPushButton#dangerButton {{
            background-color: {colors['accent_red']};
            border-color: {colors['accent_red']};
            color: white;
        }}

        QPushButton#dangerButton:hover {{
            background-color: #dc2626;
        }}

        /* 分组框 */
        QGroupBox {{
            background-color: {colors['bg_card']};
            border: 1px solid {colors['border']};
            border-radius: 8px;
            margin-top: 12px;
            padding: 12px 8px 8px 8px;
            font-weight: bold;
        }}

        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 2px 8px;
            background-color: {colors['primary']};
            border-radius: 4px;
            color: white;
            font-size: 11px;
        }}

        /* 标签 */
        QLabel {{
            color: {colors['text_primary']};
            padding: 2px;
            background-color: transparent;
        }}

        QLabel#titleLabel {{
            font-size: 18px;
            font-weight: bold;
        }}

        QLabel#subtitleLabel {{
            font-size: 11px;
            color: {colors['text_secondary']};
        }}

        QLabel#statusLabel {{
            font-size: 12px;
            padding: 6px 10px;
            background-color: {colors['bg_light']};
            border-radius: 4px;
        }}

        /* 输入框 */
        QLineEdit {{
            background-color: {colors['bg_light']};
            border: 1px solid {colors['border']};
            border-radius: 8px;
            padding: 10px 14px;
            color: {colors['text_primary']};
            selection-background-color: {colors['primary']};
        }}

        QLineEdit:focus {{
            border-color: {colors['primary']};
        }}

        /* 下拉框 */
        QComboBox {{
            background-color: {colors['bg_light']};
            border: 1px solid {colors['border']};
            border-radius: 8px;
            padding: 10px 14px;
            color: {colors['text_primary']};
            min-width: 120px;
        }}

        QComboBox:hover {{
            border-color: {colors['border_light']};
        }}

        QComboBox::drop-down {{
            border: none;
            padding-right: 10px;
        }}

        QComboBox QAbstractItemView {{
            background-color: {colors['bg_medium']};
            border: 1px solid {colors['border']};
            color: {colors['text_primary']};
            selection-background-color: {colors['primary']};
        }}

        /* 滑块 */
        QSlider::groove:horizontal {{
            height: 6px;
            background: {colors['bg_light']};
            border-radius: 3px;
        }}

        QSlider::handle:horizontal {{
            background: {colors['primary']};
            border: none;
            width: 18px;
            height: 18px;
            margin: -6px 0;
            border-radius: 9px;
        }}

        QSlider::handle:horizontal:hover {{
            background: {colors['primary_hover']};
        }}

        QSlider::sub-page:horizontal {{
            background: {colors['primary']};
            border-radius: 3px;
        }}

        /* 进度条 */
        QProgressBar {{
            background-color: {colors['bg_light']};
            border: none;
            border-radius: 8px;
            height: 12px;
            text-align: center;
            color: {colors['text_primary']};
            font-size: 10px;
        }}

        QProgressBar::chunk {{
            background-color: {colors['primary']};
            border-radius: 8px;
        }}

        /* 复选框 */
        QCheckBox {{
            spacing: 8px;
            color: {colors['text_primary']};
            padding: 4px 0px;
        }}

        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border-radius: 4px;
            border: 2px solid {colors['border']};
            background: {colors['bg_light']};
        }}

        QCheckBox::indicator:checked {{
            background: {colors['primary']};
            border-color: {colors['primary']};
        }}

        QCheckBox::indicator:hover {{
            border-color: {colors['primary']};
        }}

        /* 数字输入框 */
        QSpinBox, QDoubleSpinBox {{
            background-color: {colors['bg_light']};
            border: 1px solid {colors['border']};
            border-radius: 6px;
            padding: 6px 10px;
            color: {colors['text_primary']};
        }}

        QSpinBox:focus, QDoubleSpinBox:focus {{
            border-color: {colors['primary']};
        }}

        /* 文本编辑器 */
        QTextEdit {{
            background-color: {colors['bg_light']};
            border: 1px solid {colors['border']};
            border-radius: 8px;
            padding: 10px;
            color: {colors['text_primary']};
            font-family: "Consolas", "Courier New", monospace;
        }}

        /* 滚动条 */
        QScrollBar:vertical {{
            background: {colors['bg_dark']};
            width: 10px;
            margin: 0;
        }}

        QScrollBar::handle:vertical {{
            background: {colors['border']};
            min-height: 30px;
            border-radius: 5px;
        }}

        QScrollBar::handle:vertical:hover {{
            background: {colors['border_light']};
        }}

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0;
        }}

        QScrollBar:horizontal {{
            background: {colors['bg_dark']};
            height: 10px;
            margin: 0;
        }}

        QScrollBar::handle:horizontal {{
            background: {colors['border']};
            min-width: 30px;
            border-radius: 5px;
        }}

        QScrollBar::handle:horizontal:hover {{
            background: {colors['border_light']};
        }}

        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0;
        }}

        /* 工具提示 */
        QToolTip {{
            background-color: {colors['bg_medium']};
            color: {colors['text_primary']};
            border: 1px solid {colors['border']};
            border-radius: 6px;
            padding: 8px;
            font-size: 12px;
        }}

        /* 滚动区域 */
        QScrollArea {{
            background-color: transparent;
            border: none;
        }}

        QScrollArea > QWidget > QWidget {{
            background-color: transparent;
        }}

        /* 标签页 */
        QTabWidget::pane {{
            background-color: {colors['bg_card']};
            border: 1px solid {colors['border']};
            border-radius: 8px;
        }}

        QTabBar::tab {{
            background-color: {colors['bg_light']};
            border: 1px solid {colors['border']};
            border-bottom: none;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            padding: 10px 20px;
            color: {colors['text_secondary']};
            margin-right: 2px;
        }}

        QTabBar::tab:selected {{
            background-color: {colors['bg_card']};
            color: {colors['text_primary']};
            border-bottom: 2px solid {colors['primary']};
        }}

        QTabBar::tab:hover {{
            background-color: {colors['border']};
            color: {colors['text_primary']};
        }}
        """

    @staticmethod
    def get_dark_palette():
        """获取深色调色板（可选）"""
        from PyQt6.QtGui import QPalette, QColor
        from PyQt6.QtCore import Qt

        colors = AppStyle.COLORS
        palette = QPalette()

        # 设置各种颜色角色
        palette.setColor(QPalette.ColorRole.Window, QColor(colors['bg_dark']))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(colors['text_primary']))
        palette.setColor(QPalette.ColorRole.Base, QColor(colors['bg_medium']))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(colors['bg_light']))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(colors['bg_medium']))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(colors['text_primary']))
        palette.setColor(QPalette.ColorRole.Text, QColor(colors['text_primary']))
        palette.setColor(QPalette.ColorRole.Button, QColor(colors['bg_light']))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(colors['text_primary']))
        palette.setColor(QPalette.ColorRole.BrightText, QColor('#ffffff'))
        palette.setColor(QPalette.ColorRole.Link, QColor(colors['primary']))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(colors['primary']))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor('#ffffff'))

        return palette
