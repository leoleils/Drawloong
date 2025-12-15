#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频浏览器组件
支持播放视频文件
"""

import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QGroupBox, QMessageBox, QSlider
)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtGui import QIcon


class VideoViewerWidget(QWidget):
    """视频浏览器组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_video_path = None
        self.setup_ui()
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        
        # 创建组框
        group_box = QGroupBox("视频浏览")
        group_layout = QVBoxLayout(group_box)
        
        # 视频显示区域
        self.video_widget = QVideoWidget()
        self.video_widget.setMinimumHeight(300)
        self.video_widget.setStyleSheet("""
            QVideoWidget {
                background-color: #000;
            }
        """)
        group_layout.addWidget(self.video_widget)
        
        # 空状态提示
        self.empty_label = QLabel("👤 点击输出视频进行播放")
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.empty_label.setStyleSheet("""
            QLabel {
                color: #999;
                font-size: 14px;
                padding: 100px;
                background-color: #000;
            }
        """)
        group_layout.addWidget(self.empty_label)
        
        # 默认隐藏视频控件，显示空状态
        self.video_widget.hide()
        self.empty_label.show()
        
        # 进度条和时间显示
        progress_layout = QHBoxLayout()
        
        # 当前时间
        self.current_time_label = QLabel("00:00")
        self.current_time_label.setStyleSheet("color: #666; font-size: 12px; min-width: 45px;")
        progress_layout.addWidget(self.current_time_label)
        
        # 进度条
        self.progress_slider = QSlider(Qt.Horizontal)
        self.progress_slider.setRange(0, 0)
        self.progress_slider.sliderMoved.connect(self.set_position)
        self.progress_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #bbb;
                background: #ddd;
                height: 6px;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #007bff;
                border: 1px solid #0056b3;
                width: 14px;
                margin: -5px 0;
                border-radius: 7px;
            }
            QSlider::handle:horizontal:hover {
                background: #0056b3;
            }
            QSlider::sub-page:horizontal {
                background: #007bff;
                border-radius: 3px;
            }
        """)
        progress_layout.addWidget(self.progress_slider)
        
        # 总时长
        self.duration_label = QLabel("00:00")
        self.duration_label.setStyleSheet("color: #666; font-size: 12px; min-width: 45px;")
        progress_layout.addWidget(self.duration_label)
        
        group_layout.addLayout(progress_layout)
        
        # 控制栏
        control_layout = QHBoxLayout()
        
        # 视频信息
        self.video_info_label = QLabel("未加载视频")
        self.video_info_label.setStyleSheet("color: #666;")
        control_layout.addWidget(self.video_info_label)
        
        control_layout.addStretch()
        
        # 播放/暂停按钮
        self.play_pause_btn = QPushButton("▶ 播放")
        self.play_pause_btn.setEnabled(False)
        self.play_pause_btn.clicked.connect(self.toggle_play_pause)
        self.play_pause_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                padding: 6px 12px;
                border-radius: 4px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:disabled {
                background-color: #ccc;
                color: #666;
            }
        """)
        control_layout.addWidget(self.play_pause_btn)
        
        # 停止按钮
        self.stop_btn = QPushButton("■ 停止")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_video)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                padding: 6px 12px;
                border-radius: 4px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:disabled {
                background-color: #ccc;
                color: #666;
            }
        """)
        control_layout.addWidget(self.stop_btn)
        
        group_layout.addLayout(control_layout)
        layout.addWidget(group_box)
        
        # 创建媒体播放器
        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.media_player.setVideoOutput(self.video_widget)
        self.media_player.stateChanged.connect(self.on_state_changed)
        self.media_player.error.connect(self.on_error)
        self.media_player.durationChanged.connect(self.on_duration_changed)
        self.media_player.positionChanged.connect(self.on_position_changed)
    
    def load_video(self, video_path):
        """加载视频文件"""
        if not os.path.exists(video_path):
            QMessageBox.warning(self, "错误", "视频文件不存在")
            return False
        
        self.current_video_path = video_path
        
        # 隐藏空状态，显示视频控件
        self.empty_label.hide()
        self.video_widget.show()
        
        # 加载视频
        media_content = QMediaContent(QUrl.fromLocalFile(video_path))
        self.media_player.setMedia(media_content)
        
        # 更新信息
        video_name = os.path.basename(video_path)
        self.video_info_label.setText(f"视频: {video_name}")
        
        # 启用控制按钮
        self.play_pause_btn.setEnabled(True)
        self.stop_btn.setEnabled(True)
        
        # 自动播放
        self.media_player.play()
        
        return True
    
    def toggle_play_pause(self):
        """切换播放/暂停"""
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.pause()
        else:
            self.media_player.play()
    
    def stop_video(self):
        """停止播放"""
        self.media_player.stop()
        self.play_pause_btn.setText("▶ 播放")
    
    def on_state_changed(self, state):
        """播放状态改变"""
        if state == QMediaPlayer.PlayingState:
            self.play_pause_btn.setText("⏸ 暂停")
        else:
            self.play_pause_btn.setText("▶ 播放")
    
    def on_error(self, error):
        """播放错误"""
        error_string = self.media_player.errorString()
        QMessageBox.critical(self, "播放错误", f"无法播放视频:\n{error_string}")
    
    def on_duration_changed(self, duration):
        """视频时长改变"""
        self.progress_slider.setRange(0, duration)
        self.duration_label.setText(self.format_time(duration))
    
    def on_position_changed(self, position):
        """播放位置改变"""
        self.progress_slider.setValue(position)
        self.current_time_label.setText(self.format_time(position))
    
    def set_position(self, position):
        """设置播放位置"""
        self.media_player.setPosition(position)
    
    def format_time(self, ms):
        """格式化时间（毫秒转为 MM:SS）"""
        seconds = ms // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    def clear(self):
        """清空视频"""
        self.media_player.stop()
        self.media_player.setMedia(QMediaContent())
        self.current_video_path = None
        
        # 显示空状态
        self.video_widget.hide()
        self.empty_label.show()
        
        self.video_info_label.setText("未加载视频")
        self.play_pause_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        
        # 重置进度条和时间
        self.progress_slider.setValue(0)
        self.progress_slider.setRange(0, 0)
        self.current_time_label.setText("00:00")
        self.duration_label.setText("00:00")
