#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图生视频 QT 客户端应用 - 主入口
基于 PyQt5 的桌面客户端，调用阿里云 DashScope API 实现图片转视频功能
"""

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from ui.main_window import MainWindow
from ui.splash_screen import SplashScreen


def main():
    """应用程序主入口"""
    # 启用高DPI缩放
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    app.setApplicationName("Drawloong")
    app.setOrganizationName("烛龙绘影")
    
    # 设置应用样式
    app.setStyle('Fusion')
    
    # 创建主窗口(但不显示)
    window = MainWindow()
    
    # 创建并显示开机动画
    splash = SplashScreen()
    
    # 动画播放完成后显示主窗口
    def show_main_window():
        window.show()
        splash.deleteLater()  # 删除启动画面对象
    
    splash.finished.connect(show_main_window)
    splash.play()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
