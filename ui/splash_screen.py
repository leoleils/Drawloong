#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
启动画面
显示开机动画视频
"""

import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt, QUrl, QTimer, pyqtSignal
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtGui import QPixmap


class SplashScreen(QWidget):
    """启动画面窗口"""
    
    # 定义信号
    finished = pyqtSignal()  # 动画播放完成
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_player()
    
    def setup_ui(self):
        """设置界面"""
        # 无边框窗口,置顶显示
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 设置固定大小
        self.setFixedSize(400, 400)
        
        # 居中显示
        from PyQt5.QtWidgets import QDesktopWidget
        screen = QDesktopWidget().screenGeometry()
        self.move((screen.width() - self.width()) // 2,
                  (screen.height() - self.height()) // 2)
        
        # 主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 视频播放器
        self.video_widget = QVideoWidget()
        self.video_widget.setStyleSheet("background-color: black;")
        layout.addWidget(self.video_widget)
    
    def setup_player(self):
        """设置媒体播放器"""
        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.media_player.setVideoOutput(self.video_widget)
        
        # 连接信号
        self.media_player.mediaStatusChanged.connect(self.on_media_status_changed)
        self.media_player.error.connect(self.on_error)
    
    def get_resource_path(self, relative_path):
        """获取资源文件的绝对路径（支持打包后的路径）"""
        import sys
        if hasattr(sys, '_MEIPASS'):
            # PyInstaller 打包后的路径
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.dirname(os.path.dirname(__file__)), relative_path)
    
    def play(self):
        """播放开机动画"""
        # 获取动画视频路径（支持打包后的路径）
        video_path = self.get_resource_path('launch_animation.mp4')
        
        if not os.path.exists(video_path):
            print(f"开机动画文件不存在: {video_path}")
            # 如果文件不存在,延迟后直接关闭
            QTimer.singleShot(500, self.close_and_finish)
            return
        
        # 加载并播放视频
        media_content = QMediaContent(QUrl.fromLocalFile(video_path))
        self.media_player.setMedia(media_content)
        self.media_player.play()
        
        # 显示窗口
        self.show()
    
    def on_media_status_changed(self, status):
        """媒体状态改变"""
        if status == QMediaPlayer.EndOfMedia:
            # 播放结束
            self.close_and_finish()
        elif status == QMediaPlayer.InvalidMedia:
            # 无效媒体
            print("无效的媒体文件")
            self.close_and_finish()
    
    def on_error(self, error):
        """播放错误"""
        error_string = self.media_player.errorString()
        print(f"播放开机动画出错: {error_string}")
        self.close_and_finish()
    
    def close_and_finish(self):
        """关闭并发送完成信号"""
        self.media_player.stop()
        self.close()
        self.finished.emit()
    
    def mousePressEvent(self, event):
        """点击跳过动画"""
        self.close_and_finish()
    
    def keyPressEvent(self, event):
        """按键跳过动画"""
        self.close_and_finish()
