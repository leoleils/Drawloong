#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
上传组件
支持拖拽和点击上传图片
使用 QFluentWidgets 组件实现现代化 UI
"""

import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFileDialog, QGroupBox, QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QDragEnterEvent, QDropEvent

from config.settings import settings

try:
    from qfluentwidgets import (
        PushButton, CardWidget, BodyLabel, IconWidget, FluentIcon,
        isDarkTheme
    )
    FLUENT_AVAILABLE = True
except ImportError:
    FLUENT_AVAILABLE = False
    print("警告: QFluentWidgets 未安装，将使用原生 PyQt5 组件")


class UploadWidget(QWidget):
    """图片上传组件"""
    
    # 定义信号
    image_selected = pyqtSignal(str)  # 图片路径
    
    def __init__(self, parent=None):
        """初始化上传组件"""
        super().__init__(parent)
        self.current_image_path = None
        self.original_pixmap = None  # 存储原始图片
        self.project_manager = None  # 工程管理器引用
        self.setup_ui()
        
        # 启用拖拽
        self.setAcceptDrops(True)
    
    def set_project_manager(self, project_manager):
        """设置工程管理器引用"""
        self.project_manager = project_manager
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        if FLUENT_AVAILABLE:
            self._setup_fluent_ui(layout)
        else:
            self._setup_native_ui(layout)
    
    def _setup_fluent_ui(self, layout: QVBoxLayout):
        """设置 Fluent 风格 UI"""
        # 按钮组
        btn_layout = QHBoxLayout()
        # 统一按钮间距：12px
        btn_layout.setSpacing(12)
        
        # 从工程选择按钮
        self.select_from_project_btn = PushButton(FluentIcon.DOCUMENT, "从工程选择")
        self.select_from_project_btn.clicked.connect(self.select_from_project)
        self.select_from_project_btn.setMinimumHeight(36)
        btn_layout.addWidget(self.select_from_project_btn)
        
        # 浏览按钮
        self.browse_btn = PushButton(FluentIcon.FOLDER, "浏览...")
        self.browse_btn.clicked.connect(self.select_image)
        self.browse_btn.setMinimumHeight(36)
        btn_layout.addWidget(self.browse_btn)
        
        layout.addLayout(btn_layout)
        layout.addSpacing(8)
        
        # 拖放区域卡片
        self.drop_card = CardWidget()
        self.drop_card.setMinimumHeight(200)
        drop_card_layout = QVBoxLayout(self.drop_card)
        # 统一卡片内边距：16px
        drop_card_layout.setContentsMargins(16, 16, 16, 16)
        drop_card_layout.setAlignment(Qt.AlignCenter)
        
        # 上传图标
        self.upload_icon = IconWidget(FluentIcon.PHOTO)
        self.upload_icon.setFixedSize(48, 48)
        drop_card_layout.addWidget(self.upload_icon, alignment=Qt.AlignCenter)
        
        # 提示文字
        self.hint_label = BodyLabel("拖拽图片到此处\n或点击上方按钮选择")
        self.hint_label.setAlignment(Qt.AlignCenter)
        drop_card_layout.addWidget(self.hint_label, alignment=Qt.AlignCenter)
        
        # 预览标签（用于显示图片）
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setVisible(False)
        drop_card_layout.addWidget(self.preview_label, 1)
        
        layout.addWidget(self.drop_card, 1)
        
        # 文件名标签
        self.filename_label = BodyLabel()
        self.filename_label.setAlignment(Qt.AlignCenter)
        self.filename_label.setVisible(False)
        layout.addWidget(self.filename_label)
        
        # 设置拖放区域的初始样式
        self._update_drop_card_style(False)
    
    def _setup_native_ui(self, layout: QVBoxLayout):
        """设置原生 PyQt5 UI（降级方案）"""
        # 创建组框
        group_box = QGroupBox("上传图片")
        group_layout = QVBoxLayout(group_box)
        
        # 按钮组（从工程选择 + 浏览）
        btn_layout = QHBoxLayout()
        
        # 从工程选择按钮
        self.select_from_project_btn = QPushButton("从工程选择")
        self.select_from_project_btn.clicked.connect(self.select_from_project)
        self.select_from_project_btn.setMinimumHeight(36)
        self.select_from_project_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        btn_layout.addWidget(self.select_from_project_btn)
        
        # 浏览按钮
        self.browse_btn = QPushButton("浏览...")
        self.browse_btn.clicked.connect(self.select_image)
        self.browse_btn.setMinimumHeight(36)
        self.browse_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        btn_layout.addWidget(self.browse_btn)
        
        group_layout.addLayout(btn_layout)
        
        # 预览区域（占满剩余空间）
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumHeight(200)
        self.preview_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #ccc;
                border-radius: 10px;
                background-color: #f9f9f9;
            }
        """)
        # 将提示文字放在预览区域中央
        self.preview_label.setText("拖拽图片到此处\n或点击上方按钮选择")
        group_layout.addWidget(self.preview_label, 1)  # stretch=1 让它占满空间
        
        # 文件名标签
        self.filename_label = QLabel()
        self.filename_label.setAlignment(Qt.AlignCenter)
        self.filename_label.setStyleSheet("color: #333; font-size: 12px; padding: 5px;")
        self.filename_label.setVisible(False)
        group_layout.addWidget(self.filename_label)
        
        layout.addWidget(group_box)
        
        # 为原生 UI 创建占位属性
        self.drop_card = None
        self.upload_icon = None
        self.hint_label = None
    
    def _update_drop_card_style(self, has_image: bool, is_dragging: bool = False):
        """更新拖放卡片样式（仅 Fluent 模式）"""
        if not FLUENT_AVAILABLE or not self.drop_card:
            return
        
        if is_dragging:
            # 拖拽中的高亮样式
            if isDarkTheme():
                self.drop_card.setStyleSheet("""
                    CardWidget {
                        border: 2px dashed #0078d4;
                        background-color: rgba(0, 120, 212, 0.1);
                        border-radius: 8px;
                    }
                """)
            else:
                self.drop_card.setStyleSheet("""
                    CardWidget {
                        border: 2px dashed #0078d4;
                        background-color: rgba(0, 120, 212, 0.05);
                        border-radius: 8px;
                    }
                """)
        elif has_image:
            # 已选择图片的样式
            if isDarkTheme():
                self.drop_card.setStyleSheet("""
                    CardWidget {
                        border: 2px solid #28a745;
                        border-radius: 8px;
                    }
                """)
            else:
                self.drop_card.setStyleSheet("""
                    CardWidget {
                        border: 2px solid #28a745;
                        border-radius: 8px;
                    }
                """)
        else:
            # 默认样式
            self.drop_card.setStyleSheet("")
    
    def select_from_project(self):
        """从工程文件中选择图片"""
        from utils.message_helper import MessageHelper
        
        # 检查是否有工程
        if not self.project_manager or not self.project_manager.has_project():
            parent = self.window()
            MessageHelper.warning(parent, "提示", "请先创建或打开工程")
            return
        
        # 获取工程目录
        project = self.project_manager.get_current_project()
        project_dir = project.inputs_folder
        
        # 打开文件选择对话框，默认在工程目录
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "从工程选择图片",
            project_dir,
            "图片文件 (*.png *.jpg *.jpeg)"
        )
        
        if file_path:
            self.load_image(file_path)
    
    def select_image(self):
        """选择图片文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择图片",
            "",
            "图片文件 (*.png *.jpg *.jpeg)"
        )
        
        if file_path:
            self.load_image(file_path)
    
    def load_image(self, file_path):
        """加载并显示图片"""
        from utils.message_helper import MessageHelper
        parent = self.window()
        
        # 检查文件大小
        file_size = os.path.getsize(file_path)
        if file_size > settings.MAX_FILE_SIZE:
            MessageHelper.warning(
                parent,
                "文件过大",
                f"图片大小超过限制 ({settings.MAX_FILE_SIZE / 1024 / 1024:.1f}MB)"
            )
            return
        
        # 检查文件格式
        if not settings.allowed_file(file_path):
            MessageHelper.warning(
                parent,
                "格式错误",
                "仅支持 PNG、JPG、JPEG 格式"
            )
            return
        
        # 保存路径和原始图片
        self.current_image_path = file_path
        self.original_pixmap = QPixmap(file_path)
        
        # 更新预览显示
        self.update_preview()
        
        # 更新样式
        if FLUENT_AVAILABLE:
            # 隐藏图标和提示文字，显示预览
            if self.upload_icon:
                self.upload_icon.setVisible(False)
            if self.hint_label:
                self.hint_label.setVisible(False)
            self.preview_label.setVisible(True)
            self._update_drop_card_style(True)
        else:
            self.preview_label.setStyleSheet("""
                QLabel {
                    border: 2px solid #28a745;
                    border-radius: 10px;
                    background-color: white;
                    padding: 5px;
                }
            """)
        
        # 显示文件名
        filename = os.path.basename(file_path)
        self.filename_label.setText(f"已选择: {filename}")
        self.filename_label.setVisible(True)
        
        # 发送信号
        self.image_selected.emit(file_path)
    
    def update_preview(self):
        """更新图片预览，根据可用空间缩放"""
        if self.original_pixmap and not self.original_pixmap.isNull():
            # 获取预览区域的可用大小
            if FLUENT_AVAILABLE and self.drop_card:
                available_width = max(self.drop_card.width() - 40, 200)
                available_height = max(self.drop_card.height() - 40, 150)
            else:
                available_width = max(self.preview_label.width() - 20, 200)
                available_height = max(self.preview_label.height() - 20, 150)
            
            # 缩放图片保持宽高比
            scaled_pixmap = self.original_pixmap.scaled(
                available_width, 
                available_height,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.preview_label.setPixmap(scaled_pixmap)
    
    def resizeEvent(self, event):
        """窗口大小改变时重新缩放图片"""
        super().resizeEvent(event)
        if self.original_pixmap:
            self.update_preview()
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """拖拽进入事件"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            # 高亮预览区域
            if FLUENT_AVAILABLE:
                self._update_drop_card_style(False, is_dragging=True)
            else:
                self.preview_label.setStyleSheet("""
                    QLabel {
                        border: 2px dashed #007bff;
                        border-radius: 10px;
                        background-color: #e7f3ff;
                        color: #007bff;
                    }
                """)
    
    def dragLeaveEvent(self, event):
        """拖拽离开事件"""
        # 恢复预览区域样式
        if FLUENT_AVAILABLE:
            self._update_drop_card_style(self.original_pixmap is not None)
        else:
            if self.original_pixmap:
                self.preview_label.setStyleSheet("""
                    QLabel {
                        border: 2px solid #28a745;
                        border-radius: 10px;
                        background-color: white;
                        padding: 5px;
                    }
                """)
            else:
                self.preview_label.setStyleSheet("""
                    QLabel {
                        border: 2px dashed #ccc;
                        border-radius: 10px;
                        background-color: #f9f9f9;
                    }
                """)
    
    def dropEvent(self, event: QDropEvent):
        """拖放事件"""
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                self.load_image(file_path)
                event.acceptProposedAction()
                return
        
        # 恢复样式
        self.dragLeaveEvent(None)
    
    def clear_image(self):
        """清除已选择的图片"""
        self.current_image_path = None
        self.original_pixmap = None
        
        if FLUENT_AVAILABLE:
            # 显示图标和提示文字，隐藏预览
            if self.upload_icon:
                self.upload_icon.setVisible(True)
            if self.hint_label:
                self.hint_label.setVisible(True)
            self.preview_label.setVisible(False)
            self.preview_label.clear()
            self._update_drop_card_style(False)
        else:
            self.preview_label.clear()
            self.preview_label.setText("拖拽图片到此处\n或点击上方按钮选择")
            self.preview_label.setStyleSheet("""
                QLabel {
                    border: 2px dashed #ccc;
                    border-radius: 10px;
                    background-color: #f9f9f9;
                }
            """)
        
        self.filename_label.setVisible(False)
