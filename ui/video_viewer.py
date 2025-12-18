#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频浏览器组件
支持播放视频文件
使用 QFluentWidgets 组件实现现代化 UI
"""

import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel
)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget

try:
    from qfluentwidgets import (
        CardWidget, ToolButton, BodyLabel, CaptionLabel,
        Slider, FluentIcon, isDarkTheme
    )
    FLUENT_AVAILABLE = True
except ImportError:
    FLUENT_AVAILABLE = False
    from PyQt5.QtWidgets import QPushButton, QSlider, QGroupBox
    print("警告: QFluentWidgets 未安装，将使用原生 PyQt5 组件")

from utils.message_helper import MessageHelper


class VideoViewerWidget(QWidget):
    """视频浏览器组件 - 使用 QFluentWidgets 美化"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_video_path = None
        self.setup_ui()
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        if FLUENT_AVAILABLE:
            self._setup_fluent_ui(layout)
        else:
            self._setup_native_ui(layout)
        
        # 创建媒体播放器
        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.media_player.setVideoOutput(self.video_widget)
        self.media_player.stateChanged.connect(self.on_state_changed)
        self.media_player.error.connect(self.on_error)
        self.media_player.durationChanged.connect(self.on_duration_changed)
        self.media_player.positionChanged.connect(self.on_position_changed)
    
    def _setup_fluent_ui(self, layout: QVBoxLayout):
        """设置 Fluent 风格 UI"""
        # 视频区域卡片
        self.video_card = CardWidget()
        video_card_layout = QVBoxLayout(self.video_card)
        # 统一卡片内边距：12px（视频播放器稍小以留更多空间给视频）
        video_card_layout.setContentsMargins(12, 12, 12, 12)
        # 统一组件间距：8px
        video_card_layout.setSpacing(8)
        
        # 视频显示区域 - 按16:9比例设置
        self.video_widget = QVideoWidget()
        self.video_widget.setMinimumSize(640, 360)  # 16:9比例，更大的基础尺寸
        self.video_widget.setAspectRatioMode(1)  # 保持宽高比
        self.video_widget.setStyleSheet("""
            QVideoWidget {
                background-color: #000;
                border-radius: 8px;
            }
        """)
        video_card_layout.addWidget(self.video_widget, 1)  # 添加stretch factor
        
        # 空状态提示 - 按16:9比例设置
        self.empty_label = BodyLabel("🎬 点击输出视频进行播放")
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.empty_label.setMinimumSize(640, 360)  # 16:9比例，更大的基础尺寸
        self.empty_label.setStyleSheet("""
            BodyLabel {
                background-color: #000;
                border-radius: 8px;
                padding: 100px;
            }
        """)
        video_card_layout.addWidget(self.empty_label, 1)  # 添加stretch factor
        
        # 默认隐藏视频控件，显示空状态
        self.video_widget.hide()
        self.empty_label.show()
        
        # 进度条和时间显示
        progress_layout = QHBoxLayout()
        progress_layout.setSpacing(12)
        
        # 当前时间
        self.current_time_label = CaptionLabel("00:00")
        self.current_time_label.setFixedWidth(45)
        progress_layout.addWidget(self.current_time_label)
        
        # 进度条 - 使用 QFluentWidgets 的 Slider
        self.progress_slider = Slider(Qt.Horizontal)
        self.progress_slider.setRange(0, 0)
        self.progress_slider.sliderMoved.connect(self.set_position)
        progress_layout.addWidget(self.progress_slider, 1)
        
        # 总时长
        self.duration_label = CaptionLabel("00:00")
        self.duration_label.setFixedWidth(45)
        progress_layout.addWidget(self.duration_label)
        
        video_card_layout.addLayout(progress_layout)
        
        # 控制栏
        control_layout = QHBoxLayout()
        control_layout.setSpacing(8)
        
        # 视频信息
        self.video_info_label = CaptionLabel("未加载视频")
        control_layout.addWidget(self.video_info_label)
        
        control_layout.addStretch()
        
        # 播放/暂停按钮 - 使用 ToolButton 配合 FluentIcon
        self.play_btn = ToolButton(FluentIcon.PLAY)
        self.play_btn.setFixedSize(36, 36)
        self.play_btn.setEnabled(False)
        self.play_btn.clicked.connect(self.toggle_play_pause)
        self.play_btn.setToolTip("播放")
        control_layout.addWidget(self.play_btn)
        
        # 暂停按钮
        self.pause_btn = ToolButton(FluentIcon.PAUSE)
        self.pause_btn.setFixedSize(36, 36)
        self.pause_btn.setEnabled(False)
        self.pause_btn.clicked.connect(self.toggle_play_pause)
        self.pause_btn.setToolTip("暂停")
        self.pause_btn.hide()  # 初始隐藏
        control_layout.addWidget(self.pause_btn)
        
        # 停止按钮
        self.stop_btn = ToolButton(FluentIcon.POWER_BUTTON)
        self.stop_btn.setFixedSize(36, 36)
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_video)
        self.stop_btn.setToolTip("停止")
        control_layout.addWidget(self.stop_btn)
        
        video_card_layout.addLayout(control_layout)
        layout.addWidget(self.video_card)
    
    def _setup_native_ui(self, layout: QVBoxLayout):
        """设置原生 PyQt5 UI（降级方案）"""
        # 创建组框
        group_box = QGroupBox("视频浏览")
        group_layout = QVBoxLayout(group_box)
        
        # 视频显示区域 - 按16:9比例设置
        self.video_widget = QVideoWidget()
        self.video_widget.setMinimumSize(640, 360)  # 16:9比例，更大的基础尺寸
        self.video_widget.setAspectRatioMode(1)  # 保持宽高比
        self.video_widget.setStyleSheet("""
            QVideoWidget {
                background-color: #000;
            }
        """)
        group_layout.addWidget(self.video_widget, 1)  # 添加stretch factor
        
        # 空状态提示 - 按16:9比例设置
        self.empty_label = QLabel("👤 点击输出视频进行播放")
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.empty_label.setMinimumSize(640, 360)  # 16:9比例，更大的基础尺寸
        self.empty_label.setStyleSheet("""
            QLabel {
                color: #999;
                font-size: 14px;
                padding: 100px;
                background-color: #000;
            }
        """)
        group_layout.addWidget(self.empty_label, 1)  # 添加stretch factor
        
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
        self.play_btn = QPushButton("▶ 播放")
        self.play_btn.setEnabled(False)
        self.play_btn.clicked.connect(self.toggle_play_pause)
        self.play_btn.setStyleSheet("""
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
        control_layout.addWidget(self.play_btn)
        
        # 暂停按钮（原生模式下不单独显示）
        self.pause_btn = None
        
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
        
        # 原生模式下没有 video_card
        self.video_card = None
    
    def load_video(self, video_path):
        """加载视频文件"""
        if not os.path.exists(video_path):
            parent = self.window()
            MessageHelper.warning(parent, "错误", "视频文件不存在")
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
        self.play_btn.setEnabled(True)
        self.stop_btn.setEnabled(True)
        if FLUENT_AVAILABLE and self.pause_btn:
            self.pause_btn.setEnabled(True)
        
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
        self._update_play_button_state(False)
    
    def _update_play_button_state(self, is_playing: bool):
        """更新播放按钮状态"""
        if FLUENT_AVAILABLE and self.pause_btn:
            # Fluent 模式：切换显示播放/暂停按钮
            if is_playing:
                self.play_btn.hide()
                self.pause_btn.show()
            else:
                self.play_btn.show()
                self.pause_btn.hide()
        else:
            # 原生模式：更新按钮文字
            if is_playing:
                self.play_btn.setText("⏸ 暂停")
            else:
                self.play_btn.setText("▶ 播放")
    
    def on_state_changed(self, state):
        """播放状态改变"""
        is_playing = (state == QMediaPlayer.PlayingState)
        self._update_play_button_state(is_playing)
    
    def on_error(self, error):
        """播放错误"""
        error_string = self.media_player.errorString()
        parent = self.window()
        MessageHelper.error(parent, "播放错误", f"无法播放视频:\n{error_string}")
    
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
        self.play_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        if FLUENT_AVAILABLE and self.pause_btn:
            self.pause_btn.setEnabled(False)
            self.pause_btn.hide()
            self.play_btn.show()
        
        # 重置进度条和时间
        self.progress_slider.setValue(0)
        self.progress_slider.setRange(0, 0)
        self.current_time_label.setText("00:00")
        self.duration_label.setText("00:00")
