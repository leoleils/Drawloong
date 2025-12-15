#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
首尾帧生成视频组件
支持上传首帧和尾帧图片，生成视频
"""

import os
import base64
import time
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QTextEdit, QGroupBox, QFileDialog, QMessageBox,
    QSplitter, QScrollArea, QGridLayout, QCheckBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QDragEnterEvent, QDropEvent

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
                            border: 2px dashed #007bff;
                            border-radius: 4px;
                            background: #e7f3ff;
                            color: #007bff;
                        }
                    """)
    
    def dragLeaveEvent(self, event):
        """拖拽离开事件"""
        if not self.pixmap():
            self.setStyleSheet("""
                QLabel {
                    border: 2px dashed #ddd;
                    border-radius: 4px;
                    background: #f9f9f9;
                    color: #999;
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
            # 获取可用空间，留出边距
            available_width = max(self.width() - 10, 340)
            available_height = max(self.height() - 10, 210)
            # 缩放图片保持宽高比
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
            self.progress.emit("📤 正在提交任务...")
            
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
            self.progress.emit(f"⏳ 任务已提交 (ID: {task_id})")
            
            # 轮询任务状态
            max_retries = 180  # 最多轮询180次（约15分钟）
            retry_count = 0
            
            while retry_count < max_retries:
                time.sleep(5)  # 每5秒查询一次
                retry_count += 1
                
                self.progress.emit(f"🔄 正在生成视频... ({retry_count}/{max_retries})")
                
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
                    
                    self.progress.emit("📥 正在下载视频...")
                    
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
    """首尾帧生成视频组件"""
    
    def __init__(self, api_client, project_manager, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.project_manager = project_manager
        self.worker = None
        self.first_frame_path = None
        self.last_frame_path = None
        self.history_videos = []  # 历史视频列表
        self.history_file = None  # 历史记录文件路径
        self.setup_ui()
        self.load_history()  # 加载历史记录
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 主水平分割器 - 左右布局
        main_splitter = QSplitter(Qt.Horizontal)
        
        # 左侧：关键帧预览和历史记录
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        left_splitter = QSplitter(Qt.Vertical)
        
        # 左上：关键帧预览（占大部分）
        preview_widget = self.create_preview_panel()
        left_splitter.addWidget(preview_widget)
        
        # 左下：历史记录（类似任务列表）
        left_bottom_widget = QWidget()
        left_bottom_layout = QVBoxLayout(left_bottom_widget)
        left_bottom_layout.setContentsMargins(5, 5, 5, 5)
        
        # 历史记录面板
        history_group = QGroupBox("历史视频")
        history_layout = QVBoxLayout(history_group)
        
        # 历史列表
        from PyQt5.QtWidgets import QListWidget, QListWidgetItem
        self.history_list = QListWidget()
        self.history_list.setMinimumHeight(150)
        self.history_list.itemClicked.connect(self.on_history_item_clicked)
        self.history_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                background: #f9f9f9;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:hover {
                background: #e7f3ff;
            }
            QListWidget::item:selected {
                background: #007bff;
                color: white;
            }
        """)
        history_layout.addWidget(self.history_list)
        left_bottom_layout.addWidget(history_group)
        
        # 元数据信息面板
        metadata_group = QGroupBox("视频生成信息")
        metadata_layout = QVBoxLayout(metadata_group)
        
        # 创建可滚动的内容区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumHeight(150)
        
        scroll_content = QWidget()
        self.metadata_layout = QVBoxLayout(scroll_content)
        self.metadata_layout.setContentsMargins(5, 5, 5, 5)
        
        # 默认提示
        self.metadata_placeholder = QLabel("📊 生成视频或点击历史记录，查看生成参数")
        self.metadata_placeholder.setAlignment(Qt.AlignCenter)
        self.metadata_placeholder.setStyleSheet("""
            QLabel {
                color: #999;
                font-size: 12px;
                padding: 20px;
            }
        """)
        self.metadata_layout.addWidget(self.metadata_placeholder)
        
        scroll_area.setWidget(scroll_content)
        metadata_layout.addWidget(scroll_area)
        
        left_bottom_layout.addWidget(metadata_group)
        left_splitter.addWidget(left_bottom_widget)
        
        # 左侧上下比例：关键帧占2份，历史记录占1份
        left_splitter.setStretchFactor(0, 2)
        left_splitter.setStretchFactor(1, 1)
        
        left_layout.addWidget(left_splitter)
        main_splitter.addWidget(left_widget)
        
        # 右侧：配置面板和视频预览
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        right_splitter = QSplitter(Qt.Vertical)
        
        # 右上：配置面板
        config_widget = self.create_config_panel()
        right_splitter.addWidget(config_widget)
        
        # 右下：视频预览
        self.video_viewer = VideoViewerWidget()
        right_splitter.addWidget(self.video_viewer)
        
        # 右侧上下各占一半
        right_splitter.setStretchFactor(0, 1)
        right_splitter.setStretchFactor(1, 1)
        
        right_layout.addWidget(right_splitter)
        main_splitter.addWidget(right_widget)
        
        # 左右比例：左侧占2份，右侧占1份
        main_splitter.setStretchFactor(0, 2)
        main_splitter.setStretchFactor(1, 1)
        
        layout.addWidget(main_splitter)
    
    def create_config_panel(self):
        """创建配置面板"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
        """)
        
        # 滚动内容容器
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
        self.prompt_edit.setPlaceholderText("描述首尾帧之间的过渡效果...\n例如：写实风格，一只黑色小猫好奇地看向天空，镜头从平视逐渐上升，最后俯拍它的好奇的眼神。")
        self.prompt_edit.setMinimumHeight(100)
        group_layout.addWidget(self.prompt_edit)
        
        # 模型选择
        model_label = QLabel("模型:")
        model_label.setStyleSheet("font-weight: bold; font-size: 12px; margin-top: 5px;")
        group_layout.addWidget(model_label)
        
        self.model_combo = QComboBox()
        self.model_combo.setMinimumHeight(32)
        self.model_combo.addItem("🌟 wan2.2-kf2v-flash（推荐，快速）", "wan2.2-kf2v-flash")
        self.model_combo.addItem("wanx2.1-kf2v-plus（稳定）", "wanx2.1-kf2v-plus")
        group_layout.addWidget(self.model_combo)
        
        # 分辨率选择
        resolution_label = QLabel("分辨率:")
        resolution_label.setStyleSheet("font-weight: bold; font-size: 12px; margin-top: 5px;")
        group_layout.addWidget(resolution_label)
        
        self.resolution_combo = QComboBox()
        self.resolution_combo.setMinimumHeight(32)
        self.resolution_combo.addItem("480P (854x480)", "480P")
        self.resolution_combo.addItem("720P (1280x720)", "720P")
        self.resolution_combo.addItem("1080P (1920x1080)", "1080P")
        self.resolution_combo.setCurrentIndex(1)  # 默认720P
        group_layout.addWidget(self.resolution_combo)
        
        # 提示词扩展
        self.prompt_extend_checkbox = QCheckBox("启用提示词扩展")
        self.prompt_extend_checkbox.setChecked(True)
        self.prompt_extend_checkbox.setMinimumHeight(28)
        self.prompt_extend_checkbox.setStyleSheet("""
            QCheckBox {
                font-size: 12px;
                padding: 5px;
                margin-top: 5px;
            }
        """)
        group_layout.addWidget(self.prompt_extend_checkbox)
        
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
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
        """)
        group_layout.addWidget(self.generate_btn)
        
        # 状态标签
        self.status_label = QLabel("💡 请先选择首帧和尾帧图片")
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
        """创建关键帧预览面板"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # 创建可滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)  # 始终显示垂直滚动条
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                width: 12px;
                background: #f0f0f0;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #c0c0c0;
                border-radius: 6px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: #a0a0a0;
            }
        """)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(5, 5, 15, 5)  # 右边留出滚动条空间
        
        group_box = QGroupBox("关键帧图片")
        group_layout = QVBoxLayout(group_box)
        
        # 首帧区域
        first_frame_label = QLabel("首帧图片:")
        first_frame_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        group_layout.addWidget(first_frame_label)
        
        # 使用支持拖拽的Label - 增大显示区域
        self.first_frame_preview = DragDropLabel("🖼️ 未选择\n(支持拖拽图片)")
        self.first_frame_preview.setAlignment(Qt.AlignCenter)
        self.first_frame_preview.setMinimumHeight(150)  # 设置合理的最小高度
        self.first_frame_preview.setMinimumWidth(300)  # 设置最小宽度
        self.first_frame_preview.setScaledContents(False)  # 不拉伸内容
        self.first_frame_preview.setStyleSheet("""
            QLabel {
                border: 2px dashed #ddd;
                border-radius: 4px;
                background: #f9f9f9;
                color: #999;
            }
        """)
        self.first_frame_preview.image_dropped.connect(self.on_first_frame_dropped)
        group_layout.addWidget(self.first_frame_preview)
        
        # 首帧按钮组
        first_btn_layout = QHBoxLayout()
        
        self.select_first_btn = QPushButton("从工程选择")
        self.select_first_btn.clicked.connect(lambda: self.select_from_project('first'))
        self.select_first_btn.setMinimumHeight(32)  # 设置最小高度，避免被压缩
        self.select_first_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                padding: 6px 12px;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        first_btn_layout.addWidget(self.select_first_btn)
        
        self.browse_first_btn = QPushButton("浏览...")
        self.browse_first_btn.clicked.connect(self.select_first_frame)
        self.browse_first_btn.setMinimumHeight(32)  # 设置最小高度
        self.browse_first_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                padding: 6px 12px;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        first_btn_layout.addWidget(self.browse_first_btn)
        
        group_layout.addLayout(first_btn_layout)
        
        # 尾帧区域
        last_frame_label = QLabel("尾帧图片:")
        last_frame_label.setStyleSheet("font-weight: bold; font-size: 12px; margin-top: 10px;")
        group_layout.addWidget(last_frame_label)
        
        self.last_frame_preview = DragDropLabel("🖼️ 未选择\n(支持拖拽图片)")
        self.last_frame_preview.setAlignment(Qt.AlignCenter)
        self.last_frame_preview.setMinimumHeight(150)  # 设置合理的最小高度
        self.last_frame_preview.setMinimumWidth(300)  # 设置最小宽度
        self.last_frame_preview.setScaledContents(False)  # 不拉伸内容
        self.last_frame_preview.setStyleSheet("""
            QLabel {
                border: 2px dashed #ddd;
                border-radius: 4px;
                background: #f9f9f9;
                color: #999;
            }
        """)
        self.last_frame_preview.image_dropped.connect(self.on_last_frame_dropped)
        group_layout.addWidget(self.last_frame_preview)
        
        # 尾帧按钮组
        last_btn_layout = QHBoxLayout()
        
        self.select_last_btn = QPushButton("从工程选择")
        self.select_last_btn.clicked.connect(lambda: self.select_from_project('last'))
        self.select_last_btn.setMinimumHeight(32)  # 设置最小高度
        self.select_last_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                padding: 6px 12px;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        last_btn_layout.addWidget(self.select_last_btn)
        
        self.browse_last_btn = QPushButton("浏览...")
        self.browse_last_btn.clicked.connect(self.select_last_frame)
        self.browse_last_btn.setMinimumHeight(32)  # 设置最小高度
        self.browse_last_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                padding: 6px 12px;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        last_btn_layout.addWidget(self.browse_last_btn)
        
        group_layout.addLayout(last_btn_layout)
        
        scroll_layout.addWidget(group_box)
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)
        return widget
    
    def select_first_frame(self):
        """选择首帧图片(浏览文件系统)"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择首帧图片",
            "",
            "图片文件 (*.png *.jpg *.jpeg)"
        )
        
        if file_path:
            self.load_first_frame(file_path)
    
    def select_last_frame(self):
        """选择尾帧图片(浏览文件系统)"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择尾帧图片",
            "",
            "图片文件 (*.png *.jpg *.jpeg)"
        )
        
        if file_path:
            self.load_last_frame(file_path)
    
    def select_from_project(self, frame_type):
        """从工程文件中选择图片"""
        # 检查是否有工程
        if not self.project_manager.has_project():
            QMessageBox.warning(self, "提示", "请先创建或打开工程")
            return
        
        # 获取工程目录
        project = self.project_manager.get_current_project()
        project_dir = project.inputs_folder
        
        # 打开文件选择对话框，默认在工程目录
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            f"从工程选择{'首帧' if frame_type == 'first' else '尾帧'}图片",
            project_dir,
            "图片文件 (*.png *.jpg *.jpeg)"
        )
        
        if file_path:
            if frame_type == 'first':
                self.load_first_frame(file_path)
            else:
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
                    border: 2px solid #28a745;
                    border-radius: 4px;
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
                    border: 2px solid #28a745;
                    border-radius: 4px;
                    background: white;
                    padding: 2px;
                }
            """)
            self.update_status()
    
    def update_status(self):
        """更新状态提示"""
        if self.first_frame_path and self.last_frame_path:
            self.status_label.setText("✅ 已选择首帧和尾帧，可以开始生成")
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #28a745;
                    font-size: 12px;
                    padding: 10px;
                    background: #d4edda;
                    border-radius: 4px;
                }
            """)
        elif self.first_frame_path:
            self.status_label.setText("⚠️ 请选择尾帧图片")
        elif self.last_frame_path:
            self.status_label.setText("⚠️ 请选择首帧图片")
    
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
        model = self.model_combo.currentData()
        resolution = self.resolution_combo.currentData()
        prompt_extend = self.prompt_extend_checkbox.isChecked()
        
        # 获取输出文件夹 (视频保存到outputs文件夹)
        project = self.project_manager.get_current_project()
        output_folder = project.outputs_folder
        
        # 禁用按钮
        self.generate_btn.setEnabled(False)
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
        self.generate_btn.setText("开始生成")
        self.status_label.setText("✅ 视频生成成功！")
        
        # 加载视频到视频查看器
        self.video_viewer.load_video(video_path)
        
        # 显示元数据信息
        self.display_metadata(video_info)
        
        # 添加到历史记录
        import time
        video_history = {
            'path': video_path,
            'timestamp': time.time(),
            'metadata': video_info
        }
        self.history_videos.insert(0, video_history)  # 插入到最前面
        self.save_history()
        self.refresh_history_list()
        
        # 刷新资源管理器
        main_window = self.window()
        if hasattr(main_window, 'project_explorer'):
            main_window.project_explorer.refresh()
        
        QMessageBox.information(
            self,
            "成功",
            f"视频生成完成！\n已保存到: {os.path.basename(video_path)}"
        )
    
    def display_metadata(self, video_info):
        """显示元数据信息"""
        # 清空现有内容
        while self.metadata_layout.count():
            item = self.metadata_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # 模型信息
        model_label = QLabel(f"🤖 模型: {video_info.get('model', 'N/A')}")
        model_label.setStyleSheet("""
            QLabel {
                color: #333;
                font-size: 11px;
                font-weight: bold;
                padding: 5px;
                background: #e7f3ff;
                border-radius: 3px;
            }
        """)
        self.metadata_layout.addWidget(model_label)
        
        # 分辨率信息
        resolution_label = QLabel(f"📺 分辨率: {video_info.get('resolution', 'N/A')}")
        resolution_label.setStyleSheet("""
            QLabel {
                color: #333;
                font-size: 11px;
                font-weight: bold;
                padding: 5px;
                background: #f0f8ff;
                border-radius: 3px;
                margin-top: 3px;
            }
        """)
        self.metadata_layout.addWidget(resolution_label)
        
        # 首帧和尾帧信息
        frames_label = QLabel(
            f"🎬 关键帧: {video_info.get('first_frame', 'N/A')} → {video_info.get('last_frame', 'N/A')}"
        )
        frames_label.setStyleSheet("""
            QLabel {
                color: #333;
                font-size: 11px;
                padding: 5px;
                background: #fff8e1;
                border-radius: 3px;
                margin-top: 3px;
            }
        """)
        self.metadata_layout.addWidget(frames_label)
        
        # 提示词扩展
        prompt_extend_text = "✅ 已启用" if video_info.get('prompt_extend') else "❌ 未启用"
        prompt_extend_label = QLabel(f"✨ 提示词扩展: {prompt_extend_text}")
        prompt_extend_label.setStyleSheet("""
            QLabel {
                color: #333;
                font-size: 11px;
                padding: 5px;
                background: #f5f5f5;
                border-radius: 3px;
                margin-top: 3px;
            }
        """)
        self.metadata_layout.addWidget(prompt_extend_label)
        
        # 原始提示词
        orig_prompt = video_info.get('orig_prompt', '')
        if orig_prompt:
            orig_title = QLabel("📝 原始提示词:")
            orig_title.setStyleSheet("""
                QLabel {
                    color: #666;
                    font-size: 10px;
                    font-weight: bold;
                    margin-top: 8px;
                }
            """)
            self.metadata_layout.addWidget(orig_title)
            
            orig_text = QLabel(orig_prompt)
            orig_text.setWordWrap(True)
            orig_text.setTextInteractionFlags(Qt.TextSelectableByMouse)
            orig_text.setStyleSheet("""
                QLabel {
                    color: #555;
                    font-size: 10px;
                    padding: 6px;
                    background: #f8f9fa;
                    border-radius: 3px;
                    border-left: 3px solid #007bff;
                }
            """)
            self.metadata_layout.addWidget(orig_text)
        
        # 实际使用的提示词
        actual_prompt = video_info.get('actual_prompt', '')
        if actual_prompt and actual_prompt != orig_prompt:
            actual_title = QLabel("⚙️ AI扩展后的提示词:")
            actual_title.setStyleSheet("""
                QLabel {
                    color: #666;
                    font-size: 10px;
                    font-weight: bold;
                    margin-top: 8px;
                }
            """)
            self.metadata_layout.addWidget(actual_title)
            
            actual_text = QLabel(actual_prompt)
            actual_text.setWordWrap(True)
            actual_text.setTextInteractionFlags(Qt.TextSelectableByMouse)
            actual_text.setStyleSheet("""
                QLabel {
                    color: #555;
                    font-size: 10px;
                    padding: 6px;
                    background: #fff9e6;
                    border-radius: 3px;
                    border-left: 3px solid #ffc107;
                }
            """)
            self.metadata_layout.addWidget(actual_text)
        
        # Task ID
        task_id = video_info.get('task_id', '')
        if task_id:
            task_id_label = QLabel(f"🎯 Task ID: {task_id}")
            task_id_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            task_id_label.setStyleSheet("""
                QLabel {
                    color: #999;
                    font-size: 9px;
                    padding: 4px;
                    margin-top: 5px;
                    font-family: monospace;
                }
            """)
            self.metadata_layout.addWidget(task_id_label)
        
        self.metadata_layout.addStretch()
    
    def on_generate_error(self, error_msg):
        """生成错误"""
        self.generate_btn.setEnabled(True)
        self.generate_btn.setText("开始生成")
        self.status_label.setText(f"❌ {error_msg}")
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
    
    def load_history(self):
        """加载历史记录"""
        try:
            import json
            
            # 获取当前工程
            if not self.project_manager.has_project():
                return
            
            project = self.project_manager.get_current_project()
            self.history_file = os.path.join(project.path, 'keyframe_video_history.json')
            
            if not os.path.exists(self.history_file):
                return
            
            # 读取历史文件
            with open(self.history_file, 'r', encoding='utf-8') as f:
                loaded_history = json.load(f)
            
            # 只加载存在的视频
            self.history_videos = []
            for video_info in loaded_history:
                video_path = video_info.get('path', '')
                if os.path.exists(video_path):
                    self.history_videos.append(video_info)
            
            # 刷新列表
            self.refresh_history_list()
            
        except Exception as e:
            print(f"加载历史记录失败: {e}")
    
    def save_history(self):
        """保存历史记录"""
        try:
            import json
            
            # 获取当前工程
            if not self.project_manager.has_project():
                return
            
            project = self.project_manager.get_current_project()
            self.history_file = os.path.join(project.path, 'keyframe_video_history.json')
            
            # 只保存存在的视频
            valid_videos = []
            for video_info in self.history_videos:
                if os.path.exists(video_info.get('path', '')):
                    valid_videos.append(video_info)
            
            # 保存到文件
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(valid_videos, f, ensure_ascii=False, indent=2)
            
        except Exception as e:
            print(f"保存历史记录失败: {e}")
    
    def refresh_history_list(self):
        """刷新历史列表显示"""
        from PyQt5.QtWidgets import QListWidgetItem
        from datetime import datetime
        
        self.history_list.clear()
        
        if not self.history_videos:
            # 显示空状态
            empty_item = QListWidgetItem("📁 暂无历史记录")
            empty_item.setData(Qt.UserRole, None)
            self.history_list.addItem(empty_item)
            return
        
        # 添加历史视频
        for video_info in self.history_videos:
            metadata = video_info.get('metadata', {})
            timestamp = video_info.get('timestamp', 0)
            
            # 格式化时间
            dt = datetime.fromtimestamp(timestamp)
            time_str = dt.strftime('%m-%d %H:%M')
            
            # 获取提示词（截断）
            orig_prompt = metadata.get('orig_prompt', '')
            if len(orig_prompt) > 30:
                prompt_preview = orig_prompt[:30] + '...'
            else:
                prompt_preview = orig_prompt or '未知'
            
            # 创建列表项
            item_text = f"🎥 {time_str} - {prompt_preview}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, video_info)
            item.setToolTip(f"视频: {os.path.basename(video_info['path'])}\n提示词: {orig_prompt}")
            self.history_list.addItem(item)
    
    def on_history_item_clicked(self, item):
        """点击历史记录项"""
        video_info = item.data(Qt.UserRole)
        
        if not video_info:
            return
        
        video_path = video_info.get('path')
        metadata = video_info.get('metadata', {})
        
        # 检查视频是否存在
        if not os.path.exists(video_path):
            QMessageBox.warning(self, "提示", f"视频文件不存在:\n{video_path}")
            return
        
        # 加载视频
        self.video_viewer.load_video(video_path)
        
        # 显示元数据
        self.display_metadata(metadata)
