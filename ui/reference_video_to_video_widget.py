#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
参考视频生成视频组件
支持上传参考视频，通过文本提示词生成新视频
布局：左上-参考视频预览，左下-模型配置，右上-提示词，右下-生成视频预览
"""

import os
import time
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QTextEdit, QFileDialog, QMessageBox,
    QSplitter, QScrollArea, QCheckBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QDragEnterEvent, QDropEvent

try:
    from qfluentwidgets import (
        PushButton, PrimaryPushButton, FluentIcon,
        ComboBox, SwitchButton, BodyLabel,
        StrongBodyLabel, CaptionLabel, TransparentPushButton
    )
    FLUENT_AVAILABLE = True
except ImportError:
    FLUENT_AVAILABLE = False

from .video_viewer import VideoViewerWidget


class DragDropVideoLabel(QLabel):
    """支持拖拽的视频标签组件，支持显示视频缩略图"""
    
    video_dropped = pyqtSignal(str)  # 视频路径
    
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setAcceptDrops(True)
        self.default_text = text
        self.video_path = None
        self.thumbnail_pixmap = None
    
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
                            border: 2px dashed #0078d4;
                            border-radius: 8px;
                            background: rgba(0, 120, 212, 0.1);
                            color: #0078d4;
                        }
                    """)
                    return
        event.ignore()
    
    def dragLeaveEvent(self, event):
        """拖拽离开事件"""
        if not self.video_path:
            self.setStyleSheet("""
                QLabel {
                    border: 2px dashed #d0d0d0;
                    border-radius: 8px;
                    background: #fafafa;
                    color: #888;
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
                self.setAlignment(Qt.AlignCenter)
            else:
                # 如果无法生成缩略图，显示文本信息
                self.setText(f"{file_name}\n({file_size:.1f} MB)")
            
            self.setStyleSheet("""
                QLabel {
                    border: 2px solid #0078d4;
                    border-radius: 8px;
                    background: white;
                    color: #333;
                    padding: 5px;
                }
            """)
    
    def generate_video_thumbnail(self, video_path):
        """生成视频缩略图（使用OpenCV提取第一帧）"""
        try:
            import cv2
            from PyQt5.QtGui import QImage, QPixmap
            
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return None
            
            ret, frame = cap.read()
            cap.release()
            
            if not ret or frame is None:
                return None
            
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width, channel = frame_rgb.shape
            bytes_per_line = 3 * width
            q_image = QImage(frame_rgb.data, width, height, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_image)
            
            if not pixmap.isNull():
                return pixmap
            return None
            
        except ImportError:
            return None
        except Exception:
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
    """参考视频生成视频工作线程"""
    
    finished = pyqtSignal(str, dict)
    error = pyqtSignal(str)
    progress = pyqtSignal(str)
    task_submitted = pyqtSignal(str)
    
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
            self.progress.emit("正在上传参考视频...")
            
            reference_video_urls = []
            for video_path in self.reference_videos:
                self.progress.emit(f"正在上传: {os.path.basename(video_path)}")
                video_url = self.api_client.upload_video_and_get_url(video_path, "wan2.6-r2v")
                reference_video_urls.append(video_url)
            
            self.progress.emit("正在提交任务...")
            
            result = self.api_client.submit_reference_video_to_video(
                reference_video_urls=reference_video_urls,
                prompt=self.prompt,
                negative_prompt=self.negative_prompt,
                size=self.size,
                duration=self.duration,
                shot_type=self.shot_type,
                audio=self.audio
            )
            
            task_id = result['output']['task_id']
            self.progress.emit(f"任务已提交 (ID: {task_id})")
            self.task_submitted.emit(task_id)
            
            max_retries = 180
            retry_count = 0
            
            while retry_count < max_retries:
                time.sleep(5)
                retry_count += 1
                
                self.progress.emit(f"正在生成视频... ({retry_count}/{max_retries})")
                
                task_result = self.api_client.query_task(task_id)
                task_status = task_result['output'].get('task_status', '')
                
                if task_status == 'SUCCEEDED':
                    video_url = task_result['output'].get('video_url', '')
                    orig_prompt = task_result['output'].get('orig_prompt', self.prompt)
                    
                    if not video_url:
                        self.error.emit("视频URL为空")
                        return
                    
                    self.progress.emit("正在下载视频...")
                    video_path = self.api_client.download_video(video_url, self.output_folder)
                    
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
    """参考视频生成视频组件
    
    布局：
    - 左上：参考视频预览
    - 左下：模型配置
    - 右上：提示词
    - 右下：生成视频预览
    """
    
    def __init__(self, api_client, project_manager, task_manager, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.project_manager = project_manager
        self.task_manager = task_manager
        self.worker = None
        self.reference_videos = []
        self.current_task = None
        self.setup_ui()
    
    def setup_ui(self):
        """设置用户界面 - 四象限布局"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        main_splitter = QSplitter(Qt.Horizontal)
        
        # === 左侧面板 ===
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        left_splitter = QSplitter(Qt.Vertical)
        
        # 左上：参考视频预览
        preview_widget = self.create_preview_panel()
        left_splitter.addWidget(preview_widget)
        
        # 左下：模型配置
        config_widget = self.create_config_panel()
        left_splitter.addWidget(config_widget)
        
        left_splitter.setStretchFactor(0, 2)
        left_splitter.setStretchFactor(1, 1)
        
        left_layout.addWidget(left_splitter)
        main_splitter.addWidget(left_widget)
        
        # === 右侧面板 ===
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        right_splitter = QSplitter(Qt.Vertical)
        
        # 右上：提示词
        prompt_widget = self.create_prompt_panel()
        right_splitter.addWidget(prompt_widget)
        
        # 右下：生成视频预览
        self.video_viewer = VideoViewerWidget()
        right_splitter.addWidget(self.video_viewer)
        
        right_splitter.setStretchFactor(0, 1)
        right_splitter.setStretchFactor(1, 2)
        
        right_layout.addWidget(right_splitter)
        main_splitter.addWidget(right_widget)
        
        main_splitter.setStretchFactor(0, 1)
        main_splitter.setStretchFactor(1, 1)
        
        layout.addWidget(main_splitter)
    
    def create_preview_panel(self):
        """创建参考视频预览面板 - 左上区域"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(12)
        
        # 参考视频1
        video1_container = QWidget()
        video1_layout = QVBoxLayout(video1_container)
        video1_layout.setContentsMargins(0, 0, 0, 0)
        video1_layout.setSpacing(8)
        
        # 标题和按钮行
        video1_header = QHBoxLayout()
        video1_header.setSpacing(8)
        
        if FLUENT_AVAILABLE:
            video1_label = StrongBodyLabel("参考视频1 (character1)")
            video1_header.addWidget(video1_label)
            video1_header.addStretch()
            
            self.select_video1_btn = TransparentPushButton(FluentIcon.FOLDER, "选择")
            self.select_video1_btn.setFixedHeight(28)
            self.select_video1_btn.clicked.connect(lambda: self.select_video(0))
            video1_header.addWidget(self.select_video1_btn)
            
            self.clear_video1_btn = TransparentPushButton(FluentIcon.DELETE, "清除")
            self.clear_video1_btn.setFixedHeight(28)
            self.clear_video1_btn.clicked.connect(lambda: self.clear_video(0))
            video1_header.addWidget(self.clear_video1_btn)
        else:
            video1_label = QLabel("参考视频1 (character1)")
            video1_label.setStyleSheet("font-weight: bold; font-size: 13px;")
            video1_header.addWidget(video1_label)
            video1_header.addStretch()
            
            self.select_video1_btn = QPushButton("选择")
            self.select_video1_btn.setFixedHeight(28)
            self.select_video1_btn.clicked.connect(lambda: self.select_video(0))
            video1_header.addWidget(self.select_video1_btn)
            
            self.clear_video1_btn = QPushButton("清除")
            self.clear_video1_btn.setFixedHeight(28)
            self.clear_video1_btn.clicked.connect(lambda: self.clear_video(0))
            video1_header.addWidget(self.clear_video1_btn)
        
        video1_layout.addLayout(video1_header)
        
        self.video1_preview = DragDropVideoLabel("拖拽视频到此处\n或点击选择按钮")
        self.video1_preview.setAlignment(Qt.AlignCenter)
        self.video1_preview.setMinimumHeight(120)
        self.video1_preview.setStyleSheet("""
            QLabel {
                border: 2px dashed #d0d0d0;
                border-radius: 8px;
                background: #fafafa;
                color: #888;
            }
        """)
        self.video1_preview.video_dropped.connect(lambda p: self.on_video_dropped(p, 0))
        video1_layout.addWidget(self.video1_preview, 1)
        
        layout.addWidget(video1_container, 1)
        
        # 参考视频2
        video2_container = QWidget()
        video2_layout = QVBoxLayout(video2_container)
        video2_layout.setContentsMargins(0, 0, 0, 0)
        video2_layout.setSpacing(8)
        
        video2_header = QHBoxLayout()
        video2_header.setSpacing(8)
        
        if FLUENT_AVAILABLE:
            video2_label = StrongBodyLabel("参考视频2 (character2，可选)")
            video2_header.addWidget(video2_label)
            video2_header.addStretch()
            
            self.select_video2_btn = TransparentPushButton(FluentIcon.FOLDER, "选择")
            self.select_video2_btn.setFixedHeight(28)
            self.select_video2_btn.clicked.connect(lambda: self.select_video(1))
            video2_header.addWidget(self.select_video2_btn)
            
            self.clear_video2_btn = TransparentPushButton(FluentIcon.DELETE, "清除")
            self.clear_video2_btn.setFixedHeight(28)
            self.clear_video2_btn.clicked.connect(lambda: self.clear_video(1))
            video2_header.addWidget(self.clear_video2_btn)
        else:
            video2_label = QLabel("参考视频2 (character2，可选)")
            video2_label.setStyleSheet("font-weight: bold; font-size: 13px;")
            video2_header.addWidget(video2_label)
            video2_header.addStretch()
            
            self.select_video2_btn = QPushButton("选择")
            self.select_video2_btn.setFixedHeight(28)
            self.select_video2_btn.clicked.connect(lambda: self.select_video(1))
            video2_header.addWidget(self.select_video2_btn)
            
            self.clear_video2_btn = QPushButton("清除")
            self.clear_video2_btn.setFixedHeight(28)
            self.clear_video2_btn.clicked.connect(lambda: self.clear_video(1))
            video2_header.addWidget(self.clear_video2_btn)
        
        video2_layout.addLayout(video2_header)
        
        self.video2_preview = DragDropVideoLabel("拖拽视频到此处\n或点击选择按钮")
        self.video2_preview.setAlignment(Qt.AlignCenter)
        self.video2_preview.setMinimumHeight(120)
        self.video2_preview.setStyleSheet("""
            QLabel {
                border: 2px dashed #d0d0d0;
                border-radius: 8px;
                background: #fafafa;
                color: #888;
            }
        """)
        self.video2_preview.video_dropped.connect(lambda p: self.on_video_dropped(p, 1))
        video2_layout.addWidget(self.video2_preview, 1)
        
        layout.addWidget(video2_container, 1)
        
        return widget

    def create_config_panel(self):
        """创建配置面板 - 左下区域（分辨率、时长、镜头类型等）"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(10)
        
        # 数据映射
        self.resolution_data = [
            "1280*720", "720*1280", "960*960", "1088*832", "832*1088",
            "1920*1080", "1080*1920", "1440*1440", "1632*1248", "1248*1632"
        ]
        self.duration_data = [5, 10]
        self.shot_type_data = ["single", "multi"]
        
        # 分辨率选择
        resolution_row = QHBoxLayout()
        resolution_row.setSpacing(12)
        
        if FLUENT_AVAILABLE:
            resolution_label = BodyLabel("分辨率")
            resolution_label.setFixedWidth(60)
            resolution_row.addWidget(resolution_label)
            
            self.resolution_combo = ComboBox()
            self.resolution_combo.addItems([
                "720P 16:9 (1280*720)", "720P 9:16 (720*1280)", "720P 1:1 (960*960)",
                "720P 4:3 (1088*832)", "720P 3:4 (832*1088)",
                "1080P 16:9 (1920*1080)", "1080P 9:16 (1080*1920)", "1080P 1:1 (1440*1440)",
                "1080P 4:3 (1632*1248)", "1080P 3:4 (1248*1632)"
            ])
        else:
            resolution_label = QLabel("分辨率:")
            resolution_label.setFixedWidth(60)
            resolution_row.addWidget(resolution_label)
            
            self.resolution_combo = QComboBox()
            self.resolution_combo.addItem("720P 16:9 (1280*720)", "1280*720")
            self.resolution_combo.addItem("720P 9:16 (720*1280)", "720*1280")
            self.resolution_combo.addItem("720P 1:1 (960*960)", "960*960")
            self.resolution_combo.addItem("720P 4:3 (1088*832)", "1088*832")
            self.resolution_combo.addItem("720P 3:4 (832*1088)", "832*1088")
            self.resolution_combo.addItem("1080P 16:9 (1920*1080)", "1920*1080")
            self.resolution_combo.addItem("1080P 9:16 (1080*1920)", "1080*1920")
            self.resolution_combo.addItem("1080P 1:1 (1440*1440)", "1440*1440")
            self.resolution_combo.addItem("1080P 4:3 (1632*1248)", "1632*1248")
            self.resolution_combo.addItem("1080P 3:4 (1248*1632)", "1248*1632")
        
        self.resolution_combo.setMinimumHeight(32)
        self.resolution_combo.setCurrentIndex(5)  # 默认1080P 16:9
        resolution_row.addWidget(self.resolution_combo, 1)
        layout.addLayout(resolution_row)
        
        # 视频时长
        duration_row = QHBoxLayout()
        duration_row.setSpacing(12)
        
        if FLUENT_AVAILABLE:
            duration_label = BodyLabel("时长")
            duration_label.setFixedWidth(60)
            duration_row.addWidget(duration_label)
            
            self.duration_combo = ComboBox()
            self.duration_combo.addItems(["5秒", "10秒"])
        else:
            duration_label = QLabel("时长:")
            duration_label.setFixedWidth(60)
            duration_row.addWidget(duration_label)
            
            self.duration_combo = QComboBox()
            self.duration_combo.addItem("5秒", 5)
            self.duration_combo.addItem("10秒", 10)
        
        self.duration_combo.setMinimumHeight(32)
        duration_row.addWidget(self.duration_combo, 1)
        layout.addLayout(duration_row)
        
        # 镜头类型
        shot_row = QHBoxLayout()
        shot_row.setSpacing(12)
        
        if FLUENT_AVAILABLE:
            shot_label = BodyLabel("镜头")
            shot_label.setFixedWidth(60)
            shot_row.addWidget(shot_label)
            
            self.shot_type_combo = ComboBox()
            self.shot_type_combo.addItems(["单镜头", "多镜头"])
        else:
            shot_label = QLabel("镜头:")
            shot_label.setFixedWidth(60)
            shot_row.addWidget(shot_label)
            
            self.shot_type_combo = QComboBox()
            self.shot_type_combo.addItem("单镜头", "single")
            self.shot_type_combo.addItem("多镜头", "multi")
        
        self.shot_type_combo.setMinimumHeight(32)
        shot_row.addWidget(self.shot_type_combo, 1)
        layout.addLayout(shot_row)
        
        # 音频选项
        audio_row = QHBoxLayout()
        audio_row.setSpacing(12)
        
        if FLUENT_AVAILABLE:
            audio_label = BodyLabel("音频")
            audio_label.setFixedWidth(60)
            audio_row.addWidget(audio_label)
            audio_row.addStretch()
            
            self.audio_switch = SwitchButton()
            self.audio_switch.setChecked(True)
            audio_row.addWidget(self.audio_switch)
        else:
            self.audio_switch = QCheckBox("包含音频")
            self.audio_switch.setChecked(True)
            audio_row.addWidget(self.audio_switch)
        
        layout.addLayout(audio_row)
        
        # 状态标签
        if FLUENT_AVAILABLE:
            self.status_label = CaptionLabel("请先选择参考视频")
            self.status_label.setStyleSheet("color: #888;")
        else:
            self.status_label = QLabel("请先选择参考视频")
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #888;
                    font-size: 12px;
                    padding: 8px;
                    background: #f5f5f5;
                    border-radius: 4px;
                }
            """)
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
        return widget
    
    def create_prompt_panel(self):
        """创建提示词面板 - 右上区域"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # 标题行
        header_layout = QHBoxLayout()
        
        if FLUENT_AVAILABLE:
            prompt_label = StrongBodyLabel("视频描述")
            header_layout.addWidget(prompt_label)
            header_layout.addStretch()
            
            self.generate_btn = PrimaryPushButton(FluentIcon.PLAY, "生成视频")
        else:
            prompt_label = QLabel("视频描述")
            prompt_label.setStyleSheet("font-weight: bold; font-size: 13px;")
            header_layout.addWidget(prompt_label)
            header_layout.addStretch()
            
            self.generate_btn = QPushButton("生成视频")
            self.generate_btn.setStyleSheet("""
                QPushButton {
                    background-color: #0078d4;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #106ebe;
                }
                QPushButton:disabled {
                    background-color: #ccc;
                }
            """)
        
        self.generate_btn.setMinimumHeight(36)
        self.generate_btn.clicked.connect(self.on_generate_clicked)
        header_layout.addWidget(self.generate_btn)
        
        layout.addLayout(header_layout)
        
        # 提示词输入框
        self.prompt_edit = QTextEdit()
        self.prompt_edit.setPlaceholderText(
            "使用 character1 指代第一个参考视频中的主体\n"
            "使用 character2 指代第二个参考视频中的主体\n\n"
            "例如：character1在沙发上开心地看电影"
        )
        self.prompt_edit.setStyleSheet("""
            QTextEdit {
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 8px;
                background: white;
            }
            QTextEdit:focus {
                border: 1px solid #0078d4;
            }
        """)
        layout.addWidget(self.prompt_edit, 2)
        
        # 反向提示词
        if FLUENT_AVAILABLE:
            negative_label = BodyLabel("反向提示词（可选）")
        else:
            negative_label = QLabel("反向提示词（可选）")
            negative_label.setStyleSheet("font-size: 12px; color: #666;")
        layout.addWidget(negative_label)
        
        self.negative_edit = QTextEdit()
        self.negative_edit.setPlaceholderText("描述不希望出现的内容...")
        self.negative_edit.setMaximumHeight(60)
        self.negative_edit.setStyleSheet("""
            QTextEdit {
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 8px;
                background: white;
            }
            QTextEdit:focus {
                border: 1px solid #0078d4;
            }
        """)
        layout.addWidget(self.negative_edit, 1)
        
        return widget
    
    def select_video(self, index):
        """选择视频文件"""
        start_dir = ""
        if self.project_manager.has_project():
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
        
        file_size = os.path.getsize(file_path) / (1024 * 1024)
        if file_size > 100:
            QMessageBox.warning(self, "提示", f"视频文件过大（{file_size:.1f}MB），最大支持100MB")
            return
        
        while len(self.reference_videos) <= index:
            self.reference_videos.append(None)
        
        self.reference_videos[index] = file_path
        
        if index == 0:
            self.video1_preview.setVideoPath(file_path)
        else:
            self.video2_preview.setVideoPath(file_path)
        
        self.update_status()
    
    def clear_video(self, index):
        """清除视频"""
        if index < len(self.reference_videos):
            self.reference_videos[index] = None
        
        preview = self.video1_preview if index == 0 else self.video2_preview
        preview.setVideoPath(None)
        preview.thumbnail_pixmap = None
        preview.setText("拖拽视频到此处\n或点击选择按钮")
        preview.setStyleSheet("""
            QLabel {
                border: 2px dashed #d0d0d0;
                border-radius: 8px;
                background: #fafafa;
                color: #888;
            }
        """)
        
        self.update_status()
    
    def update_status(self):
        """更新状态提示"""
        valid_videos = [v for v in self.reference_videos if v]
        
        if len(valid_videos) > 0:
            self.status_label.setText(f"已选择 {len(valid_videos)} 个参考视频，可以开始生成")
            if FLUENT_AVAILABLE:
                self.status_label.setStyleSheet("color: #0078d4;")
            else:
                self.status_label.setStyleSheet("""
                    QLabel {
                        color: #0078d4;
                        font-size: 12px;
                        padding: 8px;
                        background: rgba(0, 120, 212, 0.1);
                        border-radius: 4px;
                    }
                """)
        else:
            self.status_label.setText("请先选择参考视频")
            if FLUENT_AVAILABLE:
                self.status_label.setStyleSheet("color: #888;")
            else:
                self.status_label.setStyleSheet("""
                    QLabel {
                        color: #888;
                        font-size: 12px;
                        padding: 8px;
                        background: #f5f5f5;
                        border-radius: 4px;
                    }
                """)

    def on_generate_clicked(self):
        """生成按钮点击"""
        valid_videos = [v for v in self.reference_videos if v]
        if not valid_videos:
            QMessageBox.warning(self, "提示", "请先选择至少一个参考视频")
            return
        
        prompt = self.prompt_edit.toPlainText().strip()
        if not prompt:
            QMessageBox.warning(self, "提示", "请输入视频描述")
            return
        
        if 'character1' not in prompt.lower():
            reply = QMessageBox.question(
                self,
                "提示",
                "提示词中未包含 'character1' 关键字，这可能导致无法正确引用参考视频中的主体。\n\n是否继续？",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        
        if not self.project_manager.has_project():
            QMessageBox.warning(self, "提示", "请先创建或打开工程")
            return
        
        negative_prompt = self.negative_edit.toPlainText().strip()
        
        # 获取配置数据
        if FLUENT_AVAILABLE:
            size = self.resolution_data[self.resolution_combo.currentIndex()]
            duration = self.duration_data[self.duration_combo.currentIndex()]
            shot_type = self.shot_type_data[self.shot_type_combo.currentIndex()]
            audio = self.audio_switch.isChecked()
        else:
            size = self.resolution_combo.currentData()
            duration = self.duration_combo.currentData()
            shot_type = self.shot_type_combo.currentData()
            audio = self.audio_switch.isChecked()
        
        project = self.project_manager.get_current_project()
        output_folder = project.outputs_folder
        
        self.generate_btn.setEnabled(False)
        self.generate_btn.setText("生成中...")
        
        self.current_task = self.task_manager.create_task(
            prompt=prompt,
            model='wan2.6-r2v',
            resolution=size,
            negative_prompt=negative_prompt,
            prompt_extend=False,
            input_file=valid_videos[0] if valid_videos else ""
        )
        
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
            self.task_manager.update_task(
                self.current_task.id,
                async_task_id=async_task_id,
                status='RUNNING'
            )
            main_window = self.window()
            if hasattr(main_window, 'floating_task_list'):
                main_window.floating_task_list.refresh_tasks()
                main_window.floating_task_list.start_monitoring_task(self.current_task.id)
                if not main_window.floating_task_list.is_drawer_visible():
                    main_window.floating_task_list.show_drawer(main_window)
    
    def on_generate_finished(self, video_path, video_info):
        """生成完成"""
        self.generate_btn.setEnabled(True)
        if FLUENT_AVAILABLE:
            self.generate_btn.setText("生成视频")
        else:
            self.generate_btn.setText("生成视频")
        self.status_label.setText("视频生成成功！")
        
        if hasattr(self, 'current_task') and self.current_task:
            self.task_manager.update_task(
                self.current_task.id,
                status='SUCCEEDED',
                output_path=video_path
            )
        
        self.video_viewer.load_video(video_path)
        
        main_window = self.window()
        if hasattr(main_window, 'project_explorer'):
            main_window.project_explorer.refresh()
        
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
        if FLUENT_AVAILABLE:
            self.generate_btn.setText("生成视频")
        else:
            self.generate_btn.setText("生成视频")
        
        self.status_label.setText(f"生成失败: {error_msg}")
        if FLUENT_AVAILABLE:
            self.status_label.setStyleSheet("color: #d13438;")
        else:
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #d13438;
                    font-size: 12px;
                    padding: 8px;
                    background: rgba(209, 52, 56, 0.1);
                    border-radius: 4px;
                }
            """)
        
        if hasattr(self, 'current_task') and self.current_task:
            self.task_manager.update_task(
                self.current_task.id,
                status='FAILED',
                error_message=error_msg
            )
            main_window = self.window()
            if hasattr(main_window, 'floating_task_list'):
                main_window.floating_task_list.refresh_tasks()
        
        QMessageBox.critical(self, "错误", error_msg)
    
    def on_generate_progress(self, status_msg):
        """生成进度更新"""
        self.status_label.setText(status_msg)

    def showEvent(self, event):
        """显示事件"""
        super().showEvent(event)
        if not hasattr(self, '_first_show_done'):
            self._first_show_done = True
            from PyQt5.QtCore import QTimer
            QTimer.singleShot(50, self.updateGeometry)
