#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
参考生视频组件
支持上传参考视频，通过文本提示词生成新视频
"""

import os
import time
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QTextEdit, QGroupBox, QFileDialog, QMessageBox,
    QSplitter, QScrollArea, QCheckBox, QSpinBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QDragEnterEvent, QDropEvent

from .video_viewer import VideoViewerWidget


class DragDropVideoLabel(QLabel):
    """支持拖拽的视频标签组件，支持显示视频缩略图"""
    
    video_dropped = pyqtSignal(str)  # 视频路径
    
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setAcceptDrops(True)
        self.default_text = text
        self.video_path = None
        self.thumbnail_pixmap = None  # 存储缩略图
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """拖拽进入事件"""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls:
                file_path = urls[0].toLocalFile()
                if file_path.lower().endswith(('.mp4', '.mov')):
                    event.acceptProposedAction()
                    self.setStyleSheet("""
                        QLabel {
                            border: 2px dashed #007bff;
                            border-radius: 4px;
                            background: #e7f3ff;
                            color: #007bff;
                        }
                    """)
                    return
        event.ignore()
    
    def dragLeaveEvent(self, event):
        """拖拽离开事件"""
        if not self.video_path:
            self.setStyleSheet("""
                QLabel {
                    border: 2px dashed #ddd;
                    border-radius: 4px;
                    background: #f9f9f9;
                    color: #999;
                }
            """)
    
    def dragMoveEvent(self, event):
        """拖拽移动事件"""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls:
                file_path = urls[0].toLocalFile()
                if file_path.lower().endswith(('.mp4', '.mov')):
                    event.acceptProposedAction()
                    return
        event.ignore()
    
    def dropEvent(self, event: QDropEvent):
        """拖放事件"""
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if file_path.lower().endswith(('.mp4', '.mov')):
                self.video_dropped.emit(file_path)
                event.acceptProposedAction()
                return
        event.ignore()
    
    def setVideoPath(self, path):
        """设置视频路径并生成缩略图"""
        self.video_path = path
        if path and os.path.exists(path):
            file_name = os.path.basename(path)
            file_size = os.path.getsize(path) / (1024 * 1024)  # MB
            
            # 尝试生成视频缩略图
            thumbnail = self.generate_video_thumbnail(path)
            if thumbnail:
                self.thumbnail_pixmap = thumbnail
                self.setPixmap(thumbnail.scaled(
                    self.width() - 20, 
                    self.height() - 40, 
                    Qt.KeepAspectRatio, 
                    Qt.SmoothTransformation
                ))
                # 在图片下方显示文件信息
                self.setAlignment(Qt.AlignCenter)
            else:
                # 如果无法生成缩略图，显示文本信息
                self.setText(f"🎬 {file_name}\n({file_size:.1f} MB)")
            
            self.setStyleSheet("""
                QLabel {
                    border: 2px solid #28a745;
                    border-radius: 4px;
                    background: #f8f9fa;
                    color: #155724;
                    padding: 5px;
                }
            """)
    
    def generate_video_thumbnail(self, video_path):
        """生成视频缩略图（使用OpenCV提取第一帧）"""
        try:
            import cv2
            import numpy as np
            from PyQt5.QtGui import QImage, QPixmap
            
            # 打开视频文件
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                return None
            
            # 读取第一帧
            ret, frame = cap.read()
            cap.release()
            
            if not ret or frame is None:
                return None
            
            # 转换BGR到RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # 转换为QImage
            height, width, channel = frame_rgb.shape
            bytes_per_line = 3 * width
            q_image = QImage(frame_rgb.data, width, height, bytes_per_line, QImage.Format_RGB888)
            
            # 转换为QPixmap
            pixmap = QPixmap.fromImage(q_image)
            
            if not pixmap.isNull():
                return pixmap
            
            return None
            
        except ImportError:
            # 如果没有安装cv2，静默失败
            return None
        except Exception as e:
            # 静默失败，不打印错误
            return None
    
    def resizeEvent(self, event):
        """窗口大小改变时重新缩放缩略图"""
        super().resizeEvent(event)
        if self.thumbnail_pixmap and not self.thumbnail_pixmap.isNull():
            self.setPixmap(self.thumbnail_pixmap.scaled(
                self.width() - 20,
                self.height() - 40,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            ))


class ReferenceVideoWorker(QThread):
    """参考生视频工作线程"""
    
    finished = pyqtSignal(str, dict)  # 视频路径, 视频信息
    error = pyqtSignal(str)
    progress = pyqtSignal(str)
    task_submitted = pyqtSignal(str)  # 任务ID，用于任务管理器监控
    
    def __init__(self, api_client, reference_videos, prompt, negative_prompt,
                 size, duration, shot_type, audio, output_folder):
        super().__init__()
        self.api_client = api_client
        self.reference_videos = reference_videos
        self.prompt = prompt
        self.negative_prompt = negative_prompt
        self.size = size
        self.duration = duration
        self.shot_type = shot_type
        self.audio = audio
        self.output_folder = output_folder
    
    def run(self):
        """执行生成任务"""
        try:
            self.progress.emit("📤 正在上传参考视频...")
            
            # 上传视频并获取URL
            reference_video_urls = []
            for video_path in self.reference_videos:
                self.progress.emit(f"📤 正在上传: {os.path.basename(video_path)}")
                video_url = self.api_client.upload_video_and_get_url(video_path, "wan2.6-r2v")
                reference_video_urls.append(video_url)
            
            self.progress.emit("📤 正在提交任务...")
            
            # 提交任务
            result = self.api_client.submit_reference_video_to_video(
                reference_video_urls=reference_video_urls,
                prompt=self.prompt,
                negative_prompt=self.negative_prompt,
                size=self.size,
                duration=self.duration,
                shot_type=self.shot_type,
                audio=self.audio
            )
            
            # 获取任务ID
            task_id = result['output']['task_id']
            self.progress.emit(f"⏳ 任务已提交 (ID: {task_id})")
            
            # 发送任务ID信号，用于任务管理器监控
            self.task_submitted.emit(task_id)
            
            # 轮询任务状态
            max_retries = 180
            retry_count = 0
            
            while retry_count < max_retries:
                time.sleep(5)
                retry_count += 1
                
                self.progress.emit(f"🔄 正在生成视频... ({retry_count}/{max_retries})")
                
                task_result = self.api_client.query_task(task_id)
                task_status = task_result['output'].get('task_status', '')
                
                if task_status == 'SUCCEEDED':
                    video_url = task_result['output'].get('video_url', '')
                    orig_prompt = task_result['output'].get('orig_prompt', self.prompt)
                    
                    if not video_url:
                        self.error.emit("视频URL为空")
                        return
                    
                    self.progress.emit("📥 正在下载视频...")
                    video_path = self.api_client.download_video(video_url, self.output_folder)
                    
                    # 构建视频信息
                    video_info = {
                        'model': 'wan2.6-r2v',
                        'size': self.size,
                        'duration': self.duration,
                        'shot_type': self.shot_type,
                        'audio': self.audio,
                        'orig_prompt': orig_prompt,
                        'reference_videos': [os.path.basename(v) for v in self.reference_videos],
                        'video_url': video_url,
                        'task_id': task_id
                    }
                    
                    # 保存元数据
                    try:
                        import json
                        metadata_path = video_path.replace('.mp4', '_metadata.json')
                        with open(metadata_path, 'w', encoding='utf-8') as f:
                            json.dump(video_info, f, ensure_ascii=False, indent=2)
                    except Exception as e:
                        print(f"保存元数据失败: {e}")
                    
                    self.finished.emit(video_path, video_info)
                    return
                    
                elif task_status == 'FAILED':
                    error_code = task_result['output'].get('code', 'Unknown')
                    error_msg = task_result['output'].get('message', '未知错误')
                    self.error.emit(f"生成失败 [{error_code}]: {error_msg}")
                    return
                    
                elif task_status == 'UNKNOWN':
                    self.error.emit("任务查询过期，请重试")
                    return
            
            self.error.emit(f"生成超时（已等待{max_retries * 5}秒）")
            
        except Exception as e:
            self.error.emit(f"生成失败: {str(e)}")


class ReferenceVideoToVideoWidget(QWidget):
    """参考生视频组件"""
    
    def __init__(self, api_client, project_manager, task_manager, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.project_manager = project_manager
        self.task_manager = task_manager
        self.worker = None
        self.reference_videos = []
        self.current_task = None  # 当前正在执行的任务
        self.setup_ui()
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        main_splitter = QSplitter(Qt.Horizontal)
        
        # 左侧：参考视频预览和任务列表
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        left_splitter = QSplitter(Qt.Vertical)
        
        preview_widget = self.create_preview_panel()
        left_splitter.addWidget(preview_widget)
        
        left_layout.addWidget(left_splitter)
        main_splitter.addWidget(left_widget)
        
        # 右侧：配置面板和视频预览
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        right_splitter = QSplitter(Qt.Vertical)
        
        config_widget = self.create_config_panel()
        right_splitter.addWidget(config_widget)
        
        self.video_viewer = VideoViewerWidget()
        right_splitter.addWidget(self.video_viewer)
        
        right_splitter.setStretchFactor(0, 1)
        right_splitter.setStretchFactor(1, 1)
        
        right_layout.addWidget(right_splitter)
        main_splitter.addWidget(right_widget)
        
        main_splitter.setStretchFactor(0, 2)
        main_splitter.setStretchFactor(1, 1)
        
        layout.addWidget(main_splitter)

    
    def create_config_panel(self):
        """创建配置面板"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(5, 5, 10, 5)
        
        group_box = QGroupBox("视频生成配置")
        group_layout = QVBoxLayout(group_box)
        
        # 提示词
        prompt_label = QLabel("视频描述:")
        prompt_label.setStyleSheet("font-weight: bold; font-size: 13px;")
        group_layout.addWidget(prompt_label)
        
        self.prompt_edit = QTextEdit()
        self.prompt_edit.setPlaceholderText(
            "使用 character1 指代第一个参考视频中的主体\n"
            "使用 character2 指代第二个参考视频中的主体\n\n"
            "例如：character1在沙发上开心地看电影"
        )
        self.prompt_edit.setMinimumHeight(100)
        group_layout.addWidget(self.prompt_edit)
        
        # 反向提示词
        negative_label = QLabel("反向提示词（可选）:")
        negative_label.setStyleSheet("font-weight: bold; font-size: 12px; margin-top: 5px;")
        group_layout.addWidget(negative_label)
        
        self.negative_edit = QTextEdit()
        self.negative_edit.setPlaceholderText("描述不希望出现的内容...")
        self.negative_edit.setMaximumHeight(60)
        group_layout.addWidget(self.negative_edit)
        
        # 分辨率选择
        resolution_label = QLabel("分辨率:")
        resolution_label.setStyleSheet("font-weight: bold; font-size: 12px; margin-top: 5px;")
        group_layout.addWidget(resolution_label)
        
        self.resolution_combo = QComboBox()
        self.resolution_combo.setMinimumHeight(32)
        # 720P档位
        self.resolution_combo.addItem("720P - 16:9 (1280*720)", "1280*720")
        self.resolution_combo.addItem("720P - 9:16 (720*1280)", "720*1280")
        self.resolution_combo.addItem("720P - 1:1 (960*960)", "960*960")
        self.resolution_combo.addItem("720P - 4:3 (1088*832)", "1088*832")
        self.resolution_combo.addItem("720P - 3:4 (832*1088)", "832*1088")
        # 1080P档位
        self.resolution_combo.addItem("1080P - 16:9 (1920*1080)", "1920*1080")
        self.resolution_combo.addItem("1080P - 9:16 (1080*1920)", "1080*1920")
        self.resolution_combo.addItem("1080P - 1:1 (1440*1440)", "1440*1440")
        self.resolution_combo.addItem("1080P - 4:3 (1632*1248)", "1632*1248")
        self.resolution_combo.addItem("1080P - 3:4 (1248*1632)", "1248*1632")
        self.resolution_combo.setCurrentIndex(5)  # 默认1080P 16:9
        group_layout.addWidget(self.resolution_combo)
        
        # 视频时长
        duration_label = QLabel("视频时长:")
        duration_label.setStyleSheet("font-weight: bold; font-size: 12px; margin-top: 5px;")
        group_layout.addWidget(duration_label)
        
        self.duration_combo = QComboBox()
        self.duration_combo.setMinimumHeight(32)
        self.duration_combo.addItem("5秒", 5)
        self.duration_combo.addItem("10秒", 10)
        group_layout.addWidget(self.duration_combo)
        
        # 镜头类型
        shot_label = QLabel("镜头类型:")
        shot_label.setStyleSheet("font-weight: bold; font-size: 12px; margin-top: 5px;")
        group_layout.addWidget(shot_label)
        
        self.shot_type_combo = QComboBox()
        self.shot_type_combo.setMinimumHeight(32)
        self.shot_type_combo.addItem("单镜头", "single")
        self.shot_type_combo.addItem("多镜头", "multi")
        group_layout.addWidget(self.shot_type_combo)
        
        # 音频选项
        self.audio_checkbox = QCheckBox("包含音频")
        self.audio_checkbox.setChecked(True)
        self.audio_checkbox.setMinimumHeight(28)
        self.audio_checkbox.setStyleSheet("QCheckBox { font-size: 12px; padding: 5px; margin-top: 5px; }")
        group_layout.addWidget(self.audio_checkbox)
        
        # 生成按钮
        self.generate_btn = QPushButton("开始生成")
        self.generate_btn.clicked.connect(self.on_generate_clicked)
        self.generate_btn.setMinimumHeight(40)
        self.generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                padding: 10px 16px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 4px;
                margin-top: 10px;
            }
            QPushButton:hover { background-color: #0056b3; }
            QPushButton:disabled { background-color: #6c757d; }
        """)
        group_layout.addWidget(self.generate_btn)
        
        # 状态标签
        self.status_label = QLabel("💡 请先选择参考视频")
        self.status_label.setMinimumHeight(45)
        self.status_label.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 11px;
                padding: 8px;
                background: #f8f9fa;
                border-radius: 4px;
                margin-top: 5px;
            }
        """)
        self.status_label.setWordWrap(True)
        group_layout.addWidget(self.status_label)
        
        scroll_layout.addWidget(group_box)
        scroll_layout.addStretch()
        
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)
        return widget
    
    def create_preview_panel(self):
        """创建参考视频预览面板"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(5, 5, 15, 5)
        
        group_box = QGroupBox("参考视频（最多2个）")
        group_layout = QVBoxLayout(group_box)
        
        # 参考视频1
        video1_label = QLabel("参考视频1 (character1):")
        video1_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        group_layout.addWidget(video1_label)
        
        self.video1_preview = DragDropVideoLabel("🎬 未选择\n(支持拖拽视频)")
        self.video1_preview.setAlignment(Qt.AlignCenter)
        self.video1_preview.setMinimumHeight(180)  # 增加高度以显示缩略图
        self.video1_preview.setStyleSheet("""
            QLabel {
                border: 2px dashed #ddd;
                border-radius: 4px;
                background: #f9f9f9;
                color: #999;
            }
        """)
        self.video1_preview.video_dropped.connect(lambda p: self.on_video_dropped(p, 0))
        group_layout.addWidget(self.video1_preview)
        
        video1_btn_layout = QHBoxLayout()
        self.select_video1_btn = QPushButton("📁 浏览...")
        self.select_video1_btn.clicked.connect(lambda: self.select_video(0))
        self.select_video1_btn.setMinimumHeight(32)
        self.select_video1_btn.setToolTip("从文件系统或工程文件夹选择视频")
        self.select_video1_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                padding: 6px 12px;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover { background-color: #0056b3; }
        """)
        video1_btn_layout.addWidget(self.select_video1_btn)
        
        self.clear_video1_btn = QPushButton("清除")
        self.clear_video1_btn.clicked.connect(lambda: self.clear_video(0))
        self.clear_video1_btn.setMinimumHeight(32)
        self.clear_video1_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                padding: 6px 12px;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover { background-color: #c82333; }
        """)
        video1_btn_layout.addWidget(self.clear_video1_btn)
        group_layout.addLayout(video1_btn_layout)
        
        # 参考视频2
        video2_label = QLabel("参考视频2 (character2，可选):")
        video2_label.setStyleSheet("font-weight: bold; font-size: 12px; margin-top: 10px;")
        group_layout.addWidget(video2_label)
        
        self.video2_preview = DragDropVideoLabel("🎬 未选择\n(支持拖拽视频)")
        self.video2_preview.setAlignment(Qt.AlignCenter)
        self.video2_preview.setMinimumHeight(180)  # 增加高度以显示缩略图
        self.video2_preview.setStyleSheet("""
            QLabel {
                border: 2px dashed #ddd;
                border-radius: 4px;
                background: #f9f9f9;
                color: #999;
            }
        """)
        self.video2_preview.video_dropped.connect(lambda p: self.on_video_dropped(p, 1))
        group_layout.addWidget(self.video2_preview)
        
        video2_btn_layout = QHBoxLayout()
        self.select_video2_btn = QPushButton("📁 浏览...")
        self.select_video2_btn.clicked.connect(lambda: self.select_video(1))
        self.select_video2_btn.setMinimumHeight(32)
        self.select_video2_btn.setToolTip("从文件系统或工程文件夹选择视频")
        self.select_video2_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                padding: 6px 12px;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover { background-color: #0056b3; }
        """)
        video2_btn_layout.addWidget(self.select_video2_btn)
        
        self.clear_video2_btn = QPushButton("清除")
        self.clear_video2_btn.clicked.connect(lambda: self.clear_video(1))
        self.clear_video2_btn.setMinimumHeight(32)
        self.clear_video2_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                padding: 6px 12px;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover { background-color: #c82333; }
        """)
        video2_btn_layout.addWidget(self.clear_video2_btn)
        group_layout.addLayout(video2_btn_layout)
        
        scroll_layout.addWidget(group_box)
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)
        return widget

    
    def select_video(self, index):
        """选择视频文件"""
        # 检查是否有工程
        start_dir = ""
        if self.project_manager.has_project():
            # 如果有工程，默认从工程的inputs文件夹开始
            project = self.project_manager.get_current_project()
            start_dir = project.inputs_folder
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            f"选择参考视频{index + 1}",
            start_dir,
            "视频文件 (*.mp4 *.mov)"
        )
        
        if file_path:
            self.load_video(file_path, index)
    
    def on_video_dropped(self, file_path, index):
        """视频拖拽事件"""
        self.load_video(file_path, index)
    
    def load_video(self, file_path, index):
        """加载视频"""
        if not os.path.exists(file_path):
            return
        
        # 检查文件大小
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
        if file_size > 100:
            QMessageBox.warning(self, "提示", f"视频文件过大（{file_size:.1f}MB），最大支持100MB")
            return
        
        # 确保列表足够长
        while len(self.reference_videos) <= index:
            self.reference_videos.append(None)
        
        self.reference_videos[index] = file_path
        
        # 更新预览
        if index == 0:
            self.video1_preview.setVideoPath(file_path)
        else:
            self.video2_preview.setVideoPath(file_path)
        
        self.update_status()
    
    def clear_video(self, index):
        """清除视频"""
        if index < len(self.reference_videos):
            self.reference_videos[index] = None
        
        if index == 0:
            self.video1_preview.setVideoPath(None)
            self.video1_preview.setText("🎬 未选择\n(支持拖拽视频)")
            self.video1_preview.setStyleSheet("""
                QLabel {
                    border: 2px dashed #ddd;
                    border-radius: 4px;
                    background: #f9f9f9;
                    color: #999;
                }
            """)
        else:
            self.video2_preview.setVideoPath(None)
            self.video2_preview.setText("🎬 未选择\n(支持拖拽视频)")
            self.video2_preview.setStyleSheet("""
                QLabel {
                    border: 2px dashed #ddd;
                    border-radius: 4px;
                    background: #f9f9f9;
                    color: #999;
                }
            """)
        
        self.update_status()
    
    def update_status(self):
        """更新状态提示"""
        valid_videos = [v for v in self.reference_videos if v]
        
        if len(valid_videos) > 0:
            self.status_label.setText(f"✅ 已选择 {len(valid_videos)} 个参考视频，可以开始生成")
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #28a745;
                    font-size: 12px;
                    padding: 10px;
                    background: #d4edda;
                    border-radius: 4px;
                }
            """)
        else:
            self.status_label.setText("💡 请先选择参考视频")
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #666;
                    font-size: 11px;
                    padding: 8px;
                    background: #f8f9fa;
                    border-radius: 4px;
                }
            """)
    
    def on_generate_clicked(self):
        """生成按钮点击"""
        # 验证参考视频
        valid_videos = [v for v in self.reference_videos if v]
        if not valid_videos:
            QMessageBox.warning(self, "提示", "请先选择至少一个参考视频")
            return
        
        # 验证提示词
        prompt = self.prompt_edit.toPlainText().strip()
        if not prompt:
            QMessageBox.warning(self, "提示", "请输入视频描述")
            return
        
        # 检查提示词中是否包含character关键字
        if 'character1' not in prompt.lower():
            reply = QMessageBox.question(
                self,
                "提示",
                "提示词中未包含 'character1' 关键字，这可能导致无法正确引用参考视频中的主体。\n\n是否继续？",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        
        # 检查是否有工程
        if not self.project_manager.has_project():
            QMessageBox.warning(self, "提示", "请先创建或打开工程")
            return
        
        # 获取配置
        negative_prompt = self.negative_edit.toPlainText().strip()
        size = self.resolution_combo.currentData()
        duration = self.duration_combo.currentData()
        shot_type = self.shot_type_combo.currentData()
        audio = self.audio_checkbox.isChecked()
        
        # 获取输出文件夹
        project = self.project_manager.get_current_project()
        output_folder = project.outputs_folder
        
        # 禁用按钮
        self.generate_btn.setEnabled(False)
        self.generate_btn.setText("生成中...")
        
        # 创建任务记录
        self.current_task = self.task_manager.create_task(
            prompt=prompt,
            model='wan2.6-r2v',
            resolution=size,
            negative_prompt=negative_prompt,
            prompt_extend=False,
            input_file=valid_videos[0] if valid_videos else ""
        )
        
        # 创建工作线程
        self.worker = ReferenceVideoWorker(
            self.api_client,
            valid_videos,
            prompt,
            negative_prompt,
            size,
            duration,
            shot_type,
            audio,
            output_folder
        )
        self.worker.finished.connect(self.on_generate_finished)
        self.worker.error.connect(self.on_generate_error)
        self.worker.progress.connect(self.on_generate_progress)
        self.worker.task_submitted.connect(self.on_task_submitted)
        self.worker.start()
    
    def on_task_submitted(self, async_task_id):
        """任务提交成功，更新任务管理器"""
        if hasattr(self, 'current_task') and self.current_task:
            # 更新任务的异步任务ID
            self.task_manager.update_task(
                self.current_task.id,
                async_task_id=async_task_id,
                status='RUNNING'
            )
            # 刷新浮动任务列表并开始监控
            main_window = self.window()
            if hasattr(main_window, 'floating_task_list'):
                main_window.floating_task_list.refresh_tasks()
                main_window.floating_task_list.start_monitoring_task(self.current_task.id)
                # 自动打开浮动任务列表
                if not main_window.floating_task_list.is_drawer_visible():
                    main_window.floating_task_list.show_drawer(main_window)
    
    def on_generate_finished(self, video_path, video_info):
        """生成完成"""
        self.generate_btn.setEnabled(True)
        self.generate_btn.setText("开始生成")
        self.status_label.setText("✅ 视频生成成功！")
        
        # 更新任务状态
        if hasattr(self, 'current_task') and self.current_task:
            self.task_manager.update_task(
                self.current_task.id,
                status='SUCCEEDED',
                output_path=video_path
            )
        
        # 加载视频到视频查看器
        self.video_viewer.load_video(video_path)
        
        # 刷新资源管理器
        main_window = self.window()
        if hasattr(main_window, 'project_explorer'):
            main_window.project_explorer.refresh()
        
        # 刷新浮动任务列表
        if hasattr(main_window, 'floating_task_list'):
            main_window.floating_task_list.refresh_tasks()
        
        QMessageBox.information(
            self,
            "成功",
            f"视频生成完成！\n已保存到: {os.path.basename(video_path)}"
        )
    
    def on_generate_error(self, error_msg):
        """生成错误"""
        self.generate_btn.setEnabled(True)
        self.generate_btn.setText("开始生成")
        self.status_label.setText(f"❌ {error_msg}")
        
        # 更新任务状态为失败
        if hasattr(self, 'current_task') and self.current_task:
            self.task_manager.update_task(
                self.current_task.id,
                status='FAILED',
                error_message=error_msg
            )
            # 刷新浮动任务列表
            main_window = self.window()
            if hasattr(main_window, 'floating_task_list'):
                main_window.floating_task_list.refresh_tasks()
        
        self.status_label.setStyleSheet("""
            QLabel {
                color: #dc3545;
                font-size: 12px;
                padding: 10px;
                background: #f8d7da;
                border-radius: 4px;
            }
        """)
        
        QMessageBox.critical(self, "错误", error_msg)
    
    def on_generate_progress(self, status_msg):
        """生成进度更新"""
        self.status_label.setText(status_msg)
