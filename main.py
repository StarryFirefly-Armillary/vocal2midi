# -*- coding: utf-8 -*-
"""
Vocal2MIDI - 人声转MIDI转换器
主程序入口
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from gui import MainWindow
from config import ensure_dirs


def main():
    """主函数"""
    # 确保必要的目录存在
    ensure_dirs()

    # 设置高DPI支持（必须在创建QApplication之前）
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    # 创建应用
    app = QApplication(sys.argv)

    # 创建并显示主窗口
    window = MainWindow()
    window.show()

    # 运行应用
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
