#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
上传组件
支持拖拽和点击上传图片
"""

import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, 
    QFileDialog, QGroupBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QDragEnterEvent, QDropEvent

from config.settings import settings


class UploadWidget(QWidget):
    """图片上传组件"""
    
    # 定义信号
    image_selected = pyqtSignal(str)  # 图片路径
    
    def __init__(self, parent=None):
        """初始化上传组件"""
        super().__init__(parent)
        self.current_image_path = None
        self.setup_ui()
        
        # 启用拖拽
        self.setAcceptDrops(True)
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        
        # 创建组框
        group_box = QGroupBox("上传图片")
        group_layout = QVBoxLayout(group_box)
        
        # 拖拽提示区域
        self.drop_label = QLabel("拖拽图片到此处\n或点击下方按钮选择")
        self.drop_label.setAlignment(Qt.AlignCenter)
        self.drop_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #ccc;
                border-radius: 10px;
                padding: 40px;
                background-color: #f9f9f9;
                color: #666;
                font-size: 14px;
            }
        """)
        self.drop_label.setMinimumHeight(150)
        group_layout.addWidget(self.drop_label)
        
        # 选择文件按钮
        self.select_btn = QPushButton("选择图片")
        self.select_btn.clicked.connect(self.select_image)
        self.select_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        group_layout.addWidget(self.select_btn)
        
        # 预览区域
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMaximumHeight(200)
        self.preview_label.setVisible(False)
        group_layout.addWidget(self.preview_label)
        
        # 文件名标签
        self.filename_label = QLabel()
        self.filename_label.setAlignment(Qt.AlignCenter)
        self.filename_label.setStyleSheet("color: #333; font-size: 12px;")
        self.filename_label.setVisible(False)
        group_layout.addWidget(self.filename_label)
        
        layout.addWidget(group_box)
    
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
        # 检查文件大小
        file_size = os.path.getsize(file_path)
        if file_size > settings.MAX_FILE_SIZE:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                "文件过大",
                f"图片大小超过限制 ({settings.MAX_FILE_SIZE / 1024 / 1024:.1f}MB)"
            )
            return
        
        # 检查文件格式
        if not settings.allowed_file(file_path):
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                "格式错误",
                "仅支持 PNG、JPG、JPEG 格式"
            )
            return
        
        # 保存路径
        self.current_image_path = file_path
        
        # 显示预览
        pixmap = QPixmap(file_path)
        scaled_pixmap = pixmap.scaled(
            300, 200,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.preview_label.setPixmap(scaled_pixmap)
        self.preview_label.setVisible(True)
        
        # 显示文件名
        filename = os.path.basename(file_path)
        self.filename_label.setText(f"已选择: {filename}")
        self.filename_label.setVisible(True)
        
        # 隐藏拖拽提示
        self.drop_label.setVisible(False)
        
        # 发送信号
        self.image_selected.emit(file_path)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """拖拽进入事件"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.drop_label.setStyleSheet("""
                QLabel {
                    border: 2px dashed #007bff;
                    border-radius: 10px;
                    padding: 40px;
                    background-color: #e7f3ff;
                    color: #007bff;
                    font-size: 14px;
                }
            """)
    
    def dragLeaveEvent(self, event):
        """拖拽离开事件"""
        self.drop_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #ccc;
                border-radius: 10px;
                padding: 40px;
                background-color: #f9f9f9;
                color: #666;
                font-size: 14px;
            }
        """)
    
    def dropEvent(self, event: QDropEvent):
        """拖放事件"""
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            self.load_image(file_path)
        
        # 恢复样式
        self.dragLeaveEvent(None)
