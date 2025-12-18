#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图生视频 QT 客户端应用 - 主入口
基于 PyQt5 + QFluentWidgets 的桌面客户端，调用阿里云 DashScope API 实现图片转视频功能
"""

__version__ = "1.15.1"

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from ui.fluent_main_window import FluentMainWindow
from ui.splash_screen import SplashScreen
from themes.fluent_theme import apply_fluent_theme, FLUENT_AVAILABLE


def get_resource_path(relative_path):
    """获取资源文件的绝对路径（支持打包后的路径）"""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller 打包后的路径
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)


def main():
    """应用程序主入口"""
    # 设置环境变量，避免 macOS 输入法相关的崩溃
    os.environ['QT_MAC_WANTS_LAYER'] = '1'
    
    # 启用高DPI缩放
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    app.setApplicationName("Drawloong")
    app.setOrganizationName("烛龙绘影")
    
    # 设置应用图标
    icon_path = get_resource_path('logo.png')
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    # 初始化 Fluent 主题（如果可用）
    if FLUENT_AVAILABLE:
        # 应用已保存的 Fluent 主题配置
        apply_fluent_theme()
    else:
        # 如果 QFluentWidgets 不可用，使用 Fusion 样式作为降级方案
        app.setStyle('Fusion')
    
    # 创建 Fluent 风格主窗口(但不显示)
    window = FluentMainWindow()
    
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
