#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
首尾帧生成视频组件
支持上传首帧和尾帧图片，生成视频
布局：左上-首尾帧预览，左下-模型配置，右上-提示词，右下-生成视频预览
"""

import os
import base64
import time
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QTextEdit, QGroupBox, QFileDialog, QMessageBox,
    QSplitter, QScrollArea, QGridLayout, QCheckBox, QFrame
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QDragEnterEvent, QDropEvent

try:
    from qfluentwidgets import (
        PushButton, PrimaryPushButton, FluentIcon,
        ComboBox, SwitchButton, BodyLabel, CardWidget,
        StrongBodyLabel, CaptionLabel, TransparentPushButton
    )
    FLUENT_AVAILABLE = True
except ImportError:
    FLUENT_AVAILABLE = False

from .video_viewer import VideoViewerWidget


class DragDropLabel(QLabel):
    """支持拖拽的标签组件"""
    
    image_dropped = pyqtSignal(str)  # 图片路径
    
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setAcceptDrops(True)
        self.default_text = text
        self.image_path = None  # 存储图片路径
        self.original_pixmap = None  # 存储原始图片
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """拖拽进入事件"""
        if event.mimeData().hasUrls():
            # 检查是否为图片文件
            urls = event.mimeData().urls()
            if urls:
                file_path = urls[0].toLocalFile()
                if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                    event.acceptProposedAction()
                    self.setStyleSheet("""
                        QLabel {
                            border: 2px dashed #0078d4;
                            border-radius: 8px;
                            background: rgba(0, 120, 212, 0.1);
                            color: #0078d4;
                        }
                    """)
    
    def dragLeaveEvent(self, event):
        """拖拽离开事件"""
        if not self.pixmap():
            self.setStyleSheet("""
                QLabel {
                    border: 2px dashed #d0d0d0;
                    border-radius: 8px;
                    background: #fafafa;
                    color: #888;
                }
            """)
    
    def dropEvent(self, event: QDropEvent):
        """拖放事件"""
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                self.image_dropped.emit(file_path)
                event.acceptProposedAction()
    
    def setImagePath(self, path):
        """设置图片路径并加载"""
        self.image_path = path
        if path and os.path.exists(path):
            self.original_pixmap = QPixmap(path)
            self.updateScaledPixmap()
    
    def updateScaledPixmap(self):
        """根据当前大小更新缩放后的图片"""
        if self.original_pixmap and not self.original_pixmap.isNull():
            # 获取可用空间
            available_width = self.width() - 20
            available_height = self.height() - 20
            
            # 确保最小尺寸
            available_width = max(available_width, 280)
            available_height = max(available_height, 160)
            
            # 缩放图片，保持原始宽高比
            scaled = self.original_pixmap.scaled(
                available_width, 
                available_height, 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
            self.setPixmap(scaled)
    
    def resizeEvent(self, event):
        """窗口大小改变时重新缩放图片"""
        super().resizeEvent(event)
        if self.original_pixmap:
            self.updateScaledPixmap()


class KeyframeVideoWorker(QThread):
    """首尾帧生成视频工作线程"""
    
    finished = pyqtSignal(str, dict)  # 视频路径, 视频信息
    error = pyqtSignal(str)
    progress = pyqtSignal(str)
    
    def __init__(self, api_client, first_frame_path, last_frame_path, prompt, 
                 model, resolution, prompt_extend, output_folder):
        super().__init__()
        self.api_client = api_client
        self.first_frame_path = first_frame_path
        self.last_frame_path = last_frame_path
        self.prompt = prompt
        self.model = model
        self.resolution = resolution
        self.prompt_extend = prompt_extend
        self.output_folder = output_folder
    
    def run(self):
        """执行生成任务"""
        try:
            self.progress.emit("正在提交任务...")
            
            # 读取并编码图片
            with open(self.first_frame_path, 'rb') as f:
                first_frame_data = base64.b64encode(f.read()).decode('utf-8')
            
            with open(self.last_frame_path, 'rb') as f:
                last_frame_data = base64.b64encode(f.read()).decode('utf-8')
            
            # 获取图片MIME类型
            ext = os.path.splitext(self.first_frame_path)[1].lower()
            mime_types = {'.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg'}
            mime_type = mime_types.get(ext, 'image/jpeg')
            
            first_frame_url = f"data:{mime_type};base64,{first_frame_data}"
            last_frame_url = f"data:{mime_type};base64,{last_frame_data}"
            
            # 提交任务
            result = self.api_client.submit_keyframe_to_video(
                first_frame_url=first_frame_url,
                last_frame_url=last_frame_url,
                prompt=self.prompt,
                model=self.model,
                resolution=self.resolution,
                prompt_extend=self.prompt_extend
            )
            
            # 获取任务ID
            task_id = result['output']['task_id']
            self.progress.emit(f"任务已提交 (ID: {task_id})")
            
            # 轮询任务状态
            max_retries = 180  # 最多轮询180次（约15分钟）
            retry_count = 0
            
            while retry_count < max_retries:
                time.sleep(5)  # 每5秒查询一次
                retry_count += 1
                
                self.progress.emit(f"正在生成视频... ({retry_count}/{max_retries})")
                
                # 查询任务状态
                task_result = self.api_client.query_task(task_id)
                task_status = task_result['output'].get('task_status', '')
                
                if task_status == 'SUCCEEDED':
                    # 任务成功
                    video_url = task_result['output'].get('video_url', '')
                    orig_prompt = task_result['output'].get('orig_prompt', self.prompt)
                    actual_prompt = task_result['output'].get('actual_prompt', self.prompt)
                    
                    if not video_url:
                        self.error.emit("视频URL为空")
                        return
                    
                    self.progress.emit("正在下载视频...")
                    
                    # 下载视频
                    video_path = self.api_client.download_video(video_url, self.output_folder)
                    
                    # 构建视频信息
                    video_info = {
                        'model': self.model,
                        'resolution': self.resolution,
                        'prompt_extend': self.prompt_extend,
                        'orig_prompt': orig_prompt,
                        'actual_prompt': actual_prompt,
                        'first_frame': os.path.basename(self.first_frame_path),
                        'last_frame': os.path.basename(self.last_frame_path),
                        'first_frame_path': self.first_frame_path,
                        'last_frame_path': self.last_frame_path,
                        'video_url': video_url,
                        'task_id': task_id
                    }
                    
                    # 保存元数据到JSON文件
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
                    # 任务失败
                    error_code = task_result['output'].get('code', 'Unknown')
                    error_msg = task_result['output'].get('message', '未知错误')
                    self.error.emit(f"生成失败 [{error_code}]: {error_msg}")
                    return
                    
                elif task_status == 'UNKNOWN':
                    # 任务过期
                    self.error.emit("任务查询过期，请重试")
                    return
            
            # 超时
            self.error.emit(f"生成超时（已等待{max_retries * 5}秒）")
            
        except Exception as e:
            self.error.emit(f"生成失败: {str(e)}")


class KeyframeToVideoWidget(QWidget):
    """首尾帧生成视频组件
    
    布局：
    - 左上：首尾帧预览
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
        self.first_frame_path = None
        self.last_frame_path = None
        self.setup_ui()
    
    def setup_ui(self):
        """设置用户界面 - 四象限布局"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 主水平分割器 - 左右布局
        main_splitter = QSplitter(Qt.Horizontal)
        
        # === 左侧面板 ===
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        left_splitter = QSplitter(Qt.Vertical)
        
        # 左上：首尾帧预览
        preview_widget = self.create_preview_panel()
        left_splitter.addWidget(preview_widget)
        
        # 左下：模型配置
        config_widget = self.create_config_panel()
        left_splitter.addWidget(config_widget)
        
        # 左侧比例：预览占2份，配置占1份
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
        
        # 右侧比例：提示词占1份，视频预览占2份
        right_splitter.setStretchFactor(0, 1)
        right_splitter.setStretchFactor(1, 2)
        
        right_layout.addWidget(right_splitter)
        main_splitter.addWidget(right_widget)
        
        # 左右比例：各占1份
        main_splitter.setStretchFactor(0, 1)
        main_splitter.setStretchFactor(1, 1)
        
        layout.addWidget(main_splitter)
    
    def create_preview_panel(self):
        """创建首尾帧预览面板 - 左上区域"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(12)
        
        # 首帧区域
        first_frame_container = QWidget()
        first_layout = QVBoxLayout(first_frame_container)
        first_layout.setContentsMargins(0, 0, 0, 0)
        first_layout.setSpacing(8)
        
        # 首帧标题和按钮行
        first_header = QHBoxLayout()
        first_header.setSpacing(8)
        
        if FLUENT_AVAILABLE:
            first_label = StrongBodyLabel("首帧图片")
            first_header.addWidget(first_label)
            first_header.addStretch()
            
            self.select_first_btn = TransparentPushButton(FluentIcon.FOLDER, "选择")
            self.select_first_btn.setFixedHeight(28)
            self.select_first_btn.clicked.connect(self.select_first_frame)
            first_header.addWidget(self.select_first_btn)
            
            self.clear_first_btn = TransparentPushButton(FluentIcon.DELETE, "清除")
            self.clear_first_btn.setFixedHeight(28)
            self.clear_first_btn.clicked.connect(self.clear_first_frame)
            first_header.addWidget(self.clear_first_btn)
        else:
            first_label = QLabel("首帧图片")
            first_label.setStyleSheet("font-weight: bold; font-size: 13px;")
            first_header.addWidget(first_label)
            first_header.addStretch()
            
            self.select_first_btn = QPushButton("选择")
            self.select_first_btn.setFixedHeight(28)
            self.select_first_btn.clicked.connect(self.select_first_frame)
            first_header.addWidget(self.select_first_btn)
            
            self.clear_first_btn = QPushButton("清除")
            self.clear_first_btn.setFixedHeight(28)
            self.clear_first_btn.clicked.connect(self.clear_first_frame)
            first_header.addWidget(self.clear_first_btn)
        
        first_layout.addLayout(first_header)
        
        # 首帧预览
        self.first_frame_preview = DragDropLabel("拖拽图片到此处\n或点击选择按钮")
        self.first_frame_preview.setAlignment(Qt.AlignCenter)
        self.first_frame_preview.setMinimumHeight(140)
        self.first_frame_preview.setStyleSheet("""
            QLabel {
                border: 2px dashed #d0d0d0;
                border-radius: 8px;
                background: #fafafa;
                color: #888;
            }
        """)
        self.first_frame_preview.image_dropped.connect(self.on_first_frame_dropped)
        first_layout.addWidget(self.first_frame_preview, 1)
        
        layout.addWidget(first_frame_container, 1)
        
        # 尾帧区域
        last_frame_container = QWidget()
        last_layout = QVBoxLayout(last_frame_container)
        last_layout.setContentsMargins(0, 0, 0, 0)
        last_layout.setSpacing(8)
        
        # 尾帧标题和按钮行
        last_header = QHBoxLayout()
        last_header.setSpacing(8)
        
        if FLUENT_AVAILABLE:
            last_label = StrongBodyLabel("尾帧图片")
            last_header.addWidget(last_label)
            last_header.addStretch()
            
            self.select_last_btn = TransparentPushButton(FluentIcon.FOLDER, "选择")
            self.select_last_btn.setFixedHeight(28)
            self.select_last_btn.clicked.connect(self.select_last_frame)
            last_header.addWidget(self.select_last_btn)
            
            self.clear_last_btn = TransparentPushButton(FluentIcon.DELETE, "清除")
            self.clear_last_btn.setFixedHeight(28)
            self.clear_last_btn.clicked.connect(self.clear_last_frame)
            last_header.addWidget(self.clear_last_btn)
        else:
            last_label = QLabel("尾帧图片")
            last_label.setStyleSheet("font-weight: bold; font-size: 13px;")
            last_header.addWidget(last_label)
            last_header.addStretch()
            
            self.select_last_btn = QPushButton("选择")
            self.select_last_btn.setFixedHeight(28)
            self.select_last_btn.clicked.connect(self.select_last_frame)
            last_header.addWidget(self.select_last_btn)
            
            self.clear_last_btn = QPushButton("清除")
            self.clear_last_btn.setFixedHeight(28)
            self.clear_last_btn.clicked.connect(self.clear_last_frame)
            last_header.addWidget(self.clear_last_btn)
        
        last_layout.addLayout(last_header)
        
        # 尾帧预览
        self.last_frame_preview = DragDropLabel("拖拽图片到此处\n或点击选择按钮")
        self.last_frame_preview.setAlignment(Qt.AlignCenter)
        self.last_frame_preview.setMinimumHeight(140)
        self.last_frame_preview.setStyleSheet("""
            QLabel {
                border: 2px dashed #d0d0d0;
                border-radius: 8px;
                background: #fafafa;
                color: #888;
            }
        """)
        self.last_frame_preview.image_dropped.connect(self.on_last_frame_dropped)
        last_layout.addWidget(self.last_frame_preview, 1)
        
        layout.addWidget(last_frame_container, 1)
        
        return widget
    
    def create_config_panel(self):
        """创建配置面板 - 左下区域（模型、分辨率等）"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(12)
        
        # 数据映射
        self.model_data = ["wan2.2-kf2v-flash", "wanx2.1-kf2v-plus"]
        self.resolution_data = ["480P", "720P", "1080P"]
        
        # 模型选择
        model_row = QHBoxLayout()
        model_row.setSpacing(12)
        
        if FLUENT_AVAILABLE:
            model_label = BodyLabel("模型")
            model_label.setFixedWidth(60)
            model_row.addWidget(model_label)
            
            self.model_combo = ComboBox()
            self.model_combo.addItems(["wan2.2-kf2v-flash（推荐）", "wanx2.1-kf2v-plus（稳定）"])
        else:
            model_label = QLabel("模型:")
            model_label.setFixedWidth(60)
            model_row.addWidget(model_label)
            
            self.model_combo = QComboBox()
            self.model_combo.addItem("wan2.2-kf2v-flash（推荐）", "wan2.2-kf2v-flash")
            self.model_combo.addItem("wanx2.1-kf2v-plus（稳定）", "wanx2.1-kf2v-plus")
        
        self.model_combo.setMinimumHeight(32)
        model_row.addWidget(self.model_combo, 1)
        layout.addLayout(model_row)
        
        # 分辨率选择
        resolution_row = QHBoxLayout()
        resolution_row.setSpacing(12)
        
        if FLUENT_AVAILABLE:
            resolution_label = BodyLabel("分辨率")
            resolution_label.setFixedWidth(60)
            resolution_row.addWidget(resolution_label)
            
            self.resolution_combo = ComboBox()
            self.resolution_combo.addItems(["480P (854x480)", "720P (1280x720)", "1080P (1920x1080)"])
        else:
            resolution_label = QLabel("分辨率:")
            resolution_label.setFixedWidth(60)
            resolution_row.addWidget(resolution_label)
            
            self.resolution_combo = QComboBox()
            self.resolution_combo.addItem("480P (854x480)", "480P")
            self.resolution_combo.addItem("720P (1280x720)", "720P")
            self.resolution_combo.addItem("1080P (1920x1080)", "1080P")
        
        self.resolution_combo.setMinimumHeight(32)
        self.resolution_combo.setCurrentIndex(1)  # 默认720P
        resolution_row.addWidget(self.resolution_combo, 1)
        layout.addLayout(resolution_row)
        
        # 提示词智能改写开关
        extend_row = QHBoxLayout()
        extend_row.setSpacing(12)
        
        if FLUENT_AVAILABLE:
            extend_label = BodyLabel("智能改写")
            extend_label.setFixedWidth(60)
            extend_row.addWidget(extend_label)
            extend_row.addStretch()
            
            self.prompt_extend_switch = SwitchButton()
            self.prompt_extend_switch.setChecked(True)
            extend_row.addWidget(self.prompt_extend_switch)
        else:
            self.prompt_extend_switch = QCheckBox("启用提示词智能改写")
            self.prompt_extend_switch.setChecked(True)
            extend_row.addWidget(self.prompt_extend_switch)
        
        layout.addLayout(extend_row)
        
        # 状态标签
        if FLUENT_AVAILABLE:
            self.status_label = CaptionLabel("请先选择首帧和尾帧图片")
            self.status_label.setStyleSheet("color: #888;")
        else:
            self.status_label = QLabel("请先选择首帧和尾帧图片")
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
            
            # 生成按钮
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
            "描述首尾帧之间的过渡效果...\n\n"
            "例如：写实风格，一只黑色小猫好奇地看向天空，镜头从平视逐渐上升，最后俯拍它的好奇的眼神。"
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
        layout.addWidget(self.prompt_edit, 1)
        
        return widget

    def clear_first_frame(self):
        """清除首帧图片"""
        self.first_frame_path = None
        self.first_frame_preview.clear()
        self.first_frame_preview.setText("拖拽图片到此处\n或点击选择按钮")
        self.first_frame_preview.original_pixmap = None
        self.first_frame_preview.setStyleSheet("""
            QLabel {
                border: 2px dashed #d0d0d0;
                border-radius: 8px;
                background: #fafafa;
                color: #888;
            }
        """)
        self.update_status()
    
    def clear_last_frame(self):
        """清除尾帧图片"""
        self.last_frame_path = None
        self.last_frame_preview.clear()
        self.last_frame_preview.setText("拖拽图片到此处\n或点击选择按钮")
        self.last_frame_preview.original_pixmap = None
        self.last_frame_preview.setStyleSheet("""
            QLabel {
                border: 2px dashed #d0d0d0;
                border-radius: 8px;
                background: #fafafa;
                color: #888;
            }
        """)
        self.update_status()
    
    def select_first_frame(self):
        """选择首帧图片"""
        default_dir = ""
        if self.project_manager.has_project():
            project = self.project_manager.get_current_project()
            default_dir = project.inputs_folder
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择首帧图片",
            default_dir,
            "图片文件 (*.png *.jpg *.jpeg)"
        )
        
        if file_path:
            self.load_first_frame(file_path)
    
    def select_last_frame(self):
        """选择尾帧图片"""
        default_dir = ""
        if self.project_manager.has_project():
            project = self.project_manager.get_current_project()
            default_dir = project.inputs_folder
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择尾帧图片",
            default_dir,
            "图片文件 (*.png *.jpg *.jpeg)"
        )
        
        if file_path:
            self.load_last_frame(file_path)
    
    def on_first_frame_dropped(self, file_path):
        """首帧图片拖拽事件"""
        self.load_first_frame(file_path)
    
    def on_last_frame_dropped(self, file_path):
        """尾帧图片拖拽事件"""
        self.load_last_frame(file_path)
    
    def load_first_frame(self, file_path):
        """加载首帧图片"""
        if os.path.exists(file_path):
            self.first_frame_path = file_path
            self.first_frame_preview.setImagePath(file_path)
            self.first_frame_preview.setStyleSheet("""
                QLabel {
                    border: 2px solid #0078d4;
                    border-radius: 8px;
                    background: white;
                    padding: 2px;
                }
            """)
            self.update_status()
    
    def load_last_frame(self, file_path):
        """加载尾帧图片"""
        if os.path.exists(file_path):
            self.last_frame_path = file_path
            self.last_frame_preview.setImagePath(file_path)
            self.last_frame_preview.setStyleSheet("""
                QLabel {
                    border: 2px solid #0078d4;
                    border-radius: 8px;
                    background: white;
                    padding: 2px;
                }
            """)
            self.update_status()
    
    def update_status(self):
        """更新状态提示"""
        if self.first_frame_path and self.last_frame_path:
            self.status_label.setText("已选择首帧和尾帧，可以开始生成")
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
        elif self.first_frame_path:
            self.status_label.setText("请选择尾帧图片")
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
        elif self.last_frame_path:
            self.status_label.setText("请选择首帧图片")
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
        else:
            self.status_label.setText("请先选择首帧和尾帧图片")
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
        # 验证图片
        if not self.first_frame_path:
            QMessageBox.warning(self, "提示", "请先选择首帧图片")
            return
        
        if not self.last_frame_path:
            QMessageBox.warning(self, "提示", "请先选择尾帧图片")
            return
        
        # 验证提示词
        prompt = self.prompt_edit.toPlainText().strip()
        if not prompt:
            QMessageBox.warning(self, "提示", "请输入视频描述")
            return
        
        # 检查是否有工程
        if not self.project_manager.has_project():
            QMessageBox.warning(self, "提示", "请先创建或打开工程")
            return
        
        # 获取配置
        if FLUENT_AVAILABLE:
            model = self.model_data[self.model_combo.currentIndex()]
            resolution = self.resolution_data[self.resolution_combo.currentIndex()]
            prompt_extend = self.prompt_extend_switch.isChecked()
        else:
            model = self.model_combo.currentData()
            resolution = self.resolution_combo.currentData()
            prompt_extend = self.prompt_extend_switch.isChecked()
        
        # 获取输出文件夹
        project = self.project_manager.get_current_project()
        output_folder = project.outputs_folder
        
        # 禁用按钮
        self.generate_btn.setEnabled(False)
        if FLUENT_AVAILABLE:
            self.generate_btn.setText("生成中...")
        else:
            self.generate_btn.setText("生成中...")
        
        # 创建工作线程
        self.worker = KeyframeVideoWorker(
            self.api_client,
            self.first_frame_path,
            self.last_frame_path,
            prompt,
            model,
            resolution,
            prompt_extend,
            output_folder
        )
        self.worker.finished.connect(self.on_generate_finished)
        self.worker.error.connect(self.on_generate_error)
        self.worker.progress.connect(self.on_generate_progress)
        self.worker.start()
    
    def on_generate_finished(self, video_path, video_info):
        """生成完成"""
        self.generate_btn.setEnabled(True)
        if FLUENT_AVAILABLE:
            self.generate_btn.setText("生成视频")
        else:
            self.generate_btn.setText("生成视频")
        self.status_label.setText("视频生成成功！")
        
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
        
        QMessageBox.critical(self, "错误", error_msg)
    
    def on_generate_progress(self, status_msg):
        """生成进度更新"""
        self.status_label.setText(status_msg)

    def showEvent(self, event):
        """显示事件 - 仅首次显示时刷新布局"""
        super().showEvent(event)
        # 只在首次显示时刷新，避免抖动
        if not hasattr(self, '_first_show_done'):
            self._first_show_done = True
            from PyQt5.QtCore import QTimer
            QTimer.singleShot(50, self.updateGeometry)
